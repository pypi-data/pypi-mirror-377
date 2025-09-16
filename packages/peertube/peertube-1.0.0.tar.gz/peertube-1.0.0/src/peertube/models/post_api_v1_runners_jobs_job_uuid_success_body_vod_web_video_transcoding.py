from collections.abc import Mapping
from io import BytesIO
from typing import (
    Any,
    TypeVar,
)

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from typing_extensions import Self

from peertube.types import UNSET, File, FileTypes, Unset

T = TypeVar("T", bound="PostApiV1RunnersJobsJobUUIDSuccessBodyVODWebVideoTranscoding")


@_attrs_define
class PostApiV1RunnersJobsJobUUIDSuccessBodyVODWebVideoTranscoding:
    """Attributes:
    video_file (Union[Unset, File]):
    """

    video_file: Unset | File = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        video_file: Unset | FileTypes = UNSET
        if not isinstance(self.video_file, Unset):
            video_file = self.video_file.to_tuple()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if video_file is not UNSET:
            field_dict["videoFile"] = video_file

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        """Create from dictionary."""
        d = dict(src_dict)
        _video_file = d.pop("videoFile", UNSET)
        video_file: Unset | File
        if isinstance(_video_file, Unset):
            video_file = UNSET
        else:
            video_file = File(payload=BytesIO(_video_file))

        post_api_v1_runners_jobs_job_uuid_success_body_vod_web_video_transcoding = cls(
            video_file=video_file,
        )

        post_api_v1_runners_jobs_job_uuid_success_body_vod_web_video_transcoding.additional_properties = d
        return post_api_v1_runners_jobs_job_uuid_success_body_vod_web_video_transcoding

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
