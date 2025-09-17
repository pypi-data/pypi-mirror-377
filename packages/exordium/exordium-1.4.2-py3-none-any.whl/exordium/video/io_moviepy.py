import os
import logging
from typing import Sequence
from pathlib import Path
import numpy as np
from moviepy import ImageSequenceClip
from exordium import PathType


def frames2video(frames: PathType | Sequence[str] | Sequence[np.ndarray],
                 output_path: PathType,
                 fps: int | float = 25.,
                 extension: str = '.png',
                 overwrite: bool = False) -> None:
    """Saves frames to a video without audio using moviepy.

    Args:
        frames (PathType | Sequence[str] | Sequence[np.ndarray]): frames or path to the frames.
        output_path (PathType): path to the output video.
        fps (int | float, optional): frame per sec. Defaults to 25.
        extension (str, optional): frame file extension. Defaults to '.png'.
        overwrite (bool, optional): if True it overwrites existing file. Defaults to False.
    """
    output_path = Path(output_path)
    if output_path.exists() and not overwrite:
        logging.info(f'Video already exists')
        return

    output_path.parent.mkdir(parents=True, exist_ok=True)

    if isinstance(frames, (str, os.PathLike)):
        frames = sorted([str(elem) for elem in list(Path(frames).iterdir()) if elem.suffix == extension])

    logging.info(f'Found {len(frames)} frames.')
    movie_clip = ImageSequenceClip(frames, fps)
    movie_clip.write_videofile(str(output_path), fps=fps, logger="bar")
    movie_clip.close()
    logging.info(f'Video is done: {str(output_path)}')
