from collections.abc import Mapping
from typing import (
    TYPE_CHECKING,
    Any,
    TypeVar,
)

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from typing_extensions import Self

from peertube.types import UNSET, Unset

if TYPE_CHECKING:
    from peertube.models.server_stats_videos_redundancy_item import (
        ServerStatsVideosRedundancyItem,
    )


T = TypeVar("T", bound="ServerStats")


@_attrs_define
class ServerStats:
    """Attributes:
    total_users (Union[Unset, float]):
    total_daily_active_users (Union[Unset, float]):
    total_weekly_active_users (Union[Unset, float]):
    total_monthly_active_users (Union[Unset, float]):
    total_moderators (Union[Unset, float]): **PeerTube >= 6.1** Value is null if the admin disabled total moderators
        stats
    total_admins (Union[Unset, float]): **PeerTube >= 6.1** Value is null if the admin disabled total admins stats
    total_local_videos (Union[Unset, float]):
    total_local_video_views (Union[Unset, float]): Total video views made on the instance
    total_local_video_comments (Union[Unset, float]): Total comments made by local users
    total_local_video_files_size (Union[Unset, float]):
    total_videos (Union[Unset, float]):
    total_video_comments (Union[Unset, float]):
    total_local_video_channels (Union[Unset, float]):
    total_local_daily_active_video_channels (Union[Unset, float]):
    total_local_weekly_active_video_channels (Union[Unset, float]):
    total_local_monthly_active_video_channels (Union[Unset, float]):
    total_local_playlists (Union[Unset, float]):
    total_instance_followers (Union[Unset, float]):
    total_instance_following (Union[Unset, float]):
    videos_redundancy (Union[Unset, list['ServerStatsVideosRedundancyItem']]):
    total_activity_pub_messages_processed (Union[Unset, float]):
    total_activity_pub_messages_successes (Union[Unset, float]):
    total_activity_pub_messages_errors (Union[Unset, float]):
    activity_pub_messages_processed_per_second (Union[Unset, float]):
    total_activity_pub_messages_waiting (Union[Unset, float]):
    average_registration_request_response_time_ms (Union[Unset, float]): **PeerTube >= 6.1** Value is null if the
        admin disabled registration requests stats
    total_registration_requests_processed (Union[Unset, float]): **PeerTube >= 6.1** Value is null if the admin
        disabled registration requests stats
    total_registration_requests (Union[Unset, float]): **PeerTube >= 6.1** Value is null if the admin disabled
        registration requests stats
    average_abuse_response_time_ms (Union[Unset, float]): **PeerTube >= 6.1** Value is null if the admin disabled
        abuses stats
    total_abuses_processed (Union[Unset, float]): **PeerTube >= 6.1** Value is null if the admin disabled abuses
        stats
    total_abuses (Union[Unset, float]): **PeerTube >= 6.1** Value is null if the admin disabled abuses stats
    """

    total_users: Unset | float = UNSET
    total_daily_active_users: Unset | float = UNSET
    total_weekly_active_users: Unset | float = UNSET
    total_monthly_active_users: Unset | float = UNSET
    total_moderators: Unset | float = UNSET
    total_admins: Unset | float = UNSET
    total_local_videos: Unset | float = UNSET
    total_local_video_views: Unset | float = UNSET
    total_local_video_comments: Unset | float = UNSET
    total_local_video_files_size: Unset | float = UNSET
    total_videos: Unset | float = UNSET
    total_video_comments: Unset | float = UNSET
    total_local_video_channels: Unset | float = UNSET
    total_local_daily_active_video_channels: Unset | float = UNSET
    total_local_weekly_active_video_channels: Unset | float = UNSET
    total_local_monthly_active_video_channels: Unset | float = UNSET
    total_local_playlists: Unset | float = UNSET
    total_instance_followers: Unset | float = UNSET
    total_instance_following: Unset | float = UNSET
    videos_redundancy: Unset | list["ServerStatsVideosRedundancyItem"] = UNSET
    total_activity_pub_messages_processed: Unset | float = UNSET
    total_activity_pub_messages_successes: Unset | float = UNSET
    total_activity_pub_messages_errors: Unset | float = UNSET
    activity_pub_messages_processed_per_second: Unset | float = UNSET
    total_activity_pub_messages_waiting: Unset | float = UNSET
    average_registration_request_response_time_ms: Unset | float = UNSET
    total_registration_requests_processed: Unset | float = UNSET
    total_registration_requests: Unset | float = UNSET
    average_abuse_response_time_ms: Unset | float = UNSET
    total_abuses_processed: Unset | float = UNSET
    total_abuses: Unset | float = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert instance to dictionary."""
        total_users = self.total_users

        total_daily_active_users = self.total_daily_active_users

        total_weekly_active_users = self.total_weekly_active_users

        total_monthly_active_users = self.total_monthly_active_users

        total_moderators = self.total_moderators

        total_admins = self.total_admins

        total_local_videos = self.total_local_videos

        total_local_video_views = self.total_local_video_views

        total_local_video_comments = self.total_local_video_comments

        total_local_video_files_size = self.total_local_video_files_size

        total_videos = self.total_videos

        total_video_comments = self.total_video_comments

        total_local_video_channels = self.total_local_video_channels

        total_local_daily_active_video_channels = (
            self.total_local_daily_active_video_channels
        )

        total_local_weekly_active_video_channels = (
            self.total_local_weekly_active_video_channels
        )

        total_local_monthly_active_video_channels = (
            self.total_local_monthly_active_video_channels
        )

        total_local_playlists = self.total_local_playlists

        total_instance_followers = self.total_instance_followers

        total_instance_following = self.total_instance_following

        videos_redundancy: Unset | list[dict[str, Any]] = UNSET
        if not isinstance(self.videos_redundancy, Unset):
            videos_redundancy = []
            for videos_redundancy_item_data in self.videos_redundancy:
                videos_redundancy_item = videos_redundancy_item_data.to_dict()
                videos_redundancy.append(videos_redundancy_item)

        total_activity_pub_messages_processed = (
            self.total_activity_pub_messages_processed
        )

        total_activity_pub_messages_successes = (
            self.total_activity_pub_messages_successes
        )

        total_activity_pub_messages_errors = self.total_activity_pub_messages_errors

        activity_pub_messages_processed_per_second = (
            self.activity_pub_messages_processed_per_second
        )

        total_activity_pub_messages_waiting = self.total_activity_pub_messages_waiting

        average_registration_request_response_time_ms = (
            self.average_registration_request_response_time_ms
        )

        total_registration_requests_processed = (
            self.total_registration_requests_processed
        )

        total_registration_requests = self.total_registration_requests

        average_abuse_response_time_ms = self.average_abuse_response_time_ms

        total_abuses_processed = self.total_abuses_processed

        total_abuses = self.total_abuses

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if total_users is not UNSET:
            field_dict["totalUsers"] = total_users
        if total_daily_active_users is not UNSET:
            field_dict["totalDailyActiveUsers"] = total_daily_active_users
        if total_weekly_active_users is not UNSET:
            field_dict["totalWeeklyActiveUsers"] = total_weekly_active_users
        if total_monthly_active_users is not UNSET:
            field_dict["totalMonthlyActiveUsers"] = total_monthly_active_users
        if total_moderators is not UNSET:
            field_dict["totalModerators"] = total_moderators
        if total_admins is not UNSET:
            field_dict["totalAdmins"] = total_admins
        if total_local_videos is not UNSET:
            field_dict["totalLocalVideos"] = total_local_videos
        if total_local_video_views is not UNSET:
            field_dict["totalLocalVideoViews"] = total_local_video_views
        if total_local_video_comments is not UNSET:
            field_dict["totalLocalVideoComments"] = total_local_video_comments
        if total_local_video_files_size is not UNSET:
            field_dict["totalLocalVideoFilesSize"] = total_local_video_files_size
        if total_videos is not UNSET:
            field_dict["totalVideos"] = total_videos
        if total_video_comments is not UNSET:
            field_dict["totalVideoComments"] = total_video_comments
        if total_local_video_channels is not UNSET:
            field_dict["totalLocalVideoChannels"] = total_local_video_channels
        if total_local_daily_active_video_channels is not UNSET:
            field_dict["totalLocalDailyActiveVideoChannels"] = (
                total_local_daily_active_video_channels
            )
        if total_local_weekly_active_video_channels is not UNSET:
            field_dict["totalLocalWeeklyActiveVideoChannels"] = (
                total_local_weekly_active_video_channels
            )
        if total_local_monthly_active_video_channels is not UNSET:
            field_dict["totalLocalMonthlyActiveVideoChannels"] = (
                total_local_monthly_active_video_channels
            )
        if total_local_playlists is not UNSET:
            field_dict["totalLocalPlaylists"] = total_local_playlists
        if total_instance_followers is not UNSET:
            field_dict["totalInstanceFollowers"] = total_instance_followers
        if total_instance_following is not UNSET:
            field_dict["totalInstanceFollowing"] = total_instance_following
        if videos_redundancy is not UNSET:
            field_dict["videosRedundancy"] = videos_redundancy
        if total_activity_pub_messages_processed is not UNSET:
            field_dict["totalActivityPubMessagesProcessed"] = (
                total_activity_pub_messages_processed
            )
        if total_activity_pub_messages_successes is not UNSET:
            field_dict["totalActivityPubMessagesSuccesses"] = (
                total_activity_pub_messages_successes
            )
        if total_activity_pub_messages_errors is not UNSET:
            field_dict["totalActivityPubMessagesErrors"] = (
                total_activity_pub_messages_errors
            )
        if activity_pub_messages_processed_per_second is not UNSET:
            field_dict["activityPubMessagesProcessedPerSecond"] = (
                activity_pub_messages_processed_per_second
            )
        if total_activity_pub_messages_waiting is not UNSET:
            field_dict["totalActivityPubMessagesWaiting"] = (
                total_activity_pub_messages_waiting
            )
        if average_registration_request_response_time_ms is not UNSET:
            field_dict["averageRegistrationRequestResponseTimeMs"] = (
                average_registration_request_response_time_ms
            )
        if total_registration_requests_processed is not UNSET:
            field_dict["totalRegistrationRequestsProcessed"] = (
                total_registration_requests_processed
            )
        if total_registration_requests is not UNSET:
            field_dict["totalRegistrationRequests"] = total_registration_requests
        if average_abuse_response_time_ms is not UNSET:
            field_dict["averageAbuseResponseTimeMs"] = average_abuse_response_time_ms
        if total_abuses_processed is not UNSET:
            field_dict["totalAbusesProcessed"] = total_abuses_processed
        if total_abuses is not UNSET:
            field_dict["totalAbuses"] = total_abuses

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        """Create instance from dictionary."""
        from peertube.models.server_stats_videos_redundancy_item import (
            ServerStatsVideosRedundancyItem,
        )

        d = dict(src_dict)
        total_users = d.pop("totalUsers", UNSET)

        total_daily_active_users = d.pop("totalDailyActiveUsers", UNSET)

        total_weekly_active_users = d.pop("totalWeeklyActiveUsers", UNSET)

        total_monthly_active_users = d.pop("totalMonthlyActiveUsers", UNSET)

        total_moderators = d.pop("totalModerators", UNSET)

        total_admins = d.pop("totalAdmins", UNSET)

        total_local_videos = d.pop("totalLocalVideos", UNSET)

        total_local_video_views = d.pop("totalLocalVideoViews", UNSET)

        total_local_video_comments = d.pop("totalLocalVideoComments", UNSET)

        total_local_video_files_size = d.pop("totalLocalVideoFilesSize", UNSET)

        total_videos = d.pop("totalVideos", UNSET)

        total_video_comments = d.pop("totalVideoComments", UNSET)

        total_local_video_channels = d.pop("totalLocalVideoChannels", UNSET)

        total_local_daily_active_video_channels = d.pop(
            "totalLocalDailyActiveVideoChannels", UNSET
        )

        total_local_weekly_active_video_channels = d.pop(
            "totalLocalWeeklyActiveVideoChannels", UNSET
        )

        total_local_monthly_active_video_channels = d.pop(
            "totalLocalMonthlyActiveVideoChannels", UNSET
        )

        total_local_playlists = d.pop("totalLocalPlaylists", UNSET)

        total_instance_followers = d.pop("totalInstanceFollowers", UNSET)

        total_instance_following = d.pop("totalInstanceFollowing", UNSET)

        videos_redundancy = []
        _videos_redundancy = d.pop("videosRedundancy", UNSET)
        for videos_redundancy_item_data in _videos_redundancy or []:
            videos_redundancy_item = ServerStatsVideosRedundancyItem.from_dict(
                videos_redundancy_item_data
            )

            videos_redundancy.append(videos_redundancy_item)

        total_activity_pub_messages_processed = d.pop(
            "totalActivityPubMessagesProcessed", UNSET
        )

        total_activity_pub_messages_successes = d.pop(
            "totalActivityPubMessagesSuccesses", UNSET
        )

        total_activity_pub_messages_errors = d.pop(
            "totalActivityPubMessagesErrors", UNSET
        )

        activity_pub_messages_processed_per_second = d.pop(
            "activityPubMessagesProcessedPerSecond", UNSET
        )

        total_activity_pub_messages_waiting = d.pop(
            "totalActivityPubMessagesWaiting", UNSET
        )

        average_registration_request_response_time_ms = d.pop(
            "averageRegistrationRequestResponseTimeMs", UNSET
        )

        total_registration_requests_processed = d.pop(
            "totalRegistrationRequestsProcessed", UNSET
        )

        total_registration_requests = d.pop("totalRegistrationRequests", UNSET)

        average_abuse_response_time_ms = d.pop("averageAbuseResponseTimeMs", UNSET)

        total_abuses_processed = d.pop("totalAbusesProcessed", UNSET)

        total_abuses = d.pop("totalAbuses", UNSET)

        server_stats = cls(
            total_users=total_users,
            total_daily_active_users=total_daily_active_users,
            total_weekly_active_users=total_weekly_active_users,
            total_monthly_active_users=total_monthly_active_users,
            total_moderators=total_moderators,
            total_admins=total_admins,
            total_local_videos=total_local_videos,
            total_local_video_views=total_local_video_views,
            total_local_video_comments=total_local_video_comments,
            total_local_video_files_size=total_local_video_files_size,
            total_videos=total_videos,
            total_video_comments=total_video_comments,
            total_local_video_channels=total_local_video_channels,
            total_local_daily_active_video_channels=total_local_daily_active_video_channels,
            total_local_weekly_active_video_channels=total_local_weekly_active_video_channels,
            total_local_monthly_active_video_channels=total_local_monthly_active_video_channels,
            total_local_playlists=total_local_playlists,
            total_instance_followers=total_instance_followers,
            total_instance_following=total_instance_following,
            videos_redundancy=videos_redundancy,
            total_activity_pub_messages_processed=total_activity_pub_messages_processed,
            total_activity_pub_messages_successes=total_activity_pub_messages_successes,
            total_activity_pub_messages_errors=total_activity_pub_messages_errors,
            activity_pub_messages_processed_per_second=activity_pub_messages_processed_per_second,
            total_activity_pub_messages_waiting=total_activity_pub_messages_waiting,
            average_registration_request_response_time_ms=average_registration_request_response_time_ms,
            total_registration_requests_processed=total_registration_requests_processed,
            total_registration_requests=total_registration_requests,
            average_abuse_response_time_ms=average_abuse_response_time_ms,
            total_abuses_processed=total_abuses_processed,
            total_abuses=total_abuses,
        )

        server_stats.additional_properties = d
        return server_stats

    @property
    def additional_keys(self) -> list[str]:
        """Get additional property keys."""
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
