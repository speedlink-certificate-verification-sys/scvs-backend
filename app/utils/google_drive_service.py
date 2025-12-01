import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
from googleapiclient.errors import HttpError
import io
import pickle
import tempfile
from pathlib import Path

class GoogleDriveService:
    def __init__(self):
        self.SCOPES = ['https://www.googleapis.com/auth/drive.file']
        self.creds = None
        self.service = None
        self.folder_id = None
        self._authenticate()
    
    def _authenticate(self):
        """Authenticate and create Google Drive service"""
        # Try to load existing credentials
        creds_path = os.path.join(tempfile.gettempdir(), 'google_drive_token.pickle')
        
        if os.path.exists(creds_path):
            with open(creds_path, 'rb') as token:
                self.creds = pickle.load(token)
        
        # If credentials are invalid or don't exist, get new ones
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                # IMPORTANT: Replace these with your actual credentials
                # You should store these in environment variables
                client_config = {
                    "web": {
                        "client_id": os.getenv('GOOGLE_DRIVE_CLIENT_ID', '1936528-nspdgsobqd87.apps.googleusercontent.com'),
                        "client_secret": os.getenv('GOOGLE_DRIVE_CLIENT_SECRET', 'GOCSPX-xjLHYHFkq'),
                        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                        "token_uri": "https://oauth2.googleapis.com/token",
                        "redirect_uris": [os.getenv('GOOGLE_DRIVE_REDIRECT_URI', 'https://cert-verify.speedlinkng.com')]
                    }
                }
                
                flow = Flow.from_client_config(
                    client_config,
                    scopes=self.SCOPES,
                    redirect_uri=client_config['web']['redirect_uris'][0]
                )
                
                # In production, you'll need to get the authorization URL
                # and handle the callback to get the code
                auth_url, _ = flow.authorization_url(prompt='consent')
                
                # For now, we'll create a simple auth flow
                # In your actual app, you'll need to implement the OAuth2 flow
                print(f"Please visit this URL to authorize the application: {auth_url}")
                # After authorization, you'll get a code that needs to be exchanged for tokens
                # This is usually handled via a callback route in your Flask app
            
            # Save credentials for future use
            with open(creds_path, 'wb') as token:
                pickle.dump(self.creds, token)
        
        self.service = build('drive', 'v3', credentials=self.creds)
    
    def ensure_folder_exists(self, folder_name="Certificate_QR_Codes"):
        """Ensure the folder exists in Google Drive, create if not"""
        if self.folder_id:
            return self.folder_id
        
        try:
            # Search for existing folder
            query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
            response = self.service.files().list(
                q=query,
                spaces='drive',
                fields='files(id, name)'
            ).execute()
            
            folders = response.get('files', [])
            
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
            
        except HttpError as error:
            print(f"An error occurred: {error}")
            return None
    
    def upload_file(self, file_path, file_name, mime_type='image/png'):
        """Upload a file to Google Drive"""
        try:
            folder_id = self.ensure_folder_exists()
            
            file_metadata = {
                'name': file_name,
                'parents': [folder_id]
            }
            
            media = MediaFileUpload(file_path, mimetype=mime_type)
            
            file = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id, webViewLink'
            ).execute()
            
            # Make the file publicly accessible
            self.service.permissions().create(
                fileId=file['id'],
                body={'type': 'anyone', 'role': 'reader'}
            ).execute()
            
            return {
                'file_id': file['id'],
                'web_view_link': file['webViewLink'],
                'direct_link': f"https://drive.google.com/uc?export=view&id={file['id']}"
            }
            
        except HttpError as error:
            print(f"An error occurred: {error}")
            return None
    
    def upload_file_from_memory(self, file_data, file_name, mime_type='image/png'):
        """Upload a file from memory (BytesIO) to Google Drive"""
        try:
            folder_id = self.ensure_folder_exists()
            
            file_metadata = {
                'name': file_name,
                'parents': [folder_id]
            }
            
            # Create a temporary file
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
            temp_file.write(file_data)
            temp_file.close()
            
            media = MediaFileUpload(temp_file.name, mimetype=mime_type)
            
            file = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id, webViewLink, webContentLink'
            ).execute()
            
            # Clean up temp file
            os.unlink(temp_file.name)
            
            # Make the file publicly accessible
            self.service.permissions().create(
                fileId=file['id'],
                body={'type': 'anyone', 'role': 'reader'}
            ).execute()
            
            # Get the direct download link
            direct_link = f"https://drive.google.com/uc?export=download&id={file['id']}"
            view_link = f"https://drive.google.com/uc?export=view&id={file['id']}"
            
            return {
                'file_id': file['id'],
                'web_view_link': file['webViewLink'],
                'direct_link': direct_link,
                'view_link': view_link
            }
            
        except HttpError as error:
            print(f"An error occurred: {error}")
            return None
    
    def delete_file(self, file_id):
        """Delete a file from Google Drive"""
        try:
            self.service.files().delete(fileId=file_id).execute()
            return True
        except HttpError as error:
            print(f"An error occurred: {error}")
            return False
    
    def update_file(self, file_id, new_file_path, new_file_name=None):
        """Update a file in Google Drive"""
        try:
            file_metadata = {}
            if new_file_name:
                file_metadata['name'] = new_file_name
            
            media = MediaFileUpload(new_file_path, resumable=True)
            
            updated_file = self.service.files().update(
                fileId=file_id,
                body=file_metadata,
                media_body=media,
                fields='id, webViewLink'
            ).execute()
            
            return {
                'file_id': updated_file['id'],
                'web_view_link': updated_file['webViewLink']
            }
            
        except HttpError as error:
            print(f"An error occurred: {error}")
            return None

# Global instance
drive_service = GoogleDriveService()