import os
import pickle
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Если изменится эти области доступа, удалите файл token.pickle.
CLIENT_SECRETS_FILE = "client_secret_325098205139-bci6rof494bl4u7ur59vioa478hu15p5.apps.googleusercontent.com.json"
SCOPES = ['https://www.googleapis.com/auth/drive.file']

def authenticate_google():
    creds = None
    # Файл token.pickle хранит токен доступа и обновления пользователя.
    # Он создается автоматически при авторизации.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # Если нет действительных учетных данных, запрашиваем новые
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Сохраняем учетные данные для последующего использования
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    return creds

def create_google_doc(title):
    creds = authenticate_google()
    service = build('drive', 'v3', credentials=creds)
    
    file_metadata = {
        'name': title,
        'mimeType': 'application/vnd.google-apps.document'
    }
    file = service.files().create(body=file_metadata, fields='id').execute()
    return file.get('id')

def create_google_sheet(title):
    creds = authenticate_google()
    service = build('drive', 'v3', credentials=creds)
    
    file_metadata = {
        'name': title,
        'mimeType': 'application/vnd.google-apps.spreadsheet'
    }
    file = service.files().create(body=file_metadata, fields='id').execute()
    return file.get('id')

def create_google_slide(title):
    creds = authenticate_google()
    service = build('drive', 'v3', credentials=creds)
    
    file_metadata = {
        'name': title,
        'mimeType': 'application/vnd.google-apps.presentation'
    }
    file = service.files().create(body=file_metadata, fields='id').execute()
    return file.get('id')