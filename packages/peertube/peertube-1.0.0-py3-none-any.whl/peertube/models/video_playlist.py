import datetime
from collections.abc import Mapping
from typing import (
    TYPE_CHECKING,
    Any,
    TypeVar,
    Union,
)
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse
from typing_extensions import Self

from peertube.types import UNSET, Unset

if TYPE_CHECKING:
    from peertube.models.account_summary import AccountSummary
    from peertube.models.video_channel_summary import VideoChannelSummary
    from peertube.models.video_playlist_privacy_constant import (
        VideoPlaylistPrivacyConstant,
    )
    from peertube.models.video_playlist_type_constant import VideoPlaylistTypeConstant


T = TypeVar("T", bound="VideoPlaylist")


@_attrs_define
class VideoPlaylist:
    """Attributes:
    id (Union[Unset, int]):  Example: 42.
    uuid (Union[Unset, UUID]):  Example: 9c9de5e8-0a1e-484a-b099-e80766180a6d.
    short_uuid (Union[Unset, str]): translation of a uuid v4 with a bigger alphabet to have a shorter uuid Example:
        2y84q2MQUMWPbiEcxNXMgC.
    created_at (Union[Unset, datetime.datetime]):
    updated_at (Union[Unset, datetime.datetime]):
    description (Union[Unset, str]):
    display_name (Union[Unset, str]):
    is_local (Union[Unset, bool]):
    video_length (Union[Unset, int]):
    thumbnail_path (Union[Unset, str]):
    privacy (Union[Unset, VideoPlaylistPrivacyConstant]):
    type_ (Union[Unset, VideoPlaylistTypeConstant]):
    owner_account (Union[Unset, AccountSummary]):
    video_channel (Union[Unset, VideoChannelSummary]):
    video_channel_position (Union[Unset, int]): Position of the playlist in the channel
    """

    id: Unset | int = UNSET
    uuid: Unset | UUID = UNSET
    short_uuid: Unset | str = UNSET
    created_at: Unset | datetime.datetime = UNSET
    updated_at: Unset | datetime.datetime = UNSET
    description: Unset | str = UNSET
    display_name: Unset | str = UNSET
    is_local: Unset | bool = UNSET
    video_length: Unset | int = UNSET
    thumbnail_path: Unset | str = UNSET
    privacy: Union[Unset, "VideoPlaylistPrivacyConstant"] = UNSET
    type_: Union[Unset, "VideoPlaylistTypeConstant"] = UNSET
    owner_account: Union[Unset, "AccountSummary"] = UNSET
    video_channel: Union[Unset, "VideoChannelSummary"] = UNSET
    video_channel_position: Unset | int = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert instance to dictionary."""
        id = self.id

        uuid: Unset | str = UNSET
        if not isinstance(self.uuid, Unset):
            uuid = str(self.uuid)

        short_uuid = self.short_uuid

        created_at: Unset | str = UNSET
        if not isinstance(self.created_at, Unset):
            created_at = self.created_at.isoformat()

        updated_at: Unset | str = UNSET
        if not isinstance(self.updated_at, Unset):
            updated_at = self.updated_at.isoformat()

        description = self.description

        display_name = self.display_name

        is_local = self.is_local

        video_length = self.video_length

        thumbnail_path = self.thumbnail_path

        privacy: Unset | dict[str, Any] = UNSET
        if not isinstance(self.privacy, Unset):
            privacy = self.privacy.to_dict()

        type_: Unset | dict[str, Any] = UNSET
        if not isinstance(self.type_, Unset):
            type_ = self.type_.to_dict()

        owner_account: Unset | dict[str, Any] = UNSET
        if not isinstance(self.owner_account, Unset):
            owner_account = self.owner_account.to_dict()

        video_channel: Unset | dict[str, Any] = UNSET
        if not isinstance(self.video_channel, Unset):
            video_channel = self.video_channel.to_dict()

        video_channel_position = self.video_channel_position

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if id is not UNSET:
            field_dict["id"] = id
        if uuid is not UNSET:
            field_dict["uuid"] = uuid
        if short_uuid is not UNSET:
            field_dict["shortUUID"] = short_uuid
        if created_at is not UNSET:
            field_dict["createdAt"] = created_at
        if updated_at is not UNSET:
            field_dict["updatedAt"] = updated_at
        if description is not UNSET:
            field_dict["description"] = description
        if display_name is not UNSET:
            field_dict["displayName"] = display_name
        if is_local is not UNSET:
            field_dict["isLocal"] = is_local
        if video_length is not UNSET:
            field_dict["videoLength"] = video_length
        if thumbnail_path is not UNSET:
            field_dict["thumbnailPath"] = thumbnail_path
        if privacy is not UNSET:
            field_dict["privacy"] = privacy
        if type_ is not UNSET:
            field_dict["type"] = type_
        if owner_account is not UNSET:
            field_dict["ownerAccount"] = owner_account
        if video_channel is not UNSET:
            field_dict["videoChannel"] = video_channel
        if video_channel_position is not UNSET:
            field_dict["videoChannelPosition"] = video_channel_position

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        """Create instance from dictionary."""
        from peertube.models.account_summary import AccountSummary
        from peertube.models.video_channel_summary import VideoChannelSummary
        from peertube.models.video_playlist_privacy_constant import (
            VideoPlaylistPrivacyConstant,
        )
        from peertube.models.video_playlist_type_constant import (
            VideoPlaylistTypeConstant,
        )

        d = dict(src_dict)
        id = d.pop("id", UNSET)

        _uuid = d.pop("uuid", UNSET)
        uuid: Unset | UUID
        if isinstance(_uuid, Unset):
            uuid = UNSET
        else:
            uuid = UUID(_uuid)

        short_uuid = d.pop("shortUUID", UNSET)

        _created_at = d.pop("createdAt", UNSET)
        created_at: Unset | datetime.datetime
        if isinstance(_created_at, Unset):
            created_at = UNSET
        else:
            created_at = isoparse(_created_at)

        _updated_at = d.pop("updatedAt", UNSET)
        updated_at: Unset | datetime.datetime
        if isinstance(_updated_at, Unset):
            updated_at = UNSET
        else:
            updated_at = isoparse(_updated_at)

        description = d.pop("description", UNSET)

        display_name = d.pop("displayName", UNSET)

        is_local = d.pop("isLocal", UNSET)

        video_length = d.pop("videoLength", UNSET)

        thumbnail_path = d.pop("thumbnailPath", UNSET)

        _privacy = d.pop("privacy", UNSET)
        privacy: Unset | VideoPlaylistPrivacyConstant
        if isinstance(_privacy, Unset):
            privacy = UNSET
        else:
            privacy = VideoPlaylistPrivacyConstant.from_dict(_privacy)

        _type_ = d.pop("type", UNSET)
        type_: Unset | VideoPlaylistTypeConstant
        if isinstance(_type_, Unset):
            type_ = UNSET
        else:
            type_ = VideoPlaylistTypeConstant.from_dict(_type_)

        _owner_account = d.pop("ownerAccount", UNSET)
        owner_account: Unset | AccountSummary
        if isinstance(_owner_account, Unset):
            owner_account = UNSET
        else:
            owner_account = AccountSummary.from_dict(_owner_account)

        _video_channel = d.pop("videoChannel", UNSET)
        video_channel: Unset | VideoChannelSummary
        if isinstance(_video_channel, Unset):
            video_channel = UNSET
        else:
            video_channel = VideoChannelSummary.from_dict(_video_channel)

        video_channel_position = d.pop("videoChannelPosition", UNSET)

        video_playlist = cls(
            id=id,
            uuid=uuid,
            short_uuid=short_uuid,
            created_at=created_at,
            updated_at=updated_at,
            description=description,
            display_name=display_name,
            is_local=is_local,
            video_length=video_length,
            thumbnail_path=thumbnail_path,
            privacy=privacy,
            type_=type_,
            owner_account=owner_account,
            video_channel=video_channel,
            video_channel_position=video_channel_position,
        )

        video_playlist.additional_properties = d
        return video_playlist

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
