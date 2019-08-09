# Config.py
import os


# Config file
class Config(object):
    # TODO: Change this location to the azure file share mount location
    DIR_LOCATION = os.environ.get('DIR_LOCATION') or "/mnt/csae48d5df47deax41bcxbaa/videos"
    DIR_LOCATION = os.environ.get('DIR_LOCATION') or "G:/project"
    # Defining storage name and key
    STORAGE_ACCOUNT_NAME = os.environ.get('STORAGE_ACCOUNT_NAME') or 'csae48d5df47deax41bcxbaa'
    STORAGE_ACCOUNT_KEY = os.environ.get('STORAGE_ACCOUNT_KEY') or \
        'iUTL5cLSDTObfUliySlqjT4x1dfCQ1U7l7zuaZrPEwhGIHnHPKWfYuFrq16cCjFUS/122mcwJpdseC9JI6mSGA=='
    # TODO: When deploying, remove 'testingazure' for the commented out Share Name
    SHARE_NAME = os.environ.get('SHARE_NAME') or 'cs-william-squarev-media-10037ffe909d3982' #'testingazure'  # 
    # Defining name of json file containing edits
    PROJECT_NAME = os.environ.get('PROJECT_NAME') or 'FinalSubclipJson.json'
    # TODO: The location of the resources (the silence mp3, default templates, etc.) may change
    # Defining location of generic 'resources' location
    RESOURCE_PATH = os.environ.get('RESOURCE_PATH') or 'resource'
    # Name of silence mp3
    SILENCE = os.environ.get('SILENCE') or 'silence.mp3'
    QUEUE_FOLDER = os.environ.get('QUEUE_FOLDER') or 'renderQueue'
