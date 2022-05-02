import os
import pandas as pd 

from moviepy.editor import VideoFileClip, concatenate_videoclips
from sources.videoroom import Clip, Search

_FPS_DEFAULT = 30
_SAVE_PATH = 'data'

class Video:
    """
    """
    def __init__(self, p):
        """
        """
        self.pitch = p
        self.Search = None
        self.play_id = None
        self.Clip = None
        self.file_path = ''
        
    def search(self):
        """
        """
        self.Search = Search(
            pitch = self.pitch
        )
    
    def download(self):
        """
        """
        if self.play_id:
            self.Clip = Clip(
                download = True,
                play_id = self.play_id
            )

    def render_compressed(self):
        """
        """
        n_save_path = os.path.join(
                _SAVE_PATH,
                os.path.basename(self.file_path).replace(
                    '.mp4','_compressed.mp4'
                )
        )
        comp_clip = VideoFileClip(
            self.file_path,
            fps_source = 'fps'
        )
        comp_clip.write_videofile(
            n_save_path,
            fps = _FPS_DEFAULT
        )
        self.file_path_compresssed = n_save_path

    def get_fp(self):
        """
        """
        return self.file_path
    
    def get_fp_compressed(self):
        """
        """
        return self.file_path_compressed

class VideoCompilation:
    """
    """
    def __init__(self, df: pd.DataFrame = None, name: str = None):
        """
        """
        self.pitches = df
        self.clips = df['video_path'].to_list()
        self.compclips = []
        self.compname = name

    def check_clips(self):
        """
        """
        if 'video_path' in self.df.columns.values:
            file_list = self.df['video_path'].to_list()
            for fp in file_list:
                if os.path.exists(fp):
                    continue
                else:
                    print(f'Missing file in path for {os.path.basename(fp)}..')

    def create_compilation(self):
        """
        """
        for clip in self.clips:
            self.compclips.append(
                VideoFileClip(clip,fps_source = 'fps')
            )
        self.comp = concatenate_videoclips(self.compclips,method='compose')
        self.comp.write_videofile(
            os.path.join(_SAVE_PATH,self.compname),
            fps = _FPS_DEFAULT
        )

