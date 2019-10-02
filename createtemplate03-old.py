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

from moviepy.config import change_settings
change_settings({"IMAGEMAGICK_BINARY": "/opt/local/bin/convert"})

from templatedetails import TemplateDetails

from datetime import datetime

from config import Config
cfg = Config()

import webcolors
import gizeh as gz


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


        # Set the font up for writing out the text
        fnt = ImageFont.truetype(tempdets.textLine01Font, int(tempdets.textLine01FontSize))

        # Get the width in pixels fstarttime = datetime.now()or the text so we can centre
        # on the screen
        iFontImageSize = fnt.getsize(tempdets.textLine01)

        iFW = iFontImageSize[0]
        iFH = iFontImageSize[1]

        logging.debug('After Font Setup:' + tempdets.textLine01Font)

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

        logging.debug('After Font Setup:' + tempdets.textLine02Font)

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

        textline01HEX = webcolors.rgb_to_hex((tempdets.textLine01FontColorR, tempdets.textLine01FontColorG,
                                              tempdets.textLine01FontColorB))

        textline02HEX = webcolors.rgb_to_hex((tempdets.textLine02FontColorR, tempdets.textLine02FontColorG,
                                              tempdets.textLine02FontColorB))

        textline03HEX = webcolors.rgb_to_hex((tempdets.textLine02FontColorR, tempdets.textLine02FontColorG,
                                              tempdets.textLine02FontColorB))


        logging.debug('99-VideoFileClip')

        logging.debug('99-WriteFinal')
        finaldestination = projectPath + '/intro.mp4'
        logging.debug('99-File: ' + finaldestination)

        #clips.write_videofile(finaldestination, threads=4, audio=False, codec='libx264', preset='ultrafast')

        firstclipLoc = projectPath + '/' + tempdets.firstclip

        if os.path.exists(firstclipLoc) == True:
            logging.debug('99-Composit-1')
            clip = VideoFileClip(firstclipLoc, audio=False).subclip(0, 3).add_mask()
            clipsrc = VideoFileClip(firstclipLoc, audio=False).subclip(0, 3)

            w, h = clip.size
            logging.debug('99-Composit-2')
            # The mask is a circle with vanishing radius r(t) = 800-200*t
            clip.mask.get_frame = lambda t: circle(screensize=(clip.w, clip.h),
                                                   center=( (clip.w / 3)+(10*t), clip.h / 6),
                                                   radius=max(5, int(100 + (750 * t))),
                                                   col1=1, col2=0, blur=4)

            logging.debug('99-Composit-3')
            Text1 = TextClip(tempdets.textLine01, font=tempdets.textLine01Font, color=textline01HEX,
                               fontsize=int(tempdets.textLine01FontSize)).set_duration(clip.duration)
            Text2 = TextClip(tempdets.textLine02, font=tempdets.textLine02Font, color=textline02HEX,
                             fontsize=int(tempdets.textLine01FontSize)).set_duration(clip.duration)
            logging.debug('99-Composit-4')

            final = CompositeVideoClip([clip, Text1.set_pos('center'), Text2.set_pos(('left','bottom'))],
                                       size=clip.size)
            #
            logging.debug('99-Composit')


            def make_frame(t):
                surface = gz.Surface(width=1920, height=1080)
                line = gz.polyline(points=[(200, max(180, 180 + 100 * t)), (100, max(180, 180 + 100 * t))],
                                   stroke_width=25, stroke=(1, 0, 0))
                line.draw(surface)
                return surface.get_npimage(transparent=True)

            logging.debug('99-Composit-after')
            #clipline_mask = VideoClip(make_frame, duration=duration, ismask=True)
            #clipline = VideoClip(make_frame, duration=duration).set_mask(clipline_mask)

            clipline_mask = VideoClip(lambda t: make_frame(t)[:, :, 3] / 50.0, duration=3, ismask=True)
            clipline = VideoClip(lambda t: make_frame(t)[:, :, :3], duration=3).set_mask(clipline_mask)

            #def make_frame(t):
            #    txt = TextClip("TEST %s" % t, color="#686868", fontsize=20, font="Arial")

            #    return txt.img

            #text_clip1 = VideoClip(make_frame, duration=3)
            logging.debug('99-Composit-put together')
            final2 = CompositeVideoClip([final, clipline], size=(1920,1080))
            logging.debug('99-Composit-put together and write')
            #
            final2.write_videofile(finaldestination, threads=4, audio=False, codec='libx264', preset='ultrafast', fps=50)
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

