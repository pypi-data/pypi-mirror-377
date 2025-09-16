from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from typing_extensions import Self

T = TypeVar("T", bound="PostApiV1RunnersJobsJobUUIDErrorBody")


@_attrs_define
class PostApiV1RunnersJobsJobUUIDErrorBody:
    """Attributes:
    runner_token (str):
    job_token (str):
    message (str): Why the runner failed to process this job
    """

    runner_token: str
    job_token: str
    message: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        runner_token = self.runner_token

        job_token = self.job_token

        message = self.message

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "runnerToken": runner_token,
                "jobToken": job_token,
                "message": message,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        """Create from dictionary."""
        d = dict(src_dict)
        runner_token = d.pop("runnerToken")

        job_token = d.pop("jobToken")

        message = d.pop("message")

        post_api_v1_runners_jobs_job_uuid_error_body = cls(
            runner_token=runner_token,
            job_token=job_token,
            message=message,
        )

        post_api_v1_runners_jobs_job_uuid_error_body.additional_properties = d
        return post_api_v1_runners_jobs_job_uuid_error_body

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
