from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import Project, ProjectFile
from user_account.models import Event
from .serializers import ProjectSerializer, ProjectFileSerializer
from .google_api import create_google_doc, create_google_sheet, create_google_slides, create_google_form
from rest_framework.permissions import IsAuthenticated

class ProjectListView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        projects = Project.objects.filter(parent_project__isnull=True)
        serializer = ProjectSerializer(projects, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class ProjectDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        project = get_object_or_404(Project, pk=pk)
        serializer = ProjectSerializer(project)
        return Response(serializer.data, status=status.HTTP_200_OK)

class CreateProjectView(APIView):
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
    permission_classes = [IsAuthenticated]

    def post(self, request, project_id):
        doc_type = request.data.get('doc_type')
        title = request.data.get('title')
        custom_name = request.data.get('custom_name')

        if not doc_type or not title:
            return Response({"error": "doc_type and title are required fields."}, status=status.HTTP_400_BAD_REQUEST)

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
