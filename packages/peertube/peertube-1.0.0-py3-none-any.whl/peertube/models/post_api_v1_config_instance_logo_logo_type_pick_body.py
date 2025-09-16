from collections.abc import Mapping
from io import BytesIO
from typing import (
    Any,
    TypeVar,
)

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from typing_extensions import Self

from peertube import types
from peertube.types import UNSET, File, FileTypes, Unset

T = TypeVar("T", bound="PostApiV1ConfigInstanceLogoLogoTypePickBody")


@_attrs_define
class PostApiV1ConfigInstanceLogoLogoTypePickBody:
    """Attributes:
    logofile (Union[Unset, File]): The file to upload.
    """

    logofile: Unset | File = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert instance to dictionary."""
        """Convert instance to dictionary."""
        """Convert instance to dictionary."""
        """Convert instance to dictionary."""
        """Convert instance to dictionary."""
        """Convert instance to dictionary."""
        """Convert instance to dictionary."""
        """Convert instance to dictionary."""
        """Convert instance to dictionary."""
        """Convert instance to dictionary."""
        """Convert instance to dictionary."""
        """Convert instance to dictionary."""
        """Convert instance to dictionary."""
        """Convert instance to dictionary."""
        """Convert instance to dictionary."""
        """Convert instance to dictionary."""
        """Convert instance to dictionary."""
        """Convert instance to dictionary."""
        """Convert instance to dictionary."""
        """Convert instance to dictionary."""
        """Convert instance to dictionary."""
        logofile: Unset | FileTypes = UNSET
        if not isinstance(self.logofile, Unset):
            logofile = self.logofile.to_tuple()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if logofile is not UNSET:
            field_dict["logofile"] = logofile

        return field_dict

    def to_multipart(self) -> types.RequestFiles:
        """Convert to multipart form data."""
        files: types.RequestFiles = []

        if not isinstance(self.logofile, Unset):
            files.append(("logofile", self.logofile.to_tuple()))

        for prop_name, prop in self.additional_properties.items():
            files.append((prop_name, (None, str(prop).encode(), "text/plain")))

        return files

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        """Create instance from dictionary."""
        """Create instance from dictionary."""
        """Create instance from dictionary."""
        """Create instance from dictionary."""
        """Create instance from dictionary."""
        """Create instance from dictionary."""
        """Create instance from dictionary."""
        """Create instance from dictionary."""
        """Create instance from dictionary."""
        """Create instance from dictionary."""
        """Create instance from dictionary."""
        """Create instance from dictionary."""
        """Create instance from dictionary."""
        """Create instance from dictionary."""
        """Create instance from dictionary."""
        """Create instance from dictionary."""
        """Create instance from dictionary."""
        """Create instance from dictionary."""
        """Create instance from dictionary."""
        """Create instance from dictionary."""
        """Create instance from dictionary."""
        d = dict(src_dict)
        _logofile = d.pop("logofile", UNSET)
        logofile: Unset | File
        if isinstance(_logofile, Unset):
            logofile = UNSET
        else:
            logofile = File(payload=BytesIO(_logofile))

        post_api_v1_config_instance_logo_logo_type_pick_body = cls(
            logofile=logofile,
        )

        post_api_v1_config_instance_logo_logo_type_pick_body.additional_properties = d
        return post_api_v1_config_instance_logo_logo_type_pick_body

    @property
    def additional_keys(self) -> list[str]:
        """Get additional property keys."""
        """Get additional property keys."""
        """Get additional property keys."""
        """Get additional property keys."""
        """Get additional property keys."""
        """Get additional property keys."""
        """Get additional property keys."""
        """Get additional property keys."""
        """Get additional property keys."""
        """Get additional property keys."""
        """Get additional property keys."""
        """Get additional property keys."""
        """Get additional property keys."""
        """Get additional property keys."""
        """Get additional property keys."""
        """Get additional property keys."""
        """Get additional property keys."""
        """Get additional property keys."""
        """Get additional property keys."""
        """Get additional property keys."""
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
