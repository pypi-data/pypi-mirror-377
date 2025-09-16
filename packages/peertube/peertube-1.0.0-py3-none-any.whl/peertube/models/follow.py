import datetime
from collections.abc import Mapping
from typing import (
    TYPE_CHECKING,
    Any,
    TypeVar,
    Union,
)

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse
from typing_extensions import Self

from peertube.models.follow_state import FollowState
from peertube.types import UNSET, Unset

if TYPE_CHECKING:
    from peertube.models.actor import Actor


T = TypeVar("T", bound="Follow")


@_attrs_define
class Follow:
    """Attributes:
    id (Union[Unset, int]):  Example: 42.
    follower (Union[Unset, Actor]):
    following (Union[Unset, Actor]):
    score (Union[Unset, float]): score reflecting the reachability of the actor, with steps of `10` and a base score
        of `1000`.
    state (Union[Unset, FollowState]):
    created_at (Union[Unset, datetime.datetime]):
    updated_at (Union[Unset, datetime.datetime]):
    """

    id: Unset | int = UNSET
    follower: Union[Unset, "Actor"] = UNSET
    following: Union[Unset, "Actor"] = UNSET
    score: Unset | float = UNSET
    state: Unset | FollowState = UNSET
    created_at: Unset | datetime.datetime = UNSET
    updated_at: Unset | datetime.datetime = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert instance to dictionary."""
        id = self.id

        follower: Unset | dict[str, Any] = UNSET
        if not isinstance(self.follower, Unset):
            follower = self.follower.to_dict()

        following: Unset | dict[str, Any] = UNSET
        if not isinstance(self.following, Unset):
            following = self.following.to_dict()

        score = self.score

        state: Unset | str = UNSET
        if not isinstance(self.state, Unset):
            state = self.state.value

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
        if follower is not UNSET:
            field_dict["follower"] = follower
        if following is not UNSET:
            field_dict["following"] = following
        if score is not UNSET:
            field_dict["score"] = score
        if state is not UNSET:
            field_dict["state"] = state
        if created_at is not UNSET:
            field_dict["createdAt"] = created_at
        if updated_at is not UNSET:
            field_dict["updatedAt"] = updated_at

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        """Create instance from dictionary."""
        from peertube.models.actor import Actor

        d = dict(src_dict)
        id = d.pop("id", UNSET)

        _follower = d.pop("follower", UNSET)
        follower: Unset | Actor
        if isinstance(_follower, Unset):
            follower = UNSET
        else:
            follower = Actor.from_dict(_follower)

        _following = d.pop("following", UNSET)
        following: Unset | Actor
        if isinstance(_following, Unset):
            following = UNSET
        else:
            following = Actor.from_dict(_following)

        score = d.pop("score", UNSET)

        _state = d.pop("state", UNSET)
        state: Unset | FollowState
        if isinstance(_state, Unset):
            state = UNSET
        else:
            state = FollowState(_state)

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

        follow = cls(
            id=id,
            follower=follower,
            following=following,
            score=score,
            state=state,
            created_at=created_at,
            updated_at=updated_at,
        )

        follow.additional_properties = d
        return follow

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
