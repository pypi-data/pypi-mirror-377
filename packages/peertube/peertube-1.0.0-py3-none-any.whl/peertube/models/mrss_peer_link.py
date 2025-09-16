from collections.abc import Mapping
from typing import (
    Any,
    TypeVar,
)

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from typing_extensions import Self

from peertube.models.mrss_peer_link_type import MRSSPeerLinkType
from peertube.types import UNSET, Unset

T = TypeVar("T", bound="MRSSPeerLink")


@_attrs_define
class MRSSPeerLink:
    """Attributes:
    href (Union[Unset, str]):
    type_ (Union[Unset, MRSSPeerLinkType]):
    """

    href: Unset | str = UNSET
    type_: Unset | MRSSPeerLinkType = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        href = self.href

        type_: Unset | str = UNSET
        if not isinstance(self.type_, Unset):
            type_ = self.type_.value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if href is not UNSET:
            field_dict["href"] = href
        if type_ is not UNSET:
            field_dict["type"] = type_

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        """Create from dictionary."""
        d = dict(src_dict)
        href = d.pop("href", UNSET)

        _type_ = d.pop("type", UNSET)
        type_: Unset | MRSSPeerLinkType
        if isinstance(_type_, Unset):
            type_ = UNSET
        else:
            type_ = MRSSPeerLinkType(_type_)

        mrss_peer_link = cls(
            href=href,
            type_=type_,
        )

        mrss_peer_link.additional_properties = d
        return mrss_peer_link

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
