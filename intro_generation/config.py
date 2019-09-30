import os


class Config(object):
    # Secret key used for verification
    # or statements are used as a fallback
    SECRET_KEY = os.environ.get('SECRET_KEY') or "SherpaTemplatesRender-C-QoKcBitsHqpiFi1cRE"
    # TODO: Change this location to the azure file share mount location
    #
    #LOGS_LOCATION = os.environ.get('DIR_LOCATION') or "/videosherpa/videos/"
    #VIDEOS_LOCATION = os.environ.get('VIDEOS_LOCATION') or "/videosherpa/videos/"
    #QUE_LOCATION = os.environ.get('QUE_LOCATION') or "/videosherpa/videos/templateque/"

    LOGS_LOCATION = os.environ.get('DIR_LOCATION') or "/mnt/csae48d5df47deax41bcxbaa/logs/introGen"
    VIDEOS_LOCATION = os.environ.get('VIDEOS_LOCATION') or "/mnt/csae48d5df47deax41bcxbaa/videos/"
    QUE_LOCATION = os.environ.get('QUE_LOCATION') or "/mnt/csae48d5df47deax41bcxbaa/videos/templateque/"

    SERVICENAME = os.environ.get('SERVICENAME') or "Sherpa-Templates-Render"



