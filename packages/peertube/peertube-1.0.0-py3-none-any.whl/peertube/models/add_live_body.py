import json
from collections.abc import Mapping
from io import BytesIO
from typing import (
    TYPE_CHECKING,
    Any,
    TypeVar,
    Union,
    cast,
)

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from typing_extensions import Self

from peertube import types
from peertube.models.live_video_latency_mode import LiveVideoLatencyMode
from peertube.models.nsfw_flag import NSFWFlag
from peertube.models.video_comments_policy_set import VideoCommentsPolicySet
from peertube.models.video_privacy_set import VideoPrivacySet
from peertube.types import UNSET, File, FileTypes, Unset

if TYPE_CHECKING:
    from peertube.models.live_schedule import LiveSchedule
    from peertube.models.live_video_replay_settings import LiveVideoReplaySettings


T = TypeVar("T", bound="AddLiveBody")


@_attrs_define
class AddLiveBody:
    """Attributes:
    channel_id (int): Channel id that will contain this live video
    name (str): Live video/replay name
    save_replay (Union[Unset, bool]):
    replay_settings (Union[Unset, LiveVideoReplaySettings]):
    permanent_live (Union[Unset, bool]): User can stream multiple times in a permanent live
    latency_mode (Union[Unset, LiveVideoLatencyMode]): The live latency mode (Default = `1`, High latency = `2`,
        Small Latency = `3`)
    thumbnailfile (Union[Unset, File]): Live video/replay thumbnail file
    previewfile (Union[Unset, File]): Live video/replay preview file
    privacy (Union[Unset, VideoPrivacySet]): privacy id of the video (see
        [/videos/privacies](#operation/getVideoPrivacyPolicies))
    category (Union[Unset, int]): category id of the video (see [/videos/categories](#operation/getCategories))
        Example: 15.
    licence (Union[Unset, int]): licence id of the video (see [/videos/licences](#operation/getLicences)) Example:
        2.
    language (Union[Unset, str]): language id of the video (see [/videos/languages](#operation/getLanguages))
        Example: en.
    description (Union[Unset, str]): Live video/replay description
    support (Union[Unset, str]): A text tell the audience how to support the creator Example: Please support our
        work on https://soutenir.framasoft.org/en/ <3.
    nsfw (Union[Unset, bool]): Whether or not this live video/replay contains sensitive content
    nsfw_summary (Union[Unset, Any]): More information about the sensitive content of the video
    nsfw_flags (Union[Unset, NSFWFlag]):
        NSFW flags (can be combined using bitwise or operator)
        - `0` NONE
        - `1` VIOLENT
        - `2` EXPLICIT_SEX
    tags (Union[Unset, list[str]]): Live video/replay tags (maximum 5 tags each between 2 and 30 characters)
    comments_enabled (Union[Unset, bool]): Deprecated in 6.2, use commentsPolicy instead
    comments_policy (Union[Unset, VideoCommentsPolicySet]): Comments policy of the video (Enabled = `1`, Disabled =
        `2`, Requires Approval = `3`)
    download_enabled (Union[Unset, bool]): Enable or disable downloading for the replay of this live video
    schedules (Union[Unset, list['LiveSchedule']]):
    """

    channel_id: int
    name: str
    save_replay: Unset | bool = UNSET
    replay_settings: Union[Unset, "LiveVideoReplaySettings"] = UNSET
    permanent_live: Unset | bool = UNSET
    latency_mode: Unset | LiveVideoLatencyMode = UNSET
    thumbnailfile: Unset | File = UNSET
    previewfile: Unset | File = UNSET
    privacy: Unset | VideoPrivacySet = UNSET
    category: Unset | int = UNSET
    licence: Unset | int = UNSET
    language: Unset | str = UNSET
    description: Unset | str = UNSET
    support: Unset | str = UNSET
    nsfw: Unset | bool = UNSET
    nsfw_summary: Unset | Any = UNSET
    nsfw_flags: Unset | NSFWFlag = UNSET
    tags: Unset | list[str] = UNSET
    comments_enabled: Unset | bool = UNSET
    comments_policy: Unset | VideoCommentsPolicySet = UNSET
    download_enabled: Unset | bool = UNSET
    schedules: Unset | list["LiveSchedule"] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert instance to dictionary."""
        """Convert instance to dictionary."""
        """Convert instance to dictionary."""
        """Convert instance to dictionary."""
        """Convert instance to dictionary."""
        """Convert instance to dictionary."""
        """Convert instance to dictionary."""
        """Convert instance to dictionary."""
        """Convert instance to dictionary."""
        """Convert instance to dictionary."""
        """Convert instance to dictionary."""
        """Convert instance to dictionary."""
        """Convert instance to dictionary."""
        """Convert instance to dictionary."""
        """Convert instance to dictionary."""
        """Convert instance to dictionary."""
        """Convert instance to dictionary."""
        """Convert instance to dictionary."""
        """Convert instance to dictionary."""
        """Convert instance to dictionary."""
        """Convert instance to dictionary."""
        channel_id = self.channel_id

        name = self.name

        save_replay = self.save_replay

        replay_settings: Unset | dict[str, Any] = UNSET
        if not isinstance(self.replay_settings, Unset):
            replay_settings = self.replay_settings.to_dict()

        permanent_live = self.permanent_live

        latency_mode: Unset | int = UNSET
        if not isinstance(self.latency_mode, Unset):
            latency_mode = self.latency_mode.value

        thumbnailfile: Unset | FileTypes = UNSET
        if not isinstance(self.thumbnailfile, Unset):
            thumbnailfile = self.thumbnailfile.to_tuple()

        previewfile: Unset | FileTypes = UNSET
        if not isinstance(self.previewfile, Unset):
            previewfile = self.previewfile.to_tuple()

        privacy: Unset | int = UNSET
        if not isinstance(self.privacy, Unset):
            privacy = self.privacy.value

        category = self.category

        licence = self.licence

        language = self.language

        description = self.description

        support = self.support

        nsfw = self.nsfw

        nsfw_summary = self.nsfw_summary

        nsfw_flags: Unset | int = UNSET
        if not isinstance(self.nsfw_flags, Unset):
            nsfw_flags = self.nsfw_flags.value

        tags: Unset | list[str] = UNSET
        if not isinstance(self.tags, Unset):
            tags = self.tags

        comments_enabled = self.comments_enabled

        comments_policy: Unset | int = UNSET
        if not isinstance(self.comments_policy, Unset):
            comments_policy = self.comments_policy.value

        download_enabled = self.download_enabled

        schedules: Unset | list[dict[str, Any]] = UNSET
        if not isinstance(self.schedules, Unset):
            schedules = []
            for schedules_item_data in self.schedules:
                schedules_item = schedules_item_data.to_dict()
                schedules.append(schedules_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "channelId": channel_id,
                "name": name,
            }
        )
        if save_replay is not UNSET:
            field_dict["saveReplay"] = save_replay
        if replay_settings is not UNSET:
            field_dict["replaySettings"] = replay_settings
        if permanent_live is not UNSET:
            field_dict["permanentLive"] = permanent_live
        if latency_mode is not UNSET:
            field_dict["latencyMode"] = latency_mode
        if thumbnailfile is not UNSET:
            field_dict["thumbnailfile"] = thumbnailfile
        if previewfile is not UNSET:
            field_dict["previewfile"] = previewfile
        if privacy is not UNSET:
            field_dict["privacy"] = privacy
        if category is not UNSET:
            field_dict["category"] = category
        if licence is not UNSET:
            field_dict["licence"] = licence
        if language is not UNSET:
            field_dict["language"] = language
        if description is not UNSET:
            field_dict["description"] = description
        if support is not UNSET:
            field_dict["support"] = support
        if nsfw is not UNSET:
            field_dict["nsfw"] = nsfw
        if nsfw_summary is not UNSET:
            field_dict["nsfwSummary"] = nsfw_summary
        if nsfw_flags is not UNSET:
            field_dict["nsfwFlags"] = nsfw_flags
        if tags is not UNSET:
            field_dict["tags"] = tags
        if comments_enabled is not UNSET:
            field_dict["commentsEnabled"] = comments_enabled
        if comments_policy is not UNSET:
            field_dict["commentsPolicy"] = comments_policy
        if download_enabled is not UNSET:
            field_dict["downloadEnabled"] = download_enabled
        if schedules is not UNSET:
            field_dict["schedules"] = schedules

        return field_dict

    def to_multipart(self) -> types.RequestFiles:
        """Convert to multipart form data."""
        files: types.RequestFiles = []

        files.append(("channelId", (None, str(self.channel_id).encode(), "text/plain")))

        files.append(("name", (None, str(self.name).encode(), "text/plain")))

        if not isinstance(self.save_replay, Unset):
            files.append(
                ("saveReplay", (None, str(self.save_replay).encode(), "text/plain"))
            )

        if not isinstance(self.replay_settings, Unset):
            files.append(
                (
                    "replaySettings",
                    (
                        None,
                        json.dumps(self.replay_settings.to_dict()).encode(),
                        "application/json",
                    ),
                )
            )

        if not isinstance(self.permanent_live, Unset):
            files.append(
                (
                    "permanentLive",
                    (None, str(self.permanent_live).encode(), "text/plain"),
                )
            )

        if not isinstance(self.latency_mode, Unset):
            files.append(
                (
                    "latencyMode",
                    (None, str(self.latency_mode.value).encode(), "text/plain"),
                )
            )

        if not isinstance(self.thumbnailfile, Unset):
            files.append(("thumbnailfile", self.thumbnailfile.to_tuple()))

        if not isinstance(self.previewfile, Unset):
            files.append(("previewfile", self.previewfile.to_tuple()))

        if not isinstance(self.privacy, Unset):
            files.append(
                ("privacy", (None, str(self.privacy.value).encode(), "text/plain"))
            )

        if not isinstance(self.category, Unset):
            files.append(
                ("category", (None, str(self.category).encode(), "text/plain"))
            )

        if not isinstance(self.licence, Unset):
            files.append(("licence", (None, str(self.licence).encode(), "text/plain")))

        if not isinstance(self.language, Unset):
            files.append(
                ("language", (None, str(self.language).encode(), "text/plain"))
            )

        if not isinstance(self.description, Unset):
            files.append(
                ("description", (None, str(self.description).encode(), "text/plain"))
            )

        if not isinstance(self.support, Unset):
            files.append(("support", (None, str(self.support).encode(), "text/plain")))

        if not isinstance(self.nsfw, Unset):
            files.append(("nsfw", (None, str(self.nsfw).encode(), "text/plain")))

        if not isinstance(self.nsfw_summary, Unset):
            files.append(
                ("nsfwSummary", (None, str(self.nsfw_summary).encode(), "text/plain"))
            )

        if not isinstance(self.nsfw_flags, Unset):
            files.append(
                ("nsfwFlags", (None, str(self.nsfw_flags.value).encode(), "text/plain"))
            )

        if not isinstance(self.tags, Unset):
            for tags_item_element in self.tags:
                files.append(
                    ("tags", (None, str(tags_item_element).encode(), "text/plain"))
                )

        if not isinstance(self.comments_enabled, Unset):
            files.append(
                (
                    "commentsEnabled",
                    (None, str(self.comments_enabled).encode(), "text/plain"),
                )
            )

        if not isinstance(self.comments_policy, Unset):
            files.append(
                (
                    "commentsPolicy",
                    (None, str(self.comments_policy.value).encode(), "text/plain"),
                )
            )

        if not isinstance(self.download_enabled, Unset):
            files.append(
                (
                    "downloadEnabled",
                    (None, str(self.download_enabled).encode(), "text/plain"),
                )
            )

        if not isinstance(self.schedules, Unset):
            for schedules_item_element in self.schedules:
                files.append(
                    (
                        "schedules",
                        (
                            None,
                            json.dumps(schedules_item_element.to_dict()).encode(),
                            "application/json",
                        ),
                    )
                )

        for prop_name, prop in self.additional_properties.items():
            files.append((prop_name, (None, str(prop).encode(), "text/plain")))

        return files

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        """Create instance from dictionary."""
        """Create instance from dictionary."""
        """Create instance from dictionary."""
        """Create instance from dictionary."""
        """Create instance from dictionary."""
        """Create instance from dictionary."""
        """Create instance from dictionary."""
        """Create instance from dictionary."""
        """Create instance from dictionary."""
        """Create instance from dictionary."""
        """Create instance from dictionary."""
        """Create instance from dictionary."""
        """Create instance from dictionary."""
        """Create instance from dictionary."""
        """Create instance from dictionary."""
        """Create instance from dictionary."""
        """Create instance from dictionary."""
        """Create instance from dictionary."""
        """Create instance from dictionary."""
        """Create instance from dictionary."""
        """Create instance from dictionary."""
        from peertube.models.live_schedule import LiveSchedule
        from peertube.models.live_video_replay_settings import LiveVideoReplaySettings

        d = dict(src_dict)
        channel_id = d.pop("channelId")

        name = d.pop("name")

        save_replay = d.pop("saveReplay", UNSET)

        _replay_settings = d.pop("replaySettings", UNSET)
        replay_settings: Unset | LiveVideoReplaySettings
        if isinstance(_replay_settings, Unset):
            replay_settings = UNSET
        else:
            replay_settings = LiveVideoReplaySettings.from_dict(_replay_settings)

        permanent_live = d.pop("permanentLive", UNSET)

        _latency_mode = d.pop("latencyMode", UNSET)
        latency_mode: Unset | LiveVideoLatencyMode
        if isinstance(_latency_mode, Unset):
            latency_mode = UNSET
        else:
            latency_mode = LiveVideoLatencyMode(_latency_mode)

        _thumbnailfile = d.pop("thumbnailfile", UNSET)
        thumbnailfile: Unset | File
        if isinstance(_thumbnailfile, Unset):
            thumbnailfile = UNSET
        else:
            thumbnailfile = File(payload=BytesIO(_thumbnailfile))

        _previewfile = d.pop("previewfile", UNSET)
        previewfile: Unset | File
        if isinstance(_previewfile, Unset):
            previewfile = UNSET
        else:
            previewfile = File(payload=BytesIO(_previewfile))

        _privacy = d.pop("privacy", UNSET)
        privacy: Unset | VideoPrivacySet
        if isinstance(_privacy, Unset):
            privacy = UNSET
        else:
            privacy = VideoPrivacySet(_privacy)

        category = d.pop("category", UNSET)

        licence = d.pop("licence", UNSET)

        language = d.pop("language", UNSET)

        description = d.pop("description", UNSET)

        support = d.pop("support", UNSET)

        nsfw = d.pop("nsfw", UNSET)

        nsfw_summary = d.pop("nsfwSummary", UNSET)

        _nsfw_flags = d.pop("nsfwFlags", UNSET)
        nsfw_flags: Unset | NSFWFlag
        if isinstance(_nsfw_flags, Unset):
            nsfw_flags = UNSET
        else:
            nsfw_flags = NSFWFlag(_nsfw_flags)

        tags = cast("list[str]", d.pop("tags", UNSET))

        comments_enabled = d.pop("commentsEnabled", UNSET)

        _comments_policy = d.pop("commentsPolicy", UNSET)
        comments_policy: Unset | VideoCommentsPolicySet
        if isinstance(_comments_policy, Unset):
            comments_policy = UNSET
        else:
            comments_policy = VideoCommentsPolicySet(_comments_policy)

        download_enabled = d.pop("downloadEnabled", UNSET)

        schedules = []
        _schedules = d.pop("schedules", UNSET)
        for schedules_item_data in _schedules or []:
            schedules_item = LiveSchedule.from_dict(schedules_item_data)

            schedules.append(schedules_item)

        add_live_body = cls(
            channel_id=channel_id,
            name=name,
            save_replay=save_replay,
            replay_settings=replay_settings,
            permanent_live=permanent_live,
            latency_mode=latency_mode,
            thumbnailfile=thumbnailfile,
            previewfile=previewfile,
            privacy=privacy,
            category=category,
            licence=licence,
            language=language,
            description=description,
            support=support,
            nsfw=nsfw,
            nsfw_summary=nsfw_summary,
            nsfw_flags=nsfw_flags,
            tags=tags,
            comments_enabled=comments_enabled,
            comments_policy=comments_policy,
            download_enabled=download_enabled,
            schedules=schedules,
        )

        add_live_body.additional_properties = d
        return add_live_body

    @property
    def additional_keys(self) -> list[str]:
        """Get additional property keys."""
        """Get additional property keys."""
        """Get additional property keys."""
        """Get additional property keys."""
        """Get additional property keys."""
        """Get additional property keys."""
        """Get additional property keys."""
        """Get additional property keys."""
        """Get additional property keys."""
        """Get additional property keys."""
        """Get additional property keys."""
        """Get additional property keys."""
        """Get additional property keys."""
        """Get additional property keys."""
        """Get additional property keys."""
        """Get additional property keys."""
        """Get additional property keys."""
        """Get additional property keys."""
        """Get additional property keys."""
        """Get additional property keys."""
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
