import datetime
from collections.abc import Mapping
from typing import (
    TYPE_CHECKING,
    Any,
    TypeVar,
    cast,
)

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse
from typing_extensions import Self

from peertube.types import UNSET, Unset

if TYPE_CHECKING:
    from peertube.models.actor_image import ActorImage


T = TypeVar("T", bound="Actor")


@_attrs_define
class Actor:
    """Attributes:
    id (Union[Unset, int]):  Example: 42.
    url (Union[Unset, str]):
    name (Union[Unset, str]): immutable name of the user, used to find or mention its actor Example: chocobozzz.
    avatars (Union[Unset, list['ActorImage']]):
    host (Union[Unset, str]): server on which the actor is resident
    host_redundancy_allowed (Union[None, Unset, bool]): whether this actor's host allows redundancy of its videos
    following_count (Union[Unset, int]): number of actors subscribed to by this actor, as seen by this instance
    followers_count (Union[Unset, int]): number of followers of this actor, as seen by this instance
    created_at (Union[Unset, datetime.datetime]):
    updated_at (Union[Unset, datetime.datetime]):
    """

    id: Unset | int = UNSET
    url: Unset | str = UNSET
    name: Unset | str = UNSET
    avatars: Unset | list["ActorImage"] = UNSET
    host: Unset | str = UNSET
    host_redundancy_allowed: None | Unset | bool = UNSET
    following_count: Unset | int = UNSET
    followers_count: Unset | int = UNSET
    created_at: Unset | datetime.datetime = UNSET
    updated_at: Unset | datetime.datetime = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert instance to dictionary."""
        id = self.id

        url = self.url

        name = self.name

        avatars: Unset | list[dict[str, Any]] = UNSET
        if not isinstance(self.avatars, Unset):
            avatars = []
            for avatars_item_data in self.avatars:
                avatars_item = avatars_item_data.to_dict()
                avatars.append(avatars_item)

        host = self.host

        host_redundancy_allowed: None | Unset | bool
        if isinstance(self.host_redundancy_allowed, Unset):
            host_redundancy_allowed = UNSET
        else:
            host_redundancy_allowed = self.host_redundancy_allowed

        following_count = self.following_count

        followers_count = self.followers_count

        created_at: Unset | str = UNSET
        if not isinstance(self.created_at, Unset):
            created_at = self.created_at.isoformat()

        updated_at: Unset | str = UNSET
        if not isinstance(self.updated_at, Unset):
            updated_at = self.updated_at.isoformat()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if id is not UNSET:
            field_dict["id"] = id
        if url is not UNSET:
            field_dict["url"] = url
        if name is not UNSET:
            field_dict["name"] = name
        if avatars is not UNSET:
            field_dict["avatars"] = avatars
        if host is not UNSET:
            field_dict["host"] = host
        if host_redundancy_allowed is not UNSET:
            field_dict["hostRedundancyAllowed"] = host_redundancy_allowed
        if following_count is not UNSET:
            field_dict["followingCount"] = following_count
        if followers_count is not UNSET:
            field_dict["followersCount"] = followers_count
        if created_at is not UNSET:
            field_dict["createdAt"] = created_at
        if updated_at is not UNSET:
            field_dict["updatedAt"] = updated_at

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        """Create instance from dictionary."""
        from peertube.models.actor_image import ActorImage

        d = dict(src_dict)
        id = d.pop("id", UNSET)

        url = d.pop("url", UNSET)

        name = d.pop("name", UNSET)

        avatars = []
        _avatars = d.pop("avatars", UNSET)
        for avatars_item_data in _avatars or []:
            avatars_item = ActorImage.from_dict(avatars_item_data)

            avatars.append(avatars_item)

        host = d.pop("host", UNSET)

        def _parse_host_redundancy_allowed(data: object) -> None | Unset | bool:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast("None | Unset | bool", data)

        host_redundancy_allowed = _parse_host_redundancy_allowed(
            d.pop("hostRedundancyAllowed", UNSET)
        )

        following_count = d.pop("followingCount", UNSET)

        followers_count = d.pop("followersCount", UNSET)

        _created_at = d.pop("createdAt", UNSET)
        created_at: Unset | datetime.datetime
        if isinstance(_created_at, Unset):
            created_at = UNSET
        else:
            created_at = isoparse(_created_at)

        _updated_at = d.pop("updatedAt", UNSET)
        updated_at: Unset | datetime.datetime
        if isinstance(_updated_at, Unset):
            updated_at = UNSET
        else:
            updated_at = isoparse(_updated_at)

        actor = cls(
            id=id,
            url=url,
            name=name,
            avatars=avatars,
            host=host,
            host_redundancy_allowed=host_redundancy_allowed,
            following_count=following_count,
            followers_count=followers_count,
            created_at=created_at,
            updated_at=updated_at,
        )

        actor.additional_properties = d
        return actor

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
