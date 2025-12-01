# utils/google_drive_simple.py
import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseUpload
import io
import tempfile

class GoogleDriveServiceSimple:
    def __init__(self):
        # In production, store these as environment variables
        self.SERVICE_ACCOUNT_FILE = None  # Path to service account JSON key file
        self.SCOPES = ['https://www.googleapis.com/auth/drive']
        
        # For Render, you can use environment variables to store the service account info
        service_account_info = {
            "type": "service_account",
            "project_id": os.getenv('GOOGLE_PROJECT_ID'),
            "private_key_id": os.getenv('GOOGLE_PRIVATE_KEY_ID'),
            "private_key": os.getenv('GOOGLE_PRIVATE_KEY', '').replace('\\n', '\n'),
            "client_email": os.getenv('GOOGLE_CLIENT_EMAIL'),
            "client_id": os.getenv('GOOGLE_CLIENT_ID'),
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_x509_cert_url": os.getenv('GOOGLE_CLIENT_X509_CERT_URL')
        }
        
        self.creds = service_account.Credentials.from_service_account_info(
            service_account_info, 
            scopes=self.SCOPES
        )
        
        self.service = build('drive', 'v3', credentials=self.creds)
        self.folder_id = self.ensure_folder_exists()
    
    def ensure_folder_exists(self, folder_name="Certificate_QR_Codes"):
        """Ensure the folder exists in Google Drive"""
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
                return folders[0]['id']
            
            # Create new folder
            folder_metadata = {
                'name': folder_name,
                'mimeType': 'application/vnd.google-apps.folder'
            }
            
            folder = self.service.files().create(
                body=folder_metadata,
                fields='id'
            ).execute()
            
            return folder.get('id')
            
        except Exception as error:
            print(f"Error ensuring folder exists: {error}")
            # Fallback to a default folder
            return 'root'
    
    def upload_qr_code(self, qr_image_bytes, file_name):
        """Upload QR code image to Google Drive"""
        try:
            file_metadata = {
                'name': file_name,
                'parents': [self.folder_id]
            }
            
            # Create a media upload
            file_obj = io.BytesIO(qr_image_bytes)
            media = MediaIoBaseUpload(file_obj, mimetype='image/png', resumable=True)
            
            # Upload file
            file = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id, webViewLink, webContentLink'
            ).execute()
            
            # Make the file publicly accessible
            self.service.permissions().create(
                fileId=file['id'],
                body={'type': 'anyone', 'role': 'reader'}
            ).execute()
            
            # Return the direct view link
            return f"https://drive.google.com/uc?export=view&id={file['id']}"
            
        except Exception as error:
            print(f"Error uploading to Google Drive: {error}")
            # Fallback: Save locally (temporarily for Render)
            temp_dir = '/tmp/qrcodes'
            os.makedirs(temp_dir, exist_ok=True)
            temp_path = os.path.join(temp_dir, file_name)
            with open(temp_path, 'wb') as f:
                f.write(qr_image_bytes)
            return f"/tmp/qrcodes/{file_name}"
    
    def delete_file_by_url(self, file_url):
        """Delete a file from Google Drive using its URL"""
        try:
            # Extract file ID from URL
            if 'id=' in file_url:
                file_id = file_url.split('id=')[-1].split('&')[0]
                self.service.files().delete(fileId=file_id).execute()
                return True
        except Exception as error:
            print(f"Error deleting file: {error}")
        return False

# Global instance
drive_service = GoogleDriveServiceSimple()