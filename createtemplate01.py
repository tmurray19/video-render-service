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

from intro_config import introConfig
cfg = introConfig()

def createintro(projectid):
    status = 0
    starttime = datetime.now()

    logging.debug('createtemplate00 - Start:' + str(starttime))

    projectPath = cfg.VIDEOS_LOCATION + projectid
    logging.debug('createtemplate00 - Start:' + projectPath)
    try:
        status = 1

        # Get Template Config Details
        # from template.json
        tempdets = TemplateDetails()
        tempdets.readtemplate(projectid)
        logging.debug(tempdets.textLine01)

        logging.debug('03 - OS Path & clean directories')
        # logging.debug(os.path)

        logging.debug('03 - Setup Paths')
        if not os.path.isdir(str(projectid) + 'imwkdir'):
            logging.debug('03 - Setup Paths - new directry has been created')
            os.system('mkdir ' + str(projectid) + 'imwkdir')
        else:
            logging.debug('03 - Setup Paths - Exists - Delete and resetup')
            shutil.rmtree(str(projectid) + 'imwkdir')
            os.system('mkdir ' + str(projectid) + 'imwkdir')

        if os.path.exists(projectPath + '/intro.mp4'):
            os.remove(projectPath + '/intro.mp4')

        logging.debug('04 - AFTER OS Path & clean directories')
        i = 1
        fps = 25

        # Set the Text to be Non Transparent
        iTxTransParency = 255

        iPosX = 960
        iPosY = 540

        iPos2X = 960
        iPos2Y = 540

        logging.debug('05 - Setup Fonts')
        logging.debug('05.1 - Fonts' + tempdets.textLine01Font)
        logging.debug('05.1 - Fonts Size' + str(tempdets.textLine01FontSize))

        # Set the font up for writing out the text
        if int(tempdets.textLine01FontSize) > 100:
            Line01FontSize = 100
        else:
            Line01FontSize = tempdets.textLine01FontSize
        if int(tempdets.textLine02FontSize) > 60:
            Line02FontSize = 60
        else:
            Line02FontSize = tempdets.textLine01FontSize
        pprint("fontsize")
        if tempdets.textLine01 != "":
            fnt = ImageFont.truetype(tempdets.textLine01Font, int(Line01FontSize))
        if tempdets.textLine02 != "":
            fnt2 = ImageFont.truetype(tempdets.textLine02Font, int(Line02FontSize))
        # if tempdets.textLine03 != "":
        #    fnt3 = ImageFont.truetype(tempdets.textLine01Font, int(tempdets.textLine03FontSize))
        pprint("fontsize-after")

        # Draw the line 1 second
        secs = fps * 2

        linIncr = 0
        iBoxStart = 10

        iBallSize = 20

        iLinePosY = iPosY + iBallSize / 2

        def staticline():
            # Line Remains constant
            d.line((iPosX, iLinePosY, iPosX + linIncr, iLinePosY), fill=(tempdets.textLine01FontColorR,
                                                                         tempdets.textLine01FontColorG,
                                                                         tempdets.textLine01FontColorB), width=1)
            return;

        while i < secs + 1:
            logging.debug('06 - Create The Images')
            # Set the image background
            # Needs to be a function
            img = Image.new('RGB', (1920, 1080), color=(tempdets.templateBGColorR,
                                                        tempdets.templateBGColorG,
                                                        tempdets.templateBGColorB))
            d = ImageDraw.Draw(img)

            # Only Draw the circles if less than 5 frames to go
            # want them to dissapear at the end

            iCnt = 0
            iCnt2 = 0
            if i <= secs - 10:
                # Draw the circles
                d.ellipse((iPosX, iPosY, iPosX + iBallSize, iPosY + iBallSize), fill=(tempdets.textLine01FontColorR,
                                                                                      tempdets.textLine01FontColorG,
                                                                                      tempdets.textLine01FontColorB),
                          outline=(tempdets.textLine01FontColorR, tempdets.textLine01FontColorG,
                                   tempdets.textLine01FontColorB))
                d.ellipse((iPos2X, iPos2Y, iPos2X + iBallSize, iPos2Y + iBallSize),
                          fill=(tempdets.textLine01FontColorR, tempdets.textLine01FontColorG,
                                tempdets.textLine01FontColorB), outline=(tempdets.textLine01FontColorR,
                                                                         tempdets.textLine01FontColorG,
                                                                         tempdets.textLine01FontColorB))
                # Draw The Line
                linIncr = linIncr + iBallSize
                d.line((iPosX, iLinePosY, iPosX + linIncr, iLinePosY), fill=(tempdets.textLine01FontColorR,
                                                                             tempdets.textLine01FontColorG,
                                                                             tempdets.textLine01FontColorB), width=1)
                iPosX = iPosX - (iBallSize / 2)
                iPos2X = iPos2X + (iBallSize / 2)

                # Debug - Output the Frame Number on th eSlide if needed
                # d.text((200, 200), str(i), font=fnt, fill=(iTxColorR, iTxColorG, iTxColorB, iTxTransParency))
            else:
                iCnt = iCnt + 1
                iBoxStart = iBoxStart - 1
                d.ellipse((iPosX, iPosY + iCnt, iPosX + iBoxStart, iPosY + iBoxStart),
                          fill=(tempdets.textLine01FontColorR,
                                tempdets.textLine01FontColorG,
                                tempdets.textLine01FontColorB),
                          outline=(tempdets.textLine01FontColorR,
                                   tempdets.textLine01FontColorG,
                                   tempdets.textLine01FontColorB))
                d.ellipse((iPos2X, iPos2Y + iCnt, iPos2X + iBoxStart, iPos2Y + iBoxStart),
                          fill=(tempdets.textLine01FontColorR,
                                tempdets.textLine01FontColorG,
                                tempdets.textLine01FontColorB),
                          outline=(tempdets.textLine01FontColorR,
                                   tempdets.textLine01FontColorG,
                                   tempdets.textLine01FontColorB))
                staticline()
                # Debug - Output the Frame Number on th eSlide if needed
                # d.text((200, 200), str(i), font=fnt, fill=(iTxColorR, iTxColorG, iTxColorB, iTxTransParency))

            img.save(str(projectid) + 'imwkdir/imag' + str(str(i).zfill(4)) + '.png')
            i = i + 1
        logging.debug('07 - Images done')

        # Get the width in pixels for the text so we can centre
        # on the screen
        iFontImageSize = fnt.getsize(tempdets.textLine01)
        iFontSubImageSize = fnt2.getsize(tempdets.textLine02)

        iFW = iFontImageSize[0]
        iFH = iFontImageSize[1]

        iFShW = iFontSubImageSize[0]
        iFShH = iFontSubImageSize[1]

        iTxtPosX = 960 - (iFW / 2)
        # iTxtPosY = 540 + iFH
        iTxtPosY = 540
        iTxtPosOrgY = iTxtPosY

        iTxtSPosX = 960 - (iFShW / 2)

        # Set the duration of the animation
        iMgSeq = i + 1
        secs = fps * 3
        i = 0
        # Draw the text

        iPxMov = 0
        iPos2Y = iPos2Y - iFShH / 2 + 20
        iPosSubYOrgPos = iPos2Y
        iBoxHeight = iFH
        iSubTextHeight = iFShH

        logging.debug('08 - Few More Images')
        # TODO: Need to check that the height of the text will move by the number of pixels and clear the hiding box
        # TODO: IF not then set the increment to be more than currently, evaluate versus the number of seconds for the move

        while i < secs:
            # Set the image background
            img = Image.new('RGB', (1920, 1080), color=(tempdets.templateBGColorR, tempdets.templateBGColorG,
                                                        tempdets.templateBGColorB))
            d = ImageDraw.Draw(img)

            # Title Text
            d.text((iTxtPosX, iTxtPosY), tempdets.textLine01, font=fnt,
                   fill=(tempdets.textLine01FontColorR,
                         tempdets.textLine01FontColorG,
                         tempdets.textLine01FontColorB, iTxTransParency))
            d.rectangle((iTxtPosX + 1, iTxtPosOrgY + 1, iTxtPosX + 1 + iFW, iTxtPosOrgY + 1 + iBoxHeight),
                        outline=(tempdets.templateBGColorR, tempdets.templateBGColorG,
                                 tempdets.templateBGColorB),
                        fill=(tempdets.templateBGColorR, tempdets.templateBGColorG, tempdets.templateBGColorB))

            # SubText
            # Only move it and its box if
            d.text((iTxtSPosX, iPos2Y), tempdets.textLine02, font=fnt2,
                   fill=(tempdets.textLine02FontColorR, tempdets.textLine02FontColorG,
                         tempdets.textLine02FontColorB, iTxTransParency))
            if (1 + iFShH) >= 2:
                d.rectangle((iTxtSPosX, iPosSubYOrgPos, iTxtSPosX + 1 + iFShW, iPosSubYOrgPos + 1 + iFShH),
                            outline=(tempdets.templateBGColorR, tempdets.templateBGColorG,
                                     tempdets.templateBGColorB),
                            fill=(tempdets.templateBGColorR, tempdets.templateBGColorG, tempdets.templateBGColorB))

            staticline()

            # Debug - Output the Frame Number on th eSlide if needed
            # d.text((200, 200), str(iMgSeq) , font=fnt, fill=(iTxColorR, iTxColorG, iTxColorB, iTxTransParency))

            img.save(str(projectid) + 'imwkdir/imag' + str(iMgSeq).zfill(4) + '.png')
            i = i + 1
            iMgSeq = iMgSeq + 1

            iPxMov = iPxMov + 2
            if iPxMov >= iFH + 10:
                iTxtPosY = iTxtPosY
                iPos2Y = iPos2Y
            else:
                iTxtPosY = iTxtPosY - 2
                iBoxHeight = iBoxHeight - 2
                iFShH = iFShH - 2
                if (iFShH >= 0):
                    iPos2Y = iPos2Y + 1

            logging.debug('iFShH' + str(iFShH))

            # Create 2 Versions of the output
            # one for preview and one full HD
            # needs to be a function call
        logging.debug('09 - FFMPEG')
        # (
        #     ffmpeg
        #         .input('imgwkdirs/*.png', pattern_type='glob', framerate=30)
        #         .output(projectPath + '/intro.mp4', crf=20, preset='slower', movflags='faststart', pix_fmt='yuv420p')
        #         .run()
        # )

        file_list = glob.glob(str(projectid) + 'imwkdir/*.png')  # Get all the pngs in the current directory
        file_list_sorted = natsorted(file_list, reverse=False)  # Sort the images

        print(file_list)
        print(file_list_sorted)

        logging.debug('base_dir' + str(file_list_sorted))

        logging.debug('99-ImageSequence')
        clips = ImageSequenceClip(file_list_sorted, fps=50)

        logging.debug("Intro has been successfully rendered, returning it to main render")
        return clips

        
        logging.debug('99-VideoFileClip')

        logging.debug('99-WriteFinal')
        logging.debug('99-WriteFinal')
        finaldestination = projectPath + '/intro.mp4'
        logging.debug('99-File: ' + finaldestination)
        clips.write_videofile(finaldestination, threads=4, audio=False, codec='libx264', preset='ultrafast', fps=25)
        shutil.rmtree(str(projectid) + 'imwkdir')
        os.system('mkdir ' + str(projectid) + 'imwkdir')

    except Exception as e:
        status = "exception::" + str(e)

    endtime = datetime.now()

    logging.debug('createtemplate10 - End... start:' + str(starttime) + ' end:' + str(endtime) + 'status: ' + str(status))

    return "Status : " + str(status)

