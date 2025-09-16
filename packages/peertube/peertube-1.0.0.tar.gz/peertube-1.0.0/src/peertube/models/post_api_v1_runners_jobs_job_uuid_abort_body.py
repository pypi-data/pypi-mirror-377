from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from typing_extensions import Self

T = TypeVar("T", bound="PostApiV1RunnersJobsJobUUIDAbortBody")


@_attrs_define
class PostApiV1RunnersJobsJobUUIDAbortBody:
    """Attributes:
    runner_token (str):
    job_token (str):
    reason (str): Why the runner aborts this job
    """

    runner_token: str
    job_token: str
    reason: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert instance to dictionary."""
        runner_token = self.runner_token

        job_token = self.job_token

        reason = self.reason

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "runnerToken": runner_token,
                "jobToken": job_token,
                "reason": reason,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        """Create instance from dictionary."""
        d = dict(src_dict)
        runner_token = d.pop("runnerToken")

        job_token = d.pop("jobToken")

        reason = d.pop("reason")

        post_api_v1_runners_jobs_job_uuid_abort_body = cls(
            runner_token=runner_token,
            job_token=job_token,
            reason=reason,
        )

        post_api_v1_runners_jobs_job_uuid_abort_body.additional_properties = d
        return post_api_v1_runners_jobs_job_uuid_abort_body

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
