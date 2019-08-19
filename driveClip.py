from moviepy.editor import CompositeVideoClip, concatenate_videoclips, concatenate_audioclips, CompositeAudioClip, VideoFileClip
from config import Config
from datetime import datetime
from math import floor
import generateEffects, sherpaUtils, os, time, logging, gc


# TODO: This needs to be changed in the app.config to
#  read to the correct attach directory as outlined in the configuration
attach_dir = os.path.join(Config.BASE_DIR, Config.VIDS_LOCATION)


def render_video(user, compress_render=False):
    """
    User: String -> The ID of the project (User is just a hangover from previous builds)
    compress_render: Bool -> Set to true if you want this function to return a quick render
    """

    gc.collect()

    log_file_name = os.path.join(
        Config.BASE_DIR,
        Config.LOGS_LOCATION,
        Config.RENDER_LOGS, 
        datetime.now().strftime("%Y.%m.%d-%H-%M-%S") + "_render_service_instance.log"
    )

    logging.basicConfig(
        level=logging.DEBUG, 
        format='%(asctime)s %(levelname)-8s %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        filename=log_file_name)
    logging.debug("Beginning render instance")

    # For logging
    start_time = time.time()

    # Finished timeline video
    video_list = []

    # Top audio timeline
    top_audio = []

    # Define current length of video, in terms of the 'main' timeline
    cutaway_timeline = 0

    # Look for the json file in the project folder
    json_file = sherpaUtils.open_proj(user)

    # Get timeline lengths
    cutaway_timeline_length = sherpaUtils.calculate_timeline_length(json_file['CutAwayFootage'])
    interview_timeline_length = sherpaUtils.calculate_timeline_length(json_file['InterviewFootage'])

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
        blank_len = sherpaUtils.calculate_time_at_clip(current_interview_clip['Meta'], json_file['InterviewFootage'], timeline_len=cutaway_timeline_length)


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
        cutaway_timeline_length += blank_len
        logging.debug("Cutaway length: {}, Inteview length: {}".format(cutaway_timeline_length, interview_timeline_length))
            
        smallest_timeline = sherpaUtils.order_picker(cutaway_timeline_length, interview_timeline_length)


    # Automated all the clips - Run through all the cutaway footage
    for clip_name in json_file['CutAwayFootage']:

        # Testing printout
        print(clip_name + ":")
        print("Cutaway Timeline: {}".format(cutaway_timeline))
        logging.debug(clip_name + ":")
        logging.debug("Cutaway Timeline: {}".format(cutaway_timeline))

        # Initialise clip data first
        clip_data = json_file['CutAwayFootage'][clip_name]

        clip_type = clip_data['Meta'].get('clipType')

        # If its a cutaway, just generate the clip and add a caption if it exists
        if clip_type == "CutAway":
            print(clip_name + " is a cutaway.")
            logging.debug(clip_name + " is a cutaway.")
            clip = generateEffects.generate_clip(clip_data=clip_data['Meta'], user=user, compressed=compress_render)
            # Generate caption data
            clip = generateEffects.better_generate_text_caption(clip, clip_data['edit'])
            top_audio.insert(clip_data['Meta'].get('order'), clip.audio)

        # Generate image
        elif clip_type == "Image":
            print(clip_name + " is an image.")
            logging.debug(clip_name + " is an image.")
            clip = generateEffects.generate_image_clip(clip_data['Meta'], user)
            clip = generateEffects.better_generate_text_caption(clip, clip_data['edit'])
            top_audio.insert(clip_data['Meta'].get('order'), clip.audio)

        # If it's a blank
        elif clip_type == "Blank":
            # These values are used later in the blank process
            some_filler = False
            total_insert_length = 0
            # We need to see if we can find any clips to replace the blank with
            try:
                print(clip_name + " is a blank.")
                logging.debug(clip_name + " is a blank.")
                # We need to find the clip that should be playing in the interview timeline

                cutaway_blank_len = sherpaUtils.calculate_clip_length(clip_data['Meta'])

                relevant_interview_clip_data, interview_start_time = sherpaUtils.current_interview_footage(
                    data=json_file,
                    clip_timeline=cutaway_timeline
                )

                interview_clip_meta_data = relevant_interview_clip_data['Meta']

                interview_clip_ord = interview_clip_meta_data.get('order')

                # Difference between the current time in the video, and the start time of the interview clip
                dif = cutaway_timeline-interview_start_time

                
                logging.debug("Interview clip starts at {}, Blank clip starts at {}, so difference is {}".format(
                    interview_start_time,
                    cutaway_timeline,
                    dif)
                )

                print("Interview clip starts at {}, Blank clip starts at {}, so difference is {}".format(
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

                print("Sub clip starts at {}, ends at {}".format(sub_clip_start, sub_clip_end))
                logging.debug("Sub clip starts at {}, ends at {}".format(sub_clip_start, sub_clip_end))

                sub_clip_length = sub_clip_end - sub_clip_start
                total_insert_length += sub_clip_length

                interview_clip_type = interview_clip_meta_data.get('clipType')

                # Create video clip from data found above
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
                        compressed=compress_render
                    )

                    clip = generateEffects.better_generate_text_caption(clip, relevant_interview_clip_data['edit'])

                # Blanks from the cutaway can be placed instead
                elif interview_clip_type == "Blank":
                    
                    logging.debug("Replacing blank {} with interview clip {}".format(
                        clip_data['Meta'].get('name'),
                        interview_clip_meta_data.get('name')
                    ))
                    clip = generateEffects.generate_blank(interview_clip_meta_data, start=sub_clip_start, end=sub_clip_end, compressed=compress_render)
                    clip = generateEffects.better_generate_text_caption(clip, relevant_interview_clip_data['edit'])

                # TODO: Careful here, rounding could cause issues
                total_insert_length = round(total_insert_length, 3)

                # If the blank length is longer than the length of the videos being inserted
                while total_insert_length != cutaway_blank_len:
                    some_filler = True
                    logging.debug("Clip length didn't suffice for blank, adding more files as necessary")
                    print("Clip length didn't suffice for blank, adding more files as necessary")

                    time_to_fill = cutaway_blank_len - total_insert_length

                    logging.debug("Time left to fill is {}".format(time_to_fill))

                    interview_clip_ord+=1

                    next_clip_data = sherpaUtils.give_clip_order(interview_clip_ord, json_file['InterviewFootage'])

                    # Clip should be the the same size as the time to fill if possible
                    # But it's also possible that the next clip isn't bi enough either
                    # So we'll need to go further on
                    # To stop bugs, we need to set our end time as either the time left to fill, or the length of the clip
                    end_time = min(
                        next_clip_data['Meta'].get('startTime') + time_to_fill,
                        sherpaUtils.calculate_clip_length(next_clip_data['Meta'])
                    )

                    logging.debug("End time for clip is {}".format(end_time))


                    if next_clip_data['Meta'].get('clipType') == "Interview":
                        next_clip = generateEffects.generate_clip(
                            clip_data=next_clip_data['Meta'],
                            end=next_clip_data['Meta'].get('startTime')+end_time,
                            user=user,
                            compressed=compress_render
                        )
    
                        next_clip = generateEffects.better_generate_text_caption(next_clip, next_clip_data['edit'])
    
                    elif next_clip_data['Meta'].get('clipType') == "Blank":
                        next_clip = generateEffects.generate_blank(next_clip_data['Meta'], end=end_time, compressed=compress_render)
                        next_clip = generateEffects.better_generate_text_caption(next_clip, next_clip_data['edit'])

                    total_insert_length += next_clip.duration
                    logging.debug("Total insert length {}".format(total_insert_length))
                    print("Total insert length {}".format(total_insert_length))

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
                    clip = generateEffects.generate_blank(clip_data['Meta'], compressed=compress_render)
                    clip = generateEffects.better_generate_text_caption(clip, clip_data['edit'])

                    top_audio.insert(clip_data['Meta'].get('order'), clip.audio)


        # Insert clip into correct position in array
        logging.debug("Inserted clip '{}' into pos {}.".format(clip_name, clip_data['Meta'].get('order')-1))
        print("Inserted clip '{}' into pos {}.".format(clip_name, clip_data['Meta'].get('order')-1))

        cutaway_timeline += clip.duration
        video_list.insert(clip_data['Meta'].get('order')-1, clip)

    # Printout at end
    logging.debug("Video list:")
    logging.debug(video_list)

    # We need to insert the intro if it exists
    if os.path.exists(os.path.join(attach_dir, user, "intro.mp4")):
        intro_clip = VideoFileClip(os.path.join(attach_dir, user, "intro.mp4"))
        intro_clip.set_audio(os.path.join(attach_dir, Config.RESOURCE_PATH, "silence.mp3"))
        video_list.insert(0, intro_clip)
        top_audio.insert(0, intro_clip.audio)


    # Create audio from the interview Footage
    bottom_audio = generateEffects.interview_audio_builder(interview_data=json_file['InterviewFootage'], user=user)

    # Concatenate the clips together
    top_audio = concatenate_audioclips(top_audio)
        
    # Try adding the music if it exists
    try:
        music_data = json_file['Music']
        music = generateEffects.open_music(music_data, cutaway_timeline)
        # If the video is longer than the music, replay it
        if music.duration > cutaway_timeline:
            music = CompositeAudioClip([music, generateEffects.open_music(music_data, cutaway_timeline - music.duration)])
        top_audio = CompositeAudioClip([top_audio, music])
    except Exception as e:
        logging.debug("Exception occured in render - during music audio building:")
        logging.debug(e)
        finished_audio = top_audio

    # Try concatenating the top and bottom audio lines together
    try:
        bottom_audio = concatenate_audioclips(bottom_audio)
        finished_audio = CompositeAudioClip([top_audio, bottom_audio])
    except Exception as e:
        logging.debug("Exception occured in render - during interview audio building:")
        logging.debug(e)
        finished_audio = top_audio


    # Concatenate the video files together
    finished_video = concatenate_videoclips(video_list)
    finished_video = finished_video.set_audio(finished_audio)


    # Defining path here is cleaner
    vid_name = user + "_com_preview_edited.mp4" if compress_render else user + "_edited.mp4"
    vid_dir = os.path.join(attach_dir, user, vid_name)


    logging.debug("Rendering {} clip(s) together, of total length {}.".format(len(video_list), finished_video.duration))
    logging.debug("Writing '{}' to {}".format(vid_name, vid_dir))
    # Render the finished project out into an mp4
    if compress_render:
        # Get 10 second chunks of videos
        logging.debug("Splitting video up into 10s chunks.")
        
        # Initialising variables
        finished_dur = finished_video.duration
        chunk_len = 10
        preview_chunks = []
        playtime = 0
        append_to_last_clip = True

        # Getting segment numbers, and determining if a hangover segment is necessary
        segment_no = floor(finished_dur/chunk_len)
        hangover_segment = finished_dur - finished_dur/chunk_len
        if hangover_segment > chunk_len / 2:
            append_to_last_clip = False

        logging.debug("Video duration: {}s  /{}s = {} segments)      full segments: {}".format(finished_dur, chunk_len, finished_dur/chunk_len, segment_no))

        # _ is for non important variable
        for i in range(segment_no):
            logging.debug("Start: {}      End: {}".format(playtime, playtime+chunk_len))
            logging.debug("Min of playtime, and finished video duration: {}".format(min(playtime+chunk_len, finished_dur)))
            preview_clip = finished_video.subclip(playtime, min(playtime+chunk_len, finished_dur))
            if i == segment_no and append_to_last_clip:
                logging.debug("Now clip should be from {} to {}".format(playtime, playtime+chunk_len+hangover_segment))
                preview_clip = finished_video.subclip(playtime, playtime+chunk_len+hangover_segment)
            playtime+=chunk_len
            logging.debug("Segment {} is {}s long".format(i, preview_clip.duration))
            preview_chunks.append(preview_clip)


        
        logging.debug("Preview chunk list: ")
        logging.debug(preview_chunks)

        logging.debug("Rendering out {} videos in {}s chunks".format(len(preview_chunks), chunk_len))

        for video in preview_chunks:
            vid_name = user + "_com_chunk_" + str(preview_chunks.index(video)) + "_edited.mp4"
            vid_dir = os.path.join(attach_dir, user, vid_name)

            logging.debug("Rendering {}".format(vid_name))
            video.write_videofile(
                vid_dir,
                threads=8,
                preset="ultrafast",
                bitrate="1000k",
                audio_codec="aac",
                remove_temp=True,
            )

    else:
        logging.debug("Rendering {}".format(vid_name))
        finished_video.write_videofile(            
            vid_dir,
            threads=8,
            audio_codec="aac",
            bitrate="8000k",
            remove_temp=True,
        )

    logging.debug("File '{}' successfully written to {}".format(vid_name, vid_dir))
    logging.debug("Completed in {} seconds".format(time.time() - start_time))
    logging.debug("Closing render instance")

