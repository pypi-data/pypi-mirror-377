from collections.abc import Mapping
from typing import (
    Any,
    TypeVar,
)

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from typing_extensions import Self

from peertube.types import UNSET, Unset

T = TypeVar("T", bound="OAuthClient")


@_attrs_define
class OAuthClient:
    """Attributes:
    client_id (Union[Unset, str]):  Example: v1ikx5hnfop4mdpnci8nsqh93c45rldf.
    client_secret (Union[Unset, str]):  Example: AjWiOapPltI6EnsWQwlFarRtLh4u8tDt.
    """

    client_id: Unset | str = UNSET
    client_secret: Unset | str = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert instance to dictionary."""
        client_id = self.client_id

        client_secret = self.client_secret

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if client_id is not UNSET:
            field_dict["client_id"] = client_id
        if client_secret is not UNSET:
            field_dict["client_secret"] = client_secret

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        """Create instance from dictionary."""
        d = dict(src_dict)
        client_id = d.pop("client_id", UNSET)

        client_secret = d.pop("client_secret", UNSET)

        o_auth_client = cls(
            client_id=client_id,
            client_secret=client_secret,
        )

        o_auth_client.additional_properties = d
        return o_auth_client

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
