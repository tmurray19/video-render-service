import os
import shutil

# logging and debugging
import logging

# required for image manipulation and video creation
from PIL import Image, ImageDraw, ImageFont

# required for MoviePy Stuff

from moviepy.editor import *
from moviepy.video.tools.segmenting import findObjects

import gizeh
import numpy as np

import webcolors

from templatedetails import TemplateDetails

from datetime import datetime

from intro_config import introConfig
cfg = introConfig()

def createintro(projectid):
    status = 0
    starttime = datetime.now()

    logging.debug('createtemplate06 - Start:' + str(starttime))

    projectPath = cfg.VIDEOS_LOCATION + projectid
    logging.debug('createtemplate06 - Start:' + projectPath)

    try:
        # Create
        status = 1

        if os.path.exists(projectPath + '/intro.mp4') == True:
            os.remove(projectPath + '/intro.mp4')
        if os.path.exists(projectPath + '/intro_comp.mp4') == True:
            os.remove(projectPath + '/intro_comp.mp4')

        logging.debug('99-Template5-SetUp')

        bgclip1 = ColorClip((1920, 1080), col=(0, 0, 0))
        bgclip1 = bgclip1.set_duration(.25)

        clips1 = CompositeVideoClip([bgclip1], size=(1920, 1080))

        # Put them all together
        clips = concatenate_videoclips([clips1])

        logging.debug("Intro has been successfully rendered, returning it to main render")
        return clips

        logging.debug('99-VideoFileClip')

        logging.debug('99-WriteFinal')
        finaldestination = projectPath + '/intro.mp4'
        logging.debug('99-File: ' + finaldestination)

        clips.write_videofile(finaldestination, threads=4, audio=False, codec='libx264', preset='ultrafast', fps=50)

    except Exception as e:
        status = str(e)
        logging.error("Error occured")
        logging.debug(cfg.SERVICENAME + '10 - End... start:' + status)

    endtime = datetime.now()

    logging.debug(cfg.SERVICENAME + '10 - End... start:' + str(starttime) + ' end:' + str(endtime))

    return "Status : " + str(status)


