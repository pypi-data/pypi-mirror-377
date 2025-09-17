import os
import cv2
import numpy as np
import decord
from exordium import PathType


def video2numpy(input_path: PathType):
    vr = decord.VideoReader(str(input_path))
    return np.array([vr[i].asnumpy() for i in range(len(vr))]) # (T,H,W,C)


def vr2video(video: decord.VideoReader,
             frame_start: int,
             frame_end: int,
             output_path: PathType,
             fps: int | float = 25) -> None:
    """Saves a video to a .mp4 file without audio.

    Args:
        video (decord.VideoReader): video as a VideoReader object.
        output_path (PathType): path to the output file.
        fps (int | float, optional): frame per sec. Defaults to 25.
    """
    height, width = video[0].shape[:2]
    fourcc = cv2.VideoWriter_fourcc(*'mp4v') # type: ignore
    output_video = cv2.VideoWriter(str(output_path), fourcc, fps, (width, height))

    for idx in range(frame_start, min(frame_end, len(video)), 1):
        frame = video[idx]
        frame = cv2.cvtColor(frame.asnumpy(), cv2.COLOR_RGB2BGR)
        output_video.write(frame)

    output_video.release()


def write_frames_with_audio(video: decord.VideoReader,
                            audio_path: PathType,
                            output_video_path: PathType,
                            fps: int | float = 25) -> None:
    """Write frames to a video file with audio.

    Args:
        video (decord.VideoReader): video as a VideoReader object.
        audio (PathType): path to the audio file.
        output_video_path (PathType): path to the video file.
        fps (int | float, optional): frame per sec. Defaults to 25.
    """
    height, width = video[0].shape[:2]

    # create video
    fourcc = cv2.VideoWriter_fourcc(*'mp4v') # type: ignore
    output_video = cv2.VideoWriter(str(output_video_path), fourcc, fps, (width, height))
    for idx in range(len(video)):
        frame = video[idx]
        frame = cv2.cvtColor(frame.asnumpy(), cv2.COLOR_RGB2BGR)
        output_video.write(frame)
    output_video.release()

    # add audio to video
    CMD = f"ffmpeg -i {str(output_video_path)} -i {str(audio_path)} -c:v copy -c:a aac -strict experimental -map 0:v:0 -map 1:a:0 {output_video_path}_with_audio.mp4"
    os.system(CMD)
    os.system(f'rm {audio_path}')