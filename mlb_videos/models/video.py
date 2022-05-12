import os
import pandas as pd 
import logging
import logging.config 

from moviepy.editor import VideoFileClip, concatenate_videoclips
from sources.videoroom import Clip, Search

logging.config.fileConfig('logging.ini')
logger = logging.getLogger(__name__)

FPS_DEFAULT = 30
CLIP_SUBFOLDER = 'clips'
COMPILATION_SUBFOLDER = 'compilations'

class Video:
    """
    """
    def __init__(self, p = None, dl: bool = True,
                path: str = None, compress: bool = False):
        """
        """
        self.pitch = p
        self.path = os.path.join(path,CLIP_SUBFOLDER)
        self.dl = dl
        self.compress = compress
        self.play_id = None
        self.file_path = ''
        self.search()
        if self.dl:
            self.download()
            if self.compress:
                self.render_compressed()
        
    def search(self):
        """
        """
        self.play_id = Search(
            pitch = self.pitch
        ).get_play_id()
            
    def download(self):
        """
        """
        if self.play_id:
            self.file_path = Clip(
                play_id = self.play_id,
                download = True,
                path = self.path
            ).get_file_path()

    def render_compressed(self):
        """
        """
        n_save_path = os.path.join(
                self.path,
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
            fps = FPS_DEFAULT
        )
        self.file_path = n_save_path

    def get_fp(self):
        """
        """
        return self.file_path

class VideoCompilation:
    """
    """
    def __init__(self, path:str = None, df: pd.DataFrame = None, name: str = None):
        """
        """
        self.name = name
        self.file = f'{name}.mp4'
        self.file_path = os.path.join(path, COMPILATION_SUBFOLDER, self.file)
        self.df = df
        self.clips = df['video_path'].to_list()
        self.compclips = []

    def check_clips(self):
        """
        """
        if 'video_path' in self.df.columns.values:
            file_list = self.df['video_path'].to_list()
            for fp in file_list:
                if os.path.exists(fp):
                    continue
                else:
                    logging.info(f'Missing file in path for {os.path.basename(fp)}..')

    def create_compilation(self):
        """
        """
        for clip in self.clips:
            self.compclips.append(
                VideoFileClip(clip,fps_source = 'fps')
            )
        self.comp = concatenate_videoclips(self.compclips,method='compose')
        self.comp.write_videofile(
            self.file_path,
            fps = FPS_DEFAULT
        )
        return self.file_path
        

