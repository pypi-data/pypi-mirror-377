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

from peertube import types
from peertube.types import UNSET, Unset

T = TypeVar("T", bound="PostApiV1UsersMeHistoryVideosRemoveBody")


@_attrs_define
class PostApiV1UsersMeHistoryVideosRemoveBody:
    """Attributes:
    before_date (Union[Unset, datetime.datetime]): history before this date will be deleted
    """

    before_date: Unset | datetime.datetime = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert instance to dictionary."""
        """Convert instance to dictionary."""
        """Convert instance to dictionary."""
        """Convert instance to dictionary."""
        """Convert instance to dictionary."""
        """Convert instance to dictionary."""
        """Convert instance to dictionary."""
        """Convert instance to dictionary."""
        """Convert instance to dictionary."""
        """Convert instance to dictionary."""
        """Convert instance to dictionary."""
        """Convert instance to dictionary."""
        """Convert instance to dictionary."""
        """Convert instance to dictionary."""
        """Convert instance to dictionary."""
        """Convert instance to dictionary."""
        """Convert instance to dictionary."""
        """Convert instance to dictionary."""
        """Convert instance to dictionary."""
        """Convert instance to dictionary."""
        """Convert instance to dictionary."""
        """Convert instance to dictionary."""
        """Convert instance to dictionary."""
        """Convert instance to dictionary."""
        """Convert instance to dictionary."""
        before_date: Unset | str = UNSET
        if not isinstance(self.before_date, Unset):
            before_date = self.before_date.isoformat()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if before_date is not UNSET:
            field_dict["beforeDate"] = before_date

        return field_dict

    def to_multipart(self) -> types.RequestFiles:
        """Convert to multipart form data."""
        files: types.RequestFiles = []

        if not isinstance(self.before_date, Unset):
            files.append(
                (
                    "beforeDate",
                    (None, self.before_date.isoformat().encode(), "text/plain"),
                )
            )

        for prop_name, prop in self.additional_properties.items():
            files.append((prop_name, (None, str(prop).encode(), "text/plain")))

        return files

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        """Create instance from dictionary."""
        """Create instance from dictionary."""
        """Create instance from dictionary."""
        """Create instance from dictionary."""
        """Create instance from dictionary."""
        """Create instance from dictionary."""
        """Create instance from dictionary."""
        """Create instance from dictionary."""
        """Create instance from dictionary."""
        """Create instance from dictionary."""
        """Create instance from dictionary."""
        """Create instance from dictionary."""
        """Create instance from dictionary."""
        """Create instance from dictionary."""
        """Create instance from dictionary."""
        """Create instance from dictionary."""
        """Create instance from dictionary."""
        """Create instance from dictionary."""
        """Create instance from dictionary."""
        """Create instance from dictionary."""
        """Create instance from dictionary."""
        """Create instance from dictionary."""
        """Create instance from dictionary."""
        """Create instance from dictionary."""
        """Create instance from dictionary."""
        d = dict(src_dict)
        _before_date = d.pop("beforeDate", UNSET)
        before_date: Unset | datetime.datetime
        if isinstance(_before_date, Unset):
            before_date = UNSET
        else:
            before_date = isoparse(_before_date)

        post_api_v1_users_me_history_videos_remove_body = cls(
            before_date=before_date,
        )

        post_api_v1_users_me_history_videos_remove_body.additional_properties = d
        return post_api_v1_users_me_history_videos_remove_body

    @property
    def additional_keys(self) -> list[str]:
        """Get additional property keys."""
        """Get additional property keys."""
        """Get additional property keys."""
        """Get additional property keys."""
        """Get additional property keys."""
        """Get additional property keys."""
        """Get additional property keys."""
        """Get additional property keys."""
        """Get additional property keys."""
        """Get additional property keys."""
        """Get additional property keys."""
        """Get additional property keys."""
        """Get additional property keys."""
        """Get additional property keys."""
        """Get additional property keys."""
        """Get additional property keys."""
        """Get additional property keys."""
        """Get additional property keys."""
        """Get additional property keys."""
        """Get additional property keys."""
        """Get additional property keys."""
        """Get additional property keys."""
        """Get additional property keys."""
        """Get additional property keys."""
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
