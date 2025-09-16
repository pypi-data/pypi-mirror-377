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
    from peertube.models.server_config_about_instance import ServerConfigAboutInstance


T = TypeVar("T", bound="ServerConfigAbout")


@_attrs_define
class ServerConfigAbout:
    """Attributes:
    instance (Union[Unset, ServerConfigAboutInstance]):
    """

    instance: Union[Unset, "ServerConfigAboutInstance"] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert instance to dictionary."""
        instance: Unset | dict[str, Any] = UNSET
        if not isinstance(self.instance, Unset):
            instance = self.instance.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if instance is not UNSET:
            field_dict["instance"] = instance

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        """Create instance from dictionary."""
        from peertube.models.server_config_about_instance import (
            ServerConfigAboutInstance,
        )

        d = dict(src_dict)
        _instance = d.pop("instance", UNSET)
        instance: Unset | ServerConfigAboutInstance
        if isinstance(_instance, Unset):
            instance = UNSET
        else:
            instance = ServerConfigAboutInstance.from_dict(_instance)

        server_config_about = cls(
            instance=instance,
        )

        server_config_about.additional_properties = d
        return server_config_about

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
