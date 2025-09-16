from collections.abc import Mapping
from typing import (
    TYPE_CHECKING,
    Any,
    TypeVar,
    cast,
)

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from typing_extensions import Self

from peertube.types import UNSET, Unset

if TYPE_CHECKING:
    from peertube.models.actor_image import ActorImage


T = TypeVar("T", bound="ServerConfigAboutInstance")


@_attrs_define
class ServerConfigAboutInstance:
    """Attributes:
    name (Union[Unset, str]):
    short_description (Union[Unset, str]):
    description (Union[Unset, str]):
    terms (Union[Unset, str]):
    code_of_conduct (Union[Unset, str]):
    hardware_information (Union[Unset, str]):
    creation_reason (Union[Unset, str]):
    moderation_information (Union[Unset, str]):
    administrator (Union[Unset, str]):
    maintenance_lifetime (Union[Unset, str]):
    business_model (Union[Unset, str]):
    languages (Union[Unset, list[str]]):
    categories (Union[Unset, list[int]]):
    avatars (Union[Unset, list['ActorImage']]):
    banners (Union[Unset, list['ActorImage']]):
    """

    name: Unset | str = UNSET
    short_description: Unset | str = UNSET
    description: Unset | str = UNSET
    terms: Unset | str = UNSET
    code_of_conduct: Unset | str = UNSET
    hardware_information: Unset | str = UNSET
    creation_reason: Unset | str = UNSET
    moderation_information: Unset | str = UNSET
    administrator: Unset | str = UNSET
    maintenance_lifetime: Unset | str = UNSET
    business_model: Unset | str = UNSET
    languages: Unset | list[str] = UNSET
    categories: Unset | list[int] = UNSET
    avatars: Unset | list["ActorImage"] = UNSET
    banners: Unset | list["ActorImage"] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert instance to dictionary."""
        name = self.name

        short_description = self.short_description

        description = self.description

        terms = self.terms

        code_of_conduct = self.code_of_conduct

        hardware_information = self.hardware_information

        creation_reason = self.creation_reason

        moderation_information = self.moderation_information

        administrator = self.administrator

        maintenance_lifetime = self.maintenance_lifetime

        business_model = self.business_model

        languages: Unset | list[str] = UNSET
        if not isinstance(self.languages, Unset):
            languages = self.languages

        categories: Unset | list[int] = UNSET
        if not isinstance(self.categories, Unset):
            categories = self.categories

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
        if description is not UNSET:
            field_dict["description"] = description
        if terms is not UNSET:
            field_dict["terms"] = terms
        if code_of_conduct is not UNSET:
            field_dict["codeOfConduct"] = code_of_conduct
        if hardware_information is not UNSET:
            field_dict["hardwareInformation"] = hardware_information
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
        if languages is not UNSET:
            field_dict["languages"] = languages
        if categories is not UNSET:
            field_dict["categories"] = categories
        if avatars is not UNSET:
            field_dict["avatars"] = avatars
        if banners is not UNSET:
            field_dict["banners"] = banners

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        """Create instance from dictionary."""
        from peertube.models.actor_image import ActorImage

        d = dict(src_dict)
        name = d.pop("name", UNSET)

        short_description = d.pop("shortDescription", UNSET)

        description = d.pop("description", UNSET)

        terms = d.pop("terms", UNSET)

        code_of_conduct = d.pop("codeOfConduct", UNSET)

        hardware_information = d.pop("hardwareInformation", UNSET)

        creation_reason = d.pop("creationReason", UNSET)

        moderation_information = d.pop("moderationInformation", UNSET)

        administrator = d.pop("administrator", UNSET)

        maintenance_lifetime = d.pop("maintenanceLifetime", UNSET)

        business_model = d.pop("businessModel", UNSET)

        languages = cast("list[str]", d.pop("languages", UNSET))

        categories = cast("list[int]", d.pop("categories", UNSET))

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

        server_config_about_instance = cls(
            name=name,
            short_description=short_description,
            description=description,
            terms=terms,
            code_of_conduct=code_of_conduct,
            hardware_information=hardware_information,
            creation_reason=creation_reason,
            moderation_information=moderation_information,
            administrator=administrator,
            maintenance_lifetime=maintenance_lifetime,
            business_model=business_model,
            languages=languages,
            categories=categories,
            avatars=avatars,
            banners=banners,
        )

        server_config_about_instance.additional_properties = d
        return server_config_about_instance

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
