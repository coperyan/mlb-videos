import os
from moviepy.editor import VideoFileClip, concatenate_videoclips

class VideoCompilation:
    def __init__(self,dt):
        """
        """
        self.dt = dt
        self.clip_list = [
            f'downloads/{x}' for x in os.listdir('downloads') if '.mp4' in x
        ]
        self.gen_clips()
        self.create_comp()
        self.render_comp()

    def gen_clips(self):
        """
        """
        self.clips = [
            VideoFileClip(x) for x in self.clip_list
        ]

    def create_comp(self):
        """
        """
        self.comp = concatenate_videoclips(self.clips)

    def render_comp(self):
        """
        """
        self.comp.write_videofile('downloads/final.mp4')