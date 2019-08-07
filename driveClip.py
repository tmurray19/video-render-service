from moviepy.editor import CompositeVideoClip, concatenate_videoclips, concatenate_audioclips, CompositeAudioClip
from moviepy.video.io import html_tools
from config import Config
import generateEffects, sherpaUtils, os, time, logging


# TODO: This needs to be changed in the app.config to
#  read to the correct attach directory as outlined in the configuration
attach_dir = os.path.abspath(Config.DIR_LOCATION)


def render_video(user, json_data=None, html_render=False):
    """
    User: String -> The ID of the project (User is just a hangover from previous builds)
    json_data: String -> The path to the JSON data 
    html_render: Bool -> Set to true if you want this function to return html code of the render
    """
    start_time = time.time()
    """Needs to check for a project_id (user)
    Set html_render to True if you want this function to return html embed code for a preview"""
    # Finished timeline video
    video_list = []

    # Top and Bottom audio timeline
    top_audio = []

    # Define current length of video, in terms of the 'main' timeline
    cutaway_timeline = 0

    if json_data is not None:
        json_file = sherpaUtils.open_json_file(json_data)
    else:
        json_file = sherpaUtils.set_proj(user)

    """
    cutaway_timeline_lenght = sherpaUtils.calculate_timeline_lenghth(json_file['CutAwayFootage'])
    interview_timeline_length = sherpaUtils.calculate_timeline_lenghth(json_file['InterviewFootage'])

    smallest_timeline = sherpaUtils.order_picker(cutaway_timeline_lenght, interview_timeline_length)

    end_of_file_blank = {
    "end_of_blank": {
            "Meta": {
                "name": "end_of_file_blank",
                "startTime": min(cutaway_timeline_lenght, interview_timeline_length),
                "endTime": max(cutaway_timeline_lenght, interview_timeline_length),
                "audioLevel": 1,
                "order": len(json_file[smallest_timeline])+1,
                "clipType": "Blank"
            }
        }
    }
    

    json_file[smallest_timeline].update(end_of_file_blank)

    print("Cutaway length: {}, Inteview length: {}".format(cutaway_timeline_lenght, interview_timeline_length))
    """
    # Automated all the clips
    for clip_name in json_file['CutAwayFootage']:

        # Testing printout
        print(clip_name + ":")
        print("Cutaway Timeline: {}".format(cutaway_timeline))

        # Initialise clip data first
        clip_data = sherpaUtils.open_clip_meta_data(data=json_file, clip=clip_name)

        clip_type = clip_data.get('clipType')

        # If its a cutaway, just generate the clip and add a caption if it exists
        if clip_type == "CutAway":
            print(clip_name + " is a cutaway.")
            clip = generateEffects.generate_clip(clip_data=clip_data, user=user)
            top_audio.insert(clip_data.get('order'), clip.audio)

            # Look for the clip caption data
            captionData = sherpaUtils.open_clip_caption_data(data=json_file,clip=clip_name)

            # Append here if it's needed
            if captionData is not 0:
                caption = generateEffects.generate_text_caption(captionData, clip_data)
                clip = CompositeVideoClip([clip, caption])

        # Generate image
        elif clip_type == "Image":
            print(clip_name + " is an image.")
            clip = generateEffects.generate_image_clip(clip_data, user)
            top_audio.insert(clip_data.get('order'), clip.audio)

        # If it's a blank
        elif clip_type == "Blank":
            try:
                print(clip_name + " is a blank.")

                interviewClipCaption = 0

                blankInterviewClip, interviewStartTime = sherpaUtils.current_interview_footage(
                    data=json_file,
                    clip_timeline=cutaway_timeline
                )

                # Difference between the main timeline and the starting time line
                dif = cutaway_timeline-interviewStartTime

                print("Interview clip starts at {}, Blank clip starts at {}, so difference is {}".format(
                    interviewStartTime,
                    cutaway_timeline,
                    dif)
                )

                interviewClipMeta = blankInterviewClip['Meta']

                # Create caption and clip data for interview
                try:
                    interviewClipCaption = blankInterviewClip['edit']['Caption']
                except KeyError:
                    interviewClipCaption = 0

                subClipStart = (interviewClipMeta.get('startTime')) + dif
                subClipEnd = (interviewClipMeta.get('startTime')) + dif + (
                        (clip_data.get('endTime')) - (clip_data.get('startTime'))
                )
                print("Sub clip starts at {}, ends at {}".format(subClipStart, subClipEnd))

                # Create clip with parameterised start and end times
                clip = generateEffects.generate_clip(
                    clip_data=interviewClipMeta,
                    user=user,
                    start=subClipStart,
                    end=subClipEnd
                )
            # No clip can be found, generate a blank
            except TypeError:
                print("TypeError - No clip found")
                clip = generateEffects.generate_blank(clip_data)
                top_audio.insert(clip_data.get('order'), clip.audio)
            # Clip can be found, but no caption data
            #except KeyError:
                #print("KeyError - No caption data found")
                #interviewClipCaption = 0
            # We want this code to run only if we get in the try loop
            # So we use 'finally'
            finally:
                if interviewClipCaption is not 0:
                    caption = generateEffects.generate_text_caption(
                        interviewClipCaption,
                        interviewClipMeta,
                        dur=subClipEnd - subClipStart
                    )
                    clip = CompositeVideoClip([clip, caption])

        # Insert clip into correct position in array
        print("Inserted {} into pos {}.".format(clip_data.get('name'), clip_data.get('order')-1))

        cutaway_timeline += clip.duration
        video_list.insert(clip_data.get('order')-1, clip)
    
    # Following all the cut away clips, we need to make sure any hangover interviwe clips are accounted for
    print("Total cut away timeline comes to {}.".format(cutaway_timeline))

    # Get the current runtime of the interview timeline
    current_clip = sherpaUtils.current_interview_footage(data=json_file, clip_timeline=cutaway_timeline)[0]
    print("Clip that should currently be showing is {}".format(current_clip))
    print("It should be playing at {}".format(cutaway_timeline))

    # Generate the clip based on what should currently be playi ng
    interview_clip = generateEffects.generate_clip(clip_data=current_clip['Meta'], user=user, start=cutaway_timeline)
    
    # Insert that at the end of the list
    video_list.insert(len(video_list), interview_clip)

    # Define a variable of the current list lenght to shift all remaining clips by, so they're inserted correctly
    order_shift_number = len(video_list)
    
    remaining_videos = json_file['InterviewFootage']
    del remaining_videos[current_clip['Meta'].get('name')]

    # Add remaining items to cut away timeline
    for item in remaining_videos:
        item_meta_data = remaining_videos[item]['Meta']
        #item_edit_data = remaining_videos[item]['edit']

        clip_type = item_meta_data.get('clipType')

        if clip_type == "Blank":
            print(item_meta_data.get('name') + " is a blank.")
            clip = generateEffects.generate_blank(clip_data)
            top_audio.insert(clip_data.get('order')+order_shift_number, clip.audio)

        elif clip_type == "Image":
            print(item_meta_data.get('name') + " is an image.")
            clip = generateEffects.generate_image_clip(clip_data, user)
            top_audio.insert(clip_data.get('order')+order_shift_number, clip.audio)

        elif clip_type == "Interview":
            print(item_meta_data.get('name') + " is a cutaway.")
            clip = generateEffects.generate_clip(clip_data, user)
            top_audio.insert(clip_data.get('order')+order_shift_number, clip.audio)

            # Look for the clip caption data
            captionData = sherpaUtils.open_interview_caption_data(data=json_file, clip=item)

            # Append here if it's needed
            if captionData is not 0:
                caption = generateEffects.generate_text_caption(captionData, clip_data)
                clip = CompositeVideoClip([clip, caption])

        video_list.insert(clip_data.get('order')+order_shift_number-1, clip)
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

        print("Completed in {} seconds.".format(time.time() - start_time))


project = input("Enter 1100: ")
render_video(project)