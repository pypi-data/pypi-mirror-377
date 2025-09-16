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
    from peertube.models.server_config_avatar_file_size import (
        ServerConfigAvatarFileSize,
    )


T = TypeVar("T", bound="ServerConfigAvatarFile")


@_attrs_define
class ServerConfigAvatarFile:
    """Attributes:
    size (Union[Unset, ServerConfigAvatarFileSize]):
    """

    size: Union[Unset, "ServerConfigAvatarFileSize"] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert instance to dictionary."""
        size: Unset | dict[str, Any] = UNSET
        if not isinstance(self.size, Unset):
            size = self.size.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if size is not UNSET:
            field_dict["size"] = size

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        """Create instance from dictionary."""
        from peertube.models.server_config_avatar_file_size import (
            ServerConfigAvatarFileSize,
        )

        d = dict(src_dict)
        _size = d.pop("size", UNSET)
        size: Unset | ServerConfigAvatarFileSize
        if isinstance(_size, Unset):
            size = UNSET
        else:
            size = ServerConfigAvatarFileSize.from_dict(_size)

        server_config_avatar_file = cls(
            size=size,
        )

        server_config_avatar_file.additional_properties = d
        return server_config_avatar_file

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
