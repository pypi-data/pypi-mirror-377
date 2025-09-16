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
    from peertube.models.server_config_video_file import ServerConfigVideoFile
    from peertube.models.server_config_video_image import ServerConfigVideoImage


T = TypeVar("T", bound="ServerConfigVideo")


@_attrs_define
class ServerConfigVideo:
    """Attributes:
    image (Union[Unset, ServerConfigVideoImage]):
    file (Union[Unset, ServerConfigVideoFile]):
    """

    image: Union[Unset, "ServerConfigVideoImage"] = UNSET
    file: Union[Unset, "ServerConfigVideoFile"] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert instance to dictionary."""
        image: Unset | dict[str, Any] = UNSET
        if not isinstance(self.image, Unset):
            image = self.image.to_dict()

        file: Unset | dict[str, Any] = UNSET
        if not isinstance(self.file, Unset):
            file = self.file.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if image is not UNSET:
            field_dict["image"] = image
        if file is not UNSET:
            field_dict["file"] = file

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        """Create instance from dictionary."""
        from peertube.models.server_config_video_file import ServerConfigVideoFile
        from peertube.models.server_config_video_image import ServerConfigVideoImage

        d = dict(src_dict)
        _image = d.pop("image", UNSET)
        image: Unset | ServerConfigVideoImage
        if isinstance(_image, Unset):
            image = UNSET
        else:
            image = ServerConfigVideoImage.from_dict(_image)

        _file = d.pop("file", UNSET)
        file: Unset | ServerConfigVideoFile
        if isinstance(_file, Unset):
            file = UNSET
        else:
            file = ServerConfigVideoFile.from_dict(_file)

        server_config_video = cls(
            image=image,
            file=file,
        )

        server_config_video.additional_properties = d
        return server_config_video

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
