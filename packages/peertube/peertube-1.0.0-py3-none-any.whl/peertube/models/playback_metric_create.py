from collections.abc import Mapping
from typing import (
    Any,
    TypeVar,
    cast,
)
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from typing_extensions import Self

from peertube.models.playback_metric_create_player_mode import (
    PlaybackMetricCreatePlayerMode,
)
from peertube.types import UNSET, Unset

T = TypeVar("T", bound="PlaybackMetricCreate")


@_attrs_define
class PlaybackMetricCreate:
    """Attributes:
    player_mode (PlaybackMetricCreatePlayerMode):
    p_2_p_enabled (bool):
    resolution_changes (float): How many resolution changes occurred since the last metric creation
    errors (float): How many errors occurred since the last metric creation
    downloaded_bytes_p2p (float): How many bytes were downloaded with P2P since the last metric creation
    downloaded_bytes_http (float): How many bytes were downloaded with HTTP since the last metric creation
    uploaded_bytes_p2p (float): How many bytes were uploaded with P2P since the last metric creation
    video_id (Union[UUID, int, str]):
    resolution (Union[Unset, float]): Current player video resolution
    fps (Union[Unset, float]): Current player video fps
    p_2_p_peers (Union[Unset, float]): P2P peers connected (doesn't include WebSeed peers)
    buffer_stalled (Union[Unset, float]): How many times buffer has been stalled since the last metric creation
    """

    player_mode: PlaybackMetricCreatePlayerMode
    p_2_p_enabled: bool
    resolution_changes: float
    errors: float
    downloaded_bytes_p2p: float
    downloaded_bytes_http: float
    uploaded_bytes_p2p: float
    video_id: UUID | int | str
    resolution: Unset | float = UNSET
    fps: Unset | float = UNSET
    p_2_p_peers: Unset | float = UNSET
    buffer_stalled: Unset | float = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        player_mode = self.player_mode.value

        p_2_p_enabled = self.p_2_p_enabled

        resolution_changes = self.resolution_changes

        errors = self.errors

        downloaded_bytes_p2p = self.downloaded_bytes_p2p

        downloaded_bytes_http = self.downloaded_bytes_http

        uploaded_bytes_p2p = self.uploaded_bytes_p2p

        video_id: int | str
        if isinstance(self.video_id, UUID):
            video_id = str(self.video_id)
        else:
            video_id = self.video_id

        resolution = self.resolution

        fps = self.fps

        p_2_p_peers = self.p_2_p_peers

        buffer_stalled = self.buffer_stalled

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "playerMode": player_mode,
                "p2pEnabled": p_2_p_enabled,
                "resolutionChanges": resolution_changes,
                "errors": errors,
                "downloadedBytesP2P": downloaded_bytes_p2p,
                "downloadedBytesHTTP": downloaded_bytes_http,
                "uploadedBytesP2P": uploaded_bytes_p2p,
                "videoId": video_id,
            }
        )
        if resolution is not UNSET:
            field_dict["resolution"] = resolution
        if fps is not UNSET:
            field_dict["fps"] = fps
        if p_2_p_peers is not UNSET:
            field_dict["p2pPeers"] = p_2_p_peers
        if buffer_stalled is not UNSET:
            field_dict["bufferStalled"] = buffer_stalled

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        """Create from dictionary."""
        d = dict(src_dict)
        player_mode = PlaybackMetricCreatePlayerMode(d.pop("playerMode"))

        p_2_p_enabled = d.pop("p2pEnabled")

        resolution_changes = d.pop("resolutionChanges")

        errors = d.pop("errors")

        downloaded_bytes_p2p = d.pop("downloadedBytesP2P")

        downloaded_bytes_http = d.pop("downloadedBytesHTTP")

        uploaded_bytes_p2p = d.pop("uploadedBytesP2P")

        def _parse_video_id(data: object) -> UUID | int | str:
            try:
                if not isinstance(data, str):
                    raise TypeError
                video_id_type_1 = UUID(data)

                return video_id_type_1
            except:  # noqa: E722
                pass
            return cast("UUID | int | str", data)

        video_id = _parse_video_id(d.pop("videoId"))

        resolution = d.pop("resolution", UNSET)

        fps = d.pop("fps", UNSET)

        p_2_p_peers = d.pop("p2pPeers", UNSET)

        buffer_stalled = d.pop("bufferStalled", UNSET)

        playback_metric_create = cls(
            player_mode=player_mode,
            p_2_p_enabled=p_2_p_enabled,
            resolution_changes=resolution_changes,
            errors=errors,
            downloaded_bytes_p2p=downloaded_bytes_p2p,
            downloaded_bytes_http=downloaded_bytes_http,
            uploaded_bytes_p2p=uploaded_bytes_p2p,
            video_id=video_id,
            resolution=resolution,
            fps=fps,
            p_2_p_peers=p_2_p_peers,
            buffer_stalled=buffer_stalled,
        )

        playback_metric_create.additional_properties = d
        return playback_metric_create

    @property
    def additional_keys(self) -> list[str]:
        """Get additional keys."""
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
