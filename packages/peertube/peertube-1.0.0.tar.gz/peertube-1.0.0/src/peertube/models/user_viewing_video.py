from collections.abc import Mapping
from typing import (
    Any,
    TypeVar,
)

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from typing_extensions import Self

from peertube.models.user_viewing_video_view_event import UserViewingVideoViewEvent
from peertube.models.video_stats_user_agent_device import VideoStatsUserAgentDevice
from peertube.types import UNSET, Unset

T = TypeVar("T", bound="UserViewingVideo")


@_attrs_define
class UserViewingVideo:
    """Attributes:
    current_time (int): timestamp within the video, in seconds Example: 5.
    view_event (Union[Unset, UserViewingVideoViewEvent]): Event since last viewing call:
         * `seek` - If the user seeked the video
    session_id (Union[Unset, str]): Optional param to represent the current viewer session. Used by the backend to
        properly count one view per session per video. PeerTube admin can configure the server to not trust this
        `sessionId` parameter but use the request IP address instead to identify a viewer.
    client (Union[Unset, str]): Client software used to watch the video. For example "Firefox", "PeerTube Approval
        Android", etc.
    device (Union[Unset, VideoStatsUserAgentDevice]):
    operating_system (Union[Unset, str]): Operating system used to watch the video. For example "Windows", "Ubuntu",
        etc.
    """

    current_time: int
    view_event: Unset | UserViewingVideoViewEvent = UNSET
    session_id: Unset | str = UNSET
    client: Unset | str = UNSET
    device: Unset | VideoStatsUserAgentDevice = UNSET
    operating_system: Unset | str = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert instance to dictionary."""
        current_time = self.current_time

        view_event: Unset | str = UNSET
        if not isinstance(self.view_event, Unset):
            view_event = self.view_event.value

        session_id = self.session_id

        client = self.client

        device: Unset | str = UNSET
        if not isinstance(self.device, Unset):
            device = self.device.value

        operating_system = self.operating_system

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "currentTime": current_time,
            }
        )
        if view_event is not UNSET:
            field_dict["viewEvent"] = view_event
        if session_id is not UNSET:
            field_dict["sessionId"] = session_id
        if client is not UNSET:
            field_dict["client"] = client
        if device is not UNSET:
            field_dict["device"] = device
        if operating_system is not UNSET:
            field_dict["operatingSystem"] = operating_system

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        """Create instance from dictionary."""
        d = dict(src_dict)
        current_time = d.pop("currentTime")

        _view_event = d.pop("viewEvent", UNSET)
        view_event: Unset | UserViewingVideoViewEvent
        if isinstance(_view_event, Unset):
            view_event = UNSET
        else:
            view_event = UserViewingVideoViewEvent(_view_event)

        session_id = d.pop("sessionId", UNSET)

        client = d.pop("client", UNSET)

        _device = d.pop("device", UNSET)
        device: Unset | VideoStatsUserAgentDevice
        if isinstance(_device, Unset):
            device = UNSET
        else:
            device = VideoStatsUserAgentDevice(_device)

        operating_system = d.pop("operatingSystem", UNSET)

        user_viewing_video = cls(
            current_time=current_time,
            view_event=view_event,
            session_id=session_id,
            client=client,
            device=device,
            operating_system=operating_system,
        )

        user_viewing_video.additional_properties = d
        return user_viewing_video

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
