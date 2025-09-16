import datetime
from collections.abc import Mapping
from typing import (
    TYPE_CHECKING,
    Any,
    TypeVar,
    Union,
)

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse
from typing_extensions import Self

from peertube.models.job_state import JobState
from peertube.models.job_type import JobType
from peertube.types import UNSET, Unset

if TYPE_CHECKING:
    from peertube.models.job_data import JobData
    from peertube.models.job_error import JobError


T = TypeVar("T", bound="Job")


@_attrs_define
class Job:
    """Attributes:
    id (Union[Unset, int]):  Example: 42.
    state (Union[Unset, JobState]):
    type_ (Union[Unset, JobType]):
    data (Union[Unset, JobData]):
    error (Union[Unset, JobError]):
    created_at (Union[Unset, datetime.datetime]):
    finished_on (Union[Unset, datetime.datetime]):
    processed_on (Union[Unset, datetime.datetime]):
    """

    id: Unset | int = UNSET
    state: Unset | JobState = UNSET
    type_: Unset | JobType = UNSET
    data: Union[Unset, "JobData"] = UNSET
    error: Union[Unset, "JobError"] = UNSET
    created_at: Unset | datetime.datetime = UNSET
    finished_on: Unset | datetime.datetime = UNSET
    processed_on: Unset | datetime.datetime = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert instance to dictionary."""
        id = self.id

        state: Unset | str = UNSET
        if not isinstance(self.state, Unset):
            state = self.state.value

        type_: Unset | str = UNSET
        if not isinstance(self.type_, Unset):
            type_ = self.type_.value

        data: Unset | dict[str, Any] = UNSET
        if not isinstance(self.data, Unset):
            data = self.data.to_dict()

        error: Unset | dict[str, Any] = UNSET
        if not isinstance(self.error, Unset):
            error = self.error.to_dict()

        created_at: Unset | str = UNSET
        if not isinstance(self.created_at, Unset):
            created_at = self.created_at.isoformat()

        finished_on: Unset | str = UNSET
        if not isinstance(self.finished_on, Unset):
            finished_on = self.finished_on.isoformat()

        processed_on: Unset | str = UNSET
        if not isinstance(self.processed_on, Unset):
            processed_on = self.processed_on.isoformat()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if id is not UNSET:
            field_dict["id"] = id
        if state is not UNSET:
            field_dict["state"] = state
        if type_ is not UNSET:
            field_dict["type"] = type_
        if data is not UNSET:
            field_dict["data"] = data
        if error is not UNSET:
            field_dict["error"] = error
        if created_at is not UNSET:
            field_dict["createdAt"] = created_at
        if finished_on is not UNSET:
            field_dict["finishedOn"] = finished_on
        if processed_on is not UNSET:
            field_dict["processedOn"] = processed_on

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        """Create instance from dictionary."""
        from peertube.models.job_data import JobData
        from peertube.models.job_error import JobError

        d = dict(src_dict)
        id = d.pop("id", UNSET)

        _state = d.pop("state", UNSET)
        state: Unset | JobState
        if isinstance(_state, Unset):
            state = UNSET
        else:
            state = JobState(_state)

        _type_ = d.pop("type", UNSET)
        type_: Unset | JobType
        if isinstance(_type_, Unset):
            type_ = UNSET
        else:
            type_ = JobType(_type_)

        _data = d.pop("data", UNSET)
        data: Unset | JobData
        if isinstance(_data, Unset):
            data = UNSET
        else:
            data = JobData.from_dict(_data)

        _error = d.pop("error", UNSET)
        error: Unset | JobError
        if isinstance(_error, Unset):
            error = UNSET
        else:
            error = JobError.from_dict(_error)

        _created_at = d.pop("createdAt", UNSET)
        created_at: Unset | datetime.datetime
        if isinstance(_created_at, Unset):
            created_at = UNSET
        else:
            created_at = isoparse(_created_at)

        _finished_on = d.pop("finishedOn", UNSET)
        finished_on: Unset | datetime.datetime
        if isinstance(_finished_on, Unset):
            finished_on = UNSET
        else:
            finished_on = isoparse(_finished_on)

        _processed_on = d.pop("processedOn", UNSET)
        processed_on: Unset | datetime.datetime
        if isinstance(_processed_on, Unset):
            processed_on = UNSET
        else:
            processed_on = isoparse(_processed_on)

        job = cls(
            id=id,
            state=state,
            type_=type_,
            data=data,
            error=error,
            created_at=created_at,
            finished_on=finished_on,
            processed_on=processed_on,
        )

        job.additional_properties = d
        return job

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
