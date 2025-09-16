from collections.abc import Mapping
from typing import (
    Any,
    TypeVar,
)

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from typing_extensions import Self

from peertube.types import UNSET, Unset

T = TypeVar("T", bound="Storyboard")


@_attrs_define
class Storyboard:
    """Attributes:
    storyboard_path (Union[Unset, str]):
    total_height (Union[Unset, int]):
    total_width (Union[Unset, int]):
    sprite_height (Union[Unset, int]):
    sprite_width (Union[Unset, int]):
    sprite_duration (Union[Unset, int]):
    """

    storyboard_path: Unset | str = UNSET
    total_height: Unset | int = UNSET
    total_width: Unset | int = UNSET
    sprite_height: Unset | int = UNSET
    sprite_width: Unset | int = UNSET
    sprite_duration: Unset | int = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert instance to dictionary."""
        storyboard_path = self.storyboard_path

        total_height = self.total_height

        total_width = self.total_width

        sprite_height = self.sprite_height

        sprite_width = self.sprite_width

        sprite_duration = self.sprite_duration

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if storyboard_path is not UNSET:
            field_dict["storyboardPath"] = storyboard_path
        if total_height is not UNSET:
            field_dict["totalHeight"] = total_height
        if total_width is not UNSET:
            field_dict["totalWidth"] = total_width
        if sprite_height is not UNSET:
            field_dict["spriteHeight"] = sprite_height
        if sprite_width is not UNSET:
            field_dict["spriteWidth"] = sprite_width
        if sprite_duration is not UNSET:
            field_dict["spriteDuration"] = sprite_duration

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        """Create instance from dictionary."""
        d = dict(src_dict)
        storyboard_path = d.pop("storyboardPath", UNSET)

        total_height = d.pop("totalHeight", UNSET)

        total_width = d.pop("totalWidth", UNSET)

        sprite_height = d.pop("spriteHeight", UNSET)

        sprite_width = d.pop("spriteWidth", UNSET)

        sprite_duration = d.pop("spriteDuration", UNSET)

        storyboard = cls(
            storyboard_path=storyboard_path,
            total_height=total_height,
            total_width=total_width,
            sprite_height=sprite_height,
            sprite_width=sprite_width,
            sprite_duration=sprite_duration,
        )

        storyboard.additional_properties = d
        return storyboard

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
