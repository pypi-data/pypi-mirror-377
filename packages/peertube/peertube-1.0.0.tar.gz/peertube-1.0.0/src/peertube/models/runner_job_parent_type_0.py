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
    from peertube.models.runner_job_state_constant import RunnerJobStateConstant


T = TypeVar("T", bound="RunnerJobParentType0")


@_attrs_define
class RunnerJobParentType0:
    """If job has a parent job

    Attributes:
        type_ (Union[Unset, RunnerJobType]):
        state (Union[Unset, RunnerJobStateConstant]):
        uuid (Union[Unset, UUID]):  Example: 9c9de5e8-0a1e-484a-b099-e80766180a6d.
    """

    type_: Unset | RunnerJobType = UNSET
    state: Union[Unset, "RunnerJobStateConstant"] = UNSET
    uuid: Unset | UUID = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert instance to dictionary."""
        type_: Unset | str = UNSET
        if not isinstance(self.type_, Unset):
            type_ = self.type_.value

        state: Unset | dict[str, Any] = UNSET
        if not isinstance(self.state, Unset):
            state = self.state.to_dict()

        uuid: Unset | str = UNSET
        if not isinstance(self.uuid, Unset):
            uuid = str(self.uuid)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if type_ is not UNSET:
            field_dict["type"] = type_
        if state is not UNSET:
            field_dict["state"] = state
        if uuid is not UNSET:
            field_dict["uuid"] = uuid

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        """Create instance from dictionary."""
        from peertube.models.runner_job_state_constant import RunnerJobStateConstant

        d = dict(src_dict)
        _type_ = d.pop("type", UNSET)
        type_: Unset | RunnerJobType
        if isinstance(_type_, Unset):
            type_ = UNSET
        else:
            type_ = RunnerJobType(_type_)

        _state = d.pop("state", UNSET)
        state: Unset | RunnerJobStateConstant
        if isinstance(_state, Unset):
            state = UNSET
        else:
            state = RunnerJobStateConstant.from_dict(_state)

        _uuid = d.pop("uuid", UNSET)
        uuid: Unset | UUID
        if isinstance(_uuid, Unset):
            uuid = UNSET
        else:
            uuid = UUID(_uuid)

        runner_job_parent_type_0 = cls(
            type_=type_,
            state=state,
            uuid=uuid,
        )

        runner_job_parent_type_0.additional_properties = d
        return runner_job_parent_type_0

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
