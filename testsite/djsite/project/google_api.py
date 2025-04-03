import os
import pickle
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from django.conf import settings
from google.oauth2 import service_account
from googleapiclient.errors import HttpError

CLIENT_SECRETS_FILE = os.path.join(settings.BASE_DIR, "client_secret.json")
SCOPES = [
    'https://www.googleapis.com/auth/drive',
    'https://www.googleapis.com/auth/forms.body',
    'https://www.googleapis.com/auth/documents',
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/presentations',
]
credentials = service_account.Credentials.from_service_account_file(
    CLIENT_SECRETS_FILE, scopes=SCOPES
)

def make_file_public(file_id):
    drive_service = build('drive', 'v3', credentials=credentials)

    permission = {
        'type': 'anyone',   # Доступ для всех
        'role': 'writer'    # Только чтение (можно заменить на 'writer', если нужен полный доступ)
    }

    try:
        drive_service.permissions().create(
            fileId=file_id,
            body=permission
        ).execute()
        print(f"Доступ открыт для всех: https://drive.google.com/file/d/{file_id}/view")
    except HttpError as error:
        print(f"Ошибка при изменении прав доступа: {error}")
'''
def authenticate_google():
    creds = None
    token_path = os.path.join(settings.BASE_DIR, 'token.pickle')

    if os.path.exists(token_path):
        with open(token_path, 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())else:
            flow = InstalledAppFlow.from_client_secrets_file(
                CLIENT_SECRETS_FILE, SCOPES
            )
            creds = flow.run_local_server(port=0)
        with open(token_path, 'wb') as token:
            pickle.dump(creds, token)

    return creds
'''
def create_google_doc(title):
    global credentials
    #creds = authenticate_google()
    service = build('docs', 'v1', credentials=credentials)
    document = {'title': title}
    doc = service.documents().create(body=document).execute()
    doc_id = doc.get('documentId')
    make_file_public(doc_id)
    return doc_id

def create_google_sheet(title):
    global credentials
    #creds = authenticate_google()
    service = build('sheets', 'v4', credentials=credentials)
    spreadsheet = {'properties': {'title': title}}
    sheet = service.spreadsheets().create(body=spreadsheet).execute()
    sheet_id = sheet.get('spreadsheetId')
    make_file_public(sheet_id)
    return sheet_id

def create_google_slides(title):
    global credentials
    #creds = authenticate_google()
    service = build('slides', 'v1', credentials=credentials)
    presentation = {'title': title}
    slide = service.presentations().create(body=presentation).execute()
    slides_id = slide.get('presentationId')
    make_file_public(slides_id)
    return slides_id

def create_google_form(title):
    global credentials
    #creds = authenticate_google()
    service = build('forms', 'v1', credentials=credentials)
    form = {'info': {'title': title}}
    form_result = service.forms().create(body=form).execute()
    form_id = form_result.get('formId')
    make_file_public(form_id)
    return form_id