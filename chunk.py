from moviepy.editor import CompositeVideoClip, concatenate_videoclips, concatenate_audioclips, CompositeAudioClip
from config import Config
from datetime import datetime
from math import ceil
import generateEffects, sherpaUtils, os, time, logging, gc


attach_dir = os.path.join(Config.BASE_DIR, Config.VIDS_LOCATION)
proj = Config.PROJECT_NAME

def get_chunk(json_data, user, chunk_number, send_end=None, all_clips=True):
    start_time_count = time.time()      
    log_name = datetime.now().strftime("%Y.%m.%d-%H-%M-%S") + "_chunk_service_instance_id_{}_TESTING.log".format(user)

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
        blank_len = sherpaUtils.calculate_time_at_clip(
            current_interview_clip['Meta'], 
            json_data['InterviewFootage'], 
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
        run_time = 0
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

        for clip in json_data['CutAwayFootage']:
            if json_data['CutAwayFootage'][clip]['Meta'].get('clipType') == "Blank":
                blank_start = json_data['CutAwayFootage'][clip]['Meta'].get("startTime") + run_time
                blank_end = blank_start + sherpaUtils.calculate_clip_length(json_data['CutAwayFootage'][clip]['Meta'])

                #print("BLANK START " , blank_start)
                #print("BLANK END ", blank_end)

                interview_clip = sherpaUtils.get_clip_at_time(blank_end, json_data['InterviewFootage'])
                if sherpaUtils.calculate_clip_length(interview_clip['Meta']) > sherpaUtils.calculate_clip_length(json_data['CutAwayFootage'][clip]['Meta']):
                    interview_clip['Meta']['endTime'] = interview_clip['Meta']['startTime'] + sherpaUtils.calculate_clip_length(json_data['CutAwayFootage'][clip]['Meta'])
                json_data['CutAwayFootage'][clip] = interview_clip
            

            run_time += sherpaUtils.calculate_clip_length(json_data['CutAwayFootage'][clip]['Meta'])

        #print("Before")
        #print(json_data['CutAwayFootage'])
        full_context_start = 0
    for clip in json_data['CutAwayFootage']:
        full_context_end = round(full_context_start + sherpaUtils.calculate_clip_length(json_data['CutAwayFootage'][clip]['Meta']), 2)
        #print("START: ", full_context_start)
        #print("END: ", full_context_end)
        json_data['CutAwayFootage'][clip]['Meta']['fullContextStart'] = full_context_start
        json_data['CutAwayFootage'][clip]['Meta']['fullContextEnd'] = full_context_end
        full_context_start = full_context_end
    #print("After")
    print(json_data['CutAwayFootage'])
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
            clip = generateEffects.generate_clip(clip_data=clip_data['Meta'], user=user, compressed=True)
            # Generate caption data
            logging.debug("Generating audio for {}".format(clip_name))
            clip = generateEffects.better_generate_text_caption(clip, clip_data['edit'], compressed=True)
            logging.debug("Inserting audio for clip '{}'     Clip Audio is {}   Audio length is {}".format(clip_name, clip.audio, clip.duration))
            top_audio.append(clip.audio)

        # Generate image
        elif clip_type == "Image":
            logging.debug(clip_name + " is an image.")
            clip = generateEffects.generate_image_clip(clip_data['Meta'], user)            
            logging.debug("Generating audio for {}".format(clip_name))
            clip = generateEffects.better_generate_text_caption(clip, clip_data['edit'], compressed=True)
            logging.debug("Inserting audio for clip '{}'     Clip Audio is {}   Audio length is {}".format(clip_name, clip.audio, clip.duration))
            top_audio.append(clip.audio)

        # If it's a blank
        elif clip_type == "Blank":
            pass
        
        # Insert clip into correct position in array
        logging.debug("Inserted clip '{}' into pos {}.".format(clip_name, clip_data['Meta'].get('order')-1))

        cutaway_timeline = round((cutaway_timeline+clip.duration), 2)
        video_list.append(clip)

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
    vid_name = user + "_com_preview_edited_TESTING.mp4"
    vid_dir = os.path.join(attach_dir, user, vid_name)


    logging.debug("Rendering {} clip(s) together, of total length {}.".format(len(video_list), round(finished_video.duration, 2)))
    logging.debug("Writing '{}' to {}".format(vid_name, vid_dir))

    logging.debug("Videos placed in {} seconds".format(time.time() - start_time_count))

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
            preview_clip.fps = 24
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
        logging.debug("File '{}' successfully written to {}".format(vid_name, vid_dir))
        logging.debug("Completed in {} seconds".format(time.time() - start_time))
        logging.debug("Closing render instance - Chunk")            
        if send_end is not None:
            send_end.send(results)            
        return results


    else:
        start_time = chunk_number*Config.PREVIEW_CHUNK_LENGTH
        end_time = min(start_time+Config.PREVIEW_CHUNK_LENGTH, finished_video.duration)
        finished_video = finished_video.subclip(start_time, min(end_time, finished_video.end))
        video.write_videofile(
            vid_dir,
            threads=8,
            preset="ultrafast",
            bitrate="1000k",
            audio_codec="aac",
            remove_temp=True,
            fps=24
        )        
        print(("Done in {} seconds".format(time.time() - start_time_count)))
        logging.debug("Done in {} seconds".format(time.time() - start_time_count))


get_chunk(sherpaUtils.open_proj("2312"), "2312", 1)