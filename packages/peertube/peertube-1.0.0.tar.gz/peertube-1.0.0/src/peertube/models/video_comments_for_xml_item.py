import datetime
from collections.abc import Mapping
from typing import (
    Any,
    TypeVar,
)

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse
from typing_extensions import Self

from peertube.types import UNSET, Unset

T = TypeVar("T", bound="VideoCommentsForXMLItem")


@_attrs_define
class VideoCommentsForXMLItem:
    """Attributes:
    link (Union[Unset, str]):
    guid (Union[Unset, str]):
    pub_date (Union[Unset, datetime.datetime]):
    contentencoded (Union[Unset, str]):
    dccreator (Union[Unset, str]):
    """

    link: Unset | str = UNSET
    guid: Unset | str = UNSET
    pub_date: Unset | datetime.datetime = UNSET
    contentencoded: Unset | str = UNSET
    dccreator: Unset | str = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert instance to dictionary."""
        link = self.link

        guid = self.guid

        pub_date: Unset | str = UNSET
        if not isinstance(self.pub_date, Unset):
            pub_date = self.pub_date.isoformat()

        contentencoded = self.contentencoded

        dccreator = self.dccreator

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if link is not UNSET:
            field_dict["link"] = link
        if guid is not UNSET:
            field_dict["guid"] = guid
        if pub_date is not UNSET:
            field_dict["pubDate"] = pub_date
        if contentencoded is not UNSET:
            field_dict["content:encoded"] = contentencoded
        if dccreator is not UNSET:
            field_dict["dc:creator"] = dccreator

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        """Create instance from dictionary."""
        d = dict(src_dict)
        link = d.pop("link", UNSET)

        guid = d.pop("guid", UNSET)

        _pub_date = d.pop("pubDate", UNSET)
        pub_date: Unset | datetime.datetime
        if isinstance(_pub_date, Unset):
            pub_date = UNSET
        else:
            pub_date = isoparse(_pub_date)

        contentencoded = d.pop("content:encoded", UNSET)

        dccreator = d.pop("dc:creator", UNSET)

        video_comments_for_xml_item = cls(
            link=link,
            guid=guid,
            pub_date=pub_date,
            contentencoded=contentencoded,
            dccreator=dccreator,
        )

        video_comments_for_xml_item.additional_properties = d
        return video_comments_for_xml_item

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
