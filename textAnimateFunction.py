import numpy as np
from moviepy.editor import *
from moviepy.video.tools.segmenting import findObjects


import gizeh as gz

# logging and debugging
import logging
# WE CREATE THE TEXT THAT IS GOING TO MOVE, WE CENTER IT.
#from moviepy.config import change_settings
#change_settings({"IMAGEMAGICK_BINARY": "/opt/local/bin/convert"})

def createdoubledroptext(text, font, fontsize, fontcolour):
    screensize = (720, 460)
    screensize = (1920, 1080)

    logging.debug('CreateDoubleDropText-01'+text)
    txtClipTop1 = TextClip(text, color='white', font=font, kerning=5, fontsize=int(fontsize))
    cvctop1 = CompositeVideoClip([txtClipTop1.set_pos('center')], size=screensize)

    txtClipBottom1 =  TextClip(text, color=fontcolour, font=font, kerning=5, fontsize=int(fontsize))
    cvcbottom1 = CompositeVideoClip([txtClipBottom1.set_pos('center')], size=screensize)

    # THE NEXT FOUR FUNCTIONS DEFINE FOUR WAYS OF MOVING THE LETTERS


    # helper function
    rotMatrix = lambda a: np.array([[np.cos(a), np.sin(a)],
                                    [-np.sin(a), np.cos(a)]])

    def cascade(screenpos, i, nletters):
        print('cascade:screenpos' + str(screenpos))
        print('cascade:i:' + str(i))
        v = np.array([0, -1])
        d = lambda t: 1 if t < 0 else abs(np.sinc(t) / (1 + t ** 4))
        return lambda t: screenpos + v * 50 * d(t - 0.25 * i)

    def cascadeout(screenpos, i, nletters):
        print('cascadeout:screenpos'+str(screenpos))
        print('cascadeout:i:'+str(i))
        v = np.array([0, -1])
        d = lambda t: 1 if t < 0 else abs(np.sinc(t) / (1 + t ** 4))
        return lambda t: screenpos + v * -50 * d(t + 0.25 * i)

    def cascadeback(screenpos, i, nletters):
        print('cascadeback:screenpos'+str(screenpos))
        print('cascadeback:i:'+str(i))
        v = np.array([0, -1])
        d = lambda t: 1 if t < 0 else abs(np.sinc(t) / (1 + t ** 4))
        return lambda t: screenpos + v * 55 * d(t - 0.25 * i)

    def cascadeoutback(screenpos, i, nletters):
        v = np.array([0, -1])
        d = lambda t: 1 if t < 0 else abs(np.sinc(t) / (1 + t ** 4))
        return lambda t: screenpos + v * -55 * d(t + 0.25 * i)

    logging.debug('CreateDoubleDropText-02-Letters')
    # WE USE THE PLUGIN findObjects TO LOCATE AND SEPARATE EACH LETTER
    letterstop1 = findObjects(cvctop1)  # a list of ImageClips

    lettersbottom1 = findObjects(cvcbottom1)  # a list of ImageClips

    # WE ANIMATE THE LETTERS
    def moveLetters(letters, funcpos):
        return [letter.set_pos(funcpos(letter.screenpos, i, len(letters)))
                for i, letter in enumerate(letters)]


    # clips = [CompositeVideoClip(moveLetters(letters, funcpos),
    #                             size=screensize).subclip(0, 5)
    #          for funcpos in [vortex, cascade, arrive, vortexout]]

    clipstop1 = [CompositeVideoClip(moveLetters(letterstop1, funcpos),
                                    size=screensize).subclip(0, 2)
                 for funcpos in [cascade]]

    clipstop2 = [CompositeVideoClip(moveLetters(lettersbottom1, funcpos),
                                    size=screensize).subclip(0, 2)
                 for funcpos in [cascadeback]]

    clips_bot = [CompositeVideoClip(moveLetters(letterstop1, funcpos),
                                    size=screensize).subclip(0, 2)
                 for funcpos in [cascadeout]]

    clips_bot2 = [CompositeVideoClip(moveLetters(lettersbottom1, funcpos),
                                     size=screensize).subclip(0, 2)
                  for funcpos in [cascadeoutback]]

    # WE CONCATENATE EVERYTHING AND RETURN THE CLIP
    logging.debug('CreateDoubleDropText-03-Clips')
    fclip1 = concatenate_videoclips(clipstop1)
    fclip2 = concatenate_videoclips(clipstop2)
    fclip3 = concatenate_videoclips(clips_bot2)
    fclip4 = concatenate_videoclips(clips_bot)
    logging.debug('CreateDoubleDropText-04-Final')
    final = CompositeVideoClip([fclip1, fclip2, fclip3, fclip4])

    return final