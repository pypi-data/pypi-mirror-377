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
    from peertube.models.put_api_v1_plugins_npm_name_settings_body_settings import (
        PutApiV1PluginsNpmNameSettingsBodySettings,
    )


T = TypeVar("T", bound="PutApiV1PluginsNpmNameSettingsBody")


@_attrs_define
class PutApiV1PluginsNpmNameSettingsBody:
    """Attributes:
    settings (Union[Unset, PutApiV1PluginsNpmNameSettingsBodySettings]):
    """

    settings: Union[Unset, "PutApiV1PluginsNpmNameSettingsBodySettings"] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert instance to dictionary."""
        settings: Unset | dict[str, Any] = UNSET
        if not isinstance(self.settings, Unset):
            settings = self.settings.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if settings is not UNSET:
            field_dict["settings"] = settings

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        """Create instance from dictionary."""
        from peertube.models.put_api_v1_plugins_npm_name_settings_body_settings import (
            PutApiV1PluginsNpmNameSettingsBodySettings,
        )

        d = dict(src_dict)
        _settings = d.pop("settings", UNSET)
        settings: Unset | PutApiV1PluginsNpmNameSettingsBodySettings
        if isinstance(_settings, Unset):
            settings = UNSET
        else:
            settings = PutApiV1PluginsNpmNameSettingsBodySettings.from_dict(_settings)

        put_api_v1_plugins_npm_name_settings_body = cls(
            settings=settings,
        )

        put_api_v1_plugins_npm_name_settings_body.additional_properties = d
        return put_api_v1_plugins_npm_name_settings_body

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
