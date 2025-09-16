import datetime
from collections.abc import Mapping
from typing import (
    Any,
    TypeVar,
    cast,
)

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse
from typing_extensions import Self

from peertube.types import UNSET, Unset

T = TypeVar("T", bound="WatchedWordsLists")


@_attrs_define
class WatchedWordsLists:
    """Attributes:
    id (Union[Unset, int]):  Example: 42.
    list_name (Union[Unset, str]):
    words (Union[Unset, list[str]]):
    updated_at (Union[Unset, datetime.datetime]):  Example: 2021-05-04T08:01:01.502Z.
    created_at (Union[Unset, datetime.datetime]):  Example: 2021-05-04T08:01:01.502Z.
    """

    id: Unset | int = UNSET
    list_name: Unset | str = UNSET
    words: Unset | list[str] = UNSET
    updated_at: Unset | datetime.datetime = UNSET
    created_at: Unset | datetime.datetime = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert instance to dictionary."""
        id = self.id

        list_name = self.list_name

        words: Unset | list[str] = UNSET
        if not isinstance(self.words, Unset):
            words = self.words

        updated_at: Unset | str = UNSET
        if not isinstance(self.updated_at, Unset):
            updated_at = self.updated_at.isoformat()

        created_at: Unset | str = UNSET
        if not isinstance(self.created_at, Unset):
            created_at = self.created_at.isoformat()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if id is not UNSET:
            field_dict["id"] = id
        if list_name is not UNSET:
            field_dict["listName"] = list_name
        if words is not UNSET:
            field_dict["words"] = words
        if updated_at is not UNSET:
            field_dict["updatedAt"] = updated_at
        if created_at is not UNSET:
            field_dict["createdAt"] = created_at

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        """Create instance from dictionary."""
        d = dict(src_dict)
        id = d.pop("id", UNSET)

        list_name = d.pop("listName", UNSET)

        words = cast("list[str]", d.pop("words", UNSET))

        _updated_at = d.pop("updatedAt", UNSET)
        updated_at: Unset | datetime.datetime
        if isinstance(_updated_at, Unset):
            updated_at = UNSET
        else:
            updated_at = isoparse(_updated_at)

        _created_at = d.pop("createdAt", UNSET)
        created_at: Unset | datetime.datetime
        if isinstance(_created_at, Unset):
            created_at = UNSET
        else:
            created_at = isoparse(_created_at)

        watched_words_lists = cls(
            id=id,
            list_name=list_name,
            words=words,
            updated_at=updated_at,
            created_at=created_at,
        )

        watched_words_lists.additional_properties = d
        return watched_words_lists

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
