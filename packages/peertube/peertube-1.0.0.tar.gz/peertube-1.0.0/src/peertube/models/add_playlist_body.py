from collections.abc import Mapping
from io import BytesIO
from typing import (
    Any,
    TypeVar,
)

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from typing_extensions import Self

from peertube import types
from peertube.models.video_playlist_privacy_set import VideoPlaylistPrivacySet
from peertube.types import UNSET, File, FileTypes, Unset

T = TypeVar("T", bound="AddPlaylistBody")


@_attrs_define
class AddPlaylistBody:
    """Attributes:
    display_name (str): Video playlist display name
    thumbnailfile (Union[Unset, File]): Video playlist thumbnail file
    privacy (Union[Unset, VideoPlaylistPrivacySet]): Video playlist privacy policy (see [/video-
        playlists/privacies](#operation/getPlaylistPrivacyPolicies))
    description (Union[Unset, str]): Video playlist description
    video_channel_id (Union[Unset, int]):  Example: 42.
    """

    display_name: str
    thumbnailfile: Unset | File = UNSET
    privacy: Unset | VideoPlaylistPrivacySet = UNSET
    description: Unset | str = UNSET
    video_channel_id: Unset | int = UNSET
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
        """Convert to dictionary."""
        display_name = self.display_name

        thumbnailfile: Unset | FileTypes = UNSET
        if not isinstance(self.thumbnailfile, Unset):
            thumbnailfile = self.thumbnailfile.to_tuple()

        privacy: Unset | int = UNSET
        if not isinstance(self.privacy, Unset):
            privacy = self.privacy.value

        description = self.description

        video_channel_id = self.video_channel_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "displayName": display_name,
            }
        )
        if thumbnailfile is not UNSET:
            field_dict["thumbnailfile"] = thumbnailfile
        if privacy is not UNSET:
            field_dict["privacy"] = privacy
        if description is not UNSET:
            field_dict["description"] = description
        if video_channel_id is not UNSET:
            field_dict["videoChannelId"] = video_channel_id

        return field_dict

    def to_multipart(self) -> types.RequestFiles:
        """Convert to multipart form data."""
        files: types.RequestFiles = []

        files.append(
            ("displayName", (None, str(self.display_name).encode(), "text/plain"))
        )

        if not isinstance(self.thumbnailfile, Unset):
            files.append(("thumbnailfile", self.thumbnailfile.to_tuple()))

        if not isinstance(self.privacy, Unset):
            files.append(
                ("privacy", (None, str(self.privacy.value).encode(), "text/plain"))
            )

        if not isinstance(self.description, Unset):
            files.append(
                ("description", (None, str(self.description).encode(), "text/plain"))
            )

        if not isinstance(self.video_channel_id, Unset):
            files.append(
                (
                    "videoChannelId",
                    (None, str(self.video_channel_id).encode(), "text/plain"),
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
        """Create from dictionary."""
        d = dict(src_dict)
        display_name = d.pop("displayName")

        _thumbnailfile = d.pop("thumbnailfile", UNSET)
        thumbnailfile: Unset | File
        if isinstance(_thumbnailfile, Unset):
            thumbnailfile = UNSET
        else:
            thumbnailfile = File(payload=BytesIO(_thumbnailfile))

        _privacy = d.pop("privacy", UNSET)
        privacy: Unset | VideoPlaylistPrivacySet
        if isinstance(_privacy, Unset):
            privacy = UNSET
        else:
            privacy = VideoPlaylistPrivacySet(_privacy)

        description = d.pop("description", UNSET)

        video_channel_id = d.pop("videoChannelId", UNSET)

        add_playlist_body = cls(
            display_name=display_name,
            thumbnailfile=thumbnailfile,
            privacy=privacy,
            description=description,
            video_channel_id=video_channel_id,
        )

        add_playlist_body.additional_properties = d
        return add_playlist_body

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
        """Get additional keys."""
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
