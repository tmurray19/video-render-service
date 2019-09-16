from moviepy.editor import CompositeVideoClip, concatenate_videoclips, concatenate_audioclips, CompositeAudioClip
from config import Config
import logging, time, os
from math import ceil
import generateEffects, sherpaUtils

attach_dir = os.path.join(Config.BASE_DIR, Config.VIDS_LOCATION)


def chunk_driver(json_data, user, send_end=None, compress_render=False, chunk_render=False):
    cutaways = []
    interviews = []
    
    start_time = time.time()

    for item in json_data['CutAwayFootage']:               
        logging.debug('Iterating through cutaway footage') 
        clip_data = json_data['CutAwayFootage'][item]

        logging.debug(item)
        # Get clip type
        clip_type = json_data['CutAwayFootage'][item]['Meta'].get('clipType')

        if clip_type == "Cutaway":
            logging.debug("'{}' is a cutaway".format(item))                    
            clip = generateEffects.generate_clip(clip_data=clip_data['Meta'], user=user, compressed=compress_render or chunk_render)
            # Generate caption data
            logging.debug("Creating text caption for {}".format(item))
            clip = generateEffects.better_generate_text_caption(clip, clip_data['edit'], compressed=compress_render or chunk_render)
        elif clip_type == "Image":
            logging.debug("'{}' is an image".format(item))
            clip = generateEffects.generate_image_clip(clip_data['Meta'], user)
            logging.debug("Generating text caption for '{}'".format(item))
            clip = generateEffects.better_generate_text_caption(clip, clip_data['edit'], compressed=compress_render or chunk_render)
        else:
            logging.debug("'{}' is a blank, render transparent image".format(item))
            clip = generateEffects.generate_blank(clip_data['Meta'], compressed=compress_render or chunk_render)
        cutaways.insert(clip_data['Meta'].get('order'), clip)

    
    for item in json_data['InterviewFootage']:
        logging.debug("Iterating through interview footage")
        clip_data = json_data['InterviewFootage'][item]
        
        logging.debug(item)

        clip_type = json_data['InterviewFootage'][item]['Meta'].get('clipType')

        
        if clip_type == "Interview":
            logging.debug("'{}' is an interview".format(item))                    
            clip = generateEffects.generate_clip(clip_data=clip_data['Meta'], user=user, compressed=compress_render or chunk_render)
            logging.debug("Creating text caption for {}".format(item))
            clip = generateEffects.better_generate_text_caption(clip, clip_data['edit'], compressed=compress_render or chunk_render)
        elif clip_type == "Image":
            logging.debug("'{}' is an image".format(item))
            clip = generateEffects.generate_image_clip(clip_data['Meta'], user)
            logging.debug("Generating text caption for '{}'".format(item))
            clip = generateEffects.better_generate_text_caption(clip, clip_data['edit'], compressed=compress_render or chunk_render)
        else:
            logging.debug("'{}' is a blank, render transparent image".format(item))
            clip = generateEffects.generate_blank(clip_data['Meta'], compressed=compress_render or chunk_render)
        interviews.insert(clip_data['Meta'].get('order'), clip)

    logging.debug('Files added in {}s'.format(time.time() - start_time))

    cutaways = concatenate_videoclips(cutaways)
    interviews = concatenate_videoclips(interviews)

    finished_video = CompositeVideoClip([cutaways, interviews])

                        
