from yta_constants.enum import YTAEnum as Enum
from yta_constants.ffmpeg import FfmpegPixelFormat, FfmpegVideoCodec, FfmpegAudioCodec, FfmpegAudioFormat, FfmpegAudioLayout
from yta_constants.file import FileExtension


class Settings(Enum):
    """
    The settings for our pyav video library.
    """

    DEFAULT_PIXEL_FORMAT = FfmpegPixelFormat.YUV420P.value
    """
    The pixel format we use by default.
    """
    # 'libx264' is an implementation of 'h264'
    DEFAULT_VIDEO_CODEC = FfmpegVideoCodec.LIBX264.value
    """
    The video codec we use by default.
    """
    DEFAULT_VIDEO_EXTENSION = FileExtension.MP4.value
    """
    The video file extension (and container)
    we use by default. Does not include the
    '.' at the begining.
    """
    DEFAULT_ALPHA_PIXEL_FORMAT = FfmpegPixelFormat.RGBA.value
    """
    The pixel format we use by default for
    videos with alpha layer.
    """
    DEFAULT_ALPHA_VIDEO_CODEC = FfmpegVideoCodec.LIBX264.value
    """
    The video codec we use by default for
    videos with alpha layer.
    """
    DEFAULT_ALPHA_VIDEO_EXTENSION = FileExtension.WEBM.value
    """
    The video file extension (and container)
    we use by default for videos with alpha
    layer. Does not include the '.' at the
    begining.
    """
    DEFAULT_VIDEO_FPS = 60
    """
    The video fps we use by default.
    """
    DEFAULT_VIDEO_SIZE = (1920, 1080)
    """
    The video frame size we use by default.
    """

    DEFAULT_AUDIO_CODEC = FfmpegAudioCodec.AAC.value
    """
    The audio codec we use by default.
    """
    DEFAULT_AUDIO_EXTENSION = FileExtension.MP4.value
    """
    The audio file extension (and container)
    we use by default. Does not include the
    '.' at the begining.
    """
    DEFAULT_AUDIO_FORMAT = FfmpegAudioFormat.FLTP.value
    """
    The audio format we use by default.
    """
    DEFAULT_AUDIO_LAYOUT = FfmpegAudioLayout.STEREO.value
    """
    The audio layout we use by default.
    """
    DEFAULT_AUDIO_FPS = 48_000
    """
    The audio fps (or sample rate) we use by
    default.
    """
    DEFAULT_AUDIO_SAMPLES_PER_FRAME = 1_024
    """
    The samples per frame we use by default.
    """

"""
*Otros encoders posibles para H.264
Dependiendo de cómo tengas compilado FFmpeg, podrías tener más encoders disponibles:
libx264 → CPU (default, muy usado).
h264_nvenc → acelerado por GPU Nvidia.
h264_qsv → acelerado por Intel QuickSync.
h264_amf → acelerado por GPU AMD.
h264_videotoolbox → acelerado en macOS.
h264_v4l2m2m → acelerado en dispositivos Linux ARM (ej. Raspberry Pi).
Todos generan un bitstream H.264 válido, solo cambia la implementación.

---

This command will show all the H.264 encoders
my ffmpeg version has.
- ffmpeg -encoders | grep 264
"""