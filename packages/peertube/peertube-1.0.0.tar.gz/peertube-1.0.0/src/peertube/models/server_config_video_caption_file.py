from collections.abc import Mapping
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

from peertube.types import UNSET, Unset

if TYPE_CHECKING:
    from peertube.models.server_config_video_caption_file_size import (
        ServerConfigVideoCaptionFileSize,
    )


T = TypeVar("T", bound="ServerConfigVideoCaptionFile")


@_attrs_define
class ServerConfigVideoCaptionFile:
    """Attributes:
    size (Union[Unset, ServerConfigVideoCaptionFileSize]):
    extensions (Union[Unset, list[str]]):
    """

    size: Union[Unset, "ServerConfigVideoCaptionFileSize"] = UNSET
    extensions: Unset | list[str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert instance to dictionary."""
        size: Unset | dict[str, Any] = UNSET
        if not isinstance(self.size, Unset):
            size = self.size.to_dict()

        extensions: Unset | list[str] = UNSET
        if not isinstance(self.extensions, Unset):
            extensions = self.extensions

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if size is not UNSET:
            field_dict["size"] = size
        if extensions is not UNSET:
            field_dict["extensions"] = extensions

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        """Create instance from dictionary."""
        from peertube.models.server_config_video_caption_file_size import (
            ServerConfigVideoCaptionFileSize,
        )

        d = dict(src_dict)
        _size = d.pop("size", UNSET)
        size: Unset | ServerConfigVideoCaptionFileSize
        if isinstance(_size, Unset):
            size = UNSET
        else:
            size = ServerConfigVideoCaptionFileSize.from_dict(_size)

        extensions = cast("list[str]", d.pop("extensions", UNSET))

        server_config_video_caption_file = cls(
            size=size,
            extensions=extensions,
        )

        server_config_video_caption_file.additional_properties = d
        return server_config_video_caption_file

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
