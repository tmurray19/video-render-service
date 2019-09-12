from moviepy.editor import CompositeVideoClip, concatenate_videoclips, concatenate_audioclips, CompositeAudioClip
from config import Config
import logging
import generateEffects, sherpaUtils

def chunk_driver(json_data):
    """JSON data should be in a dict format

        Chunk render:
            - Split JSON Data up into equal sized chunks (10s)
            - Run through 10s JSON intervals
            - Create and render clip
    """
    # Let's go through the cutaway footage, and preprocess any blanks
    if json_data['InterviewFootage']:
        for item in json_data['CutAwayFootage']:
                logging.debug("Interview footage is not empty")
                # Then if the given item is a blank
                if json_data['CutAwayFootage'][item]['Meta'].get("clipType") == "Blank":
                    if not json_data['CutAwayFootage'][item]['edit']['Caption']:
                        # TODO: CHECK IF THIS IS THE CASE
                        logging.debug("Blank data holds no caption, so we can assume it replaces ")
                        # Time blank shows up in completed video 
                        blank_time_in_cutaway = sherpaUtils.calculate_time_at_clip(
                            json_data['CutAwayFootage'][item]['Meta'], 
                            json_data['CutAwayFootage']
                        )
                        
                        logging.debug("Replacing blank '{}' with cutaway footage".format(item))
                        logging.debug("Blank '{}' is playing at time {}".format(item, blank_time_in_cutaway))

                        # Get length of blank
                        blank_len = sherpaUtils.calculate_clip_length(json_data['CutAwayFootage'][item]['Meta'])
                        logging.debug("Blank's length is {}".format(blank_len))

                        """  
                        Get clip that should be playing on interview timeline, and its starttime
                        Why?

                        We need the clip data to move into the cutaway footage json

                        Start time is important 
                        We have the start and end time of the interview clip
                        but we need to trim it down to fit inside the blank, chances are the blank is smaller than the interview being played
                        Logic is the same:
                                startTime is distance between when the blank starts playing in the main timeline, and when the interview clip starts playing
                                startTime is beginning of blank + difference between beginning of blank and beginning of interview clip
                                endTime is startTime + lenght of blank 
                        Following that, we need to replace the blank with the interview clip:
                                Change
                        """
                        # We have the relevant interview clip for the blank, as well as when it starts on the interview timeline
                        relevant_interview_clip, interview_start_time = sherpaUtils.current_interview_footage(json_data, blank_time_in_cutaway)
                        interview_start_time = round(interview_start_time, 2)

                        logging.debug("Clip that should be playing over blank:")
                        logging.debug(relevant_interview_clip)

                        # Calculate length of clip - why?
                        # We need to get end time of clip to place into the blank
                        interview_len = sherpaUtils.calculate_clip_length(relevant_interview_clip['Meta'])
                        logging.debug("Interview clip plays for {}s".format(interview_len))

                        if blank_len>interview_len:
                            logging.debug("We need to add more clip from the interview clips")
                        
                        # Start time is time blank starts in timeline + length of cutaway
                        start_time = blank_time_in_cutaway + relevant_interview_clip['Meta'].get('startTime')

                        end_time = min(start_time + interview_len, start_time + blank_len)

                        # Get the clip name for moviepy
                        interview_clip_name = relevant_interview_clip['Meta'].get('name')

                        # Set caption data if it exists
                        if relevant_interview_clip['edit']['Caption']:
                            caption_data = relevant_interview_clip['edit']['Caption']
                        
                        # Interview start time should be difference between blank start time, and interview clip start time
                        # End time is start time plus clip duration
                        

                        # TODO: If we need to add multiple interview clips to one blank, then we also need to 


                        # We need to replace blank in interview with this clip
                        print("Check logs so far")
    else:
        logging.debug("No blank replacement necessary")
        logging.debug("Rendering file")

