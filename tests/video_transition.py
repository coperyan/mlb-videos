import os

from moviepy.editor import (
    VideoFileClip,
    TextClip,
    CompositeVideoClip,
    concatenate_videoclips,
    vfx,
    afx,
    transfx,
    concatenate,
    CompositeVideoClip,
)

clips = ["clips/intro_720.mp4"]
clips.extend([f"clips/{x}" for x in os.listdir("clips") if "intro" not in x])
clip_ctr = 0
clip_ct = len(clips)

# clip_objs = []
# for clip in clips:
#     clip_obj = VideoFileClip(clip, fps_source="fps")
#     clip_obj = clip_obj.crossfadein(1.0)
#     clip_obj = clip_obj.crossfadeout(1.0)
#     clip_objs.append(clip_obj)

# comp_obj = concatenate_videoclips(clip_objs, method="compose")
# comp_obj.write_videofile("test.mp4", fps=30)


clip_objs = []
for clip in clips:
    clip_obj = VideoFileClip(clip, fps_source="fps")
    clip_objs.append(clip_obj)

# comp_obj = concatenate_videoclips(clip_objs, method="compose")
# comp_obj.write_videofile("test.mp4", fps=30)


clip_objs2 = []
clip_ctr = 0
clip_ct = len(clip_objs)

for clip_obj in clip_objs:
    clip_ctr += 1
    if clip_ctr == 1 or clip_ctr == clip_ct:
        clip_objs2.append(clip_obj)
    else:
        clip_objs2.append(clip_obj.crossfadein(0.5))

comp_obj = concatenate_videoclips(clip_objs2, padding=-0.5, method="compose")
comp_obj.write_videofile("test2.mp4", fps=30)


# final = concatenate([clip1,
#                      clip2.crossfadein(1),
#                      clip3.crossfadein(1),
#                      clip4.crossfadein(1)],
#              padding=-1, method="compose")
# final.write_videoclip('myvideo.mp4')


# def combine_videos_with_transition(video_list, transition_duration):
# clips = []
# for i, video_path in enumerate(video_list):
#     video_clip = video_path

#     first_video = i == 0
#     last_video = i == len(video_list)
#     if first_video or last_video:
#         clips.append(video_clip)
#     else:
#         clips.append(video_clip.crossfadein(transition_duration))

# final = concatenate_videoclips(clips,
#             padding=-transition_duration,
#             method="compose")

# return final
