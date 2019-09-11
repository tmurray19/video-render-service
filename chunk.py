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
    for item in json_data['CutAwayFootage']:
        # Define chunks to hold json instances
        chunks = []
        print(item)
        print(json_data['CutAwayFootage'][item]['Meta'].get("startTime"))
        # Replace blanks in Cutaways with interview footage, see where it gets us
        if json_data['CutAwayFootage'][item]['Meta'].get("clipType") == "Blank":
            blank_time_in_cutaway = sherpaUtils.calculate_time_at_clip(
                json_data['CutAwayFootage'][item]['Meta'], 
                json_data['CutAwayFootage']
            )
            # We've found a blank - Replace it with whatever should be playing in the
            logging.debug("Replacing blank '{}' with cutaway footage".format(item))
            logging.debug("Blank '{}' is playing at time {}".format(item, blank_time_in_cutaway))
            blank_len = sherpaUtils.calculate_clip_length(json_data['CutAwayFootage'][item]['Meta'])
            logging.debug("Blank's length is {}".format(blank_len))
            relevant_interview_clip = sherpaUtils.current_interview_footage(json_data, blank_time_in_cutaway)[0]
            logging.debug("Clip that should be playing over blank:")
            logging.debug(relevant_interview_clip)
            interview_len = sherpaUtils.calculate_clip_length(relevant_interview_clip['Meta'])
            logging.debug("Interview clip plays for {}s".format(interview_len))
            # We need to replace blank in interview with this clip
            print("Check logs so far")
            
            

        


