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
            clip = generateEffects.generate_blank(clip_data['Meta'])
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
            clip = generateEffects.generate_blank(clip_data['Meta'])
        interviews.insert(clip_data['Meta'].get('order'), clip)

    logging.debug('[CHUNK] Files added in {}s'.format(time.time() - start_time))

    cutaways = concatenate_videoclips(cutaways)
    interviews = concatenate_videoclips(interviews)

    finished_video = CompositeVideoClip([cutaways, interviews])


    vid_name = user + "_com_chunk_edited.mp4"
    vid_dir = os.path.join(attach_dir, user, vid_name)    

    if finished_video.duration<Config.PREVIEW_CHUNK_LENGTH:
        logging.debug("Rendering Video as it's smaller than chunk length")
        finished_video.write_videofile(
            vid_dir,
            threads=8,
            preset="ultrafast",
            bitrate="1000k",
            audio_codec="aac",
            remove_temp=True,
            fps=24
        )
        results = "Video Rendered Successfully", 1
        send_end.send(results)
        return
    logging.debug("Running chunk render instance")
    # Get 10 second chunks of videos
    logging.debug("Splitting video up into 10s chunks.")
    
    # Initialising variables
    finished_dur = round(finished_video.duration, 2)
    chunk_len = Config.PREVIEW_CHUNK_LENGTH
    preview_chunks = []
    playtime = 0

    # Getting segment amount (rounded up to account for section that doesn't fit within chunk lenght)
    segment_no = ceil(finished_dur/chunk_len)
    # hangover segment

    logging.debug("Video duration: {}s  /{}s = {} segments      full segments: {}".format(finished_dur, chunk_len, finished_dur/chunk_len, segment_no))

    # _ is for non important variable
    for i in range(segment_no):
        preview_clip = finished_video.subclip(playtime, min(playtime+chunk_len, finished_dur))
        logging.debug("Clip is currently from {} to {}".format(playtime, round(min(playtime+chunk_len, finished_dur), 2)))

        playtime+=chunk_len
        logging.debug("Segment {} is {}s long".format(i, round(preview_clip.duration, 2)))
        preview_clip.fps = 24
        if preview_clip.duration < chunk_len/2:
            logging.debug("Clip is smaller than {}s, so appending it to last clip instead.")
            preview_clip = concatenate_videoclips([preview_clip, preview_chunks[-1]])
            del preview_chunks[-1]
        preview_chunks.append(preview_clip)


    
    logging.debug("Preview chunk list: ")
    logging.debug(preview_chunks)

    logging.debug("Rendering out {} videos in {}s chunks".format(len(preview_chunks), chunk_len))

    
    for video in preview_chunks:
        try:
            vid_name = user + "_com_chunk_" + str(preview_chunks.index(video)) + "_edited.mp4"
            vid_dir = os.path.join(attach_dir, user, vid_name)

            logging.debug("Rendering {} at time {}s".format(vid_name, (time.time() - start_time)))
            video.write_videofile(
                vid_dir,
                threads=8,
                preset="ultrafast",
                bitrate="1000k",
                audio_codec="aac",
                remove_temp=True,
                fps=24
            )
            results = "Video Rendered Successfully", 1
            send_end.send(results)
        except:
            logging.error("Fatal error occured while writing video - Chunk Render")
            logging.exception("")
            logging.error("Exiting program without writing video file correctly")                
            results = "Video not rendered [ERROR OCCURED, VIEW LOGS FOR MORE DETAILS]", 99
            send_end.send(results)
            return
    
    logging.debug('[CHUNK] Process comlete in {}s'.format(time.time() - start_time))                    
    results = "Video Rendered Successfully", 1
    send_end.send(results)
    return
                        
