from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import Project, ProjectFile
from user_account.models import Event
from .serializers import ProjectSerializer, ProjectFileSerializer
from .google_api import create_google_doc, create_google_sheet, create_google_slides, create_google_form, delete_google_file
from rest_framework.permissions import IsAuthenticated

class ProjectListView(APIView):
    """
    API представление для работы со списком проектов.
    Возвращает только корневые проекты (без родительского проекта).
    
    Методы:
        get: Получение списка всех корневых проектов
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        projects = Project.objects.filter(parent_project__isnull=True)
        serializer = ProjectSerializer(projects, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    

class ProjectDetailView(APIView):
    """
    API представление для работы с отдельным проектом.
    
    Методы:
        get: Получение детальной информации о проекте
        delete: Удаление проекта
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        project = get_object_or_404(Project, pk=pk)
        serializer = ProjectSerializer(project)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def delete(self, request, pk):
            project = get_object_or_404(Project, pk=pk)
            project.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

class CreateProjectView(APIView):
    """
    API представление для создания нового проекта.
    Поддерживает создание как корневого проекта, так и подпроекта.
    
    Методы:
        post: Создание нового проекта
            Параметры:
                parent_id: ID родительского проекта (опционально)
                event_id: ID связанного мероприятия (опционально)
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, parent_id=None):
        parent_project = None
        event_id = request.data.get('event_id')
        if parent_id:
            parent_project = get_object_or_404(Project, pk=parent_id)
        
        serializer = ProjectSerializer(data=request.data)
        if serializer.is_valid():
            project = serializer.save()
            if parent_project:
                project.parent_project = parent_project
                project.save()
            if event_id:
                event = get_object_or_404(Event, id=event_id)
                event.projects.add(project)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CreateGoogleDocumentView(APIView):
    """
    API представление для создания и управления документами Google Workspace,
    связанными с проектом.
    
    Методы:
        post: Создание нового документа Google Workspace или добавление внешней ссылки
            Параметры:
                doc_type: Тип документа ('doc', 'sheet', 'slide', 'form', 'link')
                title: Название документа
                custom_name: Пользовательское имя файла (опционально)
                file_url: URL для внешней ссылки (только для doc_type='link')
        
        delete: Удаление документа
            - Для внешних ссылок: удаление только из базы данных
            - Для Google Workspace: удаление из Google Drive и базы данных
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, project_id):
        doc_type = request.data.get('doc_type')
        title = request.data.get('title')
        custom_name = request.data.get('custom_name')
        file_url = request.data.get('file_url')

        if not doc_type or not title:
            return Response({"error": "doc_type and title are required fields."}, status=status.HTTP_400_BAD_REQUEST)

        if doc_type == 'link':
            if not file_url:
                return Response({'error': 'file_url is required for link'}, status=400)
            project = get_object_or_404(Project, pk=project_id)
            project_file = ProjectFile.objects.create(
                project=project,
                file_type='Ссылка',
                file_url=file_url,
                file_name=custom_name or title
            )
            file_serializer = ProjectFileSerializer(project_file)
            return Response(file_serializer.data, status=status.HTTP_201_CREATED)

        file_id, file_type, file_url = None, None, None
        if doc_type == 'doc':
            file_id = create_google_doc(title)
            file_type = 'Документ'
            file_url = f'https://docs.google.com/document/d/{file_id}/edit'
        elif doc_type == 'sheet':
            file_id = create_google_sheet(title)
            file_type = 'Таблица'
            file_url = f'https://docs.google.com/spreadsheets/d/{file_id}/edit'
        elif doc_type == 'slide':
            file_id = create_google_slides(title)
            file_type = 'Презентация'
            file_url = f'https://docs.google.com/presentation/d/{file_id}/edit'
        elif doc_type == 'form':
            file_id = create_google_form(title)
            file_type = 'Форма'
            file_url = f'https://docs.google.com/forms/d/{file_id}/edit'
        else:
            return Response({'error': 'Invalid doc_type'}, status=status.HTTP_400_BAD_REQUEST)

        project = get_object_or_404(Project, pk=project_id)
        project_file = ProjectFile.objects.create(
            project=project,
            file_type=file_type,
            file_url=file_url,
            file_name=custom_name or title
        )
        file_serializer = ProjectFileSerializer(project_file)
        return Response(file_serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, file_id):
        try:
            project_file = get_object_or_404(ProjectFile, id=file_id)
            # Если это ссылка, просто удаляем из базы
            if project_file.file_type == 'Ссылка':
                project_file.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            # Для остальных файлов — удаляем из Google Drive
            file_url = project_file.file_url
            google_file_id = file_url.split('/')[-2]  # Получаем ID файла из URL
            if delete_google_file(google_file_id):
                project_file.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            else:
                return Response({"error": "Failed to delete file from Google Drive."}, 
                              status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
