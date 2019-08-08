import moviepy.editor as myp
import sherpaUtils
import os
from config import Config

DIR_LOCATION = 'G:/project'
RESOURCE_PATH = 'resource'
SILENCE = 'silence.mp3'


silence_path = os.path.join(Config.DIR_LOCATION, Config.RESOURCE_PATH, Config.SILENCE)
attach_dir = Config.DIR_LOCATION

positions = {
    0: ("left", "top"),  # Top Left
    1: ("right", "top"),  # Top Right
    2: ("center", "top"),  # Top center
    3: ("left", "center"),  # Center left
    4: "center",  # Center of image
    5: ("right", "center"),  # Center right
    6: ("left", "bottom"),  # Center left
    7: ("center", "bottom"),  # Center bottom
    8: ("right", "bottom")  # Center right
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
def generate_blank(clip_data):

    start = (clip_data.get('startTime'))
    end = (clip_data.get('endTime'))

    dur = end - start

    blank_clip = myp.ColorClip(
        size=[1920, 1080],
        color=(0, 0, 0),
        duration=dur
    )

    # Can be removed later
    text_caption = myp.TextClip(
        txt="This is a blank",
        color="White",
        fontsize=72
    )

    text_caption = text_caption.set_position('center').set_duration(dur)

    blank_clip = myp.CompositeVideoClip([blank_clip, text_caption])

    audio = myp.AudioFileClip(silence_path)

    blank_clip = blank_clip.set_audio(audio.set_duration(dur))

    return blank_clip


def generate_clip(clip_data, user, start=None, end=None):
    """Generates clip data directly, without calling sherpaUtils within function"""
    related_file_name = clip_data.get('name')+".mp4"

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

    clip = clip.resize((1920, 1080))
    print("clip length: {}".format(clip.duration))

    if clip.audio is None:
        print("No clip audio found")
        audio = myp.AudioFileClip(silence_path)
        clip = clip.set_audio(audio.set_duration(end - start))
    return clip


def generate_text_caption(caption_data, clip_data, dur=None):
    if dur is None:
        dur = (clip_data.get('endTime')) - (clip_data.get('startTime'))

    # Define Text Data
    text_caption = myp.TextClip(
        txt=caption_data.get('text'),
        fontsize=caption_data.get('fontSize'),
        color=caption_data.get('fontColour'),
    )

    # Define duration in case it
    # goes past the length of the clip
    # Although may not be necessary
    caption_duration = dur

    # Define completed text caption
    # Position taken from one of 9 possible locations
    text_caption = text_caption.set_position(
        positions[caption_data.get('screenPos')]).set_duration(caption_duration)

    print("Text caption '{}' for video '{}' has been generated.".format(caption_data.get('text'), clip_data.get('name')))

    return text_caption


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


# For reference
def add_audio_to_clip(clip_data, audio_data):
    return clip_data.set_audio(audio_data)


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


def better_generate_text_caption(clip_name):
    """
    clip_name: dict --> The json name for the clip

    Function is designed to take in the info for the clip, read the caption data for the clip,
    generate the caption, and return it

    This function also handles any error with no caption being found
    """
    clip_data = 0
    caption_data = 0

    start = (clip_data.get('startTime'))
    end = (clip_data.get('endTime'))

    dur = end - start

    blank_clip = myp.ColorClip(
        size=[1920, 1080],
        color=(0, 0, 0),
        duration=dur
    )

    # Can be removed later
    text_caption = myp.TextClip(
        txt="This is a blank",
        color="White",
        fontsize=72
    )

    text_caption = text_caption.set_position('center').set_duration(dur)

    blank_clip = myp.CompositeVideoClip([blank_clip, text_caption])

    audio = myp.AudioFileClip(silence_path)

    blank_clip = blank_clip.set_audio(audio.set_duration(dur))

    return blank_clip