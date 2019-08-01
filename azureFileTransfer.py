import json
from azure.storage.file import FileService

STORAGE_ACCOUNT_NAME = 'csae48d5df47deax41bcxbaa'
STORAGE_ACCOUNT_KEY = 'iUTL5cLSDTObfUliySlqjT4x1dfCQ1U7l7zuaZrPEwhGIHnHPKWfYuFrq16cCjFUS/122mcwJpdseC9JI6mSGA=='
   
SHARE_NAME = 'testingazure' #or 'cs-william-squarev-media-10037ffe909d3982'
PROJECT_NAME = ' FinalSubclipJson.json'

def create_share_dir(proj_id):
    """Creates a directory at the share location"""
    file_service = FileService(
        account_name=STORAGE_ACCOUNT_NAME,
        account_key=STORAGE_ACCOUNT_KEY
    )

    file_service.create_share(SHARE_NAME)

    file_service.create_directory(SHARE_NAME, proj_id)

    return file_service


def upload_proj(proj_id, local_path, file_service):
    """Uploads the file found at the local_path to the share under the directory of id"""
    file_service.create_file_from_path(
        SHARE_NAME,
        proj_id,
        PROJECT_NAME,
        local_path
    )


def upload_file(proj_id, name, local_path, file_service):
    """Uploads a generic file to the File Share, given name, local path, & project id"""
    file_service.create_file_from_path(
        SHARE_NAME,
        proj_id,
        name,
        local_path
    )


def get_json(proj_id, file_service):
    """Looks for directory in azure storage with the project id specified, and returns the json data
    (JSON data is returned as string first, then converted to json with corresponding python library)"""

    azure_file = file_service.get_file_to_text(
        SHARE_NAME,
        proj_id,
        PROJECT_NAME
    ).content

    json_data = json.loads(azure_file)

    return json_data
