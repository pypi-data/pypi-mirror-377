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
    from peertube.models.actor_image import ActorImage
    from peertube.models.server_config_instance_customizations import (
        ServerConfigInstanceCustomizations,
    )
    from peertube.models.server_config_instance_social import ServerConfigInstanceSocial
    from peertube.models.server_config_instance_support import (
        ServerConfigInstanceSupport,
    )


T = TypeVar("T", bound="ServerConfigInstance")


@_attrs_define
class ServerConfigInstance:
    """Attributes:
    name (Union[Unset, str]):
    short_description (Union[Unset, str]):
    default_client_route (Union[Unset, str]):
    is_nsfw (Union[Unset, bool]):
    default_nsfw_policy (Union[Unset, str]):
    server_country (Union[Unset, str]):
    default_language (Union[Unset, str]):
    support (Union[Unset, ServerConfigInstanceSupport]):
    social (Union[Unset, ServerConfigInstanceSocial]):
    customizations (Union[Unset, ServerConfigInstanceCustomizations]):
    avatars (Union[Unset, list['ActorImage']]):
    banners (Union[Unset, list['ActorImage']]):
    """

    name: Unset | str = UNSET
    short_description: Unset | str = UNSET
    default_client_route: Unset | str = UNSET
    is_nsfw: Unset | bool = UNSET
    default_nsfw_policy: Unset | str = UNSET
    server_country: Unset | str = UNSET
    default_language: Unset | str = UNSET
    support: Union[Unset, "ServerConfigInstanceSupport"] = UNSET
    social: Union[Unset, "ServerConfigInstanceSocial"] = UNSET
    customizations: Union[Unset, "ServerConfigInstanceCustomizations"] = UNSET
    avatars: Unset | list["ActorImage"] = UNSET
    banners: Unset | list["ActorImage"] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert instance to dictionary."""
        name = self.name

        short_description = self.short_description

        default_client_route = self.default_client_route

        is_nsfw = self.is_nsfw

        default_nsfw_policy = self.default_nsfw_policy

        server_country = self.server_country

        default_language = self.default_language

        support: Unset | dict[str, Any] = UNSET
        if not isinstance(self.support, Unset):
            support = self.support.to_dict()

        social: Unset | dict[str, Any] = UNSET
        if not isinstance(self.social, Unset):
            social = self.social.to_dict()

        customizations: Unset | dict[str, Any] = UNSET
        if not isinstance(self.customizations, Unset):
            customizations = self.customizations.to_dict()

        avatars: Unset | list[dict[str, Any]] = UNSET
        if not isinstance(self.avatars, Unset):
            avatars = []
            for avatars_item_data in self.avatars:
                avatars_item = avatars_item_data.to_dict()
                avatars.append(avatars_item)

        banners: Unset | list[dict[str, Any]] = UNSET
        if not isinstance(self.banners, Unset):
            banners = []
            for banners_item_data in self.banners:
                banners_item = banners_item_data.to_dict()
                banners.append(banners_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if name is not UNSET:
            field_dict["name"] = name
        if short_description is not UNSET:
            field_dict["shortDescription"] = short_description
        if default_client_route is not UNSET:
            field_dict["defaultClientRoute"] = default_client_route
        if is_nsfw is not UNSET:
            field_dict["isNSFW"] = is_nsfw
        if default_nsfw_policy is not UNSET:
            field_dict["defaultNSFWPolicy"] = default_nsfw_policy
        if server_country is not UNSET:
            field_dict["serverCountry"] = server_country
        if default_language is not UNSET:
            field_dict["defaultLanguage"] = default_language
        if support is not UNSET:
            field_dict["support"] = support
        if social is not UNSET:
            field_dict["social"] = social
        if customizations is not UNSET:
            field_dict["customizations"] = customizations
        if avatars is not UNSET:
            field_dict["avatars"] = avatars
        if banners is not UNSET:
            field_dict["banners"] = banners

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        """Create instance from dictionary."""
        from peertube.models.actor_image import ActorImage
        from peertube.models.server_config_instance_customizations import (
            ServerConfigInstanceCustomizations,
        )
        from peertube.models.server_config_instance_social import (
            ServerConfigInstanceSocial,
        )
        from peertube.models.server_config_instance_support import (
            ServerConfigInstanceSupport,
        )

        d = dict(src_dict)
        name = d.pop("name", UNSET)

        short_description = d.pop("shortDescription", UNSET)

        default_client_route = d.pop("defaultClientRoute", UNSET)

        is_nsfw = d.pop("isNSFW", UNSET)

        default_nsfw_policy = d.pop("defaultNSFWPolicy", UNSET)

        server_country = d.pop("serverCountry", UNSET)

        default_language = d.pop("defaultLanguage", UNSET)

        _support = d.pop("support", UNSET)
        support: Unset | ServerConfigInstanceSupport
        if isinstance(_support, Unset):
            support = UNSET
        else:
            support = ServerConfigInstanceSupport.from_dict(_support)

        _social = d.pop("social", UNSET)
        social: Unset | ServerConfigInstanceSocial
        if isinstance(_social, Unset):
            social = UNSET
        else:
            social = ServerConfigInstanceSocial.from_dict(_social)

        _customizations = d.pop("customizations", UNSET)
        customizations: Unset | ServerConfigInstanceCustomizations
        if isinstance(_customizations, Unset):
            customizations = UNSET
        else:
            customizations = ServerConfigInstanceCustomizations.from_dict(
                _customizations
            )

        avatars = []
        _avatars = d.pop("avatars", UNSET)
        for avatars_item_data in _avatars or []:
            avatars_item = ActorImage.from_dict(avatars_item_data)

            avatars.append(avatars_item)

        banners = []
        _banners = d.pop("banners", UNSET)
        for banners_item_data in _banners or []:
            banners_item = ActorImage.from_dict(banners_item_data)

            banners.append(banners_item)

        server_config_instance = cls(
            name=name,
            short_description=short_description,
            default_client_route=default_client_route,
            is_nsfw=is_nsfw,
            default_nsfw_policy=default_nsfw_policy,
            server_country=server_country,
            default_language=default_language,
            support=support,
            social=social,
            customizations=customizations,
            avatars=avatars,
            banners=banners,
        )

        server_config_instance.additional_properties = d
        return server_config_instance

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
