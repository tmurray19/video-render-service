import os
import json
from config import Config
from math import isclose
import logging, copy

# Defining the location of the Azure File Share and the name of the json file to look for in a given project
attach_dir = os.path.join(Config.BASE_DIR, Config.VIDS_LOCATION)
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


# Gives length of a given clip
def calculate_clip_length(clip_data):
    start = clip_data.get('startTime')
    end = clip_data.get('endTime')

    return round((end - start), 2)


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
        if (round((runtime - timeline_len), 2)) < 0.1:
            return (round((runtime - timeline_len)+0.1, 2))
        return round((runtime - timeline_len), 2)
    return round(runtime, 2)


def give_clip_order(clip_order, json_data):
    """
    clip_order: int --> The order of the clip you're looking for
    json_data: dict --> The data to be searching through
    
    Function for finding a clip in a file, given its order
    """
    for item in json_data:
        if json_data[item]['Meta'].get('order') == clip_order:
            return json_data[item]
            

def get_clip_at_time(time, json_data):
    """
    JSON data needs to be either cutaway or interview
    """
    #print("TIME TO REPLACE ", time)
    run_time = 0
    for item in json_data:
        #print("RUN TIME ", run_time)
        #print(json_data[item]['Meta'])
        if json_data[item]['Meta'].get('fullContextEnd') >= time:
            return json_data[item]
        run_time += calculate_clip_length(json_data[item]['Meta'])

def get_next_clip(order, clip_timeline):
    """ 
    Takes order and clip timeline,
    And returns clip with order plus one
    """
    pass
    for item in clip_timeline:
        if clip_timeline[item]['Meta']['order'] == order+1:
            return clip_timeline[item]


def tidy_clip(clip_json, start, end, blank_clip):
    """ Tidys an interview clip to be placed into a blank
    clip_json is the interview clip
    start and end must be full context"""
    if clip_json['Meta']['fullContextStart'] == 0:
        clip_json['Meta']['startTime'] = clip_json['Meta']['startTime'] + start
    else:                         
        clip_json['Meta']['startTime'] = clip_json['Meta']['startTime'] + (start - clip_json['Meta']['fullContextStart'])

    if clip_json['Meta']['fullContextEnd'] > end:
        clip_json['Meta']['endTime'] = clip_json['Meta']['startTime'] + (end - start)
    
    clip_json['Meta']['order'] = blank_clip['Meta']['order']


    return clip_json


def blank_json_replace(blank_start, blank_end, json_data, blank_clip):
    """
    blank_start and blank_end need to be full context for this to work correctly
    """
    #print(json_data['InterviewFootage'])
    for item in json_data['InterviewFootage']:
        if json_data['InterviewFootage'][item]['Meta']['fullContextStart'] <= blank_start:
            if json_data['InterviewFootage'][item]['Meta']['fullContextStart'] < blank_start and json_data['InterviewFootage'][item]['Meta']['fullContextEnd'] <= blank_start :
                # Clip doesn't play during blank
                continue
            interview_clip = copy.deepcopy(json_data['InterviewFootage'][item])
            interview_order = interview_clip['Meta']['order']
            interview_clip = tidy_clip(interview_clip, blank_start, blank_end, blank_clip)           
             # Either clip plays over full blank duration, or it doesn't                
            if json_data['InterviewFootage'][item]['Meta']['fullContextEnd'] >= blank_end:
                # This is if it does

                print(interview_clip)
                print(json_data['InterviewFootage'])

                return interview_clip
            else:
                try:
                    time_to_fill = (blank_end - blank_start)
                    print("TIME TO FILL: ", time_to_fill)
                    print(interview_clip)
                    interview_clips = []

                    interview_clips.append(interview_clip)

                    interview_len = calculate_clip_length(interview_clip['Meta'])

                    blank_start += interview_len
                    time_to_fill -= interview_len

                    cut_order = interview_clip['Meta']['order'] + 1 

                    print("int ord:", interview_order)
                    next_clip = get_next_clip(interview_order, json_data['InterviewFootage'])
                    next_copy = copy.deepcopy(next_clip)
                    print("TIME TO FILL: ", time_to_fill)
                    while time_to_fill > 0.1:
                        print("_________________________________________")
                        print("NEW LOOP")                        
                        print("INTERVIEW ORDER:", interview_order)
                        next_clip['Meta']['order'] = interview_order+1
                        interview_order+=1
                        print("INTERVIEW ORDER IS NOW: ", interview_order)
                        print("WE PUT IN")                 
                        print(next_clip)
                        print("\n")
                        next_copy['Meta']['order'] = cut_order
                        cut_order +=1              
                        interview_clips.append(next_copy)
                        interview_len = calculate_clip_length(next_clip['Meta'])


                        next_clip = get_next_clip(interview_order, json_data['InterviewFootage'])
                        next_copy = copy.deepcopy(next_clip)
                        print("CLIP IS NOW")
                        print(next_clip)                    
                        blank_start += interview_len
                        time_to_fill -= interview_len
                        print("TIME TO FILL: ", time_to_fill)

                    #print(interview_clips)
                    json_data['CutAwayFootage'] = update_order(json_data['CutAwayFootage'], blank_clip['Meta']['order'], (len(interview_clips))-1 )
                    return interview_clips
                except:
                    if interview_clips:
                        logging.debug("Something went wrong, filling the array with a blank instead")                
                        end_of_line_blank = {
                                "Meta": {
                                    "name": "broken_blank",
                                    "startTime": 0,
                                    "endTime": time_to_fill,
                                    "audioLevel": 1,
                                    "order": interview_clips[-1]["Meta"]['order']+1,
                                    "clipType": "CustomBlank"
                                }
                        }


                        interview_clips.append(end_of_line_blank)                    
                        json_data['CutAwayFootage'] = update_order(json_data['CutAwayFootage'], blank_clip['Meta']['order'], (len(interview_clips))-1 )
                        return interview_clips

def update_order(json_data, starting_point, amount):
    """
    Amount you want to update the current order by
    From what position in the json data do you want to start
    The json timeline you want to update the order of

    This function is designed to update the order of all the clips in a given timeline, from a specified position
    """
    print("__________________________________________")
    print("OLD")
    print(json_data)
    for item in json_data:
        if json_data[item]['Meta']['order']>starting_point:
            print("ORDER: ", json_data[item]['Meta']['order'])
            json_data[item]['Meta']['order']+=amount
    print("NEW")
    print(json_data)
    return json_data
    

def split_text(caption):
    """
    Takes a caption, and attempts to do a few things:

    divides the string by two to get the middle of the string
    searches left and right to find the closest space charater
    breaks the string into two at the space closest to the middle
    replaces the space between two strings with a new line
    returns the new string
    """
    caption = list(caption)
    left, right = ''.join(caption[:len(caption)//2]), ''.join(caption[len(caption)//2:])

    left_val = left.find(' ')
    right_val = right.find(' ')
    

    caption.insert((min(left_val+len(caption)//2, right_val+len(caption)//2)), '\n')

    
    return ''.join(caption)
