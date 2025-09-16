import datetime
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
from dateutil.parser import isoparse
from typing_extensions import Self

from peertube.models.live_video_session_response_error import (
    LiveVideoSessionResponseError,
)
from peertube.types import UNSET, Unset

if TYPE_CHECKING:
    from peertube.models.live_video_session_response_replay_video import (
        LiveVideoSessionResponseReplayVideo,
    )


T = TypeVar("T", bound="LiveVideoSessionResponse")


@_attrs_define
class LiveVideoSessionResponse:
    """Attributes:
    id (Union[Unset, int]):
    start_date (Union[Unset, datetime.datetime]): Start date of the live session
    end_date (Union[None, Unset, datetime.datetime]): End date of the live session
    error (Union[Unset, LiveVideoSessionResponseError]): Error type if an error occurred during the live session:
          - `1`: Bad socket health (transcoding is too slow)
          - `2`: Max duration exceeded
          - `3`: Quota exceeded
          - `4`: Quota FFmpeg error
          - `5`: Video has been blacklisted during the live
    replay_video (Union[Unset, LiveVideoSessionResponseReplayVideo]): Video replay information
    """

    id: Unset | int = UNSET
    start_date: Unset | datetime.datetime = UNSET
    end_date: None | Unset | datetime.datetime = UNSET
    error: Unset | LiveVideoSessionResponseError = UNSET
    replay_video: Union[Unset, "LiveVideoSessionResponseReplayVideo"] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert instance to dictionary."""
        id = self.id

        start_date: Unset | str = UNSET
        if not isinstance(self.start_date, Unset):
            start_date = self.start_date.isoformat()

        end_date: None | Unset | str
        if isinstance(self.end_date, Unset):
            end_date = UNSET
        elif isinstance(self.end_date, datetime.datetime):
            end_date = self.end_date.isoformat()
        else:
            end_date = self.end_date

        error: Unset | int = UNSET
        if not isinstance(self.error, Unset):
            error = self.error.value

        replay_video: Unset | dict[str, Any] = UNSET
        if not isinstance(self.replay_video, Unset):
            replay_video = self.replay_video.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if id is not UNSET:
            field_dict["id"] = id
        if start_date is not UNSET:
            field_dict["startDate"] = start_date
        if end_date is not UNSET:
            field_dict["endDate"] = end_date
        if error is not UNSET:
            field_dict["error"] = error
        if replay_video is not UNSET:
            field_dict["replayVideo"] = replay_video

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        """Create instance from dictionary."""
        from peertube.models.live_video_session_response_replay_video import (
            LiveVideoSessionResponseReplayVideo,
        )

        d = dict(src_dict)
        id = d.pop("id", UNSET)

        _start_date = d.pop("startDate", UNSET)
        start_date: Unset | datetime.datetime
        if isinstance(_start_date, Unset):
            start_date = UNSET
        else:
            start_date = isoparse(_start_date)

        def _parse_end_date(data: object) -> None | Unset | datetime.datetime:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError
                end_date_type_0 = isoparse(data)

                return end_date_type_0
            except:  # noqa: E722
                pass
            return cast("None | Unset | datetime.datetime", data)

        end_date = _parse_end_date(d.pop("endDate", UNSET))

        _error = d.pop("error", UNSET)
        error: Unset | LiveVideoSessionResponseError
        if isinstance(_error, Unset):
            error = UNSET
        else:
            error = LiveVideoSessionResponseError(_error)

        _replay_video = d.pop("replayVideo", UNSET)
        replay_video: Unset | LiveVideoSessionResponseReplayVideo
        if isinstance(_replay_video, Unset):
            replay_video = UNSET
        else:
            replay_video = LiveVideoSessionResponseReplayVideo.from_dict(_replay_video)

        live_video_session_response = cls(
            id=id,
            start_date=start_date,
            end_date=end_date,
            error=error,
            replay_video=replay_video,
        )

        live_video_session_response.additional_properties = d
        return live_video_session_response

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
