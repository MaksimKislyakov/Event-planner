from django.shortcuts import render, get_object_or_404, redirect
from .models import Project, ProjectFile
from django.http import HttpResponse
from .google_api import create_google_doc, create_google_sheet, create_google_slide
import os
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from django.conf import settings

def project_list(request):
    projects = Project.objects.all()
    return render(request, 'project/project_list.html', {'projects': projects})

def project_detail(request, pk):
    project = get_object_or_404(Project, pk=pk)
    return render(request, 'project/project_detail.html', {'project': project})

def create_google_document(request, project_id):

    if request.method == 'POST':
        doc_type = request.POST.get('doc_type')
        title = request.POST.get('title')
        if doc_type == 'doc':
            file_id = create_google_doc(title)
            file_type = 'Документ'
        elif doc_type == 'sheet':
            file_id = create_google_sheet(title)
            file_type = 'Таблица'
        elif doc_type == 'slide':
            file_id = create_google_slide(title)
            file_type = 'Презентация'
        else:
            return HttpResponse('Некорректный тип документа', status=400)

        # Сохраняем информацию о созданном файле в базу данных
        project = Project.objects.get(pk=project_id)
        ProjectFile.objects.create(
            project=project,
            file_type=file_type,
            file_url=f'https://docs.google.com/document/d/{file_id}/edit'
        )
        return redirect('project_detail', pk=project_id)
    return render(request, 'project/create_google_document.html', {'project_id': project_id})   


def get_google_service():
    credentials_path = settings.GOOGLE_APPLICATION_CREDENTIALS
    flow = InstalledAppFlow.from_client_secrets_file(
        credentials_path,
        scopes=['https://www.googleapis.com/auth/documents', 
                'https://www.googleapis.com/auth/spreadsheets', 
                'https://www.googleapis.com/auth/presentations']
    )
    creds = flow.run_local_server(port=8080)
    service = build('docs', 'v1', credentials=creds)
    return service

def create_google_doc(title):
    service = get_google_service()
    document = {
        'title': title
    }
    doc = service.documents().create(body=document).execute()
    return doc.get('documentId')

def create_google_sheet(title):
    service = build('sheets', 'v4', credentials=get_google_service().credentials)
    spreadsheet = {
        'properties': {
            'title': title
        }
    }
    sheet = service.spreadsheets().create(body=spreadsheet).execute()
    return sheet.get('spreadsheetId')

def create_google_slide(title):
    service = build('slides', 'v1', credentials=get_google_service().credentials)
    presentation = {
        'title': title
    }
    slide = service.presentations().create(body=presentation).execute()
    return slide.get('presentationId')

    
    