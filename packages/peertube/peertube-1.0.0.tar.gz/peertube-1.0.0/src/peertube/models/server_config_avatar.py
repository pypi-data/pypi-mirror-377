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
    from peertube.models.server_config_avatar_file import ServerConfigAvatarFile


T = TypeVar("T", bound="ServerConfigAvatar")


@_attrs_define
class ServerConfigAvatar:
    """Attributes:
    file (Union[Unset, ServerConfigAvatarFile]):
    extensions (Union[Unset, list[str]]):
    """

    file: Union[Unset, "ServerConfigAvatarFile"] = UNSET
    extensions: Unset | list[str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        file: Unset | dict[str, Any] = UNSET
        if not isinstance(self.file, Unset):
            file = self.file.to_dict()

        extensions: Unset | list[str] = UNSET
        if not isinstance(self.extensions, Unset):
            extensions = self.extensions

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if file is not UNSET:
            field_dict["file"] = file
        if extensions is not UNSET:
            field_dict["extensions"] = extensions

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        """Create from dictionary."""
        from peertube.models.server_config_avatar_file import ServerConfigAvatarFile

        d = dict(src_dict)
        _file = d.pop("file", UNSET)
        file: Unset | ServerConfigAvatarFile
        if isinstance(_file, Unset):
            file = UNSET
        else:
            file = ServerConfigAvatarFile.from_dict(_file)

        extensions = cast("list[str]", d.pop("extensions", UNSET))

        server_config_avatar = cls(
            file=file,
            extensions=extensions,
        )

        server_config_avatar.additional_properties = d
        return server_config_avatar

    @property
    def additional_keys(self) -> list[str]:
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
