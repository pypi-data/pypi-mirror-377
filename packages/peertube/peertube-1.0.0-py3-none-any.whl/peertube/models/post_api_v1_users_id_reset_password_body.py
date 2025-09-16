from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from typing_extensions import Self

T = TypeVar("T", bound="PostApiV1UsersIdResetPasswordBody")


@_attrs_define
class PostApiV1UsersIdResetPasswordBody:
    """Attributes:
    verification_string (str):
    password (str):
    """

    verification_string: str
    password: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert instance to dictionary."""
        verification_string = self.verification_string

        password = self.password

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "verificationString": verification_string,
                "password": password,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        """Create instance from dictionary."""
        d = dict(src_dict)
        verification_string = d.pop("verificationString")

        password = d.pop("password")

        post_api_v1_users_id_reset_password_body = cls(
            verification_string=verification_string,
            password=password,
        )

        post_api_v1_users_id_reset_password_body.additional_properties = d
        return post_api_v1_users_id_reset_password_body

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
