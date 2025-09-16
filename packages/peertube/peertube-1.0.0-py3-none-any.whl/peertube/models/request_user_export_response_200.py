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
    from peertube.models.request_user_export_response_200_export import (
        RequestUserExportResponse200Export,
    )


T = TypeVar("T", bound="RequestUserExportResponse200")


@_attrs_define
class RequestUserExportResponse200:
    """Attributes:
    export (Union[Unset, RequestUserExportResponse200Export]):
    """

    export: Union[Unset, "RequestUserExportResponse200Export"] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert instance to dictionary."""
        export: Unset | dict[str, Any] = UNSET
        if not isinstance(self.export, Unset):
            export = self.export.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if export is not UNSET:
            field_dict["export"] = export

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        """Create instance from dictionary."""
        from peertube.models.request_user_export_response_200_export import (
            RequestUserExportResponse200Export,
        )

        d = dict(src_dict)
        _export = d.pop("export", UNSET)
        export: Unset | RequestUserExportResponse200Export
        if isinstance(_export, Unset):
            export = UNSET
        else:
            export = RequestUserExportResponse200Export.from_dict(_export)

        request_user_export_response_200 = cls(
            export=export,
        )

        request_user_export_response_200.additional_properties = d
        return request_user_export_response_200

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
