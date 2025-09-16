from enum import Enum


class RunnerJobType(str, Enum):
    """RunnerJobType enumeration."""

    LIVE_RTMP_HLS_TRANSCODING = "live-rtmp-hls-transcoding"
    VOD_AUDIO_MERGE_TRANSCODING = "vod-audio-merge-transcoding"
    VOD_HLS_TRANSCODING = "vod-hls-transcoding"
    VOD_WEB_VIDEO_TRANSCODING = "vod-web-video-transcoding"

    def __str__(self) -> str:
        return str(self.value)
