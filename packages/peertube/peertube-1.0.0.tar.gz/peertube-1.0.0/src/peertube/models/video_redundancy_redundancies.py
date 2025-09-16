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
    from peertube.models.file_redundancy_information import FileRedundancyInformation


T = TypeVar("T", bound="VideoRedundancyRedundancies")


@_attrs_define
class VideoRedundancyRedundancies:
    """Attributes:
    streaming_playlists (Union[Unset, list['FileRedundancyInformation']]):
    """

    streaming_playlists: Unset | list["FileRedundancyInformation"] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert instance to dictionary."""
        streaming_playlists: Unset | list[dict[str, Any]] = UNSET
        if not isinstance(self.streaming_playlists, Unset):
            streaming_playlists = []
            for streaming_playlists_item_data in self.streaming_playlists:
                streaming_playlists_item = streaming_playlists_item_data.to_dict()
                streaming_playlists.append(streaming_playlists_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if streaming_playlists is not UNSET:
            field_dict["streamingPlaylists"] = streaming_playlists

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        """Create instance from dictionary."""
        from peertube.models.file_redundancy_information import (
            FileRedundancyInformation,
        )

        d = dict(src_dict)
        streaming_playlists = []
        _streaming_playlists = d.pop("streamingPlaylists", UNSET)
        for streaming_playlists_item_data in _streaming_playlists or []:
            streaming_playlists_item = FileRedundancyInformation.from_dict(
                streaming_playlists_item_data
            )

            streaming_playlists.append(streaming_playlists_item)

        video_redundancy_redundancies = cls(
            streaming_playlists=streaming_playlists,
        )

        video_redundancy_redundancies.additional_properties = d
        return video_redundancy_redundancies

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
