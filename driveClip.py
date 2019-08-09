from moviepy.editor import CompositeVideoClip, concatenate_videoclips, concatenate_audioclips, CompositeAudioClip
from moviepy.video.io import html_tools
from config import Config
import generateEffects, sherpaUtils, os, time, logging


# TODO: This needs to be changed in the app.config to
#  read to the correct attach directory as outlined in the configuration
attach_dir = os.path.abspath(Config.DIR_LOCATION)


def correct_timeline():
    """Function for adding necessary blanks to the cutaway timeline"""
    pass



def render_video(user, html_render=False):
    """
    User: String -> The ID of the project (User is just a hangover from previous builds)
    json_data: String -> The path to the JSON data 
    html_render: Bool -> Set to true if you want this function to return html code of the render
    """
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

    print("Cutaway length: {}s      Interview length: {}s".format(cutaway_timeline_length, interview_timeline_length))

    # Find the smallest timeline length
    smallest_timeline = sherpaUtils.order_picker(cutaway_timeline_length, interview_timeline_length)
    
    if smallest_timeline == "CutAwayFootage":
        print("Smallest timeline is currently the Cut Away Timeline, correcting timelines as necessary")
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
        print(end_of_line_blank)
        # Insert it into the timeline
        json_file[smallest_timeline].update(end_of_line_blank)

        # Update the length
        cutaway_timeline_length += blank_len
        print("Cutaway length: {}, Inteview length: {}".format(cutaway_timeline_length, interview_timeline_length))
            
        print(cutaway_timeline_length<interview_timeline_length)
        smallest_timeline = sherpaUtils.order_picker(cutaway_timeline_length, interview_timeline_length)


    # Automated all the clips - Run through all the cutaway footage
    for clip_name in json_file['CutAwayFootage']:

        # Testing printout
        print(clip_name + ":")
        print("Cutaway Timeline: {}".format(cutaway_timeline))

        # Initialise clip data first
        clip_data = json_file['CutAwayFootage'][clip_name]

        clip_type = clip_data['Meta'].get('clipType')

        # If its a cutaway, just generate the clip and add a caption if it exists
        if clip_type == "CutAway":
            print(clip_name + " is a cutaway.")
            clip = generateEffects.generate_clip(clip_data=clip_data['Meta'], user=user)
            # Generate caption data
            clip = generateEffects.better_generate_text_caption(clip, clip_data['edit'])
            top_audio.insert(clip_data['Meta'].get('order'), clip.audio)

        # Generate image
        elif clip_type == "Image":
            print(clip_name + " is an image.")
            clip = generateEffects.generate_image_clip(clip_data['Meta'], user)
            clip = generateEffects.better_generate_text_caption(clip, clip_data['edit'])
            top_audio.insert(clip_data['Meta'].get('order'), clip.audio)

        # If it's a blank
        elif clip_type == "Blank":
            total_insert_length = 0
            try:
                print(clip_name + " is a blank.")
                # We need to find the clip that should be playing in the interview timeline

                relevant_interview_clip_data, interview_start_time = sherpaUtils.current_interview_footage(
                    data=json_file,
                    clip_timeline=cutaway_timeline
                )

                interview_clip_meta_data = relevant_interview_clip_data['Meta']

                interview_clip_ord = interview_clip_meta_data.get('order')

                # Difference between the main timeline and the starting time line
                dif = cutaway_timeline-interview_start_time

                """
                print("Interview clip starts at {}, Blank clip starts at {}, so difference is {}".format(
                    interview_start_time,
                    cutaway_timeline,
                    dif)
                )
                """

                # Define clip length
                clip_dur = sherpaUtils.calculate_clip_length(interview_clip_meta_data)

                sub_clip_start = (interview_clip_meta_data.get('startTime')) + dif
                # Get end of clip or end of blank, whichever comes first
                sub_clip_end = min(
                    ((interview_clip_meta_data.get('startTime')) + dif + clip_dur), 
                    interview_clip_meta_data.get('endTime')
                )

                print("Sub clip starts at {}, ends at {}".format(sub_clip_start, sub_clip_end))

                sub_clip_length = sub_clip_end - sub_clip_start
                total_insert_length += sub_clip_length

                interview_clip_type = interview_clip_meta_data.get('clipType')

                if interview_clip_type == "Interview":
                    # Create clip with parameterised start and end times
                    clip = generateEffects.generate_clip(
                        clip_data=interview_clip_meta_data,
                        user=user,
                        start=sub_clip_start,
                        end=sub_clip_end
                    )

                    clip = generateEffects.better_generate_text_caption(clip, relevant_interview_clip_data['edit'])

                elif interview_clip_type == "Blank":
                    clip = generateEffects.generate_blank(interview_clip_meta_data, start=sub_clip_start, end=sub_clip_end)
                    clip = generateEffects.better_generate_text_caption(clip, relevant_interview_clip_data['edit'])

                while total_insert_length != sherpaUtils.calculate_clip_length(clip_data['Meta']):

                    interview_clip_ord+=1

                    next_clip_data = sherpaUtils.give_clip_order(interview_clip_ord, json_file['InterviewFootage'])

                    if next_clip_data['Meta'].get('clipType') == "Interview":

                        next_clip = generateEffects.generate_clip(
                            clip_data=next_clip_data['Meta'],
                            user=user
                        )
    
                        next_clip = generateEffects.better_generate_text_caption(next_clip, next_clip_data['edit'])
    
                    elif next_clip_data['Meta'].get('clipType') == "Blank":
                        next_clip = generateEffects.generate_blank(next_clip_data['Meta'])
                        next_clip = generateEffects.better_generate_text_caption(next_clip, next_clip_data['edit'])

                    total_insert_length += next_clip.duration
                    print("Total insert length {}".format(total_insert_length))

                    clip = concatenate_videoclips([clip, next_clip])
                    next_clip.close
                    

            # No clip can be found, generate the clip from the blank data in the cutaway timeline
            except TypeError:
                print("TypeError - No clip found")
                clip = generateEffects.generate_blank(clip_data['Meta'])
                clip = generateEffects.better_generate_text_caption(clip, clip_data['edit'])

                top_audio.insert(clip_data['Meta'].get('order'), clip.audio)


        # Insert clip into correct position in array
        print("Inserted {} into pos {}.".format(clip_data['Meta'].get('name'), clip_data['Meta'].get('order')-1))

        cutaway_timeline += clip.duration
        video_list.insert(clip_data['Meta'].get('order')-1, clip)

    # Printout at end
    print(video_list)

    # Create audio from the interview Footage
    bottom_audio = generateEffects.interview_audio_builder(interview_data=json_file['InterviewFootage'], user=user)

    # Concatenate the clips together
    top_audio = concatenate_audioclips(top_audio)

    bottom_audio = concatenate_audioclips(bottom_audio)

    finished_audio = CompositeAudioClip([top_audio, bottom_audio])


    # Concatenate the video files together
    finished_video = concatenate_videoclips(video_list)
    finished_video = finished_video.set_audio(finished_audio)

    # Returns html render of video if true
    if html_render is True:
        low_quality = finished_video.resize(0.5)
        return html_tools.html_embed(low_quality, rd_kwargs={'fps': 15, 'bitrate': '300k'})

    # Otherwise full renders
    else:
        print("Rendering {} clip(s) together, of total length {}.".format(len(video_list), finished_video.duration))
        # Render the finished project out into an mp4
        finished_video.write_videofile(
            os.path.join(
                attach_dir,
                user,
                sherpaUtils.get_proj_name(data=json_file) + "_edited.mp4"
            )
        )

        top_audio.close
        bottom_audio.close
        finished_audio.close
        finished_video.close
        print("Completed in {} seconds.".format(time.time() - start_time))

render_video("1149")