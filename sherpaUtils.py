import os
import azureFileTransfer
import json


# TODO: CHANGE
DIR_LOCATION = 'G:/project'
PROJECT_NAME = 'FinalSubclipJson.json'

attach_dir = DIR_LOCATION
proj = PROJECT_NAME


"""
Utility functions for accessing and mutating files
"""


def set_proj(id):
    """Creates an Azure File Share instance and reads the json data found in the specified ID"""
    #azure = azureFileTransfer.create_share_dir(id)
    #data = azureFileTransfer.get_json(id, azure)

    with open(os.path.join(attach_dir, id, proj)) as jfile:
        data = json.load(jfile)

    return data


def open_json_file(data):
    """Opens entire JSON file for parsing
    Data: the JSON Data ( The path string )"""
    with open(data) as jfile:
        json_data = json.load(jfile)

    return json_data


def open_interview(data):
    """Opens and returns the interview data in the JSON file"""
    interview_data = data['InterviewFootage']
    return interview_data


# Pass the json file through this data
def open_interview_meta_data(data, clip):
    """Reads metadata for the interview track of the json file
    Data: The entire JSON data
    Clip: The name of the Clip dictionary within the json data you're searching for"""
    # Read JSON File Name and load file
    interview_data = data['InterviewFootage']
    return interview_data[clip]['Meta']


# Pass the json file through this data
def open_interview_edit_data(data, clip):
    try:
        """Reads edit data for the interview track of the json file"""

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


# Creating folders for files
def dir_create(relative_path='', user=''):
    """
    Likely Depreciated
    Creates 3 directories for various files
    Passes if any one of these directories already exists
    """
    try:
        os.mkdir(os.path.join(relative_path, user, 'json/'))
        os.mkdir(os.path.join(relative_path, user, 'clips/'))
        os.mkdir(os.path.join(relative_path, user, 'edited/'))
        print("Folders successfully initialised")
    except FileExistsError:
        print("One of these folders already exists.")


# Gives the name of the overall project, passing its filename through
def get_proj_name(data):
    proj_name = data.get('Name')
    return proj_name

"""
# return full directories for each folder
def get_edit_dir(relative_path='', user=''):
    try:
        edit_dir = os.path.join(
            relative_path,
            user,
            'edited/'
        )
        return edit_dir
    except FileNotFoundError:
        print("Edited folder not found.")
        return 0


# Written as concession for having folders in different locations to py files
def get_json_dir(relative_path='', user=''):
    try:
        json_dir = os.path.join(
            relative_path,
            user,
            'json/'
        )
        return json_dir
    except FileNotFoundError:
        print("JSON folder not found.")
        return 0


# May or may not be necessary, written for the case that files are stored elsewhere
def get_clips_dir(relative_path='', user=''):
    try:
        clips_dir = os.path.join(
            relative_path,
            user,
            'clips/'
        )
        return clips_dir
    except FileNotFoundError:
        print("Clips folder not found.")
        return 0
"""

# Get the directory attached to the container
# TODO
def get_attach_dir():
    pass


# Sets caption duration to clip duration if one is longer than the other
def max_duration(caption_duration, clip_duration):
    if caption_duration > clip_duration:
        return clip_duration
    return caption_duration


# Gives length of a given clip
def calculate_clip_length(clip_data):
    #has_duration = (clip_data.get('clipType') == "Blank" or clip_data.get('clipType') == "Image")

    # If it doesn't have a duration, do calculations
    #if has_duration is False:

    start = clip_data.get('startTime')
    end = clip_data.get('endTime')

    return end - start

    # If it does, just return the duration
    #else:
        #return clip_data.get('duration')


# Find currently playing interview footage, and returns the JSON item
def current_interview_footage(data, clip_timeline):
    interview_runtime = 0

    interview_data = open_interview(data)
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
