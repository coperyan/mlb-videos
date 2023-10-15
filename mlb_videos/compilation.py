import os
import pandas as pd
import subprocess
import pathlib
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
_INTROS = {
    "720p": os.path.join(
        pathlib.Path(f"{os.path.dirname(os.path.abspath(__file__))}").parent,
        "resources/intro_720.mp4",
    ),
    "1080p": os.path.join(
        pathlib.Path(f"{os.path.dirname(os.path.abspath(__file__))}").parent,
        "resources/intro_1080.mp4",
    ),
}


class Compilation:
    def __init__(
        self,
        title: str,
        df: pd.DataFrame,
        local_path: str = None,
        use_intro: bool = False,
        metric_caption: str = None,
        player_caption: str = None,
        resize_resolution: tuple = None,
        max_clip_length: float = None,
        fps: int = _FPS_DEFAULT,
    ):
        self.title = title
        self.df = df
        self.local_path = local_path
        self.use_intro = use_intro
        self.metric_caption = metric_caption
        self.player_caption = player_caption
        self.resize_resolution = resize_resolution
        self.max_clip_length = max_clip_length
        self.fps = fps

        self.clip_files = [
            os.path.join(self.local_path, f)
            for f in os.listdir(f"{self.local_path}/clips")
        ]
        self.comp_file = os.path.join(
            self.local_path, _COMP_SUBFOLDER, f"{self.title}.mp4"
        )

        self.clip_objs = []

        self._check_clip_limit()

        if self.use_intro:
            self._add_intro()

        self._create_clip_objs()
        self._build_compilation()

    def get_comp_path(self):
        return self.comp_file

    def _check_clip_limit(self):
        if len(self.df) > _CLIP_LIMIT:
            raise Exception("Exceeded maximum numbers of clip per comp.")

    def _resize_video(self, path: str):
        new_path = path.replace(".mp4", "_rsz.mp4")
        cmd = f"ffmpeg -i {path} -vf scale={self.resize_resolution[0]}:{self.resize_resolution[1]} -preset slow -crf 18 {new_path}"
        subprocess.call(cmd, shell=True)

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
        if os.path.exists(pitch["video_file_path"]):
            if self.resize_resolution:
                self._resize_video(pitch["video_file_path"])

            clip_obj = VideoFileClip(
                (
                    pitch["video_file_path"]
                    if not self.resize_resolution
                    else f"{pitch['video_file_path'].replace('.mp4','_rsz.mp4')}"
                ),
                fps_source="fps",
            )

            if any([self.metric_caption, self.player_caption]):
                caption_obj = self._build_caption_clip(self._generate_caption(pitch))
                clip_obj = CompositeVideoClip([clip_obj, caption_obj])

            if self.max_clip_length and clip_obj.duration > self.max_clip_length:
                clip_obj = clip_obj.subclip(0, self.max_clip_length)

            return clip_obj

        else:
            logging.warning(f"Local file does not exist for: {pitch['file_path']}")

    def _create_clip_objs(self):
        for index, row in self.df.iterrows():
            try:
                self.clip_objs.append(self._create_clip_obj(row))
            except Exception as e:
                logging.warning(
                    f"Clip creation failed for: {row['pitch_id']}, skipping..\n{e}\n"
                )
                pass

    def _add_intro(self):
        if self.resize_resolution:
            self.clip_objs.append(VideoFileClip(_INTROS.get("1080p"), fps_source="fps"))
        else:
            self.clip_objs.append(VideoFileClip(_INTROS.get("720p"), fps_source="fps"))

    def _build_compilation(self):
        comp_obj = concatenate_videoclips(self.clip_objs, method="compose")
        comp_obj.write_videofile(self.comp_file, fps=self.fps)
