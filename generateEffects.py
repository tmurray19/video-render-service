import moviepy.editor as myp
from moviepy.audio.fx.volumex import volumex
import sherpaUtils
import os
from config import Config
import logging

resource_path = os.path.join(Config.BASE_DIR, Config.VIDS_LOCATION, Config.RESOURCE_PATH)
attach_dir = os.path.join(Config.BASE_DIR, Config.VIDS_LOCATION)
positions = {
    1: [("left", "top"), "West"],  # Top Left
    2: [("right", "top"), "East"],  # Top Right
    3: [("center", "top"), "Center"],  # Top center
    4: [("left", "center"), "West"],  # Center left
    5: [("center"), "Center"],  # Center of image
    6: [("right", "center"), "East"],  # Center right
    7: [("left", "bottom"), "West"],  # Center left
    8: [("center", "bottom"), "Center"],  # Center bottom
    9: [("right", "bottom"), "East"]  # Center right
}


positions_small = {
    1: (0.08, 0.1),  # Top Left
    2: (0.75, 0.1),  # Top Right
    3: (0.45, 0.1),  # Top Center
    4: (0.08, 0.5),  # Center Left
    5: ('center','center'),  # Center of image
    6: (0.75, 0.5),  # Center Right
    7: (0.08, 0.7),  # Bottom Left
    8: (0.45, 0.7),  # Bottom Center
    9: (0.75, 0.7)  # Bottom Right
}

positions_medium = {
    1: (0.03, 0.01),  # Top Left
    2: (0.3, 0.01),  # Top Right
    3: (0.5, 0.01),  # Top Center
    4: (0.03, 0.45),  # Center Left
    5: ('center','center'),  # Center of image
    6: (0.5, 0.45),  # Center Right
    7: (0.03, 0.75),  # Bottom Left
    8: (0.3, 0.75),  # Bottom Center
    9: (0.5, 0.75)  # Bottom Right
}

positions_large = {
    1: (0.02, 0.01),  # Top Left
    2: (0.4, 0.01),  # Top Right
    3: (0.25, 0.01),  # Top Center
    4: (0.02, 0.4),  # Center Left
    5: ('center','center'),  # Center of image
    6: (0.4, 0.4),  # Center Right
    7: (0.02, 0.75),  # Bottom Left
    8: (0.25, 0.75),  # Bottom Center
    9: (0.4, 0.75)  # Bottom Right
}



sizes = {
    "Small": 30,
    "Medium": 50,
    "Large": 80,
    "X-Large": 160,
    "XX-Large": 220
}

music_list = {
    0: "silence.mp3", # Mutes audio
    1: "Ambient_corporate.mp3",
    2: "Autumn_Inspiration.mp3",
    3: "Beneath_the_Moonlight.mp3",
    4: "C_Major_Prelude.mp3",
    5: "Entire.mp3",
    6: "Family_Montage.mp3",
    7: "Komiku.mp3",
    8: "Lobo.mp3",
    9: "Motivational_Beauty.mp3",
    10: "Old_Vienna.mp3",
    11: "Positive_Hip_Hop.mp3",
    12: "Rocco.mp3",
    13: "Scott_Holmes.mp3",
    14: "Soaring_High.mp3",
    15: "Steve_Combs.mp3",
    16: "To_the_Top.mp3",
    17: "Touching_Moment.mp3",
    18: "Water_Lily.mp3",
}

proj_fps=0


# Generate a blank image
# Add text right now just for clarity sake
def generate_blank(clip_data, start=None, end=None, compressed=False):

    if start is None:
        start = (clip_data.get('startTime'))

    if end is None:
        end = (clip_data.get('endTime'))
        
    dur = end - start

    
    vid_size = (852, 480) if compressed else (1920, 1080)

    """    
    blank_clip = myp.ColorClip(
        size=vid_size,
        color=(0, 0, 0),
        duration=dur
    )"""

    blank_clip = myp.VideoFileClip(os.path.join(resource_path, 'blank.mp4'))
    blank_clip = blank_clip.subclip(start, end)
    blank_clip = blank_clip.resize(vid_size)
    audio = myp.AudioFileClip(os.path.join(resource_path, music_list[0]))

    blank_clip = blank_clip.set_audio(audio.set_duration(dur))
    logging.debug("FPS is: {}".format(proj_fps))
    blank_clip.fps = proj_fps

    return blank_clip


def generate_clip(clip_data, user, start=None, end=None, compressed=False):
    """Generates clip data directly, without calling sherpaUtils within function"""
    related_file_name = clip_data.get('name')+"_com.mp4" if compressed else clip_data.get('name')+".mp4"

    if start is None:
        start = (clip_data.get('startTime'))

    if end is None:
        end = (clip_data.get('endTime'))

    # Get clip with defined start and end times
    clip = myp.VideoFileClip(os.path.join(attach_dir, user, related_file_name))
    
    if end > clip.duration:
        end = clip.duration
    clip = clip.subclip(
        start,
        end
    )

    # Reduce volume defined in data
    clip = clip.volumex(clip_data.get('audioLevel'))
    
    if not compressed:
        clip = clip.resize((1920, 1080)) 
    
    logging.debug("clip '{}' length: {}".format(clip_data.get('name'), round(clip.duration, 2)))

    if clip.audio is None:
        logging.error("No clip audio found for clip {}".format(clip_data.get('name')))
        audio = myp.AudioFileClip(os.path.join(resource_path, music_list[0]))
        clip = clip.set_audio(audio.set_duration(end - start))

    logging.debug("FPS is: {}".format(proj_fps))
    clip.fps = proj_fps
    return clip


# Generates an image clip based on json data
def generate_image_clip(clip_data, user):
    """'name' in this case refers to related file name of image"""
    # TODO

    dur = clip_data.get('duration')

    if dur is None:
        dur = clip_data.get('endTime') - clip_data.get('startTime')

    try:
        image_clip = myp.ImageClip(
            img=os.path.join(attach_dir, user, clip_data.get('name')+".jpg"),
            duration=dur
        )
    except FileNotFoundError:
        image_clip = myp.ImageClip(
            img=os.path.join(attach_dir, user, clip_data.get('name')+".png"),
            duration=dur
        )        

    audio = myp.AudioFileClip(os.path.join(resource_path, music_list[0]))

    image_clip = image_clip.set_audio(audio.set_duration(dur))
    logging.debug("FPS is: {}".format(proj_fps))
    image_clip.fps = proj_fps

    logging.debug("Image clip successfully generated.")

    return image_clip


def interview_audio_builder(interview_data, user):
    sound_builder = []

    logging.debug("Starting sound builder instance for interview audio")

    # For each item in the interview timeline
    for item in interview_data:

        # If it's a blank, add silence for the length of the clip ( May not be necessary? )
        if interview_data[item]['Meta'].get('clipType') == "Blank":
            sound_builder.append(
                myp.AudioFileClip(
                    os.path.join(
                        resource_path, 
                        music_list[0]
                    )
                ).set_duration(
                    (interview_data[item]['Meta'].get('endTime')) - (interview_data[item]['Meta'].get('startTime'))
                    ).volumex(
                        interview_data[item]['Meta'].get('audioLevel')
                    )
                )
            logging.debug("Silence audio added for blank '{}' for '{}' seconds".format(
                interview_data[item]['Meta'].get("name"),
                ((interview_data[item]['Meta'].get('endTime')) - (interview_data[item]['Meta'].get('startTime')))
            )
            )

        # Might not be needed if we append the audio when we find the full clip in the parent class
        elif interview_data[item]['Meta'].get('clipType') == 'Interview':
            audio = myp.AudioFileClip(
                os.path.join(
                    attach_dir,
                    user,
                    interview_data[item]['Meta'].get('name')+".mp4"
                )
            ).subclip(
                interview_data[item]['Meta'].get('startTime'),
                interview_data[item]['Meta'].get('endTime')
            )
            audio = audio.volumex(interview_data[item]['Meta'].get('audioLevel'))
            sound_builder.append(audio)
            logging.debug("Audio added for clip '{}' for '{}' seconds".format(
                interview_data[item]['Meta'].get("name"),
                ((interview_data[item]['Meta'].get('endTime')) - (interview_data[item]['Meta'].get('startTime')))
            )
            )

    return sound_builder


def better_generate_text_caption(clip, edit_data, compressed=False):
    """
    clip: moviepy clip --> The clip you wish to add the text too
    caption_data: dict --> The JSON/Dictionry data of the caption you want to add

    Function is designed to take in the info for the clip, read the caption data for the clip,
    generate the caption, and return it

    This function also handles any error with no caption being found.

    (Code should first try to look)
    """
    try:
        caption_data = edit_data['Caption']
        font_from_json = caption_data.get('fontSize')
        font_size = round(sizes[font_from_json] * 0.44357) if compressed else sizes[font_from_json]
        logging.debug("Font size is {}, converted to {}".format(font_from_json, font_size))
    
        caption_text = caption_data.get('text')

        rez = (752, 380) if compressed else (1820, 980)

        # TODO: Change
        dur = max(1, clip.duration - 2)
        logging.debug("Duration of text clip is {}".format(dur))

        print(caption_text)

        screen_pos, cardinal = positions[caption_data.get('screenPos')]
        print(screen_pos)
        print(cardinal)

        # Define Text Data
        text_caption = myp.TextClip(
            txt=caption_text,
            fontsize=font_size,
            font=caption_data.get('font'),
            color=caption_data.get('fontColour'),
            #method='caption',
            #align=cardinal
        ).set_duration(
                dur
            )     



        text_caption = myp.CompositeVideoClip([text_caption.set_position(screen_pos)])#, size=rez)

        logging.debug("FPS is: {}".format(proj_fps))
        text_caption.fps = proj_fps
        clip = myp.CompositeVideoClip([clip, text_caption.set_position('center').set_start(1)])
    
        return clip

    except Exception as e:
        logging.debug("Exception occured in text caption generation: {}".format(e))
        return clip
        


def open_music(music_data, audio_lvl, dur):
    """
    music_choice: string --> Which music file to open - Gonna be url, need to strip
    audio_lvl: int --> lenght of 

    For opening the music clip
    """
    try:
        file_name = music_data.split('/')[-1]
        music_location = os.path.join(resource_path, file_name)


        music = myp.AudioFileClip(music_location)
        music = volumex(music, audio_lvl)
        if music.duration > dur:
            music = music.set_duration(dur)

        # TODO: 2 second fade in and out automatically added
        music = music.audio_fadein(2)
        music = music.audio_fadeout(2)

        logging.debug("Music file '{}' chosen for video, cropped to {}s in length".format(file_name, dur))
        return music

    except Exception as e:
        logging.error("Exception occured during open_music: {}".format(e))
        return 0


def open_voice(music_data, audio_lvl, proj_id):
    """
    music_choice: string --> Which music file to open - Gonna be url, need to strip
    audio_lvl: int --> lenght of 

    For opening the music clip
    """
    try:
        file_name = music_data.split('/')[-1]
        voice_location = os.path.join(attach_dir, proj_id, file_name)

        voice = myp.AudioFileClip(voice_location)
        voice = volumex(voice, audio_lvl)

        logging.debug("Voice file '{}' chosen for video".format(file_name))
        return voice

    except Exception as e:
        logging.error("Exception occured during open_music: {}".format(e))
        return 0


def create_intro_clip(proj_id, compressed):
    logging.debug("Adding intro clip")    
    vid_size = (480, 852) if compressed else (1080, 1920)
    intro_clip = myp.VideoFileClip(
        os.path.join(attach_dir, proj_id, "intro.mp4"),
        target_resolution=vid_size
        )
    logging.debug("Intro clip is {}s long".format(intro_clip.duration))
    intro_audio = myp.AudioFileClip(os.path.join(attach_dir, Config.RESOURCE_PATH, "silence.mp3"))
    intro_clip = intro_clip.set_audio(intro_audio.set_duration(intro_clip.duration))
    return intro_clip


def generate_intro(clip, compressed, transparent=False):
    logging.debug("Adding intro")
    # We need to handle audio here for composite clips
    if transparent is True:
        logging.debug("Intro is transparent, need to composite clip on top of intro clip")
        
        # Generate intro clip
        intro = None
        # Composite both clips
        intro_composite = myp.CompositeVideoClip(clip, intro)
        intro_composite = intro_composite.set_audio(clip.audio)
        return intro_composite, True 
    else:
        logging.debug("We can just append this to the start of the video instead")
        intro = None
        intro_audio = myp.AudioFileClip(os.path.join(attach_dir, Config.RESOURCE_PATH, "silence.mp3"))
        intro = intro.set_audio(intro_audio)
        return intro, False

def get_blank_audio(clip_data):
    """
    Generates a blank audio clip given the blank audio data
    """

    audio = myp.AudioFileClip(os.path.join(resource_path, music_list[0]))
    audio = audio.fx(volumex, clip_data['Meta'].get("audioLevel"))
    audio = audio.set_duration(sherpaUtils.calculate_clip_length(clip_data['Meta']))

    return audio

def get_fps(proj_id):
    # Open proj_id
    # Get first clip
    # return fps
    global proj_fps
    logging.debug(proj_fps)
    if proj_fps > 0:
        logging.debug("Return")
        return proj_fps
    
    json_data = sherpaUtils.open_proj(proj_id)

    first_clip = json_data['CutAwayFootage'][next(iter(json_data['CutAwayFootage']))]
    logging.debug("First Clip")
    logging.debug(first_clip)
    clip_name = first_clip['Meta'].get('name')+".mp4"

    clip = myp.VideoFileClip(os.path.join(attach_dir, proj_id, clip_name))

    logging.debug("Clip FPS: {}".format(clip.fps))
    proj_fps = clip.fps
    logging.debug("proj_fps set to {}".format(proj_fps))
    return proj_fps
