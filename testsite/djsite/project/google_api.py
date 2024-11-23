import os
import pickle
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from django.conf import settings

CLIENT_SECRETS_FILE = os.path.join(settings.BASE_DIR, "client_secret.json")
SCOPES = [
    'https://www.googleapis.com/auth/drive.file',
    'https://www.googleapis.com/auth/forms.body',
    'https://www.googleapis.com/auth/documents',
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/presentations',
]

def authenticate_google():
    creds = None
    token_path = os.path.join(settings.BASE_DIR, 'token.pickle')  

    if os.path.exists(token_path):
        with open(token_path, 'rb') as token:
            creds = pickle.load(token)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                CLIENT_SECRETS_FILE, SCOPES
            )
            creds = flow.run_local_server(port=0)
        with open(token_path, 'wb') as token:
            pickle.dump(creds, token)
    
    return creds

def create_google_doc(title):
    creds = authenticate_google()
    service = build('docs', 'v1', credentials=creds)
    document = {'title': title}
    doc = service.documents().create(body=document).execute()
    return doc.get('documentId')

def create_google_sheet(title):
    creds = authenticate_google()
    service = build('sheets', 'v4', credentials=creds)
    spreadsheet = {'properties': {'title': title}}
    sheet = service.spreadsheets().create(body=spreadsheet).execute()
    return sheet.get('spreadsheetId')

def create_google_slides(title):
    creds = authenticate_google()
    service = build('slides', 'v1', credentials=creds)
    presentation = {'title': title}
    slide = service.presentations().create(body=presentation).execute()
    return slide.get('presentationId')

def create_google_form(title):
    creds = authenticate_google()
    service = build('forms', 'v1', credentials=creds)
    form = {'info': {'title': title}}
    form_result = service.forms().create(body=form).execute()
    return form_result.get('formId')
