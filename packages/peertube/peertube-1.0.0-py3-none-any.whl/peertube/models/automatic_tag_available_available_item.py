from collections.abc import Mapping
from typing import (
    Any,
    TypeVar,
)

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from typing_extensions import Self

from peertube.models.automatic_tag_available_available_item_type import (
    AutomaticTagAvailableAvailableItemType,
)
from peertube.types import UNSET, Unset

T = TypeVar("T", bound="AutomaticTagAvailableAvailableItem")


@_attrs_define
class AutomaticTagAvailableAvailableItem:
    """Attributes:
    name (Union[Unset, str]): tag name
    type_ (Union[Unset, AutomaticTagAvailableAvailableItemType]):
    """

    name: Unset | str = UNSET
    type_: Unset | AutomaticTagAvailableAvailableItemType = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert instance to dictionary."""
        name = self.name

        type_: Unset | str = UNSET
        if not isinstance(self.type_, Unset):
            type_ = self.type_.value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if name is not UNSET:
            field_dict["name"] = name
        if type_ is not UNSET:
            field_dict["type"] = type_

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        """Create instance from dictionary."""
        d = dict(src_dict)
        name = d.pop("name", UNSET)

        _type_ = d.pop("type", UNSET)
        type_: Unset | AutomaticTagAvailableAvailableItemType
        if isinstance(_type_, Unset):
            type_ = UNSET
        else:
            type_ = AutomaticTagAvailableAvailableItemType(_type_)

        automatic_tag_available_available_item = cls(
            name=name,
            type_=type_,
        )

        automatic_tag_available_available_item.additional_properties = d
        return automatic_tag_available_available_item

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
