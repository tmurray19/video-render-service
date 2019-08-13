import moviepy.editor as myp
import sherpaUtils
import os
from config import Config
import logging

silence_path = os.path.join(Config.DIR_LOCATION, Config.RESOURCE_PATH, Config.SILENCE)
attach_dir = Config.DIR_LOCATION

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

    audio = myp.AudioFileClip(silence_path)

    blank_clip = blank_clip.set_audio(audio.set_duration(dur))

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
    
    print("clip length: {}".format(clip.duration))

    if clip.audio is None:
        print("No clip audio found")
        audio = myp.AudioFileClip(silence_path)
        clip = clip.set_audio(audio.set_duration(end - start))
    return clip


# Generates an image clip based on json data
def generate_image_clip(clip_data, user):
    """'name' in this case refers to related file name of image"""
    # TODO

    image_clip = myp.ImageClip(
        img=os.path.join(attach_dir, user)+clip_data.get('name'),
        duration=clip_data.get('duration')
    )

    audio = myp.AudioFileClip(silence_path)

    image_clip = image_clip.set_audio(audio.set_duration(clip_data.get('duration')))

    print("Image clip successfully generated.")

    return image_clip


def interview_audio_builder(interview_data, user):
    sound_builder = []

    # For each item in the interview timeline
    for item in interview_data:

        # If it's a blank, add silence for the length of the clip ( May not be necessary? )
        if interview_data[item]['Meta'].get('clipType') == "Blank":
            sound_builder.append(
                myp.AudioFileClip(silence_path).set_duration(
                    (interview_data[item]['Meta'].get('endTime')) -
                    (interview_data[item]['Meta'].get('startTime'))
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
            sound_builder.append(audio)

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
        
        
        clip = myp.CompositeVideoClip([clip, text_caption.set_start(1)])
    
        return clip

    except Exception as e:
        print("Exception occured in text caption generation: {}".format(e))
        #print(e)
        return clip
        


def open_music_clip(music_choice):
    """
    music_choice: string --> Which music file to open

    For opening the music clip
    """
    #music = myp.AudioFileClip(music_choice)

    return 0