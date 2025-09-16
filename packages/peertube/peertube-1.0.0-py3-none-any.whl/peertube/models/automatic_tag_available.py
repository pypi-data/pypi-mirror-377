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
    from peertube.models.automatic_tag_available_available_item import (
        AutomaticTagAvailableAvailableItem,
    )


T = TypeVar("T", bound="AutomaticTagAvailable")


@_attrs_define
class AutomaticTagAvailable:
    """Attributes:
    available (Union[Unset, list['AutomaticTagAvailableAvailableItem']]): Available auto tags that can be used to
        filter objects or set a comment in review state
    """

    available: Unset | list["AutomaticTagAvailableAvailableItem"] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        available: Unset | list[dict[str, Any]] = UNSET
        if not isinstance(self.available, Unset):
            available = []
            for available_item_data in self.available:
                available_item = available_item_data.to_dict()
                available.append(available_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if available is not UNSET:
            field_dict["available"] = available

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        """Create from dictionary."""
        from peertube.models.automatic_tag_available_available_item import (
            AutomaticTagAvailableAvailableItem,
        )

        d = dict(src_dict)
        available = []
        _available = d.pop("available", UNSET)
        for available_item_data in _available or []:
            available_item = AutomaticTagAvailableAvailableItem.from_dict(
                available_item_data
            )

            available.append(available_item)

        automatic_tag_available = cls(
            available=available,
        )

        automatic_tag_available.additional_properties = d
        return automatic_tag_available

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
