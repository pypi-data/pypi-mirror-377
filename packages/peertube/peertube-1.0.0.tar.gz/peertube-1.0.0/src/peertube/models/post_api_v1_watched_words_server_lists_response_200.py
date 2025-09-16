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
    from peertube.models.post_api_v1_watched_words_server_lists_response_200_watched_words_list import (
        PostApiV1WatchedWordsServerListsResponse200WatchedWordsList,
    )


T = TypeVar("T", bound="PostApiV1WatchedWordsServerListsResponse200")


@_attrs_define
class PostApiV1WatchedWordsServerListsResponse200:
    """Attributes:
    watched_words_list (Union[Unset, PostApiV1WatchedWordsServerListsResponse200WatchedWordsList]):
    """

    watched_words_list: Union[
        Unset, "PostApiV1WatchedWordsServerListsResponse200WatchedWordsList"
    ] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert instance to dictionary."""
        watched_words_list: Unset | dict[str, Any] = UNSET
        if not isinstance(self.watched_words_list, Unset):
            watched_words_list = self.watched_words_list.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if watched_words_list is not UNSET:
            field_dict["watchedWordsList"] = watched_words_list

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        """Create instance from dictionary."""
        from peertube.models.post_api_v1_watched_words_server_lists_response_200_watched_words_list import (
            PostApiV1WatchedWordsServerListsResponse200WatchedWordsList,
        )

        d = dict(src_dict)
        _watched_words_list = d.pop("watchedWordsList", UNSET)
        watched_words_list: (
            Unset | PostApiV1WatchedWordsServerListsResponse200WatchedWordsList
        )
        if isinstance(_watched_words_list, Unset):
            watched_words_list = UNSET
        else:
            watched_words_list = (
                PostApiV1WatchedWordsServerListsResponse200WatchedWordsList.from_dict(
                    _watched_words_list
                )
            )

        post_api_v1_watched_words_server_lists_response_200 = cls(
            watched_words_list=watched_words_list,
        )

        post_api_v1_watched_words_server_lists_response_200.additional_properties = d
        return post_api_v1_watched_words_server_lists_response_200

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
