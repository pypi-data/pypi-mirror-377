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
    from peertube.models.server_config_custom_defaults_p2p import (
        ServerConfigCustomDefaultsP2P,
    )
    from peertube.models.server_config_custom_defaults_player import (
        ServerConfigCustomDefaultsPlayer,
    )
    from peertube.models.server_config_custom_defaults_publish import (
        ServerConfigCustomDefaultsPublish,
    )


T = TypeVar("T", bound="ServerConfigCustomDefaults")


@_attrs_define
class ServerConfigCustomDefaults:
    """Attributes:
    publish (Union[Unset, ServerConfigCustomDefaultsPublish]):
    p2p (Union[Unset, ServerConfigCustomDefaultsP2P]):
    player (Union[Unset, ServerConfigCustomDefaultsPlayer]):
    """

    publish: Union[Unset, "ServerConfigCustomDefaultsPublish"] = UNSET
    p2p: Union[Unset, "ServerConfigCustomDefaultsP2P"] = UNSET
    player: Union[Unset, "ServerConfigCustomDefaultsPlayer"] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert instance to dictionary."""
        publish: Unset | dict[str, Any] = UNSET
        if not isinstance(self.publish, Unset):
            publish = self.publish.to_dict()

        p2p: Unset | dict[str, Any] = UNSET
        if not isinstance(self.p2p, Unset):
            p2p = self.p2p.to_dict()

        player: Unset | dict[str, Any] = UNSET
        if not isinstance(self.player, Unset):
            player = self.player.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if publish is not UNSET:
            field_dict["publish"] = publish
        if p2p is not UNSET:
            field_dict["p2p"] = p2p
        if player is not UNSET:
            field_dict["player"] = player

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        """Create instance from dictionary."""
        from peertube.models.server_config_custom_defaults_p2p import (
            ServerConfigCustomDefaultsP2P,
        )
        from peertube.models.server_config_custom_defaults_player import (
            ServerConfigCustomDefaultsPlayer,
        )
        from peertube.models.server_config_custom_defaults_publish import (
            ServerConfigCustomDefaultsPublish,
        )

        d = dict(src_dict)
        _publish = d.pop("publish", UNSET)
        publish: Unset | ServerConfigCustomDefaultsPublish
        if isinstance(_publish, Unset):
            publish = UNSET
        else:
            publish = ServerConfigCustomDefaultsPublish.from_dict(_publish)

        _p2p = d.pop("p2p", UNSET)
        p2p: Unset | ServerConfigCustomDefaultsP2P
        if isinstance(_p2p, Unset):
            p2p = UNSET
        else:
            p2p = ServerConfigCustomDefaultsP2P.from_dict(_p2p)

        _player = d.pop("player", UNSET)
        player: Unset | ServerConfigCustomDefaultsPlayer
        if isinstance(_player, Unset):
            player = UNSET
        else:
            player = ServerConfigCustomDefaultsPlayer.from_dict(_player)

        server_config_custom_defaults = cls(
            publish=publish,
            p2p=p2p,
            player=player,
        )

        server_config_custom_defaults.additional_properties = d
        return server_config_custom_defaults

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
