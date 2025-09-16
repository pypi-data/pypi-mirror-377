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
    from peertube.models.server_config_followings_instance_auto_follow_index import (
        ServerConfigFollowingsInstanceAutoFollowIndex,
    )


T = TypeVar("T", bound="ServerConfigFollowingsInstance")


@_attrs_define
class ServerConfigFollowingsInstance:
    """Attributes:
    auto_follow_index (Union[Unset, ServerConfigFollowingsInstanceAutoFollowIndex]):
    """

    auto_follow_index: Union[Unset, "ServerConfigFollowingsInstanceAutoFollowIndex"] = (
        UNSET
    )
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert instance to dictionary."""
        auto_follow_index: Unset | dict[str, Any] = UNSET
        if not isinstance(self.auto_follow_index, Unset):
            auto_follow_index = self.auto_follow_index.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if auto_follow_index is not UNSET:
            field_dict["autoFollowIndex"] = auto_follow_index

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        """Create instance from dictionary."""
        from peertube.models.server_config_followings_instance_auto_follow_index import (
            ServerConfigFollowingsInstanceAutoFollowIndex,
        )

        d = dict(src_dict)
        _auto_follow_index = d.pop("autoFollowIndex", UNSET)
        auto_follow_index: Unset | ServerConfigFollowingsInstanceAutoFollowIndex
        if isinstance(_auto_follow_index, Unset):
            auto_follow_index = UNSET
        else:
            auto_follow_index = ServerConfigFollowingsInstanceAutoFollowIndex.from_dict(
                _auto_follow_index
            )

        server_config_followings_instance = cls(
            auto_follow_index=auto_follow_index,
        )

        server_config_followings_instance.additional_properties = d
        return server_config_followings_instance

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
