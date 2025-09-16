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
    from peertube.models.video_stats_user_agent_clients_item import (
        VideoStatsUserAgentClientsItem,
    )
    from peertube.models.video_stats_user_agent_devices_item import (
        VideoStatsUserAgentDevicesItem,
    )
    from peertube.models.video_stats_user_agent_operating_system_item import (
        VideoStatsUserAgentOperatingSystemItem,
    )


T = TypeVar("T", bound="VideoStatsUserAgent")


@_attrs_define
class VideoStatsUserAgent:
    """Attributes:
    clients (Union[Unset, list['VideoStatsUserAgentClientsItem']]):
    devices (Union[Unset, list['VideoStatsUserAgentDevicesItem']]):
    operating_system (Union[Unset, list['VideoStatsUserAgentOperatingSystemItem']]):
    """

    clients: Unset | list["VideoStatsUserAgentClientsItem"] = UNSET
    devices: Unset | list["VideoStatsUserAgentDevicesItem"] = UNSET
    operating_system: Unset | list["VideoStatsUserAgentOperatingSystemItem"] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert instance to dictionary."""
        clients: Unset | list[dict[str, Any]] = UNSET
        if not isinstance(self.clients, Unset):
            clients = []
            for clients_item_data in self.clients:
                clients_item = clients_item_data.to_dict()
                clients.append(clients_item)

        devices: Unset | list[dict[str, Any]] = UNSET
        if not isinstance(self.devices, Unset):
            devices = []
            for devices_item_data in self.devices:
                devices_item = devices_item_data.to_dict()
                devices.append(devices_item)

        operating_system: Unset | list[dict[str, Any]] = UNSET
        if not isinstance(self.operating_system, Unset):
            operating_system = []
            for operating_system_item_data in self.operating_system:
                operating_system_item = operating_system_item_data.to_dict()
                operating_system.append(operating_system_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if clients is not UNSET:
            field_dict["clients"] = clients
        if devices is not UNSET:
            field_dict["devices"] = devices
        if operating_system is not UNSET:
            field_dict["operatingSystem"] = operating_system

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        """Create instance from dictionary."""
        from peertube.models.video_stats_user_agent_clients_item import (
            VideoStatsUserAgentClientsItem,
        )
        from peertube.models.video_stats_user_agent_devices_item import (
            VideoStatsUserAgentDevicesItem,
        )
        from peertube.models.video_stats_user_agent_operating_system_item import (
            VideoStatsUserAgentOperatingSystemItem,
        )

        d = dict(src_dict)
        clients = []
        _clients = d.pop("clients", UNSET)
        for clients_item_data in _clients or []:
            clients_item = VideoStatsUserAgentClientsItem.from_dict(clients_item_data)

            clients.append(clients_item)

        devices = []
        _devices = d.pop("devices", UNSET)
        for devices_item_data in _devices or []:
            devices_item = VideoStatsUserAgentDevicesItem.from_dict(devices_item_data)

            devices.append(devices_item)

        operating_system = []
        _operating_system = d.pop("operatingSystem", UNSET)
        for operating_system_item_data in _operating_system or []:
            operating_system_item = VideoStatsUserAgentOperatingSystemItem.from_dict(
                operating_system_item_data
            )

            operating_system.append(operating_system_item)

        video_stats_user_agent = cls(
            clients=clients,
            devices=devices,
            operating_system=operating_system,
        )

        video_stats_user_agent.additional_properties = d
        return video_stats_user_agent

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
