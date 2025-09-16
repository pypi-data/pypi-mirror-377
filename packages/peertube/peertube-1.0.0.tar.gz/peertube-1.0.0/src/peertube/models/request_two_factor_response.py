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
    from peertube.models.request_two_factor_response_otp_request import (
        RequestTwoFactorResponseOtpRequest,
    )


T = TypeVar("T", bound="RequestTwoFactorResponse")


@_attrs_define
class RequestTwoFactorResponse:
    """Attributes:
    otp_request (Union[Unset, RequestTwoFactorResponseOtpRequest]):
    """

    otp_request: Union[Unset, "RequestTwoFactorResponseOtpRequest"] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert instance to dictionary."""
        otp_request: Unset | dict[str, Any] = UNSET
        if not isinstance(self.otp_request, Unset):
            otp_request = self.otp_request.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if otp_request is not UNSET:
            field_dict["otpRequest"] = otp_request

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        """Create instance from dictionary."""
        from peertube.models.request_two_factor_response_otp_request import (
            RequestTwoFactorResponseOtpRequest,
        )

        d = dict(src_dict)
        _otp_request = d.pop("otpRequest", UNSET)
        otp_request: Unset | RequestTwoFactorResponseOtpRequest
        if isinstance(_otp_request, Unset):
            otp_request = UNSET
        else:
            otp_request = RequestTwoFactorResponseOtpRequest.from_dict(_otp_request)

        request_two_factor_response = cls(
            otp_request=otp_request,
        )

        request_two_factor_response.additional_properties = d
        return request_two_factor_response

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
