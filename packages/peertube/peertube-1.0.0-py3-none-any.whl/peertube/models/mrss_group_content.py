from collections.abc import Mapping
from typing import (
    Any,
    TypeVar,
)

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from typing_extensions import Self

from peertube.types import UNSET, Unset

T = TypeVar("T", bound="MRSSGroupContent")


@_attrs_define
class MRSSGroupContent:
    """Attributes:
    url (Union[Unset, str]):
    file_size (Union[Unset, int]):
    type_ (Union[Unset, str]):
    framerate (Union[Unset, int]):
    duration (Union[Unset, int]):
    height (Union[Unset, int]):
    lang (Union[Unset, str]):
    """

    url: Unset | str = UNSET
    file_size: Unset | int = UNSET
    type_: Unset | str = UNSET
    framerate: Unset | int = UNSET
    duration: Unset | int = UNSET
    height: Unset | int = UNSET
    lang: Unset | str = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert instance to dictionary."""
        url = self.url

        file_size = self.file_size

        type_ = self.type_

        framerate = self.framerate

        duration = self.duration

        height = self.height

        lang = self.lang

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if url is not UNSET:
            field_dict["url"] = url
        if file_size is not UNSET:
            field_dict["fileSize"] = file_size
        if type_ is not UNSET:
            field_dict["type"] = type_
        if framerate is not UNSET:
            field_dict["framerate"] = framerate
        if duration is not UNSET:
            field_dict["duration"] = duration
        if height is not UNSET:
            field_dict["height"] = height
        if lang is not UNSET:
            field_dict["lang"] = lang

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        """Create instance from dictionary."""
        d = dict(src_dict)
        url = d.pop("url", UNSET)

        file_size = d.pop("fileSize", UNSET)

        type_ = d.pop("type", UNSET)

        framerate = d.pop("framerate", UNSET)

        duration = d.pop("duration", UNSET)

        height = d.pop("height", UNSET)

        lang = d.pop("lang", UNSET)

        mrss_group_content = cls(
            url=url,
            file_size=file_size,
            type_=type_,
            framerate=framerate,
            duration=duration,
            height=height,
            lang=lang,
        )

        mrss_group_content.additional_properties = d
        return mrss_group_content

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
