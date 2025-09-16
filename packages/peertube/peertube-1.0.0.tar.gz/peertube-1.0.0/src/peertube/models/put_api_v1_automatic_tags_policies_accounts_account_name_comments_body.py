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

T = TypeVar("T", bound="PutApiV1AutomaticTagsPoliciesAccountsAccountNameCommentsBody")


@_attrs_define
class PutApiV1AutomaticTagsPoliciesAccountsAccountNameCommentsBody:
    """Attributes:
    review (Union[Unset, list[str]]): Auto tags that automatically set the comment in review state
    """

    review: Unset | list[str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert instance to dictionary."""
        review: Unset | list[str] = UNSET
        if not isinstance(self.review, Unset):
            review = self.review

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if review is not UNSET:
            field_dict["review"] = review

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        """Create instance from dictionary."""
        d = dict(src_dict)
        review = cast("list[str]", d.pop("review", UNSET))

        put_api_v1_automatic_tags_policies_accounts_account_name_comments_body = cls(
            review=review,
        )

        put_api_v1_automatic_tags_policies_accounts_account_name_comments_body.additional_properties = d
        return put_api_v1_automatic_tags_policies_accounts_account_name_comments_body

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
