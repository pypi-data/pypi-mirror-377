from collections.abc import Mapping
from typing import (
    Any,
    TypeVar,
)

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from typing_extensions import Self

from peertube.models.videos_for_xml_item_enclosure_type import (
    VideosForXMLItemEnclosureType,
)
from peertube.types import UNSET, Unset

T = TypeVar("T", bound="VideosForXMLItemEnclosure")


@_attrs_define
class VideosForXMLItemEnclosure:
    """main streamable file for the video

    Attributes:
        url (Union[Unset, str]):
        type_ (Union[Unset, VideosForXMLItemEnclosureType]):
        length (Union[Unset, int]):
    """

    url: Unset | str = UNSET
    type_: Unset | VideosForXMLItemEnclosureType = UNSET
    length: Unset | int = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert instance to dictionary."""
        url = self.url

        type_: Unset | str = UNSET
        if not isinstance(self.type_, Unset):
            type_ = self.type_.value

        length = self.length

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if url is not UNSET:
            field_dict["url"] = url
        if type_ is not UNSET:
            field_dict["type"] = type_
        if length is not UNSET:
            field_dict["length"] = length

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        """Create instance from dictionary."""
        d = dict(src_dict)
        url = d.pop("url", UNSET)

        _type_ = d.pop("type", UNSET)
        type_: Unset | VideosForXMLItemEnclosureType
        if isinstance(_type_, Unset):
            type_ = UNSET
        else:
            type_ = VideosForXMLItemEnclosureType(_type_)

        length = d.pop("length", UNSET)

        videos_for_xml_item_enclosure = cls(
            url=url,
            type_=type_,
            length=length,
        )

        videos_for_xml_item_enclosure.additional_properties = d
        return videos_for_xml_item_enclosure

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
