import os
from googleapiclient.discovery import build
from django.conf import settings
from google.oauth2 import service_account

CLIENT_SECRETS_FILE = os.path.join(settings.BASE_DIR, "client_secret.json")
SCOPES = [
    'https://www.googleapis.com/auth/drive.file',
    'https://www.googleapis.com/auth/forms.body',
    'https://www.googleapis.com/auth/documents',
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/presentations',
]

credentials = service_account.Credentials.from_service_account_file(
    CLIENT_SECRETS_FILE, scopes=SCOPES
)

def create_google_doc(title):
    # creds = authenticate_google()
    service = build('docs', 'v1', credentials=credentials)
    document = {'title': title}
    doc = service.documents().create(body=document).execute()
    return doc.get('documentId')

def create_google_sheet(title):
    # creds = authenticate_google()
    service = build('sheets', 'v4', credentials=credentials)
    spreadsheet = {'properties': {'title': title}}
    sheet = service.spreadsheets().create(body=spreadsheet).execute()
    return sheet.get('spreadsheetId')

def create_google_slides(title):
    # creds = authenticate_google()
    service = build('slides', 'v1', credentials=credentials)
    presentation = {'title': title}
    slide = service.presentations().create(body=presentation).execute()
    return slide.get('presentationId')

def create_google_form(title):
    # creds = authenticate_google()
    service = build('forms', 'v1', credentials=credentials)
    form = {'info': {'title': title}}
    form_result = service.forms().create(body=form).execute()
    return form_result.get('formId')
