import os
import shutil

# logging and debugging
import logging
from pprint import pprint

# required for image manipulation and video creation
from PIL import Image, ImageDraw, ImageFont

# required for MoviePy Stuff
import glob
from natsort import natsorted

from moviepy.editor import *
from moviepy.video.tools.drawing import *

from templatedetails import TemplateDetails

from datetime import datetime

from config import Config
cfg = Config()

def createintro(projectid):
    status = 0
    starttime = datetime.now()

    logging.debug('createtemplate02 - Start:' + str(starttime))

    projectPath = cfg.VIDEOS_LOCATION + projectid
    logging.debug('createtemplate02 - Start:' + projectPath)

    try:
        status = 1

        if os.path.exists(projectPath + '/intro.mp4') == True:
            os.remove(projectPath + '/intro.mp4')
        if os.path.exists(projectPath + '/intro_comp.mp4') == True:
            os.remove(projectPath + '/intro_comp.mp4')

        fps = 50
        frames = 0


        logging.debug('01 - Get Template Config')
        # Get Template Config Details
        # from template.json
        tempdets = TemplateDetails()
        tempdets.readtemplate(projectid)
        logging.debug(tempdets.textLine01)

        logging.debug('02 - Set Opts')

        iBgTransp = 150
        iTxTransParency = 20

        logging.debug('03 - Setup Paths')
        if not os.path.isdir(str(projectid) + 'imgts'):
            print('new directry has been created')
            os.system('mkdir ' + str(projectid) + 'imgts')
        else:
            shutil.rmtree(str(projectid) + 'imgts')
            os.system('mkdir ' + str(projectid) + 'imgts')

        # WRITE OUT THE IMAGE SEQUENCE FOR THE
        # FIRST LINE OF TEXT
        logging.debug('04 - Setup Fonts')
        logging.debug('FontSize:' + tempdets.textLine01FontSize)
        logging.debug('Font:' + tempdets.textLine01Font)

        # Set the font up for writing out the text
        fnt = ImageFont.truetype(tempdets.textLine01Font, int(tempdets.textLine01FontSize))

        # Get the width in pixels fstarttime = datetime.now()or the text so we can centre
        # on the screen
        iFontImageSize = fnt.getsize(tempdets.textLine01)

        iFW = iFontImageSize[0]
        iFH = iFontImageSize[1]

        iTxtPosX = 1920
        iTxtPosY = (1080 - iFH) / 2

        # Set the duration of the animation
        i = 0
        iMgSeq = i + 1
        frames = fps * 1

        iMoveBy = (1920 + iFW) / frames


        # WRITE OUT THE IMAGE SEQUENCE FOR THE
        # SECOND LINE OF TEXT

        # Set the font up for writing out the text
        fnt = ImageFont.truetype(tempdets.textLine02Font, int(tempdets.textLine02FontSize))

        # Get the width in pixels fstarttime = datetime.now()or the text so we can centre
        # on the screen
        iFontImageSize = fnt.getsize(tempdets.textLine02)

        iFW = iFontImageSize[0]
        iFH = iFontImageSize[1]

        iTxtPosX = (1920 - iFW) / 2
        iTxtPosY = 1080

        # Set the duration of the animation
        i = 0
        iMgSeq = i + 1
        frames = fps * 1

        iMoveBy = ((1080 - iFH)) / frames


        # WRITE OUT THE IMAGE SEQUENCE FOR THE
        # THIRD LINE OF TEXT

        # Set the font up for writing out the text
        fnt = ImageFont.truetype(tempdets.textLine03Font, int(tempdets.textLine03FontSize))

        # Get the width in pixels fstarttime = datetime.now()or the text so we can centre
        # on the screen
        iFontImageSize = fnt.getsize(tempdets.textLine03)

        iFW = iFontImageSize[0]
        iFH = iFontImageSize[1]

        iTxtPosX = (1920 - iFW) / 2
        iTxtPosY = 0 - iFH

        # Set the duration of the animation
        i = 0
        iMgSeq = i + 1
        frames = fps * 1

        iMoveBy = ((1080 + iFH) / 2) / frames



        logging.debug('99-VideoFileClip')

        logging.debug('99-WriteFinal')
        finaldestination = projectPath + '/intro.mp4'
        logging.debug('99-File: ' + finaldestination)

        #clips.write_videofile(finaldestination, threads=4, audio=False, codec='libx264', preset='ultrafast')

        firstclipLoc = projectPath + '/' + tempdets.firstclip

        if os.path.exists(firstclipLoc) == True:
            clip = VideoFileClip(firstclipLoc, audio=False).subclip(0, 3)
            #
            logging.debug('99-Composit')
            final = CompositeVideoClip([clip, clips])
            #
            final.write_videofile(finaldestination, threads=4, audio=False, codec='libx264', preset='ultrafast', fps=50)
        else:
            logging.debug('99-No Overlay Clip')
            clips.write_videofile(finaldestination, threads=4, audio=False, codec='libx264', preset='ultrafast', fps=50)
        #
        # finaldestination = projectPath + 'intro_comp.mp4'
        # logging.debug('99-File: ' + finaldestination)
        # final.write_videofile(finaldestination, threads=4, audio=False, codec='libx264')

        # clips.close()
        # final.write_videofile(finaldestination, threads=4, audio=False, codec='libx264', progress_bar=false)
    except Exception as e:
        status = str(e)
        logging.debug(cfg.SERVICENAME + '10 - End... start:' + status)

    endtime = datetime.now()

    logging.debug(cfg.SERVICENAME + '10 - End... start:' + str(starttime) + ' end:' + str(endtime))

    return "Status : " + str(status)

