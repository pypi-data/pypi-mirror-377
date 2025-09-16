import datetime
from collections.abc import Mapping
from typing import (
    Any,
    TypeVar,
)

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse
from typing_extensions import Self

from peertube.types import UNSET, Unset

T = TypeVar("T", bound="LiveSchedule")


@_attrs_define
class LiveSchedule:
    """Attributes:
    start_at (Union[Unset, datetime.datetime]): Date when the stream is scheduled to air at
    """

    start_at: Unset | datetime.datetime = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert instance to dictionary."""
        start_at: Unset | str = UNSET
        if not isinstance(self.start_at, Unset):
            start_at = self.start_at.isoformat()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if start_at is not UNSET:
            field_dict["startAt"] = start_at

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        """Create instance from dictionary."""
        d = dict(src_dict)
        _start_at = d.pop("startAt", UNSET)
        start_at: Unset | datetime.datetime
        if isinstance(_start_at, Unset):
            start_at = UNSET
        else:
            start_at = isoparse(_start_at)

        live_schedule = cls(
            start_at=start_at,
        )

        live_schedule.additional_properties = d
        return live_schedule

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
