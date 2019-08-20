import moviepy.editor as myp
from moviepy.audio.fx.volumex import volumex
import sherpaUtils
import os
from config import Config
import logging

resource_path = os.path.join(Config.BASE_DIR, Config.VIDS_LOCATION, Config.RESOURCE_PATH)
attach_dir = os.path.join(Config.BASE_DIR, Config.VIDS_LOCATION)

positions = {
    1: ("left", "top"),  # Top Left
    2: ("right", "top"),  # Top Right
    3: ("center", "top"),  # Top center
    4: ("left", "center"),  # Center left
    5: "center",  # Center of image
    6: ("right", "center"),  # Center right
    7: ("left", "bottom"),  # Center left
    8: ("center", "bottom"),  # Center bottom
    9: ("right", "bottom")  # Center right
}

sizes = {
    "small": 12,
    "medium": 20,
    "large": 80,
    "x-large": 160,
    "xx-large": 400
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

# Generate a blank image
# Add text right now just for clarity sake
def generate_blank(clip_data, start=None, end=None, compressed=False):

    if start is None:
        start = (clip_data.get('startTime'))

    if end is None:
        end = (clip_data.get('endTime'))
        
    dur = end - start

    
    vid_size = [582, 480] if compressed else [1920, 1080]

    blank_clip = myp.ColorClip(
        size=vid_size,
        color=(0, 0, 0),
        duration=dur
    )

    audio = myp.AudioFileClip(os.path.join(resource_path, music_list[0]))

    blank_clip = blank_clip.set_audio(audio.set_duration(dur))
    blank_clip.fps = 24

    return blank_clip


def generate_clip(clip_data, user, start=None, end=None, compressed=False):
    """Generates clip data directly, without calling sherpaUtils within function"""
    related_file_name = clip_data.get('name')+"_com.mp4" if compressed else clip_data.get('name')+".mp4"

    if start is None:
        start = (clip_data.get('startTime'))

    if end is None:
        end = (clip_data.get('endTime'))

    # Get clip with defined start and end times
    clip = myp.VideoFileClip(os.path.join(attach_dir, user, related_file_name)).subclip(
        start,
        end
    )

    # Reduce volume defined in data
    clip = clip.volumex(clip_data.get('audioLevel'))
    
    if not compressed:
        clip = clip.resize((1920, 1080)) 
    
    logging.debug("clip '{}' length: {}".format(clip_data.get('name'), clip.duration))

    if clip.audio is None:
        logging.error("No clip audio found for clip {}".format(clip_data.get('name')))
        audio = myp.AudioFileClip(os.path.join(resource_path, music_list[0]))
        clip = clip.set_audio(audio.set_duration(end - start))

    clip.fps = 24
    return clip


# Generates an image clip based on json data
def generate_image_clip(clip_data, user):
    """'name' in this case refers to related file name of image"""
    # TODO

    image_clip = myp.ImageClip(
        img=os.path.join(attach_dir, user)+clip_data.get('name'),
        duration=clip_data.get('duration')
    )

    audio = myp.AudioFileClip(os.path.join(resource_path, music_list[0]))

    image_clip = image_clip.set_audio(audio.set_duration(clip_data.get('duration')))
    image_clip.fps = 24

    logging.debug("Image clip successfully generated.")

    return image_clip


def interview_audio_builder(interview_data, user):
    sound_builder = []

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


def better_generate_text_caption(clip, edit_data):
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

        # TODO: Change
        dur = max(1, clip.duration - 2)
    
        # Define Text Data
        text_caption = myp.TextClip(
            txt=caption_data.get('text'),
            fontsize=caption_data.get('fontSize'),
            color=caption_data.get('fontColour'),
        )

        text_caption = text_caption.set_position(
            positions[caption_data.get('screenPos')]).set_duration(dur)
        
        text_caption.fps = 24
        clip = myp.CompositeVideoClip([clip, text_caption.set_start(1)])
    
        return clip

    except Exception as e:
        print("Exception occured in text caption generation: {}".format(e))
        logging.debug("Exception occured in text caption generation: {}".format(e))
        return clip
        


def open_music(music_data, dur):
    """
    music_choice: string --> Which music file to open
    dur: int --> The duration of the video

    For opening the music clip
    """
    try:
        music = myp.AudioFileClip(os.path.join(resource_path, music_list[music_data.get("choice")]))
        music = music.fx(volumex, music_data.get("audioLevel"))
        music = music.set_duration(dur)

        # TODO: 2 second fade in and out automatically added
        music = music.audio_fadein(2)
        music = music.audio_fadeout(2)

        logging.debug("Music file '{}' chosen for video, cropped to {}s in length".format(music_list[music_data.get("choice")], dur))
        return music

    except Exception as e:
        logging.error("Exception occured during open_music: {}".format(e))
        return 0