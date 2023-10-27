import os
import subprocess
import pathlib
import pandas as pd

from moviepy.editor import (
    VideoFileClip,
    TextClip,
    CompositeVideoClip,
    concatenate_videoclips,
)

import logging
import logging.config

logger = logging.getLogger(__name__)

_COMP_SUBFOLDER = "compilations"
_INTROS = {
    "720p": os.path.join(
        pathlib.Path(f"{os.path.dirname(os.path.abspath(__file__))}").parent,
        "src/mp4/intro_720.mp4",
    ),
    "1080p": os.path.join(
        pathlib.Path(f"{os.path.dirname(os.path.abspath(__file__))}").parent,
        "src/mp4/intro_1080.mp4",
    ),
}
_CAPTION_SETUP = {
    "release_speed": {"format": float, "scale": 1, "suffix": "mph"},
    "launch_speed": {"format": float, "scale": 1, "suffix": "mph"},
    "hit_distance_sc": {"format": int, "scale": 0, "suffix": "ft"},
}

_TRANSITION_PADDING = 0.5
_FPS_DEFAULT = 30
_CAPTION_FONT = 75
_CLIP_LIMIT = 100


class Compilation:
    """Compilation Builder"""

    def __init__(
        self,
        df: pd.DataFrame,
        project_title: str = None,
        project_path: str = None,
        fps: int = _FPS_DEFAULT,
        use_intro: bool = False,
        add_transitions: bool = False,
        transition_padding: float = _TRANSITION_PADDING,
        max_clip_length: float = None,
        metric_caption: str = None,
        player_caption: str = None,
        resize_resolution: bool = False,
    ):
        """Initialize Build of Compilation Video

        Parameters
        ----------
            df : pd.DataFrame
                Dataframe from Client class with video_file info
            project_title (str, optional): str, default None
                project title
            project_path (str, optional): str, default None
                path to project folder in root projects dir
            fps (int, optional): int, default _FPS_DEFAULT
                int # of frames per second in comp
            use_intro (bool, optional): bool, default False
                prepend the intro video before the comp
            add_transitions (bool, optional): bool, default False
                add short fade in/out between clips
            transition_padding (float, optional): float, default _TRANSITION_PADDING
                length of fade in/out between clips
            max_clip_length (float, optional): float, default None
                max clip length/duration in seconds
            metric_caption (str, optional): str, default None
                metric/stat to include in the clip
                    see _CAPTION_SETUP above
            player_caption (str, optional): str, default None
                player caption to include in the clip
                    (is only setup for name atm)
            resize_resolution (bool, optional): bool, default False
                whether to resize the 720p MLB videos to 1080p
        """
        self.df = df
        self._validate_df()

        self.project_title = project_title if project_title else "compilation"
        self.project_path = project_path
        self.fps = fps
        self.use_intro = use_intro
        self.add_transitions = add_transitions
        self.transition_padding = transition_padding
        self.max_clip_length = max_clip_length
        self.metric_caption = metric_caption
        self.player_caption = player_caption
        self.resize_resolution = resize_resolution
        self.rez = "1080p" if self.resize_resolution else "720p"

        self.clip_files = [
            os.path.join(self.project_path, "clips", x)
            for x in self.df["video_file_path"].values
            if not pd.isnull(x)
        ]
        self.comp_file = os.path.join(
            self.project_path, _COMP_SUBFOLDER, f"{self.project_title}.mp4"
        )
        self.clip_objs = {}

        if self.use_intro:
            self._add_intro()
        if self.resize_resolution:
            self._create_resized_clips()
        self._import_clips()

        if any([self.metric_caption, self.player_caption]):
            self._add_captions()

        if self.max_clip_length:
            self._limit_clip_length()

        self._build_compilation()

    def _validate_df(self):
        """Validate compilation dataframe references existing files"""
        missing_clips = [
            x.get("pitch_id")
            for _, x in self.df.iterrows()
            if not os.path.exists(x.get("video_file_path"))
        ]
        if len(missing_clips) > 0:
            logging.warning(
                f"Missing {len(missing_clips)} clip(s) when checking local vs. clip files:"
            )
            logging.warning(f"{missing_clips}")
        self.df = self.df[self.df["video_file_path"].notnull() == True]

    def _get_caption_str(self, r: pd.Series):
        """Generate caption text

        Parameters
        ----------
            r : pd.Series
                row representing pitch/clip to display caption for

        Returns
        -------
            str
                Caption to insert into clip
        """
        if self.metric_caption is not None:
            m_config = _CAPTION_SETUP.get(self.metric_caption)
            m_value = r.get(self.metric_caption)
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
                r.get("pitcher_fullname")
                if self.player_caption == "pitcher"
                else r.get("batter_fullname")
                if self.player_caption == "batter"
                else None
            )
        else:
            return ""

    def _add_intro(self):
        """Add intro video to beginning of queue"""
        self.clip_objs["intro"] = VideoFileClip(_INTROS.get(self.rez), fps_source="fps")

    def _create_resized_clips(self):
        """Resize 720p clips to 1080p

        Opens local file, runs ffmpeg command to upscale to 1080p
        Overwrites file path in df
        """
        new_files = []
        for index, row in self.df.iterrows():
            np = row.get("video_file_path").replace(".mp4", "_rsz.mp4")
            cmd = f"ffmpeg -i {row.get('video_file_path')} -vf scale=1920:1080 -preset slow -crf 18 {np}"
            subprocess.call(cmd)
            self.df.at[index, "video_file_path"] = np
        logging.info(f"Completed resizing clip resolution to 1080p..")

    def _import_clips(self):
        """Import clips to VideoFileClip obj"""
        for _, row in self.df.iterrows():
            self.clip_objs[row.get("pitch_id")] = VideoFileClip(
                row.get("video_file_path"), fps_source="fps"
            )
        logging.info(f"Read in {len(self.clip_objs.values())} clip(s)..")

    def _get_caption_clip(self, t: str):
        """Generate Caption Clip

        Parameters
        ----------
            t : str
                text of caption

        Returns
        -------
            TextClip
                clip with caption to be displayed on-top of actual bball video
        """
        clip = TextClip(t, fontsize=_CAPTION_FONT, color="white")
        clip = clip.set_pos(("right", "bottom"))
        clip = clip.margin(bottom=100, right=50, opacity=0)
        clip = clip.set_duration(2)
        return clip

    def _add_captions(self):
        """Add caption clip to video clip"""
        for _, row in self.df.iterrows():
            caption_str = self._get_caption_str(row)
            caption_clip = self._get_caption_clip(caption_str)
            self.clip_objs[row.get("pitch_id")] = CompositeVideoClip(
                [self.clip_objs[row.get("pitch_id")], caption_clip]
            )

    def _limit_clip_length(self):
        """Apply maximum clip length (secs)"""
        for _, r in self.df.iterrows():
            iter_clip = self.clip_objs[r.get("pitch_id")]
            if self.max_clip_length < iter_clip.duration and self.max_clip_length > 0:
                self.clip_objs[r.get("pitch_id")] = iter_clip.subclip(
                    0, self.max_clip_length
                )

    def _build_compilation(self):
        """Build compilation from individual clips
        Write to local file
        """
        new_clip_objs = []

        clip_ctr = 0
        clip_ct = len(self.clip_objs.values())

        if self.add_transitions:
            if self.use_intro:
                self._add_intro()

            for clip_obj in self.clip_objs.values():
                clip_ctr += 1
                if clip_ctr == 1 or clip_ctr == clip_ct:
                    new_clip_objs.append(clip_obj)
                else:
                    new_clip_objs.append(clip_obj.crossfadein(self.transition_padding))

            comp_obj = concatenate_videoclips(
                new_clip_objs, padding=-self.transition_padding, method="compose"
            )
            comp_obj.write_videofile(self.comp_file, fps=self.fps)

        else:
            comp_obj = concatenate_videoclips(self.clip_objs.values(), method="compose")
            comp_obj.write_videofile(self.comp_file, fps=self.fps)
