from enum import Enum


class GetJobsJobType(str, Enum):
    """GetJobsJobType enumeration."""

    ACTIVITYPUB_FOLLOW = "activitypub-follow"
    ACTIVITYPUB_HTTP_BROADCAST = "activitypub-http-broadcast"
    ACTIVITYPUB_HTTP_FETCHER = "activitypub-http-fetcher"
    ACTIVITYPUB_HTTP_UNICAST = "activitypub-http-unicast"
    ACTIVITYPUB_REFRESHER = "activitypub-refresher"
    EMAIL = "email"
    VIDEOS_VIEWS_STATS = "videos-views-stats"
    VIDEO_CHANNEL_IMPORT = "video-channel-import"
    VIDEO_FILE_IMPORT = "video-file-import"
    VIDEO_IMPORT = "video-import"
    VIDEO_LIVE_ENDING = "video-live-ending"
    VIDEO_REDUNDANCY = "video-redundancy"
    VIDEO_TRANSCODING = "video-transcoding"

    def __str__(self) -> str:
        return str(self.value)
