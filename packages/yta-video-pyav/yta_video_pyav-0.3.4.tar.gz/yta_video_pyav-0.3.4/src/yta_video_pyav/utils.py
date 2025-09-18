from av.video.stream import VideoStream
from typing import Union


def get_real_duration(
    video_stream: VideoStream
) -> Union[float, None]:
    """
    Get the real video duration in seconds. This
    will look for the last pts in the packets
    without decoding the frames.

    Sometimes the video metadata is not ok and
    the real duration is different than the one
    its written, so we need to obtain the real.
    """
    # If duration, seek to the 10% last packets
    if video_stream.duration:
        target_ts = int(video_stream.duration * 0.9)
        video_stream.container.seek(target_ts, stream = video_stream)

    last_pts = None
    last_duration = None

    for packet in video_stream.container.demux(video_stream):
        if packet.pts is not None:
            last_pts = packet.pts
            last_duration = packet.duration

    video_stream.container.close()

    if last_pts is None:
        return None

    # Last packet pts + packet duration = real
    # duration
    frame_duration = (last_duration or 1) * video_stream.time_base
    real_duration = (last_pts * video_stream.time_base) + frame_duration

    return float(real_duration)
