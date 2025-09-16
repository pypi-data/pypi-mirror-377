from collections.abc import Mapping
from typing import (
    TYPE_CHECKING,
    Any,
    TypeVar,
    Union,
)

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from typing_extensions import Self

from peertube.types import UNSET, Unset

if TYPE_CHECKING:
    from peertube.models.video_token_response_files import VideoTokenResponseFiles


T = TypeVar("T", bound="VideoTokenResponse")


@_attrs_define
class VideoTokenResponse:
    """Attributes:
    files (Union[Unset, VideoTokenResponseFiles]):
    """

    files: Union[Unset, "VideoTokenResponseFiles"] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert instance to dictionary."""
        files: Unset | dict[str, Any] = UNSET
        if not isinstance(self.files, Unset):
            files = self.files.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if files is not UNSET:
            field_dict["files"] = files

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        """Create instance from dictionary."""
        from peertube.models.video_token_response_files import VideoTokenResponseFiles

        d = dict(src_dict)
        _files = d.pop("files", UNSET)
        files: Unset | VideoTokenResponseFiles
        if isinstance(_files, Unset):
            files = UNSET
        else:
            files = VideoTokenResponseFiles.from_dict(_files)

        video_token_response = cls(
            files=files,
        )

        video_token_response.additional_properties = d
        return video_token_response

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
