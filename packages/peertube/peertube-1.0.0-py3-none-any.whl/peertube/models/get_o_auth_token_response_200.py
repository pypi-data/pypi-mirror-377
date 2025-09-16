from collections.abc import Mapping
from typing import (
    Any,
    TypeVar,
)

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from typing_extensions import Self

from peertube.types import UNSET, Unset

T = TypeVar("T", bound="GetOAuthTokenResponse200")


@_attrs_define
class GetOAuthTokenResponse200:
    """Attributes:
    token_type (Union[Unset, str]):  Example: Bearer.
    access_token (Union[Unset, str]): valid for 1 day Example: 90286a0bdf0f7315d9d3fe8dabf9e1d2be9c97d0.
    refresh_token (Union[Unset, str]): valid for 2 weeks Example: 2e0d675df9fc96d2e4ec8a3ebbbf45eca9137bb7.
    expires_in (Union[Unset, int]):  Example: 14399.
    refresh_token_expires_in (Union[Unset, int]):  Example: 1209600.
    """

    token_type: Unset | str = UNSET
    access_token: Unset | str = UNSET
    refresh_token: Unset | str = UNSET
    expires_in: Unset | int = UNSET
    refresh_token_expires_in: Unset | int = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert instance to dictionary."""
        token_type = self.token_type

        access_token = self.access_token

        refresh_token = self.refresh_token

        expires_in = self.expires_in

        refresh_token_expires_in = self.refresh_token_expires_in

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if token_type is not UNSET:
            field_dict["token_type"] = token_type
        if access_token is not UNSET:
            field_dict["access_token"] = access_token
        if refresh_token is not UNSET:
            field_dict["refresh_token"] = refresh_token
        if expires_in is not UNSET:
            field_dict["expires_in"] = expires_in
        if refresh_token_expires_in is not UNSET:
            field_dict["refresh_token_expires_in"] = refresh_token_expires_in

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        """Create instance from dictionary."""
        d = dict(src_dict)
        token_type = d.pop("token_type", UNSET)

        access_token = d.pop("access_token", UNSET)

        refresh_token = d.pop("refresh_token", UNSET)

        expires_in = d.pop("expires_in", UNSET)

        refresh_token_expires_in = d.pop("refresh_token_expires_in", UNSET)

        get_o_auth_token_response_200 = cls(
            token_type=token_type,
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=expires_in,
            refresh_token_expires_in=refresh_token_expires_in,
        )

        get_o_auth_token_response_200.additional_properties = d
        return get_o_auth_token_response_200

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
