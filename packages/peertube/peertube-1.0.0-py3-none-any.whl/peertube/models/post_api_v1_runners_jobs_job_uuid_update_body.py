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
    from peertube.models.post_api_v1_runners_jobs_job_uuid_update_body_payload_type_0 import (
        PostApiV1RunnersJobsJobUUIDUpdateBodyPayloadType0,
    )


T = TypeVar("T", bound="PostApiV1RunnersJobsJobUUIDUpdateBody")


@_attrs_define
class PostApiV1RunnersJobsJobUUIDUpdateBody:
    """Attributes:
    runner_token (str):
    job_token (str):
    progress (Union[Unset, int]): Update job progression percentage (optional)
    payload (Union['PostApiV1RunnersJobsJobUUIDUpdateBodyPayloadType0', Unset]):
    """

    runner_token: str
    job_token: str
    progress: Unset | int = UNSET
    payload: Union["PostApiV1RunnersJobsJobUUIDUpdateBodyPayloadType0", Unset] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert instance to dictionary."""
        runner_token = self.runner_token

        job_token = self.job_token

        progress = self.progress

        payload: Unset | dict[str, Any]
        if isinstance(self.payload, Unset):
            payload = UNSET
        else:
            payload = self.payload.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "runnerToken": runner_token,
                "jobToken": job_token,
            }
        )
        if progress is not UNSET:
            field_dict["progress"] = progress
        if payload is not UNSET:
            field_dict["payload"] = payload

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        """Create instance from dictionary."""
        from peertube.models.post_api_v1_runners_jobs_job_uuid_update_body_payload_type_0 import (
            PostApiV1RunnersJobsJobUUIDUpdateBodyPayloadType0,
        )

        d = dict(src_dict)
        runner_token = d.pop("runnerToken")

        job_token = d.pop("jobToken")

        progress = d.pop("progress", UNSET)

        def _parse_payload(
            data: object,
        ) -> Union["PostApiV1RunnersJobsJobUUIDUpdateBodyPayloadType0", Unset]:
            if isinstance(data, Unset):
                return data
            if not isinstance(data, dict):
                raise TypeError
            payload_type_0 = (
                PostApiV1RunnersJobsJobUUIDUpdateBodyPayloadType0.from_dict(data)
            )

            return payload_type_0

        payload = _parse_payload(d.pop("payload", UNSET))

        post_api_v1_runners_jobs_job_uuid_update_body = cls(
            runner_token=runner_token,
            job_token=job_token,
            progress=progress,
            payload=payload,
        )

        post_api_v1_runners_jobs_job_uuid_update_body.additional_properties = d
        return post_api_v1_runners_jobs_job_uuid_update_body

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
