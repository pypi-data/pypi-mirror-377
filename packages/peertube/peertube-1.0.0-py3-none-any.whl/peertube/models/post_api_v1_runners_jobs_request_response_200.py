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
    from peertube.models.post_api_v1_runners_jobs_request_response_200_available_jobs_item import (
        PostApiV1RunnersJobsRequestResponse200AvailableJobsItem,
    )


T = TypeVar("T", bound="PostApiV1RunnersJobsRequestResponse200")


@_attrs_define
class PostApiV1RunnersJobsRequestResponse200:
    """Attributes:
    available_jobs (Union[Unset, list['PostApiV1RunnersJobsRequestResponse200AvailableJobsItem']]):
    """

    available_jobs: (
        Unset | list["PostApiV1RunnersJobsRequestResponse200AvailableJobsItem"]
    ) = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert instance to dictionary."""
        available_jobs: Unset | list[dict[str, Any]] = UNSET
        if not isinstance(self.available_jobs, Unset):
            available_jobs = []
            for available_jobs_item_data in self.available_jobs:
                available_jobs_item = available_jobs_item_data.to_dict()
                available_jobs.append(available_jobs_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if available_jobs is not UNSET:
            field_dict["availableJobs"] = available_jobs

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        """Create instance from dictionary."""
        from peertube.models.post_api_v1_runners_jobs_request_response_200_available_jobs_item import (
            PostApiV1RunnersJobsRequestResponse200AvailableJobsItem,
        )

        d = dict(src_dict)
        available_jobs = []
        _available_jobs = d.pop("availableJobs", UNSET)
        for available_jobs_item_data in _available_jobs or []:
            available_jobs_item = (
                PostApiV1RunnersJobsRequestResponse200AvailableJobsItem.from_dict(
                    available_jobs_item_data
                )
            )

            available_jobs.append(available_jobs_item)

        post_api_v1_runners_jobs_request_response_200 = cls(
            available_jobs=available_jobs,
        )

        post_api_v1_runners_jobs_request_response_200.additional_properties = d
        return post_api_v1_runners_jobs_request_response_200

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
