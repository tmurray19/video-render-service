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
        if not os.path.isdir(str(projectid) + 'imwkdir'):
            logging.debug('03 - Setup Paths - new directry has been created')
            os.system('mkdir ' + str(projectid) + 'imwkdir')
        else:
            logging.debug('03 - Setup Paths - Exists - Delete and resetup')
            shutil.rmtree(str(projectid) + 'imwkdir')
            os.system('mkdir ' + str(projectid) + 'imwkdir')

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

        while i < frames:
            logging.debug('05 - First Set' + str(i))
            # Set the image background
            img = Image.new('RGBA', (1920, 1080), color=(tempdets.templateBGColorR, tempdets.templateBGColorG,
                                                         tempdets.templateBGColorB, iBgTransp))
            d = ImageDraw.Draw(img)

            # Title Text
            d.text((iTxtPosX, iTxtPosY), tempdets.textLine01, font=fnt,
                   fill=(tempdets.textLine01FontColorR, tempdets.textLine01FontColorG,
                         tempdets.textLine01FontColorB, iTxTransParency))

            img.save(str(projectid) + 'imwkdir/imagtx01-' + str(i).zfill(3) + '.png')
            i = i + 1
            iTxtPosX = iTxtPosX - iMoveBy

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
        logging.debug('IntroText2:' + str(tempdets.textLine02))
        logging.debug('iMoveBy:' + str(iMoveBy))
        logging.debug('iFH:' + str(iFH))
        logging.debug('iFH:' + str(iFW))

        while i < frames:
            logging.debug('05 - Second Set' + str(i))
            # Set the image background
            img = Image.new('RGBA', (1920, 1080), color=(tempdets.templateBGColorR, tempdets.templateBGColorG,
                                                         tempdets.templateBGColorB, iBgTransp))
            d = ImageDraw.Draw(img)

            # Title Text
            d.text((iTxtPosX, iTxtPosY), tempdets.textLine02, font=fnt,
                   fill=(tempdets.textLine02FontColorR, tempdets.textLine02FontColorG,
                         tempdets.textLine02FontColorB, iTxTransParency))

            img.save(str(projectid) + 'imwkdir/imagtx02-' + str(i).zfill(3) + '.png')
            i = i + 1
            iTxtPosY = iTxtPosY - iMoveBy

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
        logging.debug('IntroText2:' + str(tempdets.textLine02))
        logging.debug('iMoveBy:' + str(iMoveBy))
        logging.debug('iFH:' + str(iFH))
        logging.debug('iFH:' + str(iFW))

        while i < frames:
            logging.debug('05 - Third Set' + str(i))
            # Set the image background
            img = Image.new('RGBA', (1920, 1080), color=(tempdets.templateBGColorR,
                                                         tempdets.templateBGColorG,
                                                         tempdets.templateBGColorB, iBgTransp))
            d = ImageDraw.Draw(img)

            # Title Text
            d.text((iTxtPosX, iTxtPosY), tempdets.textLine03, font=fnt,
                   fill=(tempdets.textLine03FontColorR, tempdets.textLine03FontColorG,
                         tempdets.textLine03FontColorB, iTxTransParency))

            img.save(str(projectid) + 'imwkdir/imagtx03-' + str(i).zfill(3) + '.png')
            i = i + 1
            iTxtPosY = iTxtPosY + iMoveBy

        base_dir = os.path.realpath("./" + str(projectid) + "imwkdir")
        print(base_dir)
        logging.debug('base_dir' + str(base_dir))

        file_list = glob.glob(base_dir + '/*.png')  # Get all the pngs in the current directory
        file_list_sorted = natsorted(file_list, reverse=False)  # Sort the images

        print(file_list)
        print(file_list_sorted)

        logging.debug('base_dir' + str(file_list_sorted))

        logging.debug('99-ImageSequence')
        clips = ImageSequenceClip(file_list_sorted, fps=50)
        return clips
        logging.debug('99-VideoFileClip')

        logging.debug('99-WriteFinal')
        finaldestination = projectPath + '/intro.mp4'
        logging.debug('99-File: ' + finaldestination)

        #clips.write_videofile(finaldestination, threads=4, audio=False, codec='libx264', preset='ultrafast')

        firstclipLoc = projectPath + '/' + tempdets.firstclip

        if os.path.exists(firstclipLoc) == True:
            clip = VideoFileClip(firstclipLoc, audio=False).subclip(0, 3)
            
            logging.debug('99-Composit')
            final = CompositeVideoClip([clip, clips])
            #
            final.write_videofile(finaldestination, threads=4, audio=False, codec='libx264', preset='ultrafast', fps=25)
        else:
            logging.debug('99-No Overlay Clip')
            clips.write_videofile(finaldestination, threads=4, audio=False, codec='libx264', preset='ultrafast', fps=25)
        #
        # finaldestination = projectPath + 'intro_comp.mp4'
        # logging.debug('99-File: ' + finaldestination)
        # final.write_videofile(finaldestination, threads=4, audio=False, codec='libx264')

        # clips.close()
        # final.write_videofile(finaldestination, threads=4, audio=False, codec='libx264', progress_bar=false)
        shutil.rmtree(str(projectid) + 'imwkdir')
        os.system('mkdir ' + str(projectid) + 'imwkdir')
    except Exception as e:
        status = str(e)
        logging.debug(cfg.SERVICENAME + '10 - End... start:' + status)

    endtime = datetime.now()

    logging.debug(cfg.SERVICENAME + '10 - End... start:' + str(starttime) + ' end:' + str(endtime))

    return "Status : " + str(status)

