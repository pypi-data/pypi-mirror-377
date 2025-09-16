from collections.abc import Mapping
from typing import (
    Any,
    TypeVar,
    cast,
)

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from typing_extensions import Self

from peertube.types import UNSET, Unset

T = TypeVar("T", bound="PostApiV1RunnersJobsRequestBody")


@_attrs_define
class PostApiV1RunnersJobsRequestBody:
    """Attributes:
    runner_token (str):
    job_types (Union[Unset, list[str]]): Filter jobs depending on their types
    """

    runner_token: str
    job_types: Unset | list[str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert instance to dictionary."""
        runner_token = self.runner_token

        job_types: Unset | list[str] = UNSET
        if not isinstance(self.job_types, Unset):
            job_types = self.job_types

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "runnerToken": runner_token,
            }
        )
        if job_types is not UNSET:
            field_dict["jobTypes"] = job_types

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        """Create instance from dictionary."""
        d = dict(src_dict)
        runner_token = d.pop("runnerToken")

        job_types = cast("list[str]", d.pop("jobTypes", UNSET))

        post_api_v1_runners_jobs_request_body = cls(
            runner_token=runner_token,
            job_types=job_types,
        )

        post_api_v1_runners_jobs_request_body.additional_properties = d
        return post_api_v1_runners_jobs_request_body

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
