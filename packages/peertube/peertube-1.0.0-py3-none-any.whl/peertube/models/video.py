import datetime
from collections.abc import Mapping
from typing import (
    TYPE_CHECKING,
    Any,
    TypeVar,
    Union,
    cast,
)
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse
from typing_extensions import Self

from peertube.models.nsfw_flag import NSFWFlag
from peertube.types import UNSET, Unset

if TYPE_CHECKING:
    from peertube.models.account_summary import AccountSummary
    from peertube.models.live_schedule import LiveSchedule
    from peertube.models.video_channel_summary import VideoChannelSummary
    from peertube.models.video_constant_number_category import (
        VideoConstantNumberCategory,
    )
    from peertube.models.video_constant_number_licence import VideoConstantNumberLicence
    from peertube.models.video_constant_string_language import (
        VideoConstantStringLanguage,
    )
    from peertube.models.video_privacy_constant import VideoPrivacyConstant
    from peertube.models.video_scheduled_update import VideoScheduledUpdate
    from peertube.models.video_state_constant import VideoStateConstant
    from peertube.models.video_user_history_type_0 import VideoUserHistoryType0


T = TypeVar("T", bound="Video")


@_attrs_define
class Video:
    r"""Attributes:
    id (Union[Unset, int]):  Example: 42.
    uuid (Union[Unset, UUID]):  Example: 9c9de5e8-0a1e-484a-b099-e80766180a6d.
    short_uuid (Union[Unset, str]): translation of a uuid v4 with a bigger alphabet to have a shorter uuid Example:
        2y84q2MQUMWPbiEcxNXMgC.
    is_live (Union[Unset, bool]):
    live_schedules (Union[Unset, list['LiveSchedule']]):
    created_at (Union[Unset, datetime.datetime]): time at which the video object was first drafted Example:
        2017-10-01T10:52:46.396Z.
    published_at (Union[Unset, datetime.datetime]): time at which the video was marked as ready for playback (with
        restrictions depending on `privacy`). Usually set after a `state` evolution. Example: 2018-10-01T10:52:46.396Z.
    updated_at (Union[Unset, datetime.datetime]): last time the video's metadata was modified Example:
        2021-05-04T08:01:01.502Z.
    originally_published_at (Union[None, Unset, datetime.datetime]): used to represent a date of first publication,
        prior to the practical publication date of `publishedAt` Example: 2010-10-01T10:52:46.396Z.
    category (Union[Unset, VideoConstantNumberCategory]):
    licence (Union[Unset, VideoConstantNumberLicence]):
    language (Union[Unset, VideoConstantStringLanguage]):
    privacy (Union[Unset, VideoPrivacyConstant]):
    truncated_description (Union[None, Unset, str]): truncated description of the video, written in Markdown.
         Example: **[Want to help to translate this video?](https://weblate.framasoft.org/projects/what-is-peertube-
        video/)**\r\n\r\n
        **Take back the control of your videos! [#JoinPeertube](https://joinpeertube.org)**\r\n*A decentralized video
        hosting network, based on fr...
        .
    duration (Union[Unset, int]): duration of the video in seconds Example: 1419.
    aspect_ratio (Union[None, Unset, float]): **PeerTube >= 6.1** Aspect ratio of the video stream Example: 1.778.
    is_local (Union[Unset, bool]):
    name (Union[Unset, str]): title of the video Example: What is PeerTube?.
    thumbnail_path (Union[Unset, str]):  Example: /lazy-static/thumbnails/a65bc12f-9383-462e-81ae-8207e8b434ee.jpg.
    preview_path (Union[Unset, str]):  Example: /lazy-static/previews/a65bc12f-9383-462e-81ae-8207e8b434ee.jpg.
    embed_path (Union[Unset, str]):  Example: /videos/embed/a65bc12f-9383-462e-81ae-8207e8b434ee.
    views (Union[Unset, int]):  Example: 1337.
    likes (Union[Unset, int]):  Example: 42.
    dislikes (Union[Unset, int]):  Example: 7.
    comments (Union[Unset, int]): **PeerTube >= 7.2** Number of comments on the video
    nsfw (Union[Unset, bool]):
    nsfw_flags (Union[Unset, NSFWFlag]):
        NSFW flags (can be combined using bitwise or operator)
        - `0` NONE
        - `1` VIOLENT
        - `2` EXPLICIT_SEX
    nsfw_summary (Union[Unset, str]): **PeerTube >= 7.2** More information about the sensitive content of the video
    wait_transcoding (Union[None, Unset, bool]):
    state (Union[Unset, VideoStateConstant]):
    scheduled_update (Union['VideoScheduledUpdate', None, Unset]):
    blacklisted (Union[None, Unset, bool]):
    blacklisted_reason (Union[None, Unset, str]):
    account (Union[Unset, AccountSummary]):
    channel (Union[Unset, VideoChannelSummary]):
    user_history (Union['VideoUserHistoryType0', None, Unset]):
    """

    id: Unset | int = UNSET
    uuid: Unset | UUID = UNSET
    short_uuid: Unset | str = UNSET
    is_live: Unset | bool = UNSET
    live_schedules: Unset | list["LiveSchedule"] = UNSET
    created_at: Unset | datetime.datetime = UNSET
    published_at: Unset | datetime.datetime = UNSET
    updated_at: Unset | datetime.datetime = UNSET
    originally_published_at: None | Unset | datetime.datetime = UNSET
    category: Union[Unset, "VideoConstantNumberCategory"] = UNSET
    licence: Union[Unset, "VideoConstantNumberLicence"] = UNSET
    language: Union[Unset, "VideoConstantStringLanguage"] = UNSET
    privacy: Union[Unset, "VideoPrivacyConstant"] = UNSET
    truncated_description: None | Unset | str = UNSET
    duration: Unset | int = UNSET
    aspect_ratio: None | Unset | float = UNSET
    is_local: Unset | bool = UNSET
    name: Unset | str = UNSET
    thumbnail_path: Unset | str = UNSET
    preview_path: Unset | str = UNSET
    embed_path: Unset | str = UNSET
    views: Unset | int = UNSET
    likes: Unset | int = UNSET
    dislikes: Unset | int = UNSET
    comments: Unset | int = UNSET
    nsfw: Unset | bool = UNSET
    nsfw_flags: Unset | NSFWFlag = UNSET
    nsfw_summary: Unset | str = UNSET
    wait_transcoding: None | Unset | bool = UNSET
    state: Union[Unset, "VideoStateConstant"] = UNSET
    scheduled_update: Union["VideoScheduledUpdate", None, Unset] = UNSET
    blacklisted: None | Unset | bool = UNSET
    blacklisted_reason: None | Unset | str = UNSET
    account: Union[Unset, "AccountSummary"] = UNSET
    channel: Union[Unset, "VideoChannelSummary"] = UNSET
    user_history: Union["VideoUserHistoryType0", None, Unset] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert instance to dictionary."""
        from peertube.models.video_scheduled_update import VideoScheduledUpdate
        from peertube.models.video_user_history_type_0 import VideoUserHistoryType0

        id = self.id

        uuid: Unset | str = UNSET
        if not isinstance(self.uuid, Unset):
            uuid = str(self.uuid)

        short_uuid = self.short_uuid

        is_live = self.is_live

        live_schedules: Unset | list[dict[str, Any]] = UNSET
        if not isinstance(self.live_schedules, Unset):
            live_schedules = []
            for live_schedules_item_data in self.live_schedules:
                live_schedules_item = live_schedules_item_data.to_dict()
                live_schedules.append(live_schedules_item)

        created_at: Unset | str = UNSET
        if not isinstance(self.created_at, Unset):
            created_at = self.created_at.isoformat()

        published_at: Unset | str = UNSET
        if not isinstance(self.published_at, Unset):
            published_at = self.published_at.isoformat()

        updated_at: Unset | str = UNSET
        if not isinstance(self.updated_at, Unset):
            updated_at = self.updated_at.isoformat()

        originally_published_at: None | Unset | str
        if isinstance(self.originally_published_at, Unset):
            originally_published_at = UNSET
        elif isinstance(self.originally_published_at, datetime.datetime):
            originally_published_at = self.originally_published_at.isoformat()
        else:
            originally_published_at = self.originally_published_at

        category: Unset | dict[str, Any] = UNSET
        if not isinstance(self.category, Unset):
            category = self.category.to_dict()

        licence: Unset | dict[str, Any] = UNSET
        if not isinstance(self.licence, Unset):
            licence = self.licence.to_dict()

        language: Unset | dict[str, Any] = UNSET
        if not isinstance(self.language, Unset):
            language = self.language.to_dict()

        privacy: Unset | dict[str, Any] = UNSET
        if not isinstance(self.privacy, Unset):
            privacy = self.privacy.to_dict()

        truncated_description: None | Unset | str
        if isinstance(self.truncated_description, Unset):
            truncated_description = UNSET
        else:
            truncated_description = self.truncated_description

        duration = self.duration

        aspect_ratio: None | Unset | float
        if isinstance(self.aspect_ratio, Unset):
            aspect_ratio = UNSET
        else:
            aspect_ratio = self.aspect_ratio

        is_local = self.is_local

        name = self.name

        thumbnail_path = self.thumbnail_path

        preview_path = self.preview_path

        embed_path = self.embed_path

        views = self.views

        likes = self.likes

        dislikes = self.dislikes

        comments = self.comments

        nsfw = self.nsfw

        nsfw_flags: Unset | int = UNSET
        if not isinstance(self.nsfw_flags, Unset):
            nsfw_flags = self.nsfw_flags.value

        nsfw_summary = self.nsfw_summary

        wait_transcoding: None | Unset | bool
        if isinstance(self.wait_transcoding, Unset):
            wait_transcoding = UNSET
        else:
            wait_transcoding = self.wait_transcoding

        state: Unset | dict[str, Any] = UNSET
        if not isinstance(self.state, Unset):
            state = self.state.to_dict()

        scheduled_update: None | Unset | dict[str, Any]
        if isinstance(self.scheduled_update, Unset):
            scheduled_update = UNSET
        elif isinstance(self.scheduled_update, VideoScheduledUpdate):
            scheduled_update = self.scheduled_update.to_dict()
        else:
            scheduled_update = self.scheduled_update

        blacklisted: None | Unset | bool
        if isinstance(self.blacklisted, Unset):
            blacklisted = UNSET
        else:
            blacklisted = self.blacklisted

        blacklisted_reason: None | Unset | str
        if isinstance(self.blacklisted_reason, Unset):
            blacklisted_reason = UNSET
        else:
            blacklisted_reason = self.blacklisted_reason

        account: Unset | dict[str, Any] = UNSET
        if not isinstance(self.account, Unset):
            account = self.account.to_dict()

        channel: Unset | dict[str, Any] = UNSET
        if not isinstance(self.channel, Unset):
            channel = self.channel.to_dict()

        user_history: None | Unset | dict[str, Any]
        if isinstance(self.user_history, Unset):
            user_history = UNSET
        elif isinstance(self.user_history, VideoUserHistoryType0):
            user_history = self.user_history.to_dict()
        else:
            user_history = self.user_history

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if id is not UNSET:
            field_dict["id"] = id
        if uuid is not UNSET:
            field_dict["uuid"] = uuid
        if short_uuid is not UNSET:
            field_dict["shortUUID"] = short_uuid
        if is_live is not UNSET:
            field_dict["isLive"] = is_live
        if live_schedules is not UNSET:
            field_dict["liveSchedules"] = live_schedules
        if created_at is not UNSET:
            field_dict["createdAt"] = created_at
        if published_at is not UNSET:
            field_dict["publishedAt"] = published_at
        if updated_at is not UNSET:
            field_dict["updatedAt"] = updated_at
        if originally_published_at is not UNSET:
            field_dict["originallyPublishedAt"] = originally_published_at
        if category is not UNSET:
            field_dict["category"] = category
        if licence is not UNSET:
            field_dict["licence"] = licence
        if language is not UNSET:
            field_dict["language"] = language
        if privacy is not UNSET:
            field_dict["privacy"] = privacy
        if truncated_description is not UNSET:
            field_dict["truncatedDescription"] = truncated_description
        if duration is not UNSET:
            field_dict["duration"] = duration
        if aspect_ratio is not UNSET:
            field_dict["aspectRatio"] = aspect_ratio
        if is_local is not UNSET:
            field_dict["isLocal"] = is_local
        if name is not UNSET:
            field_dict["name"] = name
        if thumbnail_path is not UNSET:
            field_dict["thumbnailPath"] = thumbnail_path
        if preview_path is not UNSET:
            field_dict["previewPath"] = preview_path
        if embed_path is not UNSET:
            field_dict["embedPath"] = embed_path
        if views is not UNSET:
            field_dict["views"] = views
        if likes is not UNSET:
            field_dict["likes"] = likes
        if dislikes is not UNSET:
            field_dict["dislikes"] = dislikes
        if comments is not UNSET:
            field_dict["comments"] = comments
        if nsfw is not UNSET:
            field_dict["nsfw"] = nsfw
        if nsfw_flags is not UNSET:
            field_dict["nsfwFlags"] = nsfw_flags
        if nsfw_summary is not UNSET:
            field_dict["nsfwSummary"] = nsfw_summary
        if wait_transcoding is not UNSET:
            field_dict["waitTranscoding"] = wait_transcoding
        if state is not UNSET:
            field_dict["state"] = state
        if scheduled_update is not UNSET:
            field_dict["scheduledUpdate"] = scheduled_update
        if blacklisted is not UNSET:
            field_dict["blacklisted"] = blacklisted
        if blacklisted_reason is not UNSET:
            field_dict["blacklistedReason"] = blacklisted_reason
        if account is not UNSET:
            field_dict["account"] = account
        if channel is not UNSET:
            field_dict["channel"] = channel
        if user_history is not UNSET:
            field_dict["userHistory"] = user_history

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        """Create instance from dictionary."""
        from peertube.models.account_summary import AccountSummary
        from peertube.models.live_schedule import LiveSchedule
        from peertube.models.video_channel_summary import VideoChannelSummary
        from peertube.models.video_constant_number_category import (
            VideoConstantNumberCategory,
        )
        from peertube.models.video_constant_number_licence import (
            VideoConstantNumberLicence,
        )
        from peertube.models.video_constant_string_language import (
            VideoConstantStringLanguage,
        )
        from peertube.models.video_privacy_constant import VideoPrivacyConstant
        from peertube.models.video_scheduled_update import VideoScheduledUpdate
        from peertube.models.video_state_constant import VideoStateConstant
        from peertube.models.video_user_history_type_0 import VideoUserHistoryType0

        d = dict(src_dict)
        id = d.pop("id", UNSET)

        _uuid = d.pop("uuid", UNSET)
        uuid: Unset | UUID
        if isinstance(_uuid, Unset):
            uuid = UNSET
        else:
            uuid = UUID(_uuid)

        short_uuid = d.pop("shortUUID", UNSET)

        is_live = d.pop("isLive", UNSET)

        live_schedules = []
        _live_schedules = d.pop("liveSchedules", UNSET)
        for live_schedules_item_data in _live_schedules or []:
            live_schedules_item = LiveSchedule.from_dict(live_schedules_item_data)

            live_schedules.append(live_schedules_item)

        _created_at = d.pop("createdAt", UNSET)
        created_at: Unset | datetime.datetime
        if isinstance(_created_at, Unset):
            created_at = UNSET
        else:
            created_at = isoparse(_created_at)

        _published_at = d.pop("publishedAt", UNSET)
        published_at: Unset | datetime.datetime
        if isinstance(_published_at, Unset):
            published_at = UNSET
        else:
            published_at = isoparse(_published_at)

        _updated_at = d.pop("updatedAt", UNSET)
        updated_at: Unset | datetime.datetime
        if isinstance(_updated_at, Unset):
            updated_at = UNSET
        else:
            updated_at = isoparse(_updated_at)

        def _parse_originally_published_at(
            data: object,
        ) -> None | Unset | datetime.datetime:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError
                originally_published_at_type_0 = isoparse(data)

                return originally_published_at_type_0
            except:  # noqa: E722
                pass
            return cast("None | Unset | datetime.datetime", data)

        originally_published_at = _parse_originally_published_at(
            d.pop("originallyPublishedAt", UNSET)
        )

        _category = d.pop("category", UNSET)
        category: Unset | VideoConstantNumberCategory
        if isinstance(_category, Unset):
            category = UNSET
        else:
            category = VideoConstantNumberCategory.from_dict(_category)

        _licence = d.pop("licence", UNSET)
        licence: Unset | VideoConstantNumberLicence
        if isinstance(_licence, Unset):
            licence = UNSET
        else:
            licence = VideoConstantNumberLicence.from_dict(_licence)

        _language = d.pop("language", UNSET)
        language: Unset | VideoConstantStringLanguage
        if isinstance(_language, Unset):
            language = UNSET
        else:
            language = VideoConstantStringLanguage.from_dict(_language)

        _privacy = d.pop("privacy", UNSET)
        privacy: Unset | VideoPrivacyConstant
        if isinstance(_privacy, Unset):
            privacy = UNSET
        else:
            privacy = VideoPrivacyConstant.from_dict(_privacy)

        def _parse_truncated_description(data: object) -> None | Unset | str:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast("None | Unset | str", data)

        truncated_description = _parse_truncated_description(
            d.pop("truncatedDescription", UNSET)
        )

        duration = d.pop("duration", UNSET)

        def _parse_aspect_ratio(data: object) -> None | Unset | float:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast("None | Unset | float", data)

        aspect_ratio = _parse_aspect_ratio(d.pop("aspectRatio", UNSET))

        is_local = d.pop("isLocal", UNSET)

        name = d.pop("name", UNSET)

        thumbnail_path = d.pop("thumbnailPath", UNSET)

        preview_path = d.pop("previewPath", UNSET)

        embed_path = d.pop("embedPath", UNSET)

        views = d.pop("views", UNSET)

        likes = d.pop("likes", UNSET)

        dislikes = d.pop("dislikes", UNSET)

        comments = d.pop("comments", UNSET)

        nsfw = d.pop("nsfw", UNSET)

        _nsfw_flags = d.pop("nsfwFlags", UNSET)
        nsfw_flags: Unset | NSFWFlag
        if isinstance(_nsfw_flags, Unset):
            nsfw_flags = UNSET
        else:
            nsfw_flags = NSFWFlag(_nsfw_flags)

        nsfw_summary = d.pop("nsfwSummary", UNSET)

        def _parse_wait_transcoding(data: object) -> None | Unset | bool:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast("None | Unset | bool", data)

        wait_transcoding = _parse_wait_transcoding(d.pop("waitTranscoding", UNSET))

        _state = d.pop("state", UNSET)
        state: Unset | VideoStateConstant
        if isinstance(_state, Unset):
            state = UNSET
        else:
            state = VideoStateConstant.from_dict(_state)

        def _parse_scheduled_update(
            data: object,
        ) -> Union["VideoScheduledUpdate", None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError
                scheduled_update_type_1 = VideoScheduledUpdate.from_dict(data)

                return scheduled_update_type_1
            except:  # noqa: E722
                pass
            return cast("VideoScheduledUpdate | None | Unset", data)

        scheduled_update = _parse_scheduled_update(d.pop("scheduledUpdate", UNSET))

        def _parse_blacklisted(data: object) -> None | Unset | bool:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast("None | Unset | bool", data)

        blacklisted = _parse_blacklisted(d.pop("blacklisted", UNSET))

        def _parse_blacklisted_reason(data: object) -> None | Unset | str:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast("None | Unset | str", data)

        blacklisted_reason = _parse_blacklisted_reason(
            d.pop("blacklistedReason", UNSET)
        )

        _account = d.pop("account", UNSET)
        account: Unset | AccountSummary
        if isinstance(_account, Unset):
            account = UNSET
        else:
            account = AccountSummary.from_dict(_account)

        _channel = d.pop("channel", UNSET)
        channel: Unset | VideoChannelSummary
        if isinstance(_channel, Unset):
            channel = UNSET
        else:
            channel = VideoChannelSummary.from_dict(_channel)

        def _parse_user_history(
            data: object,
        ) -> Union["VideoUserHistoryType0", None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError
                user_history_type_0 = VideoUserHistoryType0.from_dict(data)

                return user_history_type_0
            except:  # noqa: E722
                pass
            return cast("VideoUserHistoryType0 | None | Unset", data)

        user_history = _parse_user_history(d.pop("userHistory", UNSET))

        video = cls(
            id=id,
            uuid=uuid,
            short_uuid=short_uuid,
            is_live=is_live,
            live_schedules=live_schedules,
            created_at=created_at,
            published_at=published_at,
            updated_at=updated_at,
            originally_published_at=originally_published_at,
            category=category,
            licence=licence,
            language=language,
            privacy=privacy,
            truncated_description=truncated_description,
            duration=duration,
            aspect_ratio=aspect_ratio,
            is_local=is_local,
            name=name,
            thumbnail_path=thumbnail_path,
            preview_path=preview_path,
            embed_path=embed_path,
            views=views,
            likes=likes,
            dislikes=dislikes,
            comments=comments,
            nsfw=nsfw,
            nsfw_flags=nsfw_flags,
            nsfw_summary=nsfw_summary,
            wait_transcoding=wait_transcoding,
            state=state,
            scheduled_update=scheduled_update,
            blacklisted=blacklisted,
            blacklisted_reason=blacklisted_reason,
            account=account,
            channel=channel,
            user_history=user_history,
        )

        video.additional_properties = d
        return video

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
