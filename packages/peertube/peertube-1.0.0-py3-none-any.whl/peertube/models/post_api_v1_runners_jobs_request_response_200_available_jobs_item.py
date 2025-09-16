from collections.abc import Mapping
from typing import (
    TYPE_CHECKING,
    Any,
    TypeVar,
    Union,
)
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from typing_extensions import Self

from peertube.models.runner_job_type import RunnerJobType
from peertube.types import UNSET, Unset

if TYPE_CHECKING:
    from peertube.models.vod_audio_merge_transcoding import VODAudioMergeTranscoding
    from peertube.models.vod_web_video_transcoding import VODWebVideoTranscoding
    from peertube.models.vodhls_transcoding import VODHLSTranscoding


T = TypeVar("T", bound="PostApiV1RunnersJobsRequestResponse200AvailableJobsItem")


@_attrs_define
class PostApiV1RunnersJobsRequestResponse200AvailableJobsItem:
    """Attributes:
    uuid (Union[Unset, UUID]):  Example: 9c9de5e8-0a1e-484a-b099-e80766180a6d.
    type_ (Union[Unset, RunnerJobType]):
    payload (Union['VODAudioMergeTranscoding', 'VODHLSTranscoding', 'VODWebVideoTranscoding', Unset]):
    """

    uuid: Unset | UUID = UNSET
    type_: Unset | RunnerJobType = UNSET
    payload: Union[
        "VODAudioMergeTranscoding", "VODHLSTranscoding", "VODWebVideoTranscoding", Unset
    ] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert instance to dictionary."""
        from peertube.models.vod_web_video_transcoding import VODWebVideoTranscoding
        from peertube.models.vodhls_transcoding import VODHLSTranscoding

        uuid: Unset | str = UNSET
        if not isinstance(self.uuid, Unset):
            uuid = str(self.uuid)

        type_: Unset | str = UNSET
        if not isinstance(self.type_, Unset):
            type_ = self.type_.value

        payload: Unset | dict[str, Any]
        if isinstance(self.payload, Unset):
            payload = UNSET
        elif isinstance(self.payload, (VODWebVideoTranscoding, VODHLSTranscoding)):
            payload = self.payload.to_dict()
        else:
            payload = self.payload.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if uuid is not UNSET:
            field_dict["uuid"] = uuid
        if type_ is not UNSET:
            field_dict["type"] = type_
        if payload is not UNSET:
            field_dict["payload"] = payload

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        """Create instance from dictionary."""
        from peertube.models.vod_audio_merge_transcoding import VODAudioMergeTranscoding
        from peertube.models.vod_web_video_transcoding import VODWebVideoTranscoding
        from peertube.models.vodhls_transcoding import VODHLSTranscoding

        d = dict(src_dict)
        _uuid = d.pop("uuid", UNSET)
        uuid: Unset | UUID
        if isinstance(_uuid, Unset):
            uuid = UNSET
        else:
            uuid = UUID(_uuid)

        _type_ = d.pop("type", UNSET)
        type_: Unset | RunnerJobType
        if isinstance(_type_, Unset):
            type_ = UNSET
        else:
            type_ = RunnerJobType(_type_)

        def _parse_payload(
            data: object,
        ) -> Union[
            "VODAudioMergeTranscoding",
            "VODHLSTranscoding",
            "VODWebVideoTranscoding",
            Unset,
        ]:
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError
                componentsschemas_runner_job_payload_vod_web_video_transcoding = (
                    VODWebVideoTranscoding.from_dict(data)
                )

                return componentsschemas_runner_job_payload_vod_web_video_transcoding
            except:  # noqa: E722
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError
                componentsschemas_runner_job_payload_vod_hls_transcoding = (
                    VODHLSTranscoding.from_dict(data)
                )

                return componentsschemas_runner_job_payload_vod_hls_transcoding
            except:  # noqa: E722
                pass
            if not isinstance(data, dict):
                raise TypeError
            componentsschemas_runner_job_payload_vod_audio_merge_transcoding = (
                VODAudioMergeTranscoding.from_dict(data)
            )

            return componentsschemas_runner_job_payload_vod_audio_merge_transcoding

        payload = _parse_payload(d.pop("payload", UNSET))

        post_api_v1_runners_jobs_request_response_200_available_jobs_item = cls(
            uuid=uuid,
            type_=type_,
            payload=payload,
        )

        post_api_v1_runners_jobs_request_response_200_available_jobs_item.additional_properties = d
        return post_api_v1_runners_jobs_request_response_200_available_jobs_item

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
