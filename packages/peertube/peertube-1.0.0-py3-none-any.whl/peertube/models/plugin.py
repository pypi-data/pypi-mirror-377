import datetime
from collections.abc import Mapping
from typing import (
    TYPE_CHECKING,
    Any,
    TypeVar,
    Union,
)

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse
from typing_extensions import Self

from peertube.models.plugin_type import PluginType
from peertube.types import UNSET, Unset

if TYPE_CHECKING:
    from peertube.models.plugin_settings import PluginSettings


T = TypeVar("T", bound="Plugin")


@_attrs_define
class Plugin:
    """Attributes:
    name (Union[Unset, str]):  Example: peertube-plugin-auth-ldap.
    type_ (Union[Unset, PluginType]): - `1`: PLUGIN
        - `2`: THEME
    latest_version (Union[Unset, str]):  Example: 0.0.3.
    version (Union[Unset, str]):  Example: 0.0.1.
    enabled (Union[Unset, bool]):
    uninstalled (Union[Unset, bool]):
    peertube_engine (Union[Unset, str]):  Example: 2.2.0.
    description (Union[Unset, str]):
    homepage (Union[Unset, str]):  Example: https://framagit.org/framasoft/peertube/official-
        plugins/tree/master/peertube-plugin-auth-ldap.
    settings (Union[Unset, PluginSettings]):
    created_at (Union[Unset, datetime.datetime]):
    updated_at (Union[Unset, datetime.datetime]):
    """

    name: Unset | str = UNSET
    type_: Unset | PluginType = UNSET
    latest_version: Unset | str = UNSET
    version: Unset | str = UNSET
    enabled: Unset | bool = UNSET
    uninstalled: Unset | bool = UNSET
    peertube_engine: Unset | str = UNSET
    description: Unset | str = UNSET
    homepage: Unset | str = UNSET
    settings: Union[Unset, "PluginSettings"] = UNSET
    created_at: Unset | datetime.datetime = UNSET
    updated_at: Unset | datetime.datetime = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert instance to dictionary."""
        name = self.name

        type_: Unset | int = UNSET
        if not isinstance(self.type_, Unset):
            type_ = self.type_.value

        latest_version = self.latest_version

        version = self.version

        enabled = self.enabled

        uninstalled = self.uninstalled

        peertube_engine = self.peertube_engine

        description = self.description

        homepage = self.homepage

        settings: Unset | dict[str, Any] = UNSET
        if not isinstance(self.settings, Unset):
            settings = self.settings.to_dict()

        created_at: Unset | str = UNSET
        if not isinstance(self.created_at, Unset):
            created_at = self.created_at.isoformat()

        updated_at: Unset | str = UNSET
        if not isinstance(self.updated_at, Unset):
            updated_at = self.updated_at.isoformat()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if name is not UNSET:
            field_dict["name"] = name
        if type_ is not UNSET:
            field_dict["type"] = type_
        if latest_version is not UNSET:
            field_dict["latestVersion"] = latest_version
        if version is not UNSET:
            field_dict["version"] = version
        if enabled is not UNSET:
            field_dict["enabled"] = enabled
        if uninstalled is not UNSET:
            field_dict["uninstalled"] = uninstalled
        if peertube_engine is not UNSET:
            field_dict["peertubeEngine"] = peertube_engine
        if description is not UNSET:
            field_dict["description"] = description
        if homepage is not UNSET:
            field_dict["homepage"] = homepage
        if settings is not UNSET:
            field_dict["settings"] = settings
        if created_at is not UNSET:
            field_dict["createdAt"] = created_at
        if updated_at is not UNSET:
            field_dict["updatedAt"] = updated_at

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        """Create instance from dictionary."""
        from peertube.models.plugin_settings import PluginSettings

        d = dict(src_dict)
        name = d.pop("name", UNSET)

        _type_ = d.pop("type", UNSET)
        type_: Unset | PluginType
        if isinstance(_type_, Unset):
            type_ = UNSET
        else:
            type_ = PluginType(_type_)

        latest_version = d.pop("latestVersion", UNSET)

        version = d.pop("version", UNSET)

        enabled = d.pop("enabled", UNSET)

        uninstalled = d.pop("uninstalled", UNSET)

        peertube_engine = d.pop("peertubeEngine", UNSET)

        description = d.pop("description", UNSET)

        homepage = d.pop("homepage", UNSET)

        _settings = d.pop("settings", UNSET)
        settings: Unset | PluginSettings
        if isinstance(_settings, Unset):
            settings = UNSET
        else:
            settings = PluginSettings.from_dict(_settings)

        _created_at = d.pop("createdAt", UNSET)
        created_at: Unset | datetime.datetime
        if isinstance(_created_at, Unset):
            created_at = UNSET
        else:
            created_at = isoparse(_created_at)

        _updated_at = d.pop("updatedAt", UNSET)
        updated_at: Unset | datetime.datetime
        if isinstance(_updated_at, Unset):
            updated_at = UNSET
        else:
            updated_at = isoparse(_updated_at)

        plugin = cls(
            name=name,
            type_=type_,
            latest_version=latest_version,
            version=version,
            enabled=enabled,
            uninstalled=uninstalled,
            peertube_engine=peertube_engine,
            description=description,
            homepage=homepage,
            settings=settings,
            created_at=created_at,
            updated_at=updated_at,
        )

        plugin.additional_properties = d
        return plugin

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
