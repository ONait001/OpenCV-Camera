from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import os

def upload_video(video_path):
    """Uploads recorded video to Google Drive."""
    try:
        gauth = GoogleAuth()
        gauth.LocalWebserverAuth()  # Authenticate Google Drive
        drive = GoogleDrive(gauth)

        file = drive.CreateFile({"title": os.path.basename(video_path)})
        file.SetContentFile(video_path)
        file.Upload()
        
        print(f"Uploaded {video_path} to Google Drive")
    except Exception as e:
        print(f"Failed to upload {video_path}: {e}")
