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
    from peertube.models.post_api_v1_runners_jobs_job_uuid_accept_response_200_job import (
        PostApiV1RunnersJobsJobUUIDAcceptResponse200Job,
    )


T = TypeVar("T", bound="PostApiV1RunnersJobsJobUUIDAcceptResponse200")


@_attrs_define
class PostApiV1RunnersJobsJobUUIDAcceptResponse200:
    """Attributes:
    job (Union[Unset, PostApiV1RunnersJobsJobUUIDAcceptResponse200Job]):
    """

    job: Union[Unset, "PostApiV1RunnersJobsJobUUIDAcceptResponse200Job"] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert instance to dictionary."""
        job: Unset | dict[str, Any] = UNSET
        if not isinstance(self.job, Unset):
            job = self.job.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if job is not UNSET:
            field_dict["job"] = job

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        """Create instance from dictionary."""
        from peertube.models.post_api_v1_runners_jobs_job_uuid_accept_response_200_job import (
            PostApiV1RunnersJobsJobUUIDAcceptResponse200Job,
        )

        d = dict(src_dict)
        _job = d.pop("job", UNSET)
        job: Unset | PostApiV1RunnersJobsJobUUIDAcceptResponse200Job
        if isinstance(_job, Unset):
            job = UNSET
        else:
            job = PostApiV1RunnersJobsJobUUIDAcceptResponse200Job.from_dict(_job)

        post_api_v1_runners_jobs_job_uuid_accept_response_200 = cls(
            job=job,
        )

        post_api_v1_runners_jobs_job_uuid_accept_response_200.additional_properties = d
        return post_api_v1_runners_jobs_job_uuid_accept_response_200

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
