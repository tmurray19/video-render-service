from moviepy.editor import CompositeVideoClip, concatenate_videoclips, concatenate_audioclips, CompositeAudioClip
from config import Config
from datetime import datetime
from math import ceil, isclose
import generateEffects, sherpaUtils, os, time, logging, gc
import chunk

# TODO: This needs to be changed in the app.config to
#  read to the correct attach directory as outlined in the configuration
attach_dir = os.path.join(Config.BASE_DIR, Config.VIDS_LOCATION)


def render_video(user, send_end=None, compress_render=False, chunk_render=False):
    """
    User: String -> The ID of the project (User is just a hangover from previous builds)
    compress_render: Bool -> Set to true if you want this function to return a quick render
    """
    try:
        log_name = datetime.now().strftime("%Y.%m.%d-%H-%M-%S") + "_render_service_instance_id_{}.log".format(user)

        # Collecting garbage to clear out memory
        gc.collect()

        # Creating a logging instance for testing
        log_file_name = os.path.join(
            Config.BASE_DIR,
            Config.LOGS_LOCATION,
            Config.RENDER_LOGS, 
            log_name
        )

        logging.basicConfig(
            level=logging.DEBUG, 
            format='%(asctime)s %(levelname)-8s %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S',
            filename=log_file_name)
        logging.debug("Beginning render instance of project id {}".format(user))

        # For logging
        start_time = time.time()

        # Finished timeline video
        video_list = []

        # Top audio timeline
        top_audio = []

        # Define current length of video, in terms of the 'main' timeline
        cutaway_timeline = 0

        # Look for the json file in the project folder
        try:
            json_file = sherpaUtils.open_proj(user)
        except FileNotFoundError as e:
            logging.error("File or folder cannot be found")
            logging.error(e)
            results = "Render exited without error [Unable to find file or folder]", 0        
            send_end.send(results)
            return


        # If a file can be found, but no edit data exists in the file
        if not json_file['CutAwayFootage'] and not json_file['InterviewFootage']:
            logging.error("This project seems to have no edit data recorded. Exiting render session")
            results = "Render exited without error [No edit data exists in JSON]", 0        
            send_end.send(results)
            return


        # Get timeline lengths
        cutaway_timeline_length = round(sherpaUtils.calculate_timeline_length(json_file['CutAwayFootage']), 2)
        interview_timeline_length = round(sherpaUtils.calculate_timeline_length(json_file['InterviewFootage']), 2)

        logging.debug("Cutaway length: {}s      Interview length: {}s".format(cutaway_timeline_length, interview_timeline_length))

        # Find the smallest timeline length
        smallest_timeline = sherpaUtils.order_picker(cutaway_timeline_length, interview_timeline_length)
        
        if smallest_timeline == "CutAwayFootage":
            logging.debug("Smallest timeline is currently the Cut Away Timeline, correcting timelines as necessary")
            blank_no = 1

        # While the smallest timeline is the cut away timeline
        # TODO: THIS ISSUE MAY ONLY OCCUR IF THE CUTAWAY TIMELINE IS SHORTER THAN THE TOP TIMELINE
        while smallest_timeline == 'CutAwayFootage':
            # Calculate the length of the blank that should be playing at the smallest timeline 
            current_interview_clip = sherpaUtils.current_interview_footage(
                json_file, 
                cutaway_timeline_length
            )[0]

            # Calculate when the clip om the interview timeline should be playing (globally), and returns the length that the blank clip should be
            blank_len = sherpaUtils.calculate_time_at_clip(
                current_interview_clip['Meta'], 
                json_file['InterviewFootage'], 
                timeline_len=cutaway_timeline_length
            )

            # Creating a blank clip to insert into time
            blank_name = "end_of_line_blank_" + str(blank_no)

            end_of_line_blank = {
            blank_name: {
                    "Meta": {
                        "name": blank_name,
                        "startTime": 0,
                        "endTime": blank_len,
                        "audioLevel": 1,
                        "order": len(json_file[smallest_timeline])+1,
                        "clipType": "Blank"
                    },
                    "edit": {

                    }
                }
            }

            blank_no += 1
            logging.debug(blank_name + ":")
            logging.debug(end_of_line_blank)
            # Insert it into the timeline
            json_file[smallest_timeline].update(end_of_line_blank)

            # Update the length
            cutaway_timeline_length = round((cutaway_timeline_length+blank_len),2)
            logging.debug("Cutaway length: {}, Inteview length: {}".format(cutaway_timeline_length, interview_timeline_length))
                
            smallest_timeline = sherpaUtils.order_picker(cutaway_timeline_length, interview_timeline_length)

        cutaways = []
        interviews = []
        
        start_time = time.time()
        print(json_file)
        for item in json_file['CutAwayFootage']:               
            logging.debug('Iterating through cutaway footage') 
            clip_data = json_file['CutAwayFootage'][item]

            logging.debug(item)
            # Get clip type
            clip_type = json_file['CutAwayFootage'][item]['Meta'].get('clipType')

            if clip_type == "CutAway":
                logging.debug("'{}' is a cutaway".format(item))                    
                clip = generateEffects.generate_clip(clip_data=clip_data['Meta'], user=user, compressed=compress_render or chunk_render)
                # Generate caption data
                logging.debug("Creating text caption for {}".format(item))
                #clip = generateEffects.better_generate_text_caption(clip, clip_data['edit'], compressed=compress_render or chunk_render)
            elif clip_type == "Image":
                logging.debug("'{}' is an image".format(item))
                clip = generateEffects.generate_image_clip(clip_data['Meta'], user)
                logging.debug("Generating text caption for '{}'".format(item))
                #clip = generateEffects.better_generate_text_caption(clip, clip_data['edit'], compressed=compress_render or chunk_render)
            else:
                logging.debug("'{}' is a blank, render transparent image".format(item))
                clip = generateEffects.generate_blank(clip_data['Meta'])
            cutaways.insert(clip_data['Meta'].get('order'), clip)

        
        for item in json_file['InterviewFootage']:
            logging.debug("Iterating through interview footage")
            clip_data = json_file['InterviewFootage'][item]
            
            logging.debug(item)

            clip_type = json_file['InterviewFootage'][item]['Meta'].get('clipType')

            
            if clip_type == "Interview":
                logging.debug("'{}' is an interview".format(item))                    
                clip = generateEffects.generate_clip(clip_data=clip_data['Meta'], user=user, compressed=compress_render or chunk_render)
                logging.debug("Creating text caption for {}".format(item))
                #clip = generateEffects.better_generate_text_caption(clip, clip_data['edit'], compressed=compress_render or chunk_render)
            elif clip_type == "Image":
                logging.debug("'{}' is an image".format(item))
                clip = generateEffects.generate_image_clip(clip_data['Meta'], user)
                logging.debug("Generating text caption for '{}'".format(item))
                #clip = generateEffects.better_generate_text_caption(clip, clip_data['edit'], compressed=compress_render or chunk_render)
            else:
                logging.debug("'{}' is a blank, render transparent image".format(item))
                clip = generateEffects.generate_blank(clip_data['Meta'])
            interviews.insert(clip_data['Meta'].get('order'), clip)

        logging.debug('Files added in {}s'.format(time.time() - start_time))

        cuts = concatenate_videoclips(cutaways, method="compose")
        print(cuts.duration)
        ints = concatenate_videoclips(interviews, method="compose")
        print(ints.duration)

        finished_video = CompositeVideoClip([ints, cuts], use_bgclip=True)
        print(finished_video.duration)

        finished_video.write_videofile('complete.mp4')
        return
        # We need to insert the intro if it exists
        if os.path.exists(os.path.join(attach_dir, user, "intro.mp4")):
            intro_clip = generateEffects.create_intro_clip(user, compress_render)
            finished_video = CompositeVideoClip([intro_clip, finished_video])
            
        else:
            logging.error("No intro clip found, continuing")


                

        # Defining path here is cleaner
        vid_name = user + "_com_preview_edited.mp4" if compress_render else user + "_edited.mp4"
        vid_dir = os.path.join(attach_dir, user, vid_name)


        logging.debug("Rendering {} clip(s) together, of total length {}.".format(len(video_list), round(finished_video.duration, 2)))
        logging.debug("Writing '{}' to {}".format(vid_name, vid_dir))

        logging.debug("Videos placed in {} seconds".format(time.time() - start_time))

        # Render the finished project out into an mp4
        if chunk_render:
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
                    results = "Video not rendered [ERROR OCCURED, VIEW LOGS '{}' FOR MORE DETAILS]".format(log_name), 99
                    send_end.send(results)
                    return
            
            results = "Video Rendered Successfully", 1
            send_end.send(results)
            return
                
        if compress_render:
            logging.debug("Running compress render instance")
            try:
                finished_video.write_videofile(
                    vid_dir,
                    threads=8,
                    bitrate="1000k",
                    audio_codec="aac",
                    remove_temp=True,
                    fps=24
                )        
                results = "Video Rendered Successfully", 1
                send_end.send(results)
            except:
                logging.error("Fatal error occured while writing video - Compressed Render")
                logging.exception("")
                logging.error("Exiting program without writing video file correctly")
                results = "Video not rendered [ERROR OCCURED, VIEW LOGS '{}' FOR MORE DETAILS]".format(log_name), 99
                send_end.send(results)
                return        
        else:
            logging.debug("Running full render instance")
            try:
                logging.debug("Rendering {}".format(vid_name))
                finished_video.write_videofile(            
                    vid_dir,
                    threads=8,
                    audio_codec="aac",
                    bitrate="8000k",
                    remove_temp=True,
                    fps=24
                )        
                results = "Video Rendered Successfully", 1
                if send_end is not None:
                    send_end.send(results)
                return
            except:
                logging.error("Fatal error occured while writing video - Full Render")
                logging.exception("")
                logging.error("Exiting program without writing video file correctly")
                results = "Video not rendered [ERROR OCCURED, VIEW LOGS '{}' FOR MORE DETAILS]".format(log_name), 99
                if send_end is not None:
                    send_end.send(results)
                return

        logging.debug("File '{}' successfully written to {}".format(vid_name, vid_dir))
        logging.debug("Completed in {} seconds".format(time.time() - start_time))
        logging.debug("Closing render instance")
    except:
        logging.error("An unknown error has occured, causing video render instance to crash:")
        logging.exception("")
        results = "Unforseen error has occured [Contact admin]", 99      
        send_end.send(results)
        return

render_video("1149", compress_render=True)