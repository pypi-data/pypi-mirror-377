from collections.abc import Mapping
from typing import (
    Any,
    TypeVar,
)

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from typing_extensions import Self

from peertube.types import UNSET, Unset

T = TypeVar("T", bound="ServerConfigCustomTranscodingResolutions")


@_attrs_define
class ServerConfigCustomTranscodingResolutions:
    """Resolutions to transcode _new videos_ to

    Attributes:
        field_0p (Union[Unset, bool]):
        field_144p (Union[Unset, bool]):
        field_240p (Union[Unset, bool]):
        field_360p (Union[Unset, bool]):
        field_480p (Union[Unset, bool]):
        field_720p (Union[Unset, bool]):
        field_1080p (Union[Unset, bool]):
        field_1440p (Union[Unset, bool]):
        field_2160p (Union[Unset, bool]):
    """

    field_0p: Unset | bool = UNSET
    field_144p: Unset | bool = UNSET
    field_240p: Unset | bool = UNSET
    field_360p: Unset | bool = UNSET
    field_480p: Unset | bool = UNSET
    field_720p: Unset | bool = UNSET
    field_1080p: Unset | bool = UNSET
    field_1440p: Unset | bool = UNSET
    field_2160p: Unset | bool = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert instance to dictionary."""
        field_0p = self.field_0p

        field_144p = self.field_144p

        field_240p = self.field_240p

        field_360p = self.field_360p

        field_480p = self.field_480p

        field_720p = self.field_720p

        field_1080p = self.field_1080p

        field_1440p = self.field_1440p

        field_2160p = self.field_2160p

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if field_0p is not UNSET:
            field_dict["0p"] = field_0p
        if field_144p is not UNSET:
            field_dict["144p"] = field_144p
        if field_240p is not UNSET:
            field_dict["240p"] = field_240p
        if field_360p is not UNSET:
            field_dict["360p"] = field_360p
        if field_480p is not UNSET:
            field_dict["480p"] = field_480p
        if field_720p is not UNSET:
            field_dict["720p"] = field_720p
        if field_1080p is not UNSET:
            field_dict["1080p"] = field_1080p
        if field_1440p is not UNSET:
            field_dict["1440p"] = field_1440p
        if field_2160p is not UNSET:
            field_dict["2160p"] = field_2160p

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        """Create instance from dictionary."""
        d = dict(src_dict)
        field_0p = d.pop("0p", UNSET)

        field_144p = d.pop("144p", UNSET)

        field_240p = d.pop("240p", UNSET)

        field_360p = d.pop("360p", UNSET)

        field_480p = d.pop("480p", UNSET)

        field_720p = d.pop("720p", UNSET)

        field_1080p = d.pop("1080p", UNSET)

        field_1440p = d.pop("1440p", UNSET)

        field_2160p = d.pop("2160p", UNSET)

        server_config_custom_transcoding_resolutions = cls(
            field_0p=field_0p,
            field_144p=field_144p,
            field_240p=field_240p,
            field_360p=field_360p,
            field_480p=field_480p,
            field_720p=field_720p,
            field_1080p=field_1080p,
            field_1440p=field_1440p,
            field_2160p=field_2160p,
        )

        server_config_custom_transcoding_resolutions.additional_properties = d
        return server_config_custom_transcoding_resolutions

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
