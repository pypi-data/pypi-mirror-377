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

if TYPE_CHECKING:
    from peertube.models.post_api_v1_runners_jobs_job_uuid_success_body_live_rtmp_to_hls_transcoding import (
        PostApiV1RunnersJobsJobUUIDSuccessBodyLiveRTMPToHLSTranscoding,
    )
    from peertube.models.post_api_v1_runners_jobs_job_uuid_success_body_vod_audio_merge_transcoding import (
        PostApiV1RunnersJobsJobUUIDSuccessBodyVODAudioMergeTranscoding,
    )
    from peertube.models.post_api_v1_runners_jobs_job_uuid_success_body_vod_web_video_transcoding import (
        PostApiV1RunnersJobsJobUUIDSuccessBodyVODWebVideoTranscoding,
    )
    from peertube.models.post_api_v1_runners_jobs_job_uuid_success_body_vodhls_transcoding import (
        PostApiV1RunnersJobsJobUUIDSuccessBodyVODHLSTranscoding,
    )


T = TypeVar("T", bound="PostApiV1RunnersJobsJobUUIDSuccessBody")


@_attrs_define
class PostApiV1RunnersJobsJobUUIDSuccessBody:
    """Attributes:
    runner_token (str):
    job_token (str):
    payload (Union['PostApiV1RunnersJobsJobUUIDSuccessBodyLiveRTMPToHLSTranscoding',
        'PostApiV1RunnersJobsJobUUIDSuccessBodyVODAudioMergeTranscoding',
        'PostApiV1RunnersJobsJobUUIDSuccessBodyVODHLSTranscoding',
        'PostApiV1RunnersJobsJobUUIDSuccessBodyVODWebVideoTranscoding']):
    """

    runner_token: str
    job_token: str
    payload: Union[
        "PostApiV1RunnersJobsJobUUIDSuccessBodyLiveRTMPToHLSTranscoding",
        "PostApiV1RunnersJobsJobUUIDSuccessBodyVODAudioMergeTranscoding",
        "PostApiV1RunnersJobsJobUUIDSuccessBodyVODHLSTranscoding",
        "PostApiV1RunnersJobsJobUUIDSuccessBodyVODWebVideoTranscoding",
    ]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert instance to dictionary."""
        from peertube.models.post_api_v1_runners_jobs_job_uuid_success_body_vod_audio_merge_transcoding import (
            PostApiV1RunnersJobsJobUUIDSuccessBodyVODAudioMergeTranscoding,
        )
        from peertube.models.post_api_v1_runners_jobs_job_uuid_success_body_vod_web_video_transcoding import (
            PostApiV1RunnersJobsJobUUIDSuccessBodyVODWebVideoTranscoding,
        )
        from peertube.models.post_api_v1_runners_jobs_job_uuid_success_body_vodhls_transcoding import (
            PostApiV1RunnersJobsJobUUIDSuccessBodyVODHLSTranscoding,
        )

        runner_token = self.runner_token

        job_token = self.job_token

        payload: dict[str, Any]
        if isinstance(
            self.payload,
            (
                PostApiV1RunnersJobsJobUUIDSuccessBodyVODWebVideoTranscoding,
                PostApiV1RunnersJobsJobUUIDSuccessBodyVODHLSTranscoding,
                PostApiV1RunnersJobsJobUUIDSuccessBodyVODAudioMergeTranscoding,
            ),
        ):
            payload = self.payload.to_dict()
        else:
            payload = self.payload.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "runnerToken": runner_token,
                "jobToken": job_token,
                "payload": payload,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        """Create instance from dictionary."""
        from peertube.models.post_api_v1_runners_jobs_job_uuid_success_body_live_rtmp_to_hls_transcoding import (
            PostApiV1RunnersJobsJobUUIDSuccessBodyLiveRTMPToHLSTranscoding,
        )
        from peertube.models.post_api_v1_runners_jobs_job_uuid_success_body_vod_audio_merge_transcoding import (
            PostApiV1RunnersJobsJobUUIDSuccessBodyVODAudioMergeTranscoding,
        )
        from peertube.models.post_api_v1_runners_jobs_job_uuid_success_body_vod_web_video_transcoding import (
            PostApiV1RunnersJobsJobUUIDSuccessBodyVODWebVideoTranscoding,
        )
        from peertube.models.post_api_v1_runners_jobs_job_uuid_success_body_vodhls_transcoding import (
            PostApiV1RunnersJobsJobUUIDSuccessBodyVODHLSTranscoding,
        )

        d = dict(src_dict)
        runner_token = d.pop("runnerToken")

        job_token = d.pop("jobToken")

        def _parse_payload(
            data: object,
        ) -> Union[
            "PostApiV1RunnersJobsJobUUIDSuccessBodyLiveRTMPToHLSTranscoding",
            "PostApiV1RunnersJobsJobUUIDSuccessBodyVODAudioMergeTranscoding",
            "PostApiV1RunnersJobsJobUUIDSuccessBodyVODHLSTranscoding",
            "PostApiV1RunnersJobsJobUUIDSuccessBodyVODWebVideoTranscoding",
        ]:
            try:
                if not isinstance(data, dict):
                    raise TypeError
                payload_vod_web_video_transcoding = PostApiV1RunnersJobsJobUUIDSuccessBodyVODWebVideoTranscoding.from_dict(
                    data
                )

                return payload_vod_web_video_transcoding
            except:  # noqa: E722
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError
                payload_vod_hls_transcoding = (
                    PostApiV1RunnersJobsJobUUIDSuccessBodyVODHLSTranscoding.from_dict(
                        data
                    )
                )

                return payload_vod_hls_transcoding
            except:  # noqa: E722
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError
                payload_vod_audio_merge_transcoding = PostApiV1RunnersJobsJobUUIDSuccessBodyVODAudioMergeTranscoding.from_dict(
                    data
                )

                return payload_vod_audio_merge_transcoding
            except:  # noqa: E722
                pass
            if not isinstance(data, dict):
                raise TypeError
            payload_live_rtmp_to_hls_transcoding = PostApiV1RunnersJobsJobUUIDSuccessBodyLiveRTMPToHLSTranscoding.from_dict(
                data
            )

            return payload_live_rtmp_to_hls_transcoding

        payload = _parse_payload(d.pop("payload"))

        post_api_v1_runners_jobs_job_uuid_success_body = cls(
            runner_token=runner_token,
            job_token=job_token,
            payload=payload,
        )

        post_api_v1_runners_jobs_job_uuid_success_body.additional_properties = d
        return post_api_v1_runners_jobs_job_uuid_success_body

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
