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

T = TypeVar("T", bound="PutApiV1WatchedWordsServerListsListIdBody")


@_attrs_define
class PutApiV1WatchedWordsServerListsListIdBody:
    """Attributes:
    list_name (Union[Unset, str]):
    words (Union[Unset, list[str]]):
    """

    list_name: Unset | str = UNSET
    words: Unset | list[str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert instance to dictionary."""
        list_name = self.list_name

        words: Unset | list[str] = UNSET
        if not isinstance(self.words, Unset):
            words = self.words

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if list_name is not UNSET:
            field_dict["listName"] = list_name
        if words is not UNSET:
            field_dict["words"] = words

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        """Create instance from dictionary."""
        d = dict(src_dict)
        list_name = d.pop("listName", UNSET)

        words = cast("list[str]", d.pop("words", UNSET))

        put_api_v1_watched_words_server_lists_list_id_body = cls(
            list_name=list_name,
            words=words,
        )

        put_api_v1_watched_words_server_lists_list_id_body.additional_properties = d
        return put_api_v1_watched_words_server_lists_list_id_body

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
