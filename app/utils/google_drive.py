# utils/google_drive.py
import os
import io
import pickle
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from flask import session, redirect, url_for, request as flask_request

class GoogleDriveService:
    def __init__(self, app=None):
        self.app = app
        self.SCOPES = ['https://www.googleapis.com/auth/drive.file']
        self.credentials = None
        self.service = None
        self.folder_id = None
        
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        self.app = app
        # Load credentials if they exist
        self._load_credentials()
    
    def _load_credentials(self):
        """Load credentials from session or token file"""
        try:
            # Try to get from session (for web flow)
            if self.app and 'google_credentials' in session:
                creds_dict = session['google_credentials']
                self.credentials = Credentials.from_authorized_user_info(creds_dict, self.SCOPES)
            
            # Try to load from token.pickle (for CLI/background)
            elif os.path.exists('token.pickle'):
                with open('token.pickle', 'rb') as token:
                    self.credentials = pickle.load(token)
            
            if self.credentials and self.credentials.valid:
                self.service = build('drive', 'v3', credentials=self.credentials)
                return True
                
            # If credentials are expired, refresh them
            if self.credentials and self.credentials.expired and self.credentials.refresh_token:
                self.credentials.refresh(Request())
                self._save_credentials()
                self.service = build('drive', 'v3', credentials=self.credentials)
                return True
                
        except Exception as e:
            print(f"Error loading credentials: {e}")
        
        return False
    
    def _save_credentials(self):
        """Save credentials to session and file"""
        if self.credentials:
            # Save to session for web
            if self.app:
                session['google_credentials'] = {
                    'token': self.credentials.token,
                    'refresh_token': self.credentials.refresh_token,
                    'token_uri': self.credentials.token_uri,
                    'client_id': self.credentials.client_id,
                    'client_secret': self.credentials.client_secret,
                    'scopes': self.credentials.scopes
                }
            
            # Save to file for background tasks
            with open('token.pickle', 'wb') as token:
                pickle.dump(self.credentials, token)
    
    def get_authorization_url(self):
        """Get OAuth2 authorization URL"""
        flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": os.getenv('GOOGLE_CLIENT_ID', '1936528-nspdgsobqd87.apps.googleusercontent.com'),
                    "client_secret": os.getenv('GOOGLE_CLIENT_SECRET', 'GOCSPX-xjLHYHFkq'),
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": [os.getenv('GOOGLE_REDIRECT_URI', 'http://localhost:5000/oauth2callback')]
                }
            },
            scopes=self.SCOPES,
            redirect_uri=os.getenv('GOOGLE_REDIRECT_URI', 'http://localhost:5000/oauth2callback')
        )
        
        authorization_url, state = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
            prompt='consent'  # Force consent to get refresh token
        )
        
        if self.app:
            session['oauth_state'] = state
        
        return authorization_url
    
    def handle_callback(self, authorization_response):
        """Handle OAuth2 callback"""
        try:
            flow = Flow.from_client_config(
                {
                    "web": {
                        "client_id": os.getenv('GOOGLE_CLIENT_ID', '1936528-nspdgsobqd87.apps.googleusercontent.com'),
                        "client_secret": os.getenv('GOOGLE_CLIENT_SECRET', 'GOCSPX-xjLHYHFkq'),
                        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                        "token_uri": "https://oauth2.googleapis.com/token",
                        "redirect_uris": [os.getenv('GOOGLE_REDIRECT_URI', 'http://localhost:5000/oauth2callback')]
                    }
                },
                scopes=self.SCOPES,
                redirect_uri=os.getenv('GOOGLE_REDIRECT_URI', 'http://localhost:5000/oauth2callback'),
                state=session.get('oauth_state')
            )
            
            flow.fetch_token(authorization_response=authorization_response)
            self.credentials = flow.credentials
            self._save_credentials()
            self.service = build('drive', 'v3', credentials=self.credentials)
            return True
            
        except Exception as e:
            print(f"Error in callback: {e}")
            return False
    
    def ensure_folder_exists(self, folder_name="Certificate_QR_Codes"):
        """Ensure folder exists in Google Drive"""
        if self.folder_id:
            return self.folder_id
        
        if not self.service:
            raise Exception("Google Drive not authenticated")
        
        try:
            # Search for existing folder
            query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
            results = self.service.files().list(
                q=query,
                spaces='drive',
                fields='files(id, name)'
            ).execute()
            
            folders = results.get('files', [])
            
            if folders:
                self.folder_id = folders[0]['id']
                return self.folder_id
            
            # Create new folder
            folder_metadata = {
                'name': folder_name,
                'mimeType': 'application/vnd.google-apps.folder'
            }
            
            folder = self.service.files().create(
                body=folder_metadata,
                fields='id'
            ).execute()
            
            self.folder_id = folder.get('id')
            return self.folder_id
            
        except Exception as e:
            print(f"Error creating folder: {e}")
            return None
    
    def upload_file(self, file_bytes, filename, mime_type='image/png'):
        """Upload file to Google Drive"""
        if not self.service:
            raise Exception("Google Drive not authenticated")
        
        try:
            folder_id = self.ensure_folder_exists()
            if not folder_id:
                raise Exception("Could not create folder")
            
            file_metadata = {
                'name': filename,
                'parents': [folder_id]
            }
            
            file_obj = io.BytesIO(file_bytes)
            media = MediaIoBaseUpload(file_obj, mimetype=mime_type)
            
            # Upload file
            file = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id, name, webViewLink, webContentLink'
            ).execute()
            
            # Make file publicly readable
            self.service.permissions().create(
                fileId=file['id'],
                body={
                    'type': 'anyone',
                    'role': 'reader',
                    'allowFileDiscovery': False
                }
            ).execute()
            
            # Return direct view link
            return f"https://drive.google.com/uc?export=view&id={file['id']}"
            
        except Exception as e:
            print(f"Error uploading to Google Drive: {e}")
            raise
    
    def delete_file(self, file_url):
        """Delete file from Google Drive"""
        if not self.service:
            return False
        
        try:
            # Extract file ID from URL
            file_id = None
            if 'id=' in file_url:
                file_id = file_url.split('id=')[1].split('&')[0]
            
            if file_id:
                self.service.files().delete(fileId=file_id).execute()
                return True
        except Exception as e:
            print(f"Error deleting file: {e}")
        
        return False

# Create global instance
drive_service = GoogleDriveService()