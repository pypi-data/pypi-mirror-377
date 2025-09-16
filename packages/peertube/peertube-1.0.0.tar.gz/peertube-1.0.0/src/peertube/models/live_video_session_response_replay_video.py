from collections.abc import Mapping
from typing import (
    Any,
    TypeVar,
)
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from typing_extensions import Self

from peertube.types import UNSET, Unset

T = TypeVar("T", bound="LiveVideoSessionResponseReplayVideo")


@_attrs_define
class LiveVideoSessionResponseReplayVideo:
    """Video replay information

    Attributes:
        id (Union[Unset, float]):
        uuid (Union[Unset, UUID]):  Example: 9c9de5e8-0a1e-484a-b099-e80766180a6d.
        short_uuid (Union[Unset, str]): translation of a uuid v4 with a bigger alphabet to have a shorter uuid Example:
            2y84q2MQUMWPbiEcxNXMgC.
    """

    id: Unset | float = UNSET
    uuid: Unset | UUID = UNSET
    short_uuid: Unset | str = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert instance to dictionary."""
        id = self.id

        uuid: Unset | str = UNSET
        if not isinstance(self.uuid, Unset):
            uuid = str(self.uuid)

        short_uuid = self.short_uuid

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if id is not UNSET:
            field_dict["id"] = id
        if uuid is not UNSET:
            field_dict["uuid"] = uuid
        if short_uuid is not UNSET:
            field_dict["shortUUID"] = short_uuid

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        """Create instance from dictionary."""
        d = dict(src_dict)
        id = d.pop("id", UNSET)

        _uuid = d.pop("uuid", UNSET)
        uuid: Unset | UUID
        if isinstance(_uuid, Unset):
            uuid = UNSET
        else:
            uuid = UUID(_uuid)

        short_uuid = d.pop("shortUUID", UNSET)

        live_video_session_response_replay_video = cls(
            id=id,
            uuid=uuid,
            short_uuid=short_uuid,
        )

        live_video_session_response_replay_video.additional_properties = d
        return live_video_session_response_replay_video

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
