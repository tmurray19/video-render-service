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

        # FIRST LINE OF TEXT
        logging.debug('04 - Setup Fonts')
        logging.debug('FontSize:' + tempdets.textLine01FontSize)
        logging.debug('Font:' + tempdets.textLine01Font)



        logging.debug('05 - Fonts Size 1')
        # Get the width/height in pixels of the text so we can centre
        # on the screen
        # Set the font up for writing out the text
        fnt = ImageFont.truetype(tempdets.textLine01Font, int(tempdets.textLine01FontSize))
        iFontImageSize = fnt.getsize(tempdets.textLine01)
        iFW1 = iFontImageSize[0]
        iFH1 = iFontImageSize[1]

        logging.debug('05 - Fonts Size 2')
        fnt = ImageFont.truetype(tempdets.textLine02Font, int(tempdets.textLine02FontSize))
        iFontImageSize = fnt.getsize(tempdets.textLine02)

        iFW2 = iFontImageSize[0]
        iFH2 = iFontImageSize[1]

        print('iFW2:'+str(iFW2))
        print('iFH2:' + str(iFH2))

        logging.debug('05 - Fonts Size 3')
        fnt = ImageFont.truetype(tempdets.textLine03Font, int(tempdets.textLine03FontSize))
        iFontImageSize = fnt.getsize(tempdets.textLine03)

        iFW3 = iFontImageSize[0]
        iFH3 = iFontImageSize[1]

        logging.debug('05 - Fonts Colors 1 ')
        print(str(tempdets.textLine01FontColorR))
        print(str(tempdets.textLine01FontColorG))
        print(str(tempdets.textLine01FontColorB))

        if tempdets.templateBGColorR == 0:
            tempdets.templateBGColorR = 10
        if tempdets.templateBGColorG == 0:
            tempdets.templateBGColorG = 10
        if tempdets.templateBGColorB == 0:
            tempdets.templateBGColorB = 10

        # Big Dirty Hack... if any of the colours are 0 then set to 10 as it doesn't like them JIMMY!!!
        if tempdets.textLine01FontColorR == 0:
            tempdets.textLine01FontColorR = 10
        if tempdets.textLine01FontColorG == 0:
            tempdets.textLine01FontColorG = 10
        if tempdets.textLine01FontColorB == 0:
            tempdets.textLine01FontColorB = 10
        if tempdets.textLine02FontColorR == 0:
            tempdets.textLine02FontColorR = 10
        if tempdets.textLine02FontColorG == 0:
            tempdets.textLine02FontColorG = 10
        if tempdets.textLine02FontColorB == 0:
            tempdets.textLine02FontColorB = 10
        if tempdets.textLine03FontColorR == 0:
            tempdets.textLine03FontColorR = 10
        if tempdets.textLine03FontColorG == 0:
            tempdets.textLine03FontColorG = 10
        if tempdets.textLine03FontColorB == 0:
            tempdets.textLine03FontColorB = 10

        textline01HEX = webcolors.rgb_to_hex((tempdets.textLine01FontColorR, tempdets.textLine01FontColorG,
                                              tempdets.textLine01FontColorB))
        print(str(textline01HEX))
        logging.debug('05 - Fonts Colors 2')
        textline02HEX = webcolors.rgb_to_hex((tempdets.textLine02FontColorR, tempdets.textLine02FontColorG,
                                              tempdets.textLine02FontColorB))
        print(str(textline02HEX))
        logging.debug('05 - Fonts Colors 3 ')
        textline03HEX = webcolors.rgb_to_hex((tempdets.textLine03FontColorR, tempdets.textLine02FontColorG,
                                              tempdets.textLine03FontColorB))
        print(str(textline03HEX))
        screensize = (1920, 1080)

        def arrive(screenpos, i, nletters):
            logging.debug('07 - Split and move letters 3')
            print('scrrenpos:'+str(screenpos))
            print('i:'+str(i))
            v = np.array([-1, 0])
            d = lambda t: max(0, 3 - 3 * t)
            return lambda t: screenpos - 1020 * v * d(t - 0.1 * i)

        def arriveleft(screenpos, i, nletters):
            v = np.array([-1, 0])
            d = lambda t: max(0, 3 - 3 * t)
            return lambda t: screenpos + 1020 * v * d(t - 0.1 * i)

        def moveLetters(letters, funcpos):
            logging.debug('07 - move letters 3.1')
            return [letter.set_pos(funcpos(letter.screenpos, i, len(letters)))
                    for i, letter in enumerate(letters)]


        print('iFW:'+str(iFW1))


        def makeslidebox1(t):
            surface = gizeh.Surface(width=1920, height=1080)

            if t == 0:
                iW1 = 10
            else:
                iW1 = iFW1

            rect = gizeh.rectangle(lx=(iW1/2 * (t + 1)), ly=(iFH1 + 100),
                                   xy=((1920 * t), ((1080 - (iFH1 + 100)) / 2) + ((iFH1 + 50) / 2)),
                                   fill=(0, 0,
                                          tempdets.templateBGColorB),
                                   angle=0)
            rect.draw(surface)
            return surface.get_npimage(transparent=True)

        def makeslidebox2(t):
            surface2 = gizeh.Surface(width=1920, height=1080)

            if t == 0:
                iW2 = 50
            else:
                iW2 = iFW2
            print('t'+str(t))
            #print('x' + str(1920 - (100* t)))
            rect2 = gizeh.rectangle(lx=(iW2 * (t + 1)), ly=(iFH2 + 100),
                                    xy=((1920 - (750* t)), ((1080 - (iFH2 + 100)) / 2) + ((iFH2 + 50) / 2)),
                                    fill=(0, 0,
                                          tempdets.templateBGColorB),
                                    angle=0)
            rect2.draw(surface2)
            return surface2.get_npimage(transparent=True)

        def makeslidebox3(t):
            surface = gizeh.Surface(width=1920, height=1080)

            if t == 0:
                iW1 = 10
            else:
                iW1 = iFW3

            rect = gizeh.rectangle(lx=(iW1/2 * (t + 1)), ly=(iFH3 + 100),
                                   xy=((1920 * t), ((1080 - (iFH3 + 100)) / 2) + ((iFH3 + 50) / 2)),
                                   fill=(0, 0,
                                          tempdets.templateBGColorB),
                                   angle=0)
            rect.draw(surface)
            return surface.get_npimage(transparent=True)

        logging.debug('06 - Mask')

        # Line 1
        graphics_clip_mask = VideoClip(lambda t: makeslidebox1(t)[:, :, 3] / 255.0, duration=2, ismask=True)
        graphics_clip = VideoClip(lambda t: makeslidebox1(t)[:, :, :3], duration=2).set_mask(graphics_clip_mask)
        #
        logging.debug('06 - TextClip')
        logging.debug(tempdets.textLine01)
        logging.debug(textline01HEX)
        logging.debug(tempdets.textLine01Font)
        logging.debug(tempdets.textLine01FontSize)
        #

        bgclip1 = ColorClip((1920, 1080), col=(tempdets.templateBGColorR, tempdets.templateBGColorG,
                                          tempdets.templateBGColorB))
        bgclip1 = bgclip1.set_duration(3)

        txtClip = TextClip(tempdets.textLine01, color=textline01HEX, font=tempdets.textLine01Font,
                           kerning=5, fontsize=int(tempdets.textLine01FontSize))

        cvc = CompositeVideoClip([txtClip.set_pos('center')], size=screensize)
        #
        logging.debug('07 - Split and move letters')
        letters = findObjects(cvc)
        logging.debug('07 - Split and move letters 2')
        #
        textClip1 = [CompositeVideoClip(moveLetters(letters, funcpos),
                                        size=screensize).subclip(0, 2)
                 for funcpos in [arrive]]
        #
        #
        logging.debug('07 - Split and move letters 2')
        #
        txtClip1 = concatenate_videoclips(textClip1)
        #
        clips1 = CompositeVideoClip([bgclip1, txtClip1, graphics_clip], size=(1920, 1080))


        # Line 2
        graphics_clip_mask2 = VideoClip(lambda t: makeslidebox2(t)[:, :, 3] / 255.0, duration=3, ismask=True)
        graphics_clip2 = VideoClip(lambda t: makeslidebox2(t)[:, :, :3], duration=3).set_mask(graphics_clip_mask2)

        logging.debug('06 - TextClip')

        txtClip2 = TextClip(tempdets.textLine02, color=textline02HEX, font=tempdets.textLine02Font,
                           kerning=5, fontsize=int(tempdets.textLine02FontSize))

        cvc2 = CompositeVideoClip([txtClip2.set_pos('center')], size=screensize)

        logging.debug('07 - Split and move letters')
        letters2 = findObjects(cvc2)

        textClip2 = [CompositeVideoClip(moveLetters(letters2, funcpos2),
                                        size=screensize).subclip(0, 3)
                     for funcpos2 in [arriveleft]]

        logging.debug('07 - Split and move letters 2')

        txtClip2 = concatenate_videoclips(textClip2)

        clips2 = CompositeVideoClip([bgclip1, txtClip2, graphics_clip2], size=(1920, 1080))

        # Line 3
        graphics_clip_mask = VideoClip(lambda t: makeslidebox3(t)[:, :, 3] / 255.0, duration=3, ismask=True)
        graphics_clip = VideoClip(lambda t: makeslidebox3(t)[:, :, :3], duration=3).set_mask(graphics_clip_mask)
        #
        logging.debug('06 - TextClip')
        #
        txtClip = TextClip(tempdets.textLine03, color=textline03HEX, font=tempdets.textLine03Font,
                           kerning=5, fontsize=int(tempdets.textLine03FontSize))

        cvc = CompositeVideoClip([txtClip.set_pos('center')], size=screensize)
        #
        logging.debug('07 - Split and move letters')
        letters = findObjects(cvc)
        #
        textClip3 = [CompositeVideoClip(moveLetters(letters, funcpos),
                                        size=screensize).subclip(0, 2)
                     for funcpos in [arrive]]
        #
        #
        logging.debug('07 - Split and move letters 2')
        #
        txtClip3 = concatenate_videoclips(textClip3)
        #
        clips3 = CompositeVideoClip([bgclip1, txtClip3, graphics_clip], size=(1920, 1080))

        # Put them all together
        clips = concatenate_videoclips([clips1, clips2, clips3])

        logging.debug("Intro has been successfully rendered, returning it to main render")
        return clips

        logging.debug('99-VideoFileClip')

        logging.debug('99-WriteFinal')
        finaldestination = projectPath + '/intro.mp4'
        logging.debug('99-File: ' + finaldestination)

        #clips.write_videofile(finaldestination, threads=4, audio=False, codec='libx264', preset='ultrafast')

        #firstclipLoc = projectPath + '/' + tempdets.firstclip

        # if os.path.exists(firstclipLoc) == True:
        #     clip = VideoFileClip(firstclipLoc, audio=False).subclip(0, 3)
        #     #
        #     logging.debug('99-Composit')
        #     final = CompositeVideoClip([clip, clips])
        #     #
        #     final.write_videofile(finaldestination, threads=4, audio=False, codec='libx264', preset='ultrafast', fps=50)
        # else:
        #     logging.debug('99-No Overlay Clip')

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

