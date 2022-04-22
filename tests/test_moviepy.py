import os
from moviepy.editor import VideoFileClip, concatenate_videoclips, clips_array


file = '2022-04-20_trevor-richards-called-strike-to-connor-wong-zs7mct_HOME_mp4Avc.mp4'

clips = [VideoFileClip(f'downloads/{file}',fps_source='fps')]
comp = concatenate_videoclips(clips, method='compose')
comp.write_videofile('downloads/test.mp4',fps=30)

