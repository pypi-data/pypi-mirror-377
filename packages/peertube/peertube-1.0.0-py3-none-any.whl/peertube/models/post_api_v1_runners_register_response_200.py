from collections.abc import Mapping
from typing import (
    Any,
    TypeVar,
)

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from typing_extensions import Self

from peertube.types import UNSET, Unset

T = TypeVar("T", bound="PostApiV1RunnersRegisterResponse200")


@_attrs_define
class PostApiV1RunnersRegisterResponse200:
    """Attributes:
    id (Union[Unset, int]): Runner id
    runner_token (Union[Unset, str]):
    """

    id: Unset | int = UNSET
    runner_token: Unset | str = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert instance to dictionary."""
        id = self.id

        runner_token = self.runner_token

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if id is not UNSET:
            field_dict["id"] = id
        if runner_token is not UNSET:
            field_dict["runnerToken"] = runner_token

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        """Create instance from dictionary."""
        d = dict(src_dict)
        id = d.pop("id", UNSET)

        runner_token = d.pop("runnerToken", UNSET)

        post_api_v1_runners_register_response_200 = cls(
            id=id,
            runner_token=runner_token,
        )

        post_api_v1_runners_register_response_200.additional_properties = d
        return post_api_v1_runners_register_response_200

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
