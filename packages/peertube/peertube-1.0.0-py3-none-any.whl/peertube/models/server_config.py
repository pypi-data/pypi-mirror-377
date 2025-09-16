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
    from peertube.models.server_config_auto_blacklist import ServerConfigAutoBlacklist
    from peertube.models.server_config_avatar import ServerConfigAvatar
    from peertube.models.server_config_contact_form import ServerConfigContactForm
    from peertube.models.server_config_email import ServerConfigEmail
    from peertube.models.server_config_export import ServerConfigExport
    from peertube.models.server_config_federation import ServerConfigFederation
    from peertube.models.server_config_followings import ServerConfigFollowings
    from peertube.models.server_config_homepage import ServerConfigHomepage
    from peertube.models.server_config_import import ServerConfigImport
    from peertube.models.server_config_instance import ServerConfigInstance
    from peertube.models.server_config_open_telemetry import ServerConfigOpenTelemetry
    from peertube.models.server_config_plugin import ServerConfigPlugin
    from peertube.models.server_config_search import ServerConfigSearch
    from peertube.models.server_config_signup import ServerConfigSignup
    from peertube.models.server_config_theme import ServerConfigTheme
    from peertube.models.server_config_tracker import ServerConfigTracker
    from peertube.models.server_config_transcoding import ServerConfigTranscoding
    from peertube.models.server_config_trending import ServerConfigTrending
    from peertube.models.server_config_user import ServerConfigUser
    from peertube.models.server_config_video import ServerConfigVideo
    from peertube.models.server_config_video_caption import ServerConfigVideoCaption
    from peertube.models.server_config_views import ServerConfigViews


T = TypeVar("T", bound="ServerConfig")


@_attrs_define
class ServerConfig:
    """Attributes:
    instance (Union[Unset, ServerConfigInstance]):
    search (Union[Unset, ServerConfigSearch]):
    plugin (Union[Unset, ServerConfigPlugin]):
    theme (Union[Unset, ServerConfigTheme]):
    email (Union[Unset, ServerConfigEmail]):
    contact_form (Union[Unset, ServerConfigContactForm]):
    server_version (Union[Unset, str]):
    server_commit (Union[Unset, str]):
    signup (Union[Unset, ServerConfigSignup]):
    transcoding (Union[Unset, ServerConfigTranscoding]):
    import_ (Union[Unset, ServerConfigImport]):
    export (Union[Unset, ServerConfigExport]):
    auto_blacklist (Union[Unset, ServerConfigAutoBlacklist]):
    avatar (Union[Unset, ServerConfigAvatar]):
    video (Union[Unset, ServerConfigVideo]):
    video_caption (Union[Unset, ServerConfigVideoCaption]):
    user (Union[Unset, ServerConfigUser]):
    trending (Union[Unset, ServerConfigTrending]):
    tracker (Union[Unset, ServerConfigTracker]):
    followings (Union[Unset, ServerConfigFollowings]):
    federation (Union[Unset, ServerConfigFederation]):
    homepage (Union[Unset, ServerConfigHomepage]):
    open_telemetry (Union[Unset, ServerConfigOpenTelemetry]): PeerTube >= 6.1
    views (Union[Unset, ServerConfigViews]): PeerTube >= 6.1
    """

    instance: Union[Unset, "ServerConfigInstance"] = UNSET
    search: Union[Unset, "ServerConfigSearch"] = UNSET
    plugin: Union[Unset, "ServerConfigPlugin"] = UNSET
    theme: Union[Unset, "ServerConfigTheme"] = UNSET
    email: Union[Unset, "ServerConfigEmail"] = UNSET
    contact_form: Union[Unset, "ServerConfigContactForm"] = UNSET
    server_version: Unset | str = UNSET
    server_commit: Unset | str = UNSET
    signup: Union[Unset, "ServerConfigSignup"] = UNSET
    transcoding: Union[Unset, "ServerConfigTranscoding"] = UNSET
    import_: Union[Unset, "ServerConfigImport"] = UNSET
    export: Union[Unset, "ServerConfigExport"] = UNSET
    auto_blacklist: Union[Unset, "ServerConfigAutoBlacklist"] = UNSET
    avatar: Union[Unset, "ServerConfigAvatar"] = UNSET
    video: Union[Unset, "ServerConfigVideo"] = UNSET
    video_caption: Union[Unset, "ServerConfigVideoCaption"] = UNSET
    user: Union[Unset, "ServerConfigUser"] = UNSET
    trending: Union[Unset, "ServerConfigTrending"] = UNSET
    tracker: Union[Unset, "ServerConfigTracker"] = UNSET
    followings: Union[Unset, "ServerConfigFollowings"] = UNSET
    federation: Union[Unset, "ServerConfigFederation"] = UNSET
    homepage: Union[Unset, "ServerConfigHomepage"] = UNSET
    open_telemetry: Union[Unset, "ServerConfigOpenTelemetry"] = UNSET
    views: Union[Unset, "ServerConfigViews"] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert instance to dictionary."""
        instance: Unset | dict[str, Any] = UNSET
        if not isinstance(self.instance, Unset):
            instance = self.instance.to_dict()

        search: Unset | dict[str, Any] = UNSET
        if not isinstance(self.search, Unset):
            search = self.search.to_dict()

        plugin: Unset | dict[str, Any] = UNSET
        if not isinstance(self.plugin, Unset):
            plugin = self.plugin.to_dict()

        theme: Unset | dict[str, Any] = UNSET
        if not isinstance(self.theme, Unset):
            theme = self.theme.to_dict()

        email: Unset | dict[str, Any] = UNSET
        if not isinstance(self.email, Unset):
            email = self.email.to_dict()

        contact_form: Unset | dict[str, Any] = UNSET
        if not isinstance(self.contact_form, Unset):
            contact_form = self.contact_form.to_dict()

        server_version = self.server_version

        server_commit = self.server_commit

        signup: Unset | dict[str, Any] = UNSET
        if not isinstance(self.signup, Unset):
            signup = self.signup.to_dict()

        transcoding: Unset | dict[str, Any] = UNSET
        if not isinstance(self.transcoding, Unset):
            transcoding = self.transcoding.to_dict()

        import_: Unset | dict[str, Any] = UNSET
        if not isinstance(self.import_, Unset):
            import_ = self.import_.to_dict()

        export: Unset | dict[str, Any] = UNSET
        if not isinstance(self.export, Unset):
            export = self.export.to_dict()

        auto_blacklist: Unset | dict[str, Any] = UNSET
        if not isinstance(self.auto_blacklist, Unset):
            auto_blacklist = self.auto_blacklist.to_dict()

        avatar: Unset | dict[str, Any] = UNSET
        if not isinstance(self.avatar, Unset):
            avatar = self.avatar.to_dict()

        video: Unset | dict[str, Any] = UNSET
        if not isinstance(self.video, Unset):
            video = self.video.to_dict()

        video_caption: Unset | dict[str, Any] = UNSET
        if not isinstance(self.video_caption, Unset):
            video_caption = self.video_caption.to_dict()

        user: Unset | dict[str, Any] = UNSET
        if not isinstance(self.user, Unset):
            user = self.user.to_dict()

        trending: Unset | dict[str, Any] = UNSET
        if not isinstance(self.trending, Unset):
            trending = self.trending.to_dict()

        tracker: Unset | dict[str, Any] = UNSET
        if not isinstance(self.tracker, Unset):
            tracker = self.tracker.to_dict()

        followings: Unset | dict[str, Any] = UNSET
        if not isinstance(self.followings, Unset):
            followings = self.followings.to_dict()

        federation: Unset | dict[str, Any] = UNSET
        if not isinstance(self.federation, Unset):
            federation = self.federation.to_dict()

        homepage: Unset | dict[str, Any] = UNSET
        if not isinstance(self.homepage, Unset):
            homepage = self.homepage.to_dict()

        open_telemetry: Unset | dict[str, Any] = UNSET
        if not isinstance(self.open_telemetry, Unset):
            open_telemetry = self.open_telemetry.to_dict()

        views: Unset | dict[str, Any] = UNSET
        if not isinstance(self.views, Unset):
            views = self.views.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if instance is not UNSET:
            field_dict["instance"] = instance
        if search is not UNSET:
            field_dict["search"] = search
        if plugin is not UNSET:
            field_dict["plugin"] = plugin
        if theme is not UNSET:
            field_dict["theme"] = theme
        if email is not UNSET:
            field_dict["email"] = email
        if contact_form is not UNSET:
            field_dict["contactForm"] = contact_form
        if server_version is not UNSET:
            field_dict["serverVersion"] = server_version
        if server_commit is not UNSET:
            field_dict["serverCommit"] = server_commit
        if signup is not UNSET:
            field_dict["signup"] = signup
        if transcoding is not UNSET:
            field_dict["transcoding"] = transcoding
        if import_ is not UNSET:
            field_dict["import"] = import_
        if export is not UNSET:
            field_dict["export"] = export
        if auto_blacklist is not UNSET:
            field_dict["autoBlacklist"] = auto_blacklist
        if avatar is not UNSET:
            field_dict["avatar"] = avatar
        if video is not UNSET:
            field_dict["video"] = video
        if video_caption is not UNSET:
            field_dict["videoCaption"] = video_caption
        if user is not UNSET:
            field_dict["user"] = user
        if trending is not UNSET:
            field_dict["trending"] = trending
        if tracker is not UNSET:
            field_dict["tracker"] = tracker
        if followings is not UNSET:
            field_dict["followings"] = followings
        if federation is not UNSET:
            field_dict["federation"] = federation
        if homepage is not UNSET:
            field_dict["homepage"] = homepage
        if open_telemetry is not UNSET:
            field_dict["openTelemetry"] = open_telemetry
        if views is not UNSET:
            field_dict["views"] = views

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        """Create instance from dictionary."""
        from peertube.models.server_config_auto_blacklist import (
            ServerConfigAutoBlacklist,
        )
        from peertube.models.server_config_avatar import ServerConfigAvatar
        from peertube.models.server_config_contact_form import ServerConfigContactForm
        from peertube.models.server_config_email import ServerConfigEmail
        from peertube.models.server_config_export import ServerConfigExport
        from peertube.models.server_config_federation import ServerConfigFederation
        from peertube.models.server_config_followings import ServerConfigFollowings
        from peertube.models.server_config_homepage import ServerConfigHomepage
        from peertube.models.server_config_import import ServerConfigImport
        from peertube.models.server_config_instance import ServerConfigInstance
        from peertube.models.server_config_open_telemetry import (
            ServerConfigOpenTelemetry,
        )
        from peertube.models.server_config_plugin import ServerConfigPlugin
        from peertube.models.server_config_search import ServerConfigSearch
        from peertube.models.server_config_signup import ServerConfigSignup
        from peertube.models.server_config_theme import ServerConfigTheme
        from peertube.models.server_config_tracker import ServerConfigTracker
        from peertube.models.server_config_transcoding import ServerConfigTranscoding
        from peertube.models.server_config_trending import ServerConfigTrending
        from peertube.models.server_config_user import ServerConfigUser
        from peertube.models.server_config_video import ServerConfigVideo
        from peertube.models.server_config_video_caption import ServerConfigVideoCaption
        from peertube.models.server_config_views import ServerConfigViews

        d = dict(src_dict)
        _instance = d.pop("instance", UNSET)
        instance: Unset | ServerConfigInstance
        if isinstance(_instance, Unset):
            instance = UNSET
        else:
            instance = ServerConfigInstance.from_dict(_instance)

        _search = d.pop("search", UNSET)
        search: Unset | ServerConfigSearch
        if isinstance(_search, Unset):
            search = UNSET
        else:
            search = ServerConfigSearch.from_dict(_search)

        _plugin = d.pop("plugin", UNSET)
        plugin: Unset | ServerConfigPlugin
        if isinstance(_plugin, Unset):
            plugin = UNSET
        else:
            plugin = ServerConfigPlugin.from_dict(_plugin)

        _theme = d.pop("theme", UNSET)
        theme: Unset | ServerConfigTheme
        if isinstance(_theme, Unset):
            theme = UNSET
        else:
            theme = ServerConfigTheme.from_dict(_theme)

        _email = d.pop("email", UNSET)
        email: Unset | ServerConfigEmail
        if isinstance(_email, Unset):
            email = UNSET
        else:
            email = ServerConfigEmail.from_dict(_email)

        _contact_form = d.pop("contactForm", UNSET)
        contact_form: Unset | ServerConfigContactForm
        if isinstance(_contact_form, Unset):
            contact_form = UNSET
        else:
            contact_form = ServerConfigContactForm.from_dict(_contact_form)

        server_version = d.pop("serverVersion", UNSET)

        server_commit = d.pop("serverCommit", UNSET)

        _signup = d.pop("signup", UNSET)
        signup: Unset | ServerConfigSignup
        if isinstance(_signup, Unset):
            signup = UNSET
        else:
            signup = ServerConfigSignup.from_dict(_signup)

        _transcoding = d.pop("transcoding", UNSET)
        transcoding: Unset | ServerConfigTranscoding
        if isinstance(_transcoding, Unset):
            transcoding = UNSET
        else:
            transcoding = ServerConfigTranscoding.from_dict(_transcoding)

        _import_ = d.pop("import", UNSET)
        import_: Unset | ServerConfigImport
        if isinstance(_import_, Unset):
            import_ = UNSET
        else:
            import_ = ServerConfigImport.from_dict(_import_)

        _export = d.pop("export", UNSET)
        export: Unset | ServerConfigExport
        if isinstance(_export, Unset):
            export = UNSET
        else:
            export = ServerConfigExport.from_dict(_export)

        _auto_blacklist = d.pop("autoBlacklist", UNSET)
        auto_blacklist: Unset | ServerConfigAutoBlacklist
        if isinstance(_auto_blacklist, Unset):
            auto_blacklist = UNSET
        else:
            auto_blacklist = ServerConfigAutoBlacklist.from_dict(_auto_blacklist)

        _avatar = d.pop("avatar", UNSET)
        avatar: Unset | ServerConfigAvatar
        if isinstance(_avatar, Unset):
            avatar = UNSET
        else:
            avatar = ServerConfigAvatar.from_dict(_avatar)

        _video = d.pop("video", UNSET)
        video: Unset | ServerConfigVideo
        if isinstance(_video, Unset):
            video = UNSET
        else:
            video = ServerConfigVideo.from_dict(_video)

        _video_caption = d.pop("videoCaption", UNSET)
        video_caption: Unset | ServerConfigVideoCaption
        if isinstance(_video_caption, Unset):
            video_caption = UNSET
        else:
            video_caption = ServerConfigVideoCaption.from_dict(_video_caption)

        _user = d.pop("user", UNSET)
        user: Unset | ServerConfigUser
        if isinstance(_user, Unset):
            user = UNSET
        else:
            user = ServerConfigUser.from_dict(_user)

        _trending = d.pop("trending", UNSET)
        trending: Unset | ServerConfigTrending
        if isinstance(_trending, Unset):
            trending = UNSET
        else:
            trending = ServerConfigTrending.from_dict(_trending)

        _tracker = d.pop("tracker", UNSET)
        tracker: Unset | ServerConfigTracker
        if isinstance(_tracker, Unset):
            tracker = UNSET
        else:
            tracker = ServerConfigTracker.from_dict(_tracker)

        _followings = d.pop("followings", UNSET)
        followings: Unset | ServerConfigFollowings
        if isinstance(_followings, Unset):
            followings = UNSET
        else:
            followings = ServerConfigFollowings.from_dict(_followings)

        _federation = d.pop("federation", UNSET)
        federation: Unset | ServerConfigFederation
        if isinstance(_federation, Unset):
            federation = UNSET
        else:
            federation = ServerConfigFederation.from_dict(_federation)

        _homepage = d.pop("homepage", UNSET)
        homepage: Unset | ServerConfigHomepage
        if isinstance(_homepage, Unset):
            homepage = UNSET
        else:
            homepage = ServerConfigHomepage.from_dict(_homepage)

        _open_telemetry = d.pop("openTelemetry", UNSET)
        open_telemetry: Unset | ServerConfigOpenTelemetry
        if isinstance(_open_telemetry, Unset):
            open_telemetry = UNSET
        else:
            open_telemetry = ServerConfigOpenTelemetry.from_dict(_open_telemetry)

        _views = d.pop("views", UNSET)
        views: Unset | ServerConfigViews
        if isinstance(_views, Unset):
            views = UNSET
        else:
            views = ServerConfigViews.from_dict(_views)

        server_config = cls(
            instance=instance,
            search=search,
            plugin=plugin,
            theme=theme,
            email=email,
            contact_form=contact_form,
            server_version=server_version,
            server_commit=server_commit,
            signup=signup,
            transcoding=transcoding,
            import_=import_,
            export=export,
            auto_blacklist=auto_blacklist,
            avatar=avatar,
            video=video,
            video_caption=video_caption,
            user=user,
            trending=trending,
            tracker=tracker,
            followings=followings,
            federation=federation,
            homepage=homepage,
            open_telemetry=open_telemetry,
            views=views,
        )

        server_config.additional_properties = d
        return server_config

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
