from collections.abc import Mapping
from typing import (
    TYPE_CHECKING,
    Any,
    TypeVar,
)

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from typing_extensions import Self

from peertube.types import UNSET, Unset

if TYPE_CHECKING:
    from peertube.models.actor_image import ActorImage


T = TypeVar("T", bound="ActorInfo")


@_attrs_define
class ActorInfo:
    """Attributes:
    id (Union[Unset, int]):  Example: 42.
    name (Union[Unset, str]):
    display_name (Union[Unset, str]):
    host (Union[Unset, str]):
    avatars (Union[Unset, list['ActorImage']]):
    """

    id: Unset | int = UNSET
    name: Unset | str = UNSET
    display_name: Unset | str = UNSET
    host: Unset | str = UNSET
    avatars: Unset | list["ActorImage"] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert instance to dictionary."""
        id = self.id

        name = self.name

        display_name = self.display_name

        host = self.host

        avatars: Unset | list[dict[str, Any]] = UNSET
        if not isinstance(self.avatars, Unset):
            avatars = []
            for avatars_item_data in self.avatars:
                avatars_item = avatars_item_data.to_dict()
                avatars.append(avatars_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if id is not UNSET:
            field_dict["id"] = id
        if name is not UNSET:
            field_dict["name"] = name
        if display_name is not UNSET:
            field_dict["displayName"] = display_name
        if host is not UNSET:
            field_dict["host"] = host
        if avatars is not UNSET:
            field_dict["avatars"] = avatars

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        """Create instance from dictionary."""
        from peertube.models.actor_image import ActorImage

        d = dict(src_dict)
        id = d.pop("id", UNSET)

        name = d.pop("name", UNSET)

        display_name = d.pop("displayName", UNSET)

        host = d.pop("host", UNSET)

        avatars = []
        _avatars = d.pop("avatars", UNSET)
        for avatars_item_data in _avatars or []:
            avatars_item = ActorImage.from_dict(avatars_item_data)

            avatars.append(avatars_item)

        actor_info = cls(
            id=id,
            name=name,
            display_name=display_name,
            host=host,
            avatars=avatars,
        )

        actor_info.additional_properties = d
        return actor_info

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
