from django.shortcuts import render, get_object_or_404, redirect
from .models import Project, ProjectFile
from django.http import HttpResponse
from .google_api import create_google_doc, create_google_sheet, create_google_slides, create_google_form
import os
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from .forms import ProjectForm  
from django.conf import settings

def project_list(request):
    projects = Project.objects.all()
    return render(request, 'project/project_list.html', {'projects': projects})

def project_detail(request, pk):
    project = get_object_or_404(Project, pk=pk)
    return render(request, 'project/project_detail.html', {'project': project})

def create_project(request, parent_id=None):
    parent_project = None
    if parent_id:
        parent_project = get_object_or_404(Project, pk=parent_id)

    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            if parent_project:
                project.parent_project = parent_project
            project.save()
            return redirect('project_detail', pk=project.pk)
    else:
        form = ProjectForm()

    return render(request, 'project/create_project.html', {'form': form, 'parent_project': parent_project})

def create_google_document(request, project_id):
    if request.method == 'POST':
        doc_type = request.POST.get('doc_type')
        title = request.POST.get('title')
        custom_name = request.POST.get('custom_name')
        print("Custom Name:", custom_name)

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
            return HttpResponse('Некорректный тип документа', status=400)

        project = Project.objects.get(pk=project_id)
        ProjectFile.objects.create(
            project=project,
            file_type=file_type,
            file_url=file_url,
            file_name=custom_name or title
        )
        return redirect('project_detail', pk=project_id)
    return render(request, 'project/create_google_document.html', {'project_id': project_id})

def get_google_service(service_name, version, scopes):
    credentials_path = settings.GOOGLE_APPLICATION_CREDENTIALS
    flow = InstalledAppFlow.from_client_secrets_file(credentials_path, scopes)
    creds = flow.run_local_server(port=8080)
    service = build(service_name, version, credentials=creds)
    return service

def create_google_doc(title):
    service = get_google_service('docs', 'v1', ['https://www.googleapis.com/auth/documents'])
    document = {'title': title}
    doc = service.documents().create(body=document).execute()
    return doc.get('documentId')

def create_google_sheet(title):
    service = get_google_service('sheets', 'v4', ['https://www.googleapis.com/auth/spreadsheets'])
    spreadsheet = {'properties': {'title': title}}
    sheet = service.spreadsheets().create(body=spreadsheet).execute()
    return sheet.get('spreadsheetId')

def create_google_slides(title):
    service = get_google_service('slides', 'v1', ['https://www.googleapis.com/auth/presentations'])
    presentation = {'title': title}
    slide = service.presentations().create(body=presentation).execute()
    return slide.get('presentationId')

def create_google_form(title):
    service = get_google_service('forms', 'v1', ['https://www.googleapis.com/auth/forms.body'])
    form = {'info': {'title': title}}
    form_result = service.forms().create(body=form).execute()
    return form_result.get('formId')