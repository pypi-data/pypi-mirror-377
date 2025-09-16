from collections.abc import Mapping
from typing import (
    TYPE_CHECKING,
    Any,
    TypeVar,
    Union,
    cast,
)

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from typing_extensions import Self

from peertube.types import UNSET, Unset

if TYPE_CHECKING:
    from peertube.models.server_config_custom_instance_customizations import (
        ServerConfigCustomInstanceCustomizations,
    )
    from peertube.models.server_config_custom_instance_social import (
        ServerConfigCustomInstanceSocial,
    )
    from peertube.models.server_config_custom_instance_support import (
        ServerConfigCustomInstanceSupport,
    )


T = TypeVar("T", bound="ServerConfigCustomInstance")


@_attrs_define
class ServerConfigCustomInstance:
    """Attributes:
    name (Union[Unset, str]):
    short_description (Union[Unset, str]):
    description (Union[Unset, str]):
    terms (Union[Unset, str]):
    code_of_conduct (Union[Unset, str]):
    creation_reason (Union[Unset, str]):
    moderation_information (Union[Unset, str]):
    administrator (Union[Unset, str]):
    maintenance_lifetime (Union[Unset, str]):
    business_model (Union[Unset, str]):
    hardware_information (Union[Unset, str]):
    languages (Union[Unset, list[str]]):
    categories (Union[Unset, list[float]]):
    is_nsfw (Union[Unset, bool]):
    default_nsfw_policy (Union[Unset, str]):
    server_country (Union[Unset, str]):
    support (Union[Unset, ServerConfigCustomInstanceSupport]):
    social (Union[Unset, ServerConfigCustomInstanceSocial]):
    default_client_route (Union[Unset, str]):
    customizations (Union[Unset, ServerConfigCustomInstanceCustomizations]):
    """

    name: Unset | str = UNSET
    short_description: Unset | str = UNSET
    description: Unset | str = UNSET
    terms: Unset | str = UNSET
    code_of_conduct: Unset | str = UNSET
    creation_reason: Unset | str = UNSET
    moderation_information: Unset | str = UNSET
    administrator: Unset | str = UNSET
    maintenance_lifetime: Unset | str = UNSET
    business_model: Unset | str = UNSET
    hardware_information: Unset | str = UNSET
    languages: Unset | list[str] = UNSET
    categories: Unset | list[float] = UNSET
    is_nsfw: Unset | bool = UNSET
    default_nsfw_policy: Unset | str = UNSET
    server_country: Unset | str = UNSET
    support: Union[Unset, "ServerConfigCustomInstanceSupport"] = UNSET
    social: Union[Unset, "ServerConfigCustomInstanceSocial"] = UNSET
    default_client_route: Unset | str = UNSET
    customizations: Union[Unset, "ServerConfigCustomInstanceCustomizations"] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert instance to dictionary."""
        name = self.name

        short_description = self.short_description

        description = self.description

        terms = self.terms

        code_of_conduct = self.code_of_conduct

        creation_reason = self.creation_reason

        moderation_information = self.moderation_information

        administrator = self.administrator

        maintenance_lifetime = self.maintenance_lifetime

        business_model = self.business_model

        hardware_information = self.hardware_information

        languages: Unset | list[str] = UNSET
        if not isinstance(self.languages, Unset):
            languages = self.languages

        categories: Unset | list[float] = UNSET
        if not isinstance(self.categories, Unset):
            categories = self.categories

        is_nsfw = self.is_nsfw

        default_nsfw_policy = self.default_nsfw_policy

        server_country = self.server_country

        support: Unset | dict[str, Any] = UNSET
        if not isinstance(self.support, Unset):
            support = self.support.to_dict()

        social: Unset | dict[str, Any] = UNSET
        if not isinstance(self.social, Unset):
            social = self.social.to_dict()

        default_client_route = self.default_client_route

        customizations: Unset | dict[str, Any] = UNSET
        if not isinstance(self.customizations, Unset):
            customizations = self.customizations.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if name is not UNSET:
            field_dict["name"] = name
        if short_description is not UNSET:
            field_dict["shortDescription"] = short_description
        if description is not UNSET:
            field_dict["description"] = description
        if terms is not UNSET:
            field_dict["terms"] = terms
        if code_of_conduct is not UNSET:
            field_dict["codeOfConduct"] = code_of_conduct
        if creation_reason is not UNSET:
            field_dict["creationReason"] = creation_reason
        if moderation_information is not UNSET:
            field_dict["moderationInformation"] = moderation_information
        if administrator is not UNSET:
            field_dict["administrator"] = administrator
        if maintenance_lifetime is not UNSET:
            field_dict["maintenanceLifetime"] = maintenance_lifetime
        if business_model is not UNSET:
            field_dict["businessModel"] = business_model
        if hardware_information is not UNSET:
            field_dict["hardwareInformation"] = hardware_information
        if languages is not UNSET:
            field_dict["languages"] = languages
        if categories is not UNSET:
            field_dict["categories"] = categories
        if is_nsfw is not UNSET:
            field_dict["isNSFW"] = is_nsfw
        if default_nsfw_policy is not UNSET:
            field_dict["defaultNSFWPolicy"] = default_nsfw_policy
        if server_country is not UNSET:
            field_dict["serverCountry"] = server_country
        if support is not UNSET:
            field_dict["support"] = support
        if social is not UNSET:
            field_dict["social"] = social
        if default_client_route is not UNSET:
            field_dict["defaultClientRoute"] = default_client_route
        if customizations is not UNSET:
            field_dict["customizations"] = customizations

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        """Create instance from dictionary."""
        from peertube.models.server_config_custom_instance_customizations import (
            ServerConfigCustomInstanceCustomizations,
        )
        from peertube.models.server_config_custom_instance_social import (
            ServerConfigCustomInstanceSocial,
        )
        from peertube.models.server_config_custom_instance_support import (
            ServerConfigCustomInstanceSupport,
        )

        d = dict(src_dict)
        name = d.pop("name", UNSET)

        short_description = d.pop("shortDescription", UNSET)

        description = d.pop("description", UNSET)

        terms = d.pop("terms", UNSET)

        code_of_conduct = d.pop("codeOfConduct", UNSET)

        creation_reason = d.pop("creationReason", UNSET)

        moderation_information = d.pop("moderationInformation", UNSET)

        administrator = d.pop("administrator", UNSET)

        maintenance_lifetime = d.pop("maintenanceLifetime", UNSET)

        business_model = d.pop("businessModel", UNSET)

        hardware_information = d.pop("hardwareInformation", UNSET)

        languages = cast("list[str]", d.pop("languages", UNSET))

        categories = cast("list[float]", d.pop("categories", UNSET))

        is_nsfw = d.pop("isNSFW", UNSET)

        default_nsfw_policy = d.pop("defaultNSFWPolicy", UNSET)

        server_country = d.pop("serverCountry", UNSET)

        _support = d.pop("support", UNSET)
        support: Unset | ServerConfigCustomInstanceSupport
        if isinstance(_support, Unset):
            support = UNSET
        else:
            support = ServerConfigCustomInstanceSupport.from_dict(_support)

        _social = d.pop("social", UNSET)
        social: Unset | ServerConfigCustomInstanceSocial
        if isinstance(_social, Unset):
            social = UNSET
        else:
            social = ServerConfigCustomInstanceSocial.from_dict(_social)

        default_client_route = d.pop("defaultClientRoute", UNSET)

        _customizations = d.pop("customizations", UNSET)
        customizations: Unset | ServerConfigCustomInstanceCustomizations
        if isinstance(_customizations, Unset):
            customizations = UNSET
        else:
            customizations = ServerConfigCustomInstanceCustomizations.from_dict(
                _customizations
            )

        server_config_custom_instance = cls(
            name=name,
            short_description=short_description,
            description=description,
            terms=terms,
            code_of_conduct=code_of_conduct,
            creation_reason=creation_reason,
            moderation_information=moderation_information,
            administrator=administrator,
            maintenance_lifetime=maintenance_lifetime,
            business_model=business_model,
            hardware_information=hardware_information,
            languages=languages,
            categories=categories,
            is_nsfw=is_nsfw,
            default_nsfw_policy=default_nsfw_policy,
            server_country=server_country,
            support=support,
            social=social,
            default_client_route=default_client_route,
            customizations=customizations,
        )

        server_config_custom_instance.additional_properties = d
        return server_config_custom_instance

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
