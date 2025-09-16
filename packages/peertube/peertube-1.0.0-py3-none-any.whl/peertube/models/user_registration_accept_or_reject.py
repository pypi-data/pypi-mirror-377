from collections.abc import Mapping
from typing import (
    Any,
    TypeVar,
)

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from typing_extensions import Self

from peertube.types import UNSET, Unset

T = TypeVar("T", bound="UserRegistrationAcceptOrReject")


@_attrs_define
class UserRegistrationAcceptOrReject:
    """Attributes:
    moderation_response (str): Moderation response to send to the user
    prevent_email_delivery (Union[Unset, bool]): Set it to true if you don't want PeerTube to send an email to the
        user
    """

    moderation_response: str
    prevent_email_delivery: Unset | bool = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert instance to dictionary."""
        moderation_response = self.moderation_response

        prevent_email_delivery = self.prevent_email_delivery

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "moderationResponse": moderation_response,
            }
        )
        if prevent_email_delivery is not UNSET:
            field_dict["preventEmailDelivery"] = prevent_email_delivery

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        """Create instance from dictionary."""
        d = dict(src_dict)
        moderation_response = d.pop("moderationResponse")

        prevent_email_delivery = d.pop("preventEmailDelivery", UNSET)

        user_registration_accept_or_reject = cls(
            moderation_response=moderation_response,
            prevent_email_delivery=prevent_email_delivery,
        )

        user_registration_accept_or_reject.additional_properties = d
        return user_registration_accept_or_reject

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
