from collections.abc import Mapping
from typing import (
    Any,
    TypeVar,
)

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from typing_extensions import Self

from peertube.types import UNSET, Unset

T = TypeVar("T", bound="PostApiV1RunnersRegisterBody")


@_attrs_define
class PostApiV1RunnersRegisterBody:
    """Attributes:
    registration_token (str):
    name (str):
    description (Union[Unset, str]):
    """

    registration_token: str
    name: str
    description: Unset | str = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert instance to dictionary."""
        registration_token = self.registration_token

        name = self.name

        description = self.description

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "registrationToken": registration_token,
                "name": name,
            }
        )
        if description is not UNSET:
            field_dict["description"] = description

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        """Create instance from dictionary."""
        d = dict(src_dict)
        registration_token = d.pop("registrationToken")

        name = d.pop("name")

        description = d.pop("description", UNSET)

        post_api_v1_runners_register_body = cls(
            registration_token=registration_token,
            name=name,
            description=description,
        )

        post_api_v1_runners_register_body.additional_properties = d
        return post_api_v1_runners_register_body

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
