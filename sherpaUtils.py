import os
import azureFileTransfer
import json
from config import Config

# Defining the location of the Azure File Share and the name of the json file to look for in a given project
attach_dir = Config.DIR_LOCATION
proj = Config.PROJECT_NAME

"""
Utility functions for accessing and mutating files
"""

def open_proj(id):
    """
    id: string --> The id of the project
    
    Looks for the id within the video folder of the azure file share attachment, and opens the video
    """
    with open(os.path.join(attach_dir, id, proj)) as jfile:
        data = json.load(jfile)

    return data


def open_interview(data):
    """
    Data: dict --> The JSON data, opened as a dictionary using json.load

    Returns the interview data found in the json file
    """
    interview_data = data['InterviewFootage']
    return interview_data


# Pass the json file through this data
def open_interview_meta_data(data, clip):
    """
    data: dict --> The entire JSON data
    clip: string --> The name of the Clip dictionary within the json data you're searching for

    Returns the meta metadata for the interview track of the json file
    """
    # Read JSON File Name and load file
    interview_data = data['InterviewFootage']
    return interview_data[clip]['Meta']


# Pass the json file through this data
def open_interview_edit_data(data, clip):
    """Reads edit data for the interview track of the json file"""
    try:
        interview_data = data['InterviewFootage']
        return interview_data[clip]['edit']
    except KeyError:
        print("No edit data could be found for clip: {}".format(clip))
        return 0


def open_interview_caption_data(data, clip):
    try:
        """Reads caption data for interview clip in json file"""

        interview_data = data['InterviewFootage']
        return interview_data[clip]['edit']['Caption']
    except KeyError:
        print("Error: Clip '{}' has no Caption Data or Caption Data could not be found".format(clip))
        return 0


def open_cut_away(data):
    """Opens and returns the cutaway data in the JSON file"""
    clip_data = data['CutAwayFootage']
    return clip_data


def open_clip_meta_data(data, clip):
    """
    Opens and reads the metadata from a given JSON file name
    :param clip: string --> Name of clip
    :return: clip_data: dict  --> The clip data stored in JSON file
    It returns the first element of the meta section for a given clip in the JSON file,
    which is the entire meta data for the given file
    """
    # Defining common calls
    clip_data = data['CutAwayFootage']

    return clip_data[clip]['Meta']


def open_clip_edit_data(data, clip):
    try:
        # Get 'edit' section of json
        clip_data = data['CutAwayFootage']

        return clip_data[clip]['edit']
    except KeyError:
        print("No edit data could be found for clip: {}".format(clip))
        return 0


def open_clip_caption_data(data, clip):
    """
    Opens and reads the caption data from a given JSON file name
    Looks for an 'edit' list in the JSON file
    :param clip: string --> Name of clip
    :param proj_file_name: string  --> JSON file name
    :param user: string --> Name of user accessing directory
    :return: caption_data: dict  --> The caption data stored in JSON file
    Searches specifically for the caption section in the edit data
    """
    try:
        # Get 'edit' section of json
        clip_data = data['CutAwayFootage']
        return clip_data[clip]['edit']['Caption']

    except KeyError:
        print("Error: Clip '{}' has no Caption Data or Caption Data could not be found".format(clip))
        return 0


# Gives the name of the overall project, passing its filename through
def get_proj_name(data):
    proj_name = data.get('Name')
    return proj_name


# Sets caption duration to clip duration if one is longer than the other
def max_duration(caption_duration, clip_duration):
    if caption_duration > clip_duration:
        return clip_duration
    return caption_duration


# Gives length of a given clip
def calculate_clip_length(clip_data):
    start = clip_data.get('startTime')
    end = clip_data.get('endTime')

    return end - start


# Find currently playing interview footage, and returns the JSON item
def current_interview_footage(data, clip_timeline):
    interview_runtime = 0

    interview_data = data['InterviewFootage']
    # Check all the items in the interview data
    for item in interview_data:
        # Check the function above for calculating clip length
        clip_length = calculate_clip_length(interview_data[item]['Meta'])
        # add up all the interview clip run times as they appear
        interview_runtime += clip_length
        # If we find that an item exceeds or meets the current run time (where a blank should be), we return that clip
        if interview_runtime > clip_timeline:
            # Return the clip, its start time in the interview timeline, and its endtime
            return interview_data[item], interview_runtime - clip_length
    # Should only get here if no suitable clip has been found
    raise TypeError("No clip has been found")

def calculate_timeline_length(timeline_data):
    """
    timeline_data: dict --> The dictionary/json data for a timeline of a render, whether it's the
        interview timeline or the cutaway timeline
    
    Function for calculating the runtime of the given timeline. Calls the caclulate_clip_lenght on all the clips in the timeline
    """
    length = 0

    for item in timeline_data:
        length += calculate_clip_length(timeline_data[item]['Meta'])

    return length


def order_picker(timeline_1_runtime, timeline_2_runtime):
    """
    timeline_1_runtime, timeline_2_runtime: int --> The timeline lenghts in seconds
    This function returns the dictionary of either timelines, depending on which of the two is larger
    Purpose of the function is to decide which timeline should get the end of timeline blank
    The timeline with the smallest runtime should be the one to get the blank
    """
    if timeline_1_runtime < timeline_2_runtime:
        return 'CutAwayFootage'
    else:
        return 'InterviewFootage'


def calculate_time_at_clip(clip_data, clip_timeline_data, timeline_len=None):
    """
    clip_data: dict --> The dictionary information of the clip, specifically it's metadata
    clip_timeline_data: dict --> The dictionary information of the timeline the clip is coming from
    timeline_len: int --> The lenght of the smaller timeline, for calculating the lenght of the blank

    This function is designed to take in a clip, and give out the time that clip should be playing at in it's current timeline
    It runs through the dictionary, and for all items whose order is less than the clip_data order
    It calculates the lenght of the clip, and adds it to a holder variable
    It then returns this completed calculated value"""

    runtime = 0
    ord = clip_data.get('order')
    
    for clip in clip_timeline_data:
        if clip_timeline_data[clip]['Meta'].get('order') <= ord:
            clip_time = calculate_clip_length(clip_timeline_data[clip]['Meta'])
            runtime += clip_time

    if timeline_len is not None:
        return runtime - timeline_len
    return runtime


def give_clip_order(clip_order, json_data):
    """
    clip_order: int --> The order of the clip you're looking for
    json_data: dict --> The data to be searching through
    
    Function for finding a clip in a file, given its order
    """
    for item in json_data:
        if json_data[item]['Meta'].get('order') == clip_order:
            return json_data[item]
            

def truncate(n, decimals=0):
    multiplier = 10 ** decimals
    return int(n * multiplier) / multiplier