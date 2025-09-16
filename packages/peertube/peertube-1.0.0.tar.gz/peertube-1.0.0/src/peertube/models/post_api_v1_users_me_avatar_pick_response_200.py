from collections.abc import Mapping
from typing import (
    TYPE_CHECKING,
    Any,
    TypeVar,
)

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from typing_extensions import Self

from peertube.types import UNSET, Unset

if TYPE_CHECKING:
    from peertube.models.actor_image import ActorImage


T = TypeVar("T", bound="PostApiV1UsersMeAvatarPickResponse200")


@_attrs_define
class PostApiV1UsersMeAvatarPickResponse200:
    """Attributes:
    avatars (Union[Unset, list['ActorImage']]):
    """

    avatars: Unset | list["ActorImage"] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert instance to dictionary."""
        avatars: Unset | list[dict[str, Any]] = UNSET
        if not isinstance(self.avatars, Unset):
            avatars = []
            for avatars_item_data in self.avatars:
                avatars_item = avatars_item_data.to_dict()
                avatars.append(avatars_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if avatars is not UNSET:
            field_dict["avatars"] = avatars

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        """Create instance from dictionary."""
        from peertube.models.actor_image import ActorImage

        d = dict(src_dict)
        avatars = []
        _avatars = d.pop("avatars", UNSET)
        for avatars_item_data in _avatars or []:
            avatars_item = ActorImage.from_dict(avatars_item_data)

            avatars.append(avatars_item)

        post_api_v1_users_me_avatar_pick_response_200 = cls(
            avatars=avatars,
        )

        post_api_v1_users_me_avatar_pick_response_200.additional_properties = d
        return post_api_v1_users_me_avatar_pick_response_200

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
