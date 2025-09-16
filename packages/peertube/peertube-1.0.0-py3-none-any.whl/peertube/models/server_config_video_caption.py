from collections.abc import Mapping
from typing import (
    TYPE_CHECKING,
    Any,
    TypeVar,
    Union,
)

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from typing_extensions import Self

from peertube.types import UNSET, Unset

if TYPE_CHECKING:
    from peertube.models.server_config_video_caption_file import (
        ServerConfigVideoCaptionFile,
    )


T = TypeVar("T", bound="ServerConfigVideoCaption")


@_attrs_define
class ServerConfigVideoCaption:
    """Attributes:
    file (Union[Unset, ServerConfigVideoCaptionFile]):
    """

    file: Union[Unset, "ServerConfigVideoCaptionFile"] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert instance to dictionary."""
        file: Unset | dict[str, Any] = UNSET
        if not isinstance(self.file, Unset):
            file = self.file.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if file is not UNSET:
            field_dict["file"] = file

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        """Create instance from dictionary."""
        from peertube.models.server_config_video_caption_file import (
            ServerConfigVideoCaptionFile,
        )

        d = dict(src_dict)
        _file = d.pop("file", UNSET)
        file: Unset | ServerConfigVideoCaptionFile
        if isinstance(_file, Unset):
            file = UNSET
        else:
            file = ServerConfigVideoCaptionFile.from_dict(_file)

        server_config_video_caption = cls(
            file=file,
        )

        server_config_video_caption.additional_properties = d
        return server_config_video_caption

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
