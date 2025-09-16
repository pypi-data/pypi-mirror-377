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
    from peertube.models.server_config_custom_admin import ServerConfigCustomAdmin
    from peertube.models.server_config_custom_auto_blacklist import (
        ServerConfigCustomAutoBlacklist,
    )
    from peertube.models.server_config_custom_cache import ServerConfigCustomCache
    from peertube.models.server_config_custom_contact_form import (
        ServerConfigCustomContactForm,
    )
    from peertube.models.server_config_custom_defaults import ServerConfigCustomDefaults
    from peertube.models.server_config_custom_followers import (
        ServerConfigCustomFollowers,
    )
    from peertube.models.server_config_custom_import import ServerConfigCustomImport
    from peertube.models.server_config_custom_instance import ServerConfigCustomInstance
    from peertube.models.server_config_custom_services import ServerConfigCustomServices
    from peertube.models.server_config_custom_signup import ServerConfigCustomSignup
    from peertube.models.server_config_custom_storyboard import (
        ServerConfigCustomStoryboard,
    )
    from peertube.models.server_config_custom_theme import ServerConfigCustomTheme
    from peertube.models.server_config_custom_transcoding import (
        ServerConfigCustomTranscoding,
    )
    from peertube.models.server_config_custom_user import ServerConfigCustomUser


T = TypeVar("T", bound="ServerConfigCustom")


@_attrs_define
class ServerConfigCustom:
    """Attributes:
    instance (Union[Unset, ServerConfigCustomInstance]):
    theme (Union[Unset, ServerConfigCustomTheme]):
    services (Union[Unset, ServerConfigCustomServices]):
    cache (Union[Unset, ServerConfigCustomCache]):
    signup (Union[Unset, ServerConfigCustomSignup]):
    admin (Union[Unset, ServerConfigCustomAdmin]):
    contact_form (Union[Unset, ServerConfigCustomContactForm]):
    user (Union[Unset, ServerConfigCustomUser]): Settings that apply to new users, if registration is enabled
    transcoding (Union[Unset, ServerConfigCustomTranscoding]): Settings pertaining to transcoding jobs
    import_ (Union[Unset, ServerConfigCustomImport]):
    auto_blacklist (Union[Unset, ServerConfigCustomAutoBlacklist]):
    followers (Union[Unset, ServerConfigCustomFollowers]):
    storyboard (Union[Unset, ServerConfigCustomStoryboard]):
    defaults (Union[Unset, ServerConfigCustomDefaults]):
    """

    instance: Union[Unset, "ServerConfigCustomInstance"] = UNSET
    theme: Union[Unset, "ServerConfigCustomTheme"] = UNSET
    services: Union[Unset, "ServerConfigCustomServices"] = UNSET
    cache: Union[Unset, "ServerConfigCustomCache"] = UNSET
    signup: Union[Unset, "ServerConfigCustomSignup"] = UNSET
    admin: Union[Unset, "ServerConfigCustomAdmin"] = UNSET
    contact_form: Union[Unset, "ServerConfigCustomContactForm"] = UNSET
    user: Union[Unset, "ServerConfigCustomUser"] = UNSET
    transcoding: Union[Unset, "ServerConfigCustomTranscoding"] = UNSET
    import_: Union[Unset, "ServerConfigCustomImport"] = UNSET
    auto_blacklist: Union[Unset, "ServerConfigCustomAutoBlacklist"] = UNSET
    followers: Union[Unset, "ServerConfigCustomFollowers"] = UNSET
    storyboard: Union[Unset, "ServerConfigCustomStoryboard"] = UNSET
    defaults: Union[Unset, "ServerConfigCustomDefaults"] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert instance to dictionary."""
        instance: Unset | dict[str, Any] = UNSET
        if not isinstance(self.instance, Unset):
            instance = self.instance.to_dict()

        theme: Unset | dict[str, Any] = UNSET
        if not isinstance(self.theme, Unset):
            theme = self.theme.to_dict()

        services: Unset | dict[str, Any] = UNSET
        if not isinstance(self.services, Unset):
            services = self.services.to_dict()

        cache: Unset | dict[str, Any] = UNSET
        if not isinstance(self.cache, Unset):
            cache = self.cache.to_dict()

        signup: Unset | dict[str, Any] = UNSET
        if not isinstance(self.signup, Unset):
            signup = self.signup.to_dict()

        admin: Unset | dict[str, Any] = UNSET
        if not isinstance(self.admin, Unset):
            admin = self.admin.to_dict()

        contact_form: Unset | dict[str, Any] = UNSET
        if not isinstance(self.contact_form, Unset):
            contact_form = self.contact_form.to_dict()

        user: Unset | dict[str, Any] = UNSET
        if not isinstance(self.user, Unset):
            user = self.user.to_dict()

        transcoding: Unset | dict[str, Any] = UNSET
        if not isinstance(self.transcoding, Unset):
            transcoding = self.transcoding.to_dict()

        import_: Unset | dict[str, Any] = UNSET
        if not isinstance(self.import_, Unset):
            import_ = self.import_.to_dict()

        auto_blacklist: Unset | dict[str, Any] = UNSET
        if not isinstance(self.auto_blacklist, Unset):
            auto_blacklist = self.auto_blacklist.to_dict()

        followers: Unset | dict[str, Any] = UNSET
        if not isinstance(self.followers, Unset):
            followers = self.followers.to_dict()

        storyboard: Unset | dict[str, Any] = UNSET
        if not isinstance(self.storyboard, Unset):
            storyboard = self.storyboard.to_dict()

        defaults: Unset | dict[str, Any] = UNSET
        if not isinstance(self.defaults, Unset):
            defaults = self.defaults.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if instance is not UNSET:
            field_dict["instance"] = instance
        if theme is not UNSET:
            field_dict["theme"] = theme
        if services is not UNSET:
            field_dict["services"] = services
        if cache is not UNSET:
            field_dict["cache"] = cache
        if signup is not UNSET:
            field_dict["signup"] = signup
        if admin is not UNSET:
            field_dict["admin"] = admin
        if contact_form is not UNSET:
            field_dict["contactForm"] = contact_form
        if user is not UNSET:
            field_dict["user"] = user
        if transcoding is not UNSET:
            field_dict["transcoding"] = transcoding
        if import_ is not UNSET:
            field_dict["import"] = import_
        if auto_blacklist is not UNSET:
            field_dict["autoBlacklist"] = auto_blacklist
        if followers is not UNSET:
            field_dict["followers"] = followers
        if storyboard is not UNSET:
            field_dict["storyboard"] = storyboard
        if defaults is not UNSET:
            field_dict["defaults"] = defaults

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        """Create instance from dictionary."""
        from peertube.models.server_config_custom_admin import ServerConfigCustomAdmin
        from peertube.models.server_config_custom_auto_blacklist import (
            ServerConfigCustomAutoBlacklist,
        )
        from peertube.models.server_config_custom_cache import ServerConfigCustomCache
        from peertube.models.server_config_custom_contact_form import (
            ServerConfigCustomContactForm,
        )
        from peertube.models.server_config_custom_defaults import (
            ServerConfigCustomDefaults,
        )
        from peertube.models.server_config_custom_followers import (
            ServerConfigCustomFollowers,
        )
        from peertube.models.server_config_custom_import import ServerConfigCustomImport
        from peertube.models.server_config_custom_instance import (
            ServerConfigCustomInstance,
        )
        from peertube.models.server_config_custom_services import (
            ServerConfigCustomServices,
        )
        from peertube.models.server_config_custom_signup import ServerConfigCustomSignup
        from peertube.models.server_config_custom_storyboard import (
            ServerConfigCustomStoryboard,
        )
        from peertube.models.server_config_custom_theme import ServerConfigCustomTheme
        from peertube.models.server_config_custom_transcoding import (
            ServerConfigCustomTranscoding,
        )
        from peertube.models.server_config_custom_user import ServerConfigCustomUser

        d = dict(src_dict)
        _instance = d.pop("instance", UNSET)
        instance: Unset | ServerConfigCustomInstance
        if isinstance(_instance, Unset):
            instance = UNSET
        else:
            instance = ServerConfigCustomInstance.from_dict(_instance)

        _theme = d.pop("theme", UNSET)
        theme: Unset | ServerConfigCustomTheme
        if isinstance(_theme, Unset):
            theme = UNSET
        else:
            theme = ServerConfigCustomTheme.from_dict(_theme)

        _services = d.pop("services", UNSET)
        services: Unset | ServerConfigCustomServices
        if isinstance(_services, Unset):
            services = UNSET
        else:
            services = ServerConfigCustomServices.from_dict(_services)

        _cache = d.pop("cache", UNSET)
        cache: Unset | ServerConfigCustomCache
        if isinstance(_cache, Unset):
            cache = UNSET
        else:
            cache = ServerConfigCustomCache.from_dict(_cache)

        _signup = d.pop("signup", UNSET)
        signup: Unset | ServerConfigCustomSignup
        if isinstance(_signup, Unset):
            signup = UNSET
        else:
            signup = ServerConfigCustomSignup.from_dict(_signup)

        _admin = d.pop("admin", UNSET)
        admin: Unset | ServerConfigCustomAdmin
        if isinstance(_admin, Unset):
            admin = UNSET
        else:
            admin = ServerConfigCustomAdmin.from_dict(_admin)

        _contact_form = d.pop("contactForm", UNSET)
        contact_form: Unset | ServerConfigCustomContactForm
        if isinstance(_contact_form, Unset):
            contact_form = UNSET
        else:
            contact_form = ServerConfigCustomContactForm.from_dict(_contact_form)

        _user = d.pop("user", UNSET)
        user: Unset | ServerConfigCustomUser
        if isinstance(_user, Unset):
            user = UNSET
        else:
            user = ServerConfigCustomUser.from_dict(_user)

        _transcoding = d.pop("transcoding", UNSET)
        transcoding: Unset | ServerConfigCustomTranscoding
        if isinstance(_transcoding, Unset):
            transcoding = UNSET
        else:
            transcoding = ServerConfigCustomTranscoding.from_dict(_transcoding)

        _import_ = d.pop("import", UNSET)
        import_: Unset | ServerConfigCustomImport
        if isinstance(_import_, Unset):
            import_ = UNSET
        else:
            import_ = ServerConfigCustomImport.from_dict(_import_)

        _auto_blacklist = d.pop("autoBlacklist", UNSET)
        auto_blacklist: Unset | ServerConfigCustomAutoBlacklist
        if isinstance(_auto_blacklist, Unset):
            auto_blacklist = UNSET
        else:
            auto_blacklist = ServerConfigCustomAutoBlacklist.from_dict(_auto_blacklist)

        _followers = d.pop("followers", UNSET)
        followers: Unset | ServerConfigCustomFollowers
        if isinstance(_followers, Unset):
            followers = UNSET
        else:
            followers = ServerConfigCustomFollowers.from_dict(_followers)

        _storyboard = d.pop("storyboard", UNSET)
        storyboard: Unset | ServerConfigCustomStoryboard
        if isinstance(_storyboard, Unset):
            storyboard = UNSET
        else:
            storyboard = ServerConfigCustomStoryboard.from_dict(_storyboard)

        _defaults = d.pop("defaults", UNSET)
        defaults: Unset | ServerConfigCustomDefaults
        if isinstance(_defaults, Unset):
            defaults = UNSET
        else:
            defaults = ServerConfigCustomDefaults.from_dict(_defaults)

        server_config_custom = cls(
            instance=instance,
            theme=theme,
            services=services,
            cache=cache,
            signup=signup,
            admin=admin,
            contact_form=contact_form,
            user=user,
            transcoding=transcoding,
            import_=import_,
            auto_blacklist=auto_blacklist,
            followers=followers,
            storyboard=storyboard,
            defaults=defaults,
        )

        server_config_custom.additional_properties = d
        return server_config_custom

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
