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

        if chunk_render is True:
            chunk.chunk_driver(json_file, user, compress_render=compress_render, chunk_render=chunk_render)
        else:
            # Automated all the clips - Run through all the cutaway footage
            for clip_name in json_file['CutAwayFootage']:

                logging.debug(clip_name + ":")
                logging.debug("Cutaway Timeline: {}".format(cutaway_timeline))

                # Initialise clip data first
                clip_data = json_file['CutAwayFootage'][clip_name]

                clip_type = clip_data['Meta'].get('clipType')

                # If its a cutaway, just generate the clip and add a caption if it exists
                if clip_type == "CutAway":
                    logging.debug(clip_name + " is a cutaway.")
                    clip = generateEffects.generate_clip(clip_data=clip_data['Meta'], user=user, compressed=compress_render or chunk_render)
                    # Generate caption data
                    logging.debug("Generating audio for {}".format(clip_name))
                    clip = generateEffects.better_generate_text_caption(clip, clip_data['edit'], compressed=compress_render or chunk_render)
                    logging.debug("Inserting audio for clip '{}'     Clip Audio is {}   Audio length is {}".format(clip_name, clip.audio, clip.duration))
                    top_audio.insert(clip_data['Meta'].get('order'), clip.audio)

                # Generate image
                elif clip_type == "Image":
                    logging.debug(clip_name + " is an image.")
                    clip = generateEffects.generate_image_clip(clip_data['Meta'], user)            
                    logging.debug("Generating audio for {}".format(clip_name))
                    clip = generateEffects.better_generate_text_caption(clip, clip_data['edit'], compressed=compress_render or chunk_render)
                    logging.debug("Inserting audio for clip '{}'     Clip Audio is {}   Audio length is {}".format(clip_name, clip.audio, clip.duration))
                    top_audio.insert(clip_data['Meta'].get('order'), clip.audio)

                # If it's a blank
                elif clip_type == "Blank":
                    # These values are used later in the blank process
                    some_filler = False
                    total_insert_length = 0 
                    logging.debug("Generating audio for {}".format(clip_name))
                    logging.debug("Inserting audio for blank '{}'     Clip Audio is {}   Audio length is {}".format(clip_name, clip.audio, clip.duration))
                    top_audio.insert(clip_data['Meta'].get('order'), generateEffects.get_blank_audio(clip_data))
                    # We need to see if we can find any clips to replace the blank with
                    try:
                        logging.debug(clip_name + " is a blank.")
                        # We need to find the clip that should be playing in the interview timeline
                        cutaway_blank_len = sherpaUtils.calculate_clip_length(clip_data['Meta'])

                        # Gets clip on interview timeline that should be playing, as well as its start time on the interview timeline
                        relevant_interview_clip_data, interview_start_time = sherpaUtils.current_interview_footage(
                            data=json_file,
                            clip_timeline=cutaway_timeline
                        )

                        # rounding for simple calculation
                        interview_start_time = round(interview_start_time, 2)

                        # Set metadata for clip rendering and order for timeline insert
                        interview_clip_meta_data = relevant_interview_clip_data['Meta']
                        interview_clip_ord = interview_clip_meta_data.get('order')

                        # Difference between the current time in the video, and the start time of the interview clip
                        dif = round(cutaway_timeline-interview_start_time, 2)

                        
                        logging.debug("Interview clip starts at {}, Blank clip starts at {}, so difference is {}".format(
                            interview_start_time,
                            cutaway_timeline,
                            dif)
                        )

                        # Define clip length
                        clip_dur = sherpaUtils.calculate_clip_length(clip_data['Meta'])

                        sub_clip_start = (interview_clip_meta_data.get('startTime')) + dif
                        # Get end of clip or end of blank, whichever comes first
                        sub_clip_end = min(
                            ((interview_clip_meta_data.get('startTime')) + dif + clip_dur), 
                            interview_clip_meta_data.get('endTime')
                        )

                        # Round data off for simple calculation 
                        sub_clip_start = round(sub_clip_start, 2)
                        sub_clip_end = round(sub_clip_end, 2)

                        logging.debug("Sub clip starts at {}, ends at {}".format(sub_clip_start, sub_clip_end))

                        sub_clip_length = sub_clip_end - sub_clip_start
                        total_insert_length += sub_clip_length

                        interview_clip_type = interview_clip_meta_data.get('clipType')

                        # Create video clip from data found above
                        # Audio is not needed, we will insert it later
                        if interview_clip_type == "Interview":
                            logging.debug("Replacing blank {} with interview clip {}".format(
                                clip_data['Meta'].get('name'),
                                interview_clip_meta_data.get('name')
                            ))
                            # Create clip with parameterised start and end times
                            clip = generateEffects.generate_clip(
                                clip_data=interview_clip_meta_data,
                                user=user,
                                start=sub_clip_start,
                                end=sub_clip_end,
                                compressed=compress_render or chunk_render
                            )

                            clip = generateEffects.better_generate_text_caption(clip, relevant_interview_clip_data['edit'], compressed=compress_render or chunk_render)

                        # Blanks from the cutaway can be placed instead
                        elif interview_clip_type == "Blank":
                            
                            logging.debug("Replacing blank {} with interview blank {}".format(
                                clip_data['Meta'].get('name'),
                                interview_clip_meta_data.get('name')
                            ))
                            clip = generateEffects.generate_blank(interview_clip_meta_data, start=sub_clip_start, end=sub_clip_end, compressed=compress_render or chunk_render)
                            clip = generateEffects.better_generate_text_caption(clip, relevant_interview_clip_data['edit'], compressed=compress_render or chunk_render)

                        # TODO: Careful here, rounding could cause issues
                        total_insert_length = round(total_insert_length, 2)
                        logging.debug("Insert lenght: {}".format(total_insert_length))

                        # If the blank length is longer than the length of the videos being inserted
                        while not isclose(total_insert_length, cutaway_blank_len):
                            some_filler = True
                            logging.debug("Clip length didn't suffice for blank, adding more files as necessary")

                            time_to_fill = cutaway_blank_len - total_insert_length

                            time_to_fill = round(time_to_fill, 2)

                            logging.debug("Time left to fill is {}".format(time_to_fill))

                            interview_clip_ord+=1

                            next_clip_data = sherpaUtils.give_clip_order(interview_clip_ord, json_file['InterviewFootage'])

                            # Clip should be the the same size as the time to fill if possible
                            # But it's also possible that the next clip isn't bi enough either
                            # So we'll need to go further on
                            # To stop bugs, we need to set our end time as either the time left to fill, or the length of the clip
                            end_time = round(min(
                                next_clip_data['Meta'].get('startTime') + time_to_fill,
                                sherpaUtils.calculate_clip_length(next_clip_data['Meta'])
                            ), 2)

                            logging.debug("End time for clip is {}".format(end_time))


                            if next_clip_data['Meta'].get('clipType') == "Interview":
                                next_clip = generateEffects.generate_clip(
                                    clip_data=next_clip_data['Meta'],
                                    end=next_clip_data['Meta'].get('startTime')+end_time,
                                    user=user,
                                    compressed=compress_render or chunk_render
                                )
            
                                next_clip = generateEffects.better_generate_text_caption(next_clip, next_clip_data['edit'], compressed=compress_render or chunk_render)
            
                            elif next_clip_data['Meta'].get('clipType') == "Blank":
                                next_clip = generateEffects.generate_blank(next_clip_data['Meta'], end=end_time, compressed=compress_render or chunk_render)
                                next_clip = generateEffects.better_generate_text_caption(next_clip, next_clip_data['edit'], compressed=compress_render or chunk_render)

                            total_insert_length += next_clip.duration
                            logging.debug("Total insert length {}".format(total_insert_length))

                            clip = concatenate_videoclips([clip, next_clip])
                        logging.debug("Blank clip '{}' has been replaced with interview clips as necessary".format(clip_name))

                    # No clip can be found, generate the clip from the blank data in the cutaway timeline
                    except TypeError:
                        if some_filler:
                            logging.debug("Some suitable clips have been found from the interview clip, but a discrepency has still occured")
                            logging.debug("{}s of footage failed to be found in the interview footage".format(time_to_fill))
                            logging.debug("Inserting interview clips that have been found.")
                        if some_filler == False:
                            logging.error("TypeError in render - No clip found to replace blank '{}'".format(clip_data['Meta'].get("name")))
                            logging.debug("Rendering out blank file found in cutaway timeline instead")
                            clip = generateEffects.generate_blank(clip_data['Meta'], compressed=compress_render or chunk_render)            
                            clip = generateEffects.better_generate_text_caption(clip, clip_data['edit'], compressed=compress_render or chunk_render)


                # Insert clip into correct position in array
                logging.debug("Inserted clip '{}' into pos {}.".format(clip_name, clip_data['Meta'].get('order')-1))

                cutaway_timeline = round((cutaway_timeline+clip.duration), 2)
                video_list.insert(clip_data['Meta'].get('order')-1, clip)

            # Video list

            logging.debug("Video list:")
            logging.debug(video_list)

            # Create audio from the interview Footage
            bottom_audio = generateEffects.interview_audio_builder(interview_data=json_file['InterviewFootage'], user=user)

            # We need to insert the intro if it exists
            if os.path.exists(os.path.join(attach_dir, user, "intro.mp4")):
                intro_clip = generateEffects.create_intro_clip(user, compress_render)
                video_list.insert(0, intro_clip)
                logging.debug("Inserting audio for clip '{}'     Clip Audio is {}   Audio length is {}".format(intro_clip, intro_clip.audio, intro_clip.duration))
                top_audio.insert(0, intro_clip.audio)
                bottom_audio.insert(0, intro_clip.audio)
            else:
                logging.error("No intro clip found, continuing")

            # Concatenate the clips together
            top_audio = concatenate_audioclips(top_audio)    
            logging.debug("Top audio len: {}".format(round(top_audio.duration, 2)))

                
            # Try adding the music if it exists
            logging.debug("Attempting to add music...")
            try:
                music_data = json_file['Music']
                music = generateEffects.open_music(music_data, cutaway_timeline)
                # If the video is longer than the music, replay it
                if music.duration > cutaway_timeline:
                    music = CompositeAudioClip([music, generateEffects.open_music(music_data, cutaway_timeline - music.duration)])
                top_audio = CompositeAudioClip([top_audio, music])
                logging.debug("Music added successfully")
            except Exception as e:
                logging.debug("Exception occured in render - during music audio building:")
                logging.debug(e)
                finished_audio = top_audio

            # Try concatenating the top and bottom audio lines together
            logging.debug("Attepting to add interview audio...")
            try:
                bottom_audio = concatenate_audioclips(bottom_audio)    
                logging.debug("Bottom audio len: {}".format(round(bottom_audio.duration, 2)))
                finished_audio = CompositeAudioClip([top_audio, bottom_audio])
                logging.debug("Interview audio addedd successfully")
            except Exception as e:
                logging.debug("Exception occured in render - during interview audio building:")
                logging.debug(e)
                finished_audio = top_audio

            logging.debug("Finished audio len: {}".format(round(finished_audio.duration, 2)))

            # Concatenate the video files together
            finished_video = concatenate_videoclips(video_list)
            finished_video = finished_video.set_audio(finished_audio)


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
                    send_end.send(results)

                except:
                    logging.error("Fatal error occured while writing video - Full Render")
                    logging.exception("")
                    logging.error("Exiting program without writing video file correctly")
                    results = "Video not rendered [ERROR OCCURED, VIEW LOGS '{}' FOR MORE DETAILS]".format(log_name), 99
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


render_video("2303")