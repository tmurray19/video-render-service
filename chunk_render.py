from moviepy.editor import CompositeVideoClip, concatenate_videoclips, concatenate_audioclips, CompositeAudioClip
from config import Config
from datetime import datetime
from math import ceil
import generateEffects, sherpaUtils, os, time, logging, gc, copy


attach_dir = os.path.join(Config.BASE_DIR, Config.VIDS_LOCATION)
proj = Config.PROJECT_NAME

def get_chunk(user, send_end=None, compress_render=False, chunk_render=False, chunk_number=0, all_clips=True):
    start_time_count = time.time()      
    log_name = datetime.now().strftime("%Y.%m.%d-%H-%M-%S") + "_chunk_service_instance_id_{}_TESTING.log".format(user)

    # Look for the json file in the project folder
    try:
        json_data = sherpaUtils.open_proj(user)
    except FileNotFoundError as e:
        logging.error("File or folder cannot be found")
        logging.error(e)
        results = "Render exited without error [Unable to find file or folder]", 0        
        if send_end is not None:
            send_end.send(results)
        return results

    # If a file can be found, but no edit data exists in the file
    if not json_data['CutAwayFootage'] and not json_data['InterviewFootage']:
        logging.error("This project seems to have no edit data recorded. Exiting render session")
        results = "Render exited without error [No edit data exists in JSON]", 0        
        if send_end is not None:
            send_end.send(results)            
        return results

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



    global_frames = generateEffects.get_fps(user)
    logging.debug("Global fps has been set to {}".format(global_frames))



    # Get timeline lengths
    cutaway_timeline_length = round(sherpaUtils.calculate_timeline_length(json_data['CutAwayFootage']), 2)
    interview_timeline_length = round(sherpaUtils.calculate_timeline_length(json_data['InterviewFootage']), 2)

    logging.debug("Cutaway length: {}s      Interview length: {}s".format(cutaway_timeline_length, interview_timeline_length))

    # Find the smallest timeline length
    smallest_timeline = sherpaUtils.order_picker(cutaway_timeline_length, interview_timeline_length)

    if smallest_timeline == "CutAwayFootage":
        if not json_data['CutAwayFootage']:
            logging.debug("Cutaways is empty, making interview line the new cutaway line")
            json_data['CutAwayFootage'] = json_data['InterviewFootage']
            json_data['InterviewFootage'] = dict()
            cutaway_timeline_length = round(sherpaUtils.calculate_timeline_length(json_data['CutAwayFootage']), 2)
            interview_timeline_length = round(sherpaUtils.calculate_timeline_length(json_data['InterviewFootage']), 2)        
            smallest_timeline = sherpaUtils.order_picker(cutaway_timeline_length, interview_timeline_length)
        logging.debug("Smallest timeline is currently the Cut Away Timeline, correcting timelines as necessary")
        blank_no = 1

    # While the smallest timeline is the cut away timeline
    # TODO: THIS ISSUE MAY ONLY OCCUR IF THE CUTAWAY TIMELINE IS SHORTER THAN THE TOP TIMELINE
    while smallest_timeline == 'CutAwayFootage':
        if blank_no > 100:
            logging.debug("There's something wrong with the blank placement for {}. Terminating project".format(user))            
            results = "Fatal error, blank placement is in infinite loop", 99        
            if send_end is not None:
                send_end.send(results)
            return results

        # Calculate the length of the blank that should be playing at the smallest timeline 
        current_interview_clip = sherpaUtils.current_interview_footage(
            json_data, 
            cutaway_timeline_length
        )[0]

        # Calculate when the clip om the interview timeline should be playing (globally), and returns the length that the blank clip should be
        blank_len = round(sherpaUtils.calculate_time_at_clip(
            current_interview_clip['Meta'], 
            json_data['InterviewFootage'], 
            timeline_len=cutaway_timeline_length
        ), 2)

        # Creating a blank clip to insert into time
        blank_name = "end_of_line_blank_" + str(blank_no)

        end_of_line_blank = {
        blank_name: {
                "Meta": {
                    "name": blank_name,
                    "startTime": 0,
                    "endTime": blank_len,
                    "audioLevel": 1,
                    "order": len(json_data[smallest_timeline])+1,
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
        json_data[smallest_timeline].update(end_of_line_blank)

        # Update the length
        cutaway_timeline_length = round((cutaway_timeline_length+blank_len),2)
        logging.debug("Cutaway length: {}, Inteview length: {}".format(cutaway_timeline_length, interview_timeline_length))
            
        smallest_timeline = sherpaUtils.order_picker(cutaway_timeline_length, interview_timeline_length)

    blank_replace = True

    #print(json_data)
    #print(sherpaUtils.calculate_timeline_length(json_data['CutAwayFootage']))

    if not json_data['CutAwayFootage']:
        logging.debug("Only interview exists")
        json_data['CutAwayFootage'] = json_data['InterviewFootage']
        json_data['InterviewFootage'] = dict()
        blank_replace = False

    
    if not json_data['InterviewFootage']:
        logging.debug("Only CutAway Exists")
        blank_replace = False


    if blank_replace:    
        #blank replacement
        full_context_start = 0
        for clip in json_data['CutAwayFootage']:
            full_context_end = round(full_context_start + sherpaUtils.calculate_clip_length(json_data['CutAwayFootage'][clip]['Meta']), 2)
            json_data['CutAwayFootage'][clip]['Meta']['fullContextStart'] = full_context_start
            json_data['CutAwayFootage'][clip]['Meta']['fullContextEnd'] = full_context_end
            full_context_start = full_context_end
        
        full_context_start = 0
        for clip in json_data['InterviewFootage']:
            full_context_end = round(full_context_start + sherpaUtils.calculate_clip_length(json_data['InterviewFootage'][clip]['Meta']), 2)
            json_data['InterviewFootage'][clip]['Meta']['fullContextStart'] = full_context_start
            json_data['InterviewFootage'][clip]['Meta']['fullContextEnd'] = full_context_end
            full_context_start = full_context_end
        
        print(json_data)
        
        cp = copy.deepcopy(json_data['CutAwayFootage'])
        
        for clip in cp:
            # If there's any blank, clean the whole thing up
            if json_data['CutAwayFootage'][clip]['Meta'].get('clipType') == "Blank":
                if not json_data['CutAwayFootage'][clip]['edit']:
                    blank_start = json_data['CutAwayFootage'][clip]['Meta']['fullContextStart']
                    blank_end = json_data['CutAwayFootage'][clip]['Meta']['fullContextEnd']

                    print("BLANK START " , blank_start)
                    print("BLANK END ", blank_end)

                    interview_clip = sherpaUtils.blank_json_replace(blank_start, blank_end, json_data, json_data['CutAwayFootage'][clip])

                    if isinstance(interview_clip, list):
                        # Update all the orders from the blank onwards
                        #amnt = (len(interview_clip) - 1)
                        #json_data['CutAwayFootage'] = sherpaUtils.update_order(json_data['CutAwayFootage'], json_data['CutAwayFootage'][clip]['Meta']['order'], amnt)
                        print(interview_clip[0])
                        json_data['CutAwayFootage'][clip] = interview_clip[0]
                        interview_clip.pop(0)
                        pos = 0
                        count = 9999
                        for _item in interview_clip:
                            clip_name = str(count)
                            json_data['CutAwayFootage'][clip_name] = interview_clip[pos]
                            pos+=1
                            count+=1
                    else:
                        json_data['CutAwayFootage'][clip] = interview_clip
            
    #print("Before")
    print(json_data)
    full_context_start = 0
    full_context_end = 0
    for clip in json_data['CutAwayFootage']:
        full_context_end = round(full_context_start + sherpaUtils.calculate_clip_length(json_data['CutAwayFootage'][clip]['Meta']), 2)
        #print("START: ", full_context_start)
        #print("END: ", full_context_end)
        json_data['CutAwayFootage'][clip]['Meta']['fullContextStart'] = full_context_start
        json_data['CutAwayFootage'][clip]['Meta']['fullContextEnd'] = full_context_end
        full_context_start = full_context_end
    #print("After")
    print(json_data)
    video_list = []
    top_audio = []
    cutaway_timeline = 0
    print("Clips ready in: ", time.time() - start_time_count)
    for clip_name in json_data['CutAwayFootage']:
        logging.debug(clip_name + ":")
        logging.debug("Cutaway Timeline: {}".format(cutaway_timeline))

        # Initialise clip data first
        clip_data = json_data['CutAwayFootage'][clip_name]

        clip_type = clip_data['Meta'].get('clipType')

        # If its a cutaway, just generate the clip and add a caption if it exists
        if clip_type == "CutAway" or clip_type == "Interview":
            logging.debug(clip_name + " is a cutaway.")
            clip = generateEffects.generate_clip(clip_data=clip_data['Meta'], user=user, compressed=compress_render or chunk_render)
            # Generate caption data
            logging.debug("Generating audio for {}".format(clip_name))
            clip = generateEffects.better_generate_text_caption(clip, clip_data['edit'], compressed=compress_render or chunk_render)
            logging.debug("Inserting audio for clip '{}'     Clip Audio is {}   Audio length is {}".format(clip_name, clip.audio, clip.duration))
            top_audio.append(clip.audio)

        # Generate image
        elif clip_type == "Image":
            logging.debug(clip_name + " is an image.")
            clip = generateEffects.generate_image_clip(clip_data['Meta'], user)            
            logging.debug("Generating audio for {}".format(clip_name))
            clip = generateEffects.better_generate_text_caption(clip, clip_data['edit'], compressed=compress_render or chunk_render)
            logging.debug("Inserting audio for clip '{}'     Clip Audio is {}   Audio length is {}".format(clip_name, clip.audio, clip.duration))
            top_audio.append(clip.audio)

        # If it's a blank
        elif clip_type == "Blank" or clip_type == "CustomBlank":
            logging.debug(clip_name + " is a Blank.")
            clip = generateEffects.generate_blank(clip_data['Meta'], compressed=compress_render or chunk_render)
            logging.debug("Generating audio for {}".format(clip_name))
            clip = generateEffects.better_generate_text_caption(clip, clip_data['edit'], compressed=compress_render or chunk_render)
            logging.debug("Inserting audio for clip '{}'     Clip Audio is {}   Audio length is {}".format(clip_name, clip.audio, clip.duration))
            top_audio.append(clip.audio)

        # Insert clip into correct position in array
        logging.debug("Inserted clip '{}' into pos {}.".format(clip_name, clip_data['Meta'].get('order')-1))

        cutaway_timeline = round((cutaway_timeline+clip.duration), 2)
        video_list.append(clip)
    
    logging.debug("Final Cutaway Timeline: {}".format(cutaway_timeline))

    # Video list
    logging.debug("Video list:")
    logging.debug(video_list)

    # Create audio from the interview Footage
    bottom_audio = generateEffects.interview_audio_builder(interview_data=json_data['InterviewFootage'], user=user)

    # We need to insert the intro if it exists
    if os.path.exists(os.path.join(attach_dir, user, "intro.mp4")):
        logging.debug("Intro clip found")
        logging.error("WE ARE CURRENTLY NOT IMPLEMENTING INTROS")
        """       
        intro_clip = generateEffects.create_intro_clip(user, compressed=True)
        video_list.insert(0, intro_clip)
        logging.debug("Inserting audio for clip '{}'     Clip Audio is {}   Audio length is {}".format(intro_clip, intro_clip.audio, intro_clip.duration))
        top_audio.insert(0, intro_clip.audio)
        bottom_audio.insert(0, intro_clip.audio)"""
    else:
        logging.error("No intro clip found, continuing")

    # Concatenate the clips together
    top_audio = concatenate_audioclips(top_audio)    
    logging.debug("Top audio len: {}".format(round(top_audio.duration, 2)))

        
    # Try adding the music if it exists
    logging.debug("Attempting to add music...")
    try:
        music_data = json_data['MusicTrackURL']
        music_audio_lvl = float(json_data['MusicAudioLevel'])
        music = generateEffects.open_music(music_data, music_audio_lvl, cutaway_timeline)
        # If the video is longer than the music, replay it
        if music.duration > cutaway_timeline:
            music = CompositeAudioClip([music, generateEffects.open_music(music_data, music_audio_lvl, cutaway_timeline - music.duration)])
        top_audio = CompositeAudioClip([top_audio, music])
        logging.debug("Music added successfully")
    except Exception as e:
        logging.debug("Exception occured in render - during music audio building:")
        logging.debug(e)
        finished_audio = top_audio

    # Try adding the voice over 
    logging.debug("Attempting to add voice over...")
    try:
        voice_data = json_data['VoiceTrackURL']
        voice_audio_lvl = float(json_data['VoiceoverAudioLevel'])
        voice = generateEffects.open_voice(voice_data, voice_audio_lvl, user)
        top_audio = CompositeAudioClip([top_audio, voice])
        logging.debug("Music added successfully")
    except Exception as e:
        logging.debug("Exception occured in render - during voiceover audio building:")
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
    vid_name = user + "_com_chunk_edited_TESTING.mp4"
    vid_dir = os.path.join(attach_dir, user, vid_name)


    logging.debug("Rendering {} clip(s) together, of total length {}.".format(len(video_list), round(finished_video.duration, 2)))
    logging.debug("Writing '{}' to {}".format(vid_name, vid_dir))

    logging.debug("Videos placed in {} seconds".format(time.time() - start_time_count))

    if chunk_render:
        if all_clips == True:
            chunk_len = Config.PREVIEW_CHUNK_LENGTH
            start_time = 0
            end_time = start_time + chunk_len
            finished_dur = round(finished_video.duration, 2)
            preview_chunks = []
            segment_no = ceil(finished_dur/chunk_len)
            # hangover segment

            logging.debug("Video duration: {}s  /{}s = {} segments      full segments: {}".format(finished_dur, chunk_len, finished_dur/chunk_len, segment_no))

            # _ is for non important variable
            for i in range(segment_no):
                preview_clip = finished_video.subclip(start_time, min(start_time+chunk_len, finished_dur))
                logging.debug("Clip is currently from {} to {}".format(start_time, round(min(start_time+chunk_len, finished_dur), 2)))

                start_time+=chunk_len
                logging.debug("Segment {} is {}s long".format(i, round(preview_clip.duration, 2)))
                logging.debug("Global framerate: {}".format(global_frames))
                preview_clip.fps = global_frames
                if preview_clip.duration < chunk_len/2:
                    logging.debug("Clip is smaller than {}s, so appending it to last clip instead.".format(chunk_len/2))
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
                    logging.debug("Global framerate: {}".format(global_frames))
                    logging.debug("Rendering {} at time {}s".format(vid_name, (time.time() - start_time_count)))
                    video.write_videofile(
                        vid_dir,
                        threads=8,
                        preset="ultrafast",
                        bitrate="1000k",
                        audio_codec="aac",
                        remove_temp=True,
                        fps=global_frames
                    )
                    results = "Chunk {} Rendered Successfully".format(str(preview_chunks.index(video))), 1
                    results = "Chunk 1 Rendered Successfully", 1
                    if send_end is not None:
                        send_end.send(results)            
                except:
                    logging.error("Fatal error occured while writing video - Chunk Render")
                    logging.exception("")
                    logging.error("Exiting program without writing video file correctly")                
                    results = "Video not rendered [ERROR OCCURED, VIEW LOGS '{}' FOR MORE DETAILS]".format(log_name), 99
                    if send_end is not None:
                        send_end.send(results)            
                    return results
            #results = "Video Rendered Successfully", 1

            logging.debug("All chunks rendered to {}".format(vid_dir))
            logging.debug("Completed in {} seconds".format(time.time() - start_time_count))
            logging.debug("Closing render instance - Chunk")            
            if send_end is not None:
                send_end.send(results)            
            return results


        else:
            start_time = chunk_number*Config.PREVIEW_CHUNK_LENGTH
            end_time = min(start_time+Config.PREVIEW_CHUNK_LENGTH, finished_video.duration)      

            vid_name = user + "_com_chunk_" + str(chunk_number) + "_edited.mp4"
            vid_dir = os.path.join(attach_dir, user, vid_name)

            finished_video = finished_video.subclip(start_time, min(end_time, finished_video.end))
            video.write_videofile(
                vid_dir,
                threads=8,
                preset="ultrafast",
                bitrate="1000k",
                audio_codec="aac",
                remove_temp=True,
                fps=global_frames
            )        
            print(("Done in {} seconds".format(time.time() - start_time_count)))
            logging.debug("Done in {} seconds".format(time.time() - start_time_count))
            logging.debug("File '{}' successfully written to {}".format(vid_name, vid_dir))
            logging.debug("Closing render instance - Chunk")            
            results = "Chunk {} Rendered Successfully".format(chunk_number), 1
            if send_end is not None:
                send_end.send(results)            
            return results


                    
    if compress_render:
        logging.debug("Running compress render instance")
        try:            
            vid_name = user + "_com_preview_edited.mp4"
            vid_dir = os.path.join(attach_dir, user, vid_name)
            logging.debug("Global framerate: {}".format(global_frames))
            finished_video.write_videofile(
                vid_dir,
                threads=8,
                bitrate="1000k",
                audio_codec="aac",
                remove_temp=True,
                fps=global_frames
            )        
            results = "Video Rendered Successfully", 1
            logging.debug("File '{}' successfully written to {}".format(vid_name, vid_dir))
            logging.debug("Completed in {} seconds".format(time.time() - start_time_count))
            logging.debug("Closing render instance - Compress")
            if send_end is not None:
                send_end.send(results)            
            return results
        except:
            logging.error("Fatal error occured while writing video - Compressed Render")
            logging.exception("")
            logging.error("Exiting program without writing video file correctly")
            results = "Video not rendered [ERROR OCCURED, VIEW LOGS '{}' FOR MORE DETAILS]".format(log_name), 99
            if send_end is not None:
                send_end.send(results)            
            return results
    else:
        logging.debug("Running full render instance")
        try:            
            vid_name = user + "_edited.mp4"
            vid_dir = os.path.join(attach_dir, user, vid_name)
            logging.debug("Rendering {}".format(vid_name))
            logging.debug("Global framerate: {}".format(global_frames))
            finished_video.write_videofile(            
                vid_dir,
                threads=8,
                audio_codec="aac",
                bitrate="8000k",
                remove_temp=True,
                fps=fps
            )        
            results = "Video Rendered Successfully", 1
            logging.debug("File '{}' successfully written to {}".format(vid_name, vid_dir))
            logging.debug("Completed in {} seconds".format(time.time() - start_time_count))
            logging.debug("Closing render instance - Full")
            if send_end is not None:
                send_end.send(results)            
            return results

        except:
            logging.error("Fatal error occured while writing video - Full Render")
            logging.exception("")
            logging.error("Exiting program without writing video file correctly")
            results = "Video not rendered [ERROR OCCURED, VIEW LOGS '{}' FOR MORE DETAILS]".format(log_name), 99
            if send_end is not None:
                send_end.send(results)            
            return results                     
