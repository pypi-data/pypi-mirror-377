from collections.abc import Mapping
from typing import (
    Any,
    TypeVar,
)

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from typing_extensions import Self

from peertube.types import UNSET, Unset

T = TypeVar("T", bound="RequestTwoFactorResponseOtpRequest")


@_attrs_define
class RequestTwoFactorResponseOtpRequest:
    """Attributes:
    request_token (Union[Unset, str]): The token to send to confirm this request
    secret (Union[Unset, str]): The OTP secret
    uri (Union[Unset, str]): The OTP URI
    """

    request_token: Unset | str = UNSET
    secret: Unset | str = UNSET
    uri: Unset | str = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert instance to dictionary."""
        request_token = self.request_token

        secret = self.secret

        uri = self.uri

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if request_token is not UNSET:
            field_dict["requestToken"] = request_token
        if secret is not UNSET:
            field_dict["secret"] = secret
        if uri is not UNSET:
            field_dict["uri"] = uri

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        """Create instance from dictionary."""
        d = dict(src_dict)
        request_token = d.pop("requestToken", UNSET)

        secret = d.pop("secret", UNSET)

        uri = d.pop("uri", UNSET)

        request_two_factor_response_otp_request = cls(
            request_token=request_token,
            secret=secret,
            uri=uri,
        )

        request_two_factor_response_otp_request.additional_properties = d
        return request_two_factor_response_otp_request

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
