import os

import requests
import yaml
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive


def read_yaml_settings_file(settings_path: str = 'settings.yaml'):
    with open(settings_path, 'r') as stream:
        try:
            return (yaml.safe_load(stream))
        except yaml.YAMLError as exc:
            print(exc)
            return {}


def build_gauth_authentication():
    gauth = GoogleAuth()
    gauth.LocalWebserverAuth()
    return gauth


def get_candidate_files_from_drive_folder(drive_folder_link, gauth_authentication):
    drive = GoogleDrive(gauth_authentication)
    folder_id = os.path.basename(drive_folder_link)
    query = f"""parents="{folder_id}"
                            AND trashed=False
                     AND mimeType contains 'image/'
                     AND NOT fullText contains 'failed'
                     AND NOT fullText contains 'success'"""
    for file_list in drive.ListFile({"q": query}):
        yield from file_list


def detect_text_gdrive(gdrive_url, service_account_file):
    from google.cloud import vision
    client = vision.ImageAnnotatorClient.from_service_account_file(service_account_file)
    with requests.get(gdrive_url) as image_file:
        content = image_file.content
    image = vision.types.Image(content=content)
    response = client.text_detection(image=image)

    return response.text_annotation, response.full_text_annotation
