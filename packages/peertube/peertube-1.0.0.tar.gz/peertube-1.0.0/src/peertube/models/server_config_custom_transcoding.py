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

from peertube.models.server_config_custom_transcoding_profile import (
    ServerConfigCustomTranscodingProfile,
)
from peertube.types import UNSET, Unset

if TYPE_CHECKING:
    from peertube.models.server_config_custom_transcoding_hls import (
        ServerConfigCustomTranscodingHls,
    )
    from peertube.models.server_config_custom_transcoding_original_file import (
        ServerConfigCustomTranscodingOriginalFile,
    )
    from peertube.models.server_config_custom_transcoding_resolutions import (
        ServerConfigCustomTranscodingResolutions,
    )
    from peertube.models.server_config_custom_transcoding_web_videos import (
        ServerConfigCustomTranscodingWebVideos,
    )


T = TypeVar("T", bound="ServerConfigCustomTranscoding")


@_attrs_define
class ServerConfigCustomTranscoding:
    """Settings pertaining to transcoding jobs

    Attributes:
        enabled (Union[Unset, bool]):
        original_file (Union[Unset, ServerConfigCustomTranscodingOriginalFile]):
        allow_additional_extensions (Union[Unset, bool]): Allow your users to upload .mkv, .mov, .avi, .wmv, .flv, .f4v,
            .3g2, .3gp, .mts, m2ts, .mxf, .nut videos
        allow_audio_files (Union[Unset, bool]): If a user uploads an audio file, PeerTube will create a video by merging
            the preview file and the audio file
        threads (Union[Unset, int]): Amount of threads used by ffmpeg for 1 transcoding job
        concurrency (Union[Unset, float]): Amount of transcoding jobs to execute in parallel
        profile (Union[Unset, ServerConfigCustomTranscodingProfile]): New profiles can be added by plugins ; available
            in core PeerTube: 'default'.
        resolutions (Union[Unset, ServerConfigCustomTranscodingResolutions]): Resolutions to transcode _new videos_ to
        web_videos (Union[Unset, ServerConfigCustomTranscodingWebVideos]): Web Video specific settings
        hls (Union[Unset, ServerConfigCustomTranscodingHls]): HLS specific settings
    """

    enabled: Unset | bool = UNSET
    original_file: Union[Unset, "ServerConfigCustomTranscodingOriginalFile"] = UNSET
    allow_additional_extensions: Unset | bool = UNSET
    allow_audio_files: Unset | bool = UNSET
    threads: Unset | int = UNSET
    concurrency: Unset | float = UNSET
    profile: Unset | ServerConfigCustomTranscodingProfile = UNSET
    resolutions: Union[Unset, "ServerConfigCustomTranscodingResolutions"] = UNSET
    web_videos: Union[Unset, "ServerConfigCustomTranscodingWebVideos"] = UNSET
    hls: Union[Unset, "ServerConfigCustomTranscodingHls"] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert instance to dictionary."""
        enabled = self.enabled

        original_file: Unset | dict[str, Any] = UNSET
        if not isinstance(self.original_file, Unset):
            original_file = self.original_file.to_dict()

        allow_additional_extensions = self.allow_additional_extensions

        allow_audio_files = self.allow_audio_files

        threads = self.threads

        concurrency = self.concurrency

        profile: Unset | str = UNSET
        if not isinstance(self.profile, Unset):
            profile = self.profile.value

        resolutions: Unset | dict[str, Any] = UNSET
        if not isinstance(self.resolutions, Unset):
            resolutions = self.resolutions.to_dict()

        web_videos: Unset | dict[str, Any] = UNSET
        if not isinstance(self.web_videos, Unset):
            web_videos = self.web_videos.to_dict()

        hls: Unset | dict[str, Any] = UNSET
        if not isinstance(self.hls, Unset):
            hls = self.hls.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if enabled is not UNSET:
            field_dict["enabled"] = enabled
        if original_file is not UNSET:
            field_dict["originalFile"] = original_file
        if allow_additional_extensions is not UNSET:
            field_dict["allowAdditionalExtensions"] = allow_additional_extensions
        if allow_audio_files is not UNSET:
            field_dict["allowAudioFiles"] = allow_audio_files
        if threads is not UNSET:
            field_dict["threads"] = threads
        if concurrency is not UNSET:
            field_dict["concurrency"] = concurrency
        if profile is not UNSET:
            field_dict["profile"] = profile
        if resolutions is not UNSET:
            field_dict["resolutions"] = resolutions
        if web_videos is not UNSET:
            field_dict["web_videos"] = web_videos
        if hls is not UNSET:
            field_dict["hls"] = hls

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        """Create instance from dictionary."""
        from peertube.models.server_config_custom_transcoding_hls import (
            ServerConfigCustomTranscodingHls,
        )
        from peertube.models.server_config_custom_transcoding_original_file import (
            ServerConfigCustomTranscodingOriginalFile,
        )
        from peertube.models.server_config_custom_transcoding_resolutions import (
            ServerConfigCustomTranscodingResolutions,
        )
        from peertube.models.server_config_custom_transcoding_web_videos import (
            ServerConfigCustomTranscodingWebVideos,
        )

        d = dict(src_dict)
        enabled = d.pop("enabled", UNSET)

        _original_file = d.pop("originalFile", UNSET)
        original_file: Unset | ServerConfigCustomTranscodingOriginalFile
        if isinstance(_original_file, Unset):
            original_file = UNSET
        else:
            original_file = ServerConfigCustomTranscodingOriginalFile.from_dict(
                _original_file
            )

        allow_additional_extensions = d.pop("allowAdditionalExtensions", UNSET)

        allow_audio_files = d.pop("allowAudioFiles", UNSET)

        threads = d.pop("threads", UNSET)

        concurrency = d.pop("concurrency", UNSET)

        _profile = d.pop("profile", UNSET)
        profile: Unset | ServerConfigCustomTranscodingProfile
        if isinstance(_profile, Unset):
            profile = UNSET
        else:
            profile = ServerConfigCustomTranscodingProfile(_profile)

        _resolutions = d.pop("resolutions", UNSET)
        resolutions: Unset | ServerConfigCustomTranscodingResolutions
        if isinstance(_resolutions, Unset):
            resolutions = UNSET
        else:
            resolutions = ServerConfigCustomTranscodingResolutions.from_dict(
                _resolutions
            )

        _web_videos = d.pop("web_videos", UNSET)
        web_videos: Unset | ServerConfigCustomTranscodingWebVideos
        if isinstance(_web_videos, Unset):
            web_videos = UNSET
        else:
            web_videos = ServerConfigCustomTranscodingWebVideos.from_dict(_web_videos)

        _hls = d.pop("hls", UNSET)
        hls: Unset | ServerConfigCustomTranscodingHls
        if isinstance(_hls, Unset):
            hls = UNSET
        else:
            hls = ServerConfigCustomTranscodingHls.from_dict(_hls)

        server_config_custom_transcoding = cls(
            enabled=enabled,
            original_file=original_file,
            allow_additional_extensions=allow_additional_extensions,
            allow_audio_files=allow_audio_files,
            threads=threads,
            concurrency=concurrency,
            profile=profile,
            resolutions=resolutions,
            web_videos=web_videos,
            hls=hls,
        )

        server_config_custom_transcoding.additional_properties = d
        return server_config_custom_transcoding

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
