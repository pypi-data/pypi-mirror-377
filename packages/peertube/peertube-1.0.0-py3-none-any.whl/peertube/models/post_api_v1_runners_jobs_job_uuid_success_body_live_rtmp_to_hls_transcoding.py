from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from typing_extensions import Self

T = TypeVar("T", bound="PostApiV1RunnersJobsJobUUIDSuccessBodyLiveRTMPToHLSTranscoding")


@_attrs_define
class PostApiV1RunnersJobsJobUUIDSuccessBodyLiveRTMPToHLSTranscoding:
    """Data model."""

    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert instance to dictionary."""
        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        """Create instance from dictionary."""
        d = dict(src_dict)
        post_api_v1_runners_jobs_job_uuid_success_body_live_rtmp_to_hls_transcoding = (
            cls()
        )

        post_api_v1_runners_jobs_job_uuid_success_body_live_rtmp_to_hls_transcoding.additional_properties = d
        return (
            post_api_v1_runners_jobs_job_uuid_success_body_live_rtmp_to_hls_transcoding
        )

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
