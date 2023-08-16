import os
import pandas as pd
from moviepy.editor import (
    VideoFileClip,
    TextClip,
    CompositeVideoClip,
    concatenate_videoclips,
)

from filmroom import Video
from constants import _CAPTION_SETUP

_FPS_DEFAULT = 30
_CAPTION_FONT = 75
_CLIP_SUBFOLDER = "clips"
_COMP_SUBFOLDER = "compilations"


class CompClip:
    def __init__(self, pitch, metric_caption, player_caption):
        self.pitch = pitch
        self.metric_caption = metric_caption
        self.player_caption = player_caption
        self.metric_caption_text = None
        self.player_caption_text = None
        self.caption_text = None
        self.clip_path = pitch.get("video_file_path")
        if self.player_caption:
            self.get_player_caption_text()
        if self.metric_caption:
            self._get_metric_caption_text()
        self.clip_obj = None
        self._create_clip_object()

    def _get_player_caption_text(self):
        self.player_caption_text = (
            self.pitch.get("pitcher_fullname")
            if self.player_caption == "pitcher"
            else self.pitch.get("batter_fullname")
            if self.player_caption == "batter"
            else None
        )
        if not self.caption_text:
            self.caption_text = self.player_caption_text
        else:
            self.caption_text += f"\n{self.player_caption_text}"

    def _get_metric_caption_text(self):
        m_config = _CAPTION_SETUP.get(self.metric_caption)
        m_value = self.pitch.get(self.metric_caption)
        if m_config.get("format") == float:
            m_value = round(float(m_value), m_config.get("scale"))
        elif m_config.get("format") == int:
            m_value = int(round(m_value, 0))
        elif m_config.get("format") == str:
            m_value = str(m_value)
        else:
            m_value = str(m_value)

        if m_config.get("suffix"):
            m_value = f"{m_value}{m_config.get('suffix')}"

        self.metric_caption_text = m_value

        if not self.caption_text:
            self.caption_text = self.metric_caption_text
        else:
            self.caption_text += f"\n{self.metric_caption_text}"

    def _check_local_clip(self):
        if not os.path.exists(self.clip_path):
            print(f"Missing local file: {self.clip_path}")
        else:
            pass

    def _create_clip_object(self):
        clip_obj = VideoFileClip(self.clip_path, fps_source="fps")
        if self.caption_text:
            txt_clip = TextClip(
                self.caption_text, fontsize=_CAPTION_FONT, color="white"
            )
            txt_clip = txt_clip.set_pos(("right", "bottom"))
            txt_clip = txt_clip.margin(bottom=100, right=50, opacity=0)
            txt_clip = txt_clip.set_duration(2)
            self.clip_obj = CompositeVideoClip([clip_obj, txt_clip])
        else:
            self.clip_obj = clip_obj


class Compilation:
    def __init__(
        self,
        name: str,
        df: pd.DataFrame,
        local_path: str,
        metric_caption: str = None,
        player_caption: str = None,
    ):
        self.name = name
        self.comp_folder = os.path.join(local_path, _COMP_SUBFOLDER)
        self.comp_file = os.path.join(self.comp_folder, f"{self.name}.mp4")
        self.df = df
        self.clip_ct = len(df)
        self.clip_objs = []
        self.metric_caption = metric_caption
        self.player_caption = player_caption
        self.create_clip_objs()
        self.generate_compilation()

    def create_clip_objs(self):
        self.clip_objs = [
            Clip(row, self.metric_caption, self.player_caption)
            for _, row in self.df.iterrows()
        ]

    def generate_compilation(self):
        comp = concatenate_videoclips(
            [x.clip_obj for x in self.clip_objs], method="compose"
        )
        comp.write_videofile(self.comp_file, fps=_FPS_DEFAULT)
