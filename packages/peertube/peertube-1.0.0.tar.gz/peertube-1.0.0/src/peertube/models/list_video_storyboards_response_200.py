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
    from peertube.models.storyboard import Storyboard


T = TypeVar("T", bound="ListVideoStoryboardsResponse200")


@_attrs_define
class ListVideoStoryboardsResponse200:
    """Attributes:
    storyboards (Union[Unset, list['Storyboard']]):
    """

    storyboards: Unset | list["Storyboard"] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert instance to dictionary."""
        storyboards: Unset | list[dict[str, Any]] = UNSET
        if not isinstance(self.storyboards, Unset):
            storyboards = []
            for storyboards_item_data in self.storyboards:
                storyboards_item = storyboards_item_data.to_dict()
                storyboards.append(storyboards_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if storyboards is not UNSET:
            field_dict["storyboards"] = storyboards

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        """Create instance from dictionary."""
        from peertube.models.storyboard import Storyboard

        d = dict(src_dict)
        storyboards = []
        _storyboards = d.pop("storyboards", UNSET)
        for storyboards_item_data in _storyboards or []:
            storyboards_item = Storyboard.from_dict(storyboards_item_data)

            storyboards.append(storyboards_item)

        list_video_storyboards_response_200 = cls(
            storyboards=storyboards,
        )

        list_video_storyboards_response_200.additional_properties = d
        return list_video_storyboards_response_200

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
