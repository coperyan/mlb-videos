import os
import pandas as pd
from moviepy.editor import (
    VideoFileClip,
    TextClip,
    CompositeVideoClip,
    concatenate_videoclips,
)

from .constants import _CAPTION_SETUP

import logging
import logging.config

logger = logging.getLogger(__name__)

_FPS_DEFAULT = 30
_CAPTION_FONT = 75
_CLIP_LIMIT = 100
_COMP_SUBFOLDER = "compilations"


class Compilation:
    def __init__(
        self,
        title: str,
        df: pd.DataFrame,
        local_path: str = None,
        metric_caption: str = None,
        player_caption: str = None,
    ):
        self.title = title
        self.df = df
        self.local_path = local_path
        self.metric_caption = metric_caption
        self.player_caption = player_caption

        self.clip_files = [
            os.path.join(self.local_path, f)
            for f in os.listdir(f"{self.local_path}/clips")
        ]
        self.comp_file = os.path.join(
            self.local_path, _COMP_SUBFOLDER, f"{self.title}.mp4"
        )

        self.clip_objs = []

        self._check_clip_limit()

    def _check_clip_limit(self):
        if len(self.df) > _CLIP_LIMIT:
            raise Exception("Exceeded maximum numbers of clip per comp.")

    def _generate_caption(self, pitch: pd.Series) -> str:
        if self.metric_caption is not None:
            m_config = _CAPTION_SETUP.get(self.metric_caption)
            m_value = pitch.get(self.metric_caption)
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

            return m_value

        elif self.player_caption is not None:
            return (
                pitch.get("pitcher_fullname")
                if self.player_caption == "pitcher"
                else pitch.get("batter_fullname")
                if self.player_caption == "batter"
                else None
            )
        else:
            return ""

    def _build_caption_clip(self, caption: str):
        clip = TextClip(caption, fontsize=_CAPTION_FONT, color="white")
        clip = clip.set_pos(("right", "bottom"))
        clip = clip.margin(bottom=100, right=50, opacity=0)
        clip = clip.set_duration(2)
        return clip

    def _create_clip_obj(self, pitch: pd.Series):
        if os.path.exists(pitch.file_path):
            clip_obj = VideoFileClip(pitch.file_path, fps_source="fps")

            if any([self.metric_caption, self.player_caption]):
                caption_obj = self._build_caption_clip(self._generate_caption(pitch))
                clip_obj = CompositeVideoClip([clip_obj, caption_obj])
            return clip_obj

        else:
            logging.warning(f"Local file does not exist for: {pitch['file_path']}")

    def _create_clip_objs(self):
        for index, row in self.df.iterrows():
            try:
                self.clip_objs.append(self._create_clip_obj(row))
            except Exception as e:
                logging.warning(
                    f"Clip creation failed for: {row['pitch_id']}, skipping.."
                )
                pass

    def _build_compilation(self):
        comp_obj = concatenate_videoclips(self.clip_objs, method="compose")
        comp_obj.write_videofile(self.comp_file, fps=_FPS_DEFAULT)
