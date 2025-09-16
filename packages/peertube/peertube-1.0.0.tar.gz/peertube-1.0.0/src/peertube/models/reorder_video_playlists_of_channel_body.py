from collections.abc import Mapping
from typing import (
    Any,
    TypeVar,
)

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from typing_extensions import Self

from peertube.types import UNSET, Unset

T = TypeVar("T", bound="ReorderVideoPlaylistsOfChannelBody")


@_attrs_define
class ReorderVideoPlaylistsOfChannelBody:
    """Attributes:
    start_position (int): Start position of the element to reorder
    insert_after_position (int): New position for the block to reorder, to add the block before the first element
    reorder_length (Union[Unset, int]): How many element from `startPosition` to reorder
    """

    start_position: int
    insert_after_position: int
    reorder_length: Unset | int = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert instance to dictionary."""
        start_position = self.start_position

        insert_after_position = self.insert_after_position

        reorder_length = self.reorder_length

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "startPosition": start_position,
                "insertAfterPosition": insert_after_position,
            }
        )
        if reorder_length is not UNSET:
            field_dict["reorderLength"] = reorder_length

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        """Create instance from dictionary."""
        d = dict(src_dict)
        start_position = d.pop("startPosition")

        insert_after_position = d.pop("insertAfterPosition")

        reorder_length = d.pop("reorderLength", UNSET)

        reorder_video_playlists_of_channel_body = cls(
            start_position=start_position,
            insert_after_position=insert_after_position,
            reorder_length=reorder_length,
        )

        reorder_video_playlists_of_channel_body.additional_properties = d
        return reorder_video_playlists_of_channel_body

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
