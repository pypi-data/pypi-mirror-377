from collections.abc import Mapping
from typing import (
    TYPE_CHECKING,
    Any,
    TypeVar,
    Union,
)
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from typing_extensions import Self

from peertube.types import UNSET, Unset

if TYPE_CHECKING:
    from peertube.models.video_redundancy_redundancies import (
        VideoRedundancyRedundancies,
    )


T = TypeVar("T", bound="VideoRedundancy")


@_attrs_define
class VideoRedundancy:
    """Attributes:
    id (Union[Unset, int]):  Example: 42.
    name (Union[Unset, str]):
    url (Union[Unset, str]):
    uuid (Union[Unset, UUID]):  Example: 9c9de5e8-0a1e-484a-b099-e80766180a6d.
    redundancies (Union[Unset, VideoRedundancyRedundancies]):
    """

    id: Unset | int = UNSET
    name: Unset | str = UNSET
    url: Unset | str = UNSET
    uuid: Unset | UUID = UNSET
    redundancies: Union[Unset, "VideoRedundancyRedundancies"] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert instance to dictionary."""
        id = self.id

        name = self.name

        url = self.url

        uuid: Unset | str = UNSET
        if not isinstance(self.uuid, Unset):
            uuid = str(self.uuid)

        redundancies: Unset | dict[str, Any] = UNSET
        if not isinstance(self.redundancies, Unset):
            redundancies = self.redundancies.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if id is not UNSET:
            field_dict["id"] = id
        if name is not UNSET:
            field_dict["name"] = name
        if url is not UNSET:
            field_dict["url"] = url
        if uuid is not UNSET:
            field_dict["uuid"] = uuid
        if redundancies is not UNSET:
            field_dict["redundancies"] = redundancies

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        """Create instance from dictionary."""
        from peertube.models.video_redundancy_redundancies import (
            VideoRedundancyRedundancies,
        )

        d = dict(src_dict)
        id = d.pop("id", UNSET)

        name = d.pop("name", UNSET)

        url = d.pop("url", UNSET)

        _uuid = d.pop("uuid", UNSET)
        uuid: Unset | UUID
        if isinstance(_uuid, Unset):
            uuid = UNSET
        else:
            uuid = UUID(_uuid)

        _redundancies = d.pop("redundancies", UNSET)
        redundancies: Unset | VideoRedundancyRedundancies
        if isinstance(_redundancies, Unset):
            redundancies = UNSET
        else:
            redundancies = VideoRedundancyRedundancies.from_dict(_redundancies)

        video_redundancy = cls(
            id=id,
            name=name,
            url=url,
            uuid=uuid,
            redundancies=redundancies,
        )

        video_redundancy.additional_properties = d
        return video_redundancy

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
