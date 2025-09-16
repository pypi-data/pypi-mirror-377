import datetime
from collections.abc import Mapping
from typing import (
    TYPE_CHECKING,
    Any,
    TypeVar,
    Union,
    cast,
)
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse
from typing_extensions import Self

from peertube.models.runner_job_type import RunnerJobType
from peertube.types import UNSET, Unset

if TYPE_CHECKING:
    from peertube.models.runner_job_parent_type_0 import RunnerJobParentType0
    from peertube.models.runner_job_runner import RunnerJobRunner
    from peertube.models.runner_job_state_constant import RunnerJobStateConstant
    from peertube.models.vod_audio_merge_transcoding import VODAudioMergeTranscoding
    from peertube.models.vod_web_video_transcoding import VODWebVideoTranscoding
    from peertube.models.vodhls_transcoding import VODHLSTranscoding


T = TypeVar("T", bound="RunnerJob")


@_attrs_define
class RunnerJob:
    """Attributes:
    uuid (Union[Unset, UUID]):  Example: 9c9de5e8-0a1e-484a-b099-e80766180a6d.
    type_ (Union[Unset, RunnerJobType]):
    state (Union[Unset, RunnerJobStateConstant]):
    payload (Union['VODAudioMergeTranscoding', 'VODHLSTranscoding', 'VODWebVideoTranscoding', Unset]):
    failures (Union[Unset, int]): Number of times a remote runner failed to process this job. After too many
        failures, the job in "error" state
    error (Union[None, Unset, str]): Error message if the job is errored
    progress (Union[Unset, int]): Percentage progress
    priority (Union[Unset, int]): Job priority (less has more priority)
    updated_at (Union[Unset, datetime.datetime]):
    created_at (Union[Unset, datetime.datetime]):
    started_at (Union[Unset, datetime.datetime]):
    finished_at (Union[Unset, datetime.datetime]):
    parent (Union['RunnerJobParentType0', None, Unset]): If job has a parent job
    runner (Union[Unset, RunnerJobRunner]): If job is associated to a runner
    """

    uuid: Unset | UUID = UNSET
    type_: Unset | RunnerJobType = UNSET
    state: Union[Unset, "RunnerJobStateConstant"] = UNSET
    payload: Union[
        "VODAudioMergeTranscoding", "VODHLSTranscoding", "VODWebVideoTranscoding", Unset
    ] = UNSET
    failures: Unset | int = UNSET
    error: None | Unset | str = UNSET
    progress: Unset | int = UNSET
    priority: Unset | int = UNSET
    updated_at: Unset | datetime.datetime = UNSET
    created_at: Unset | datetime.datetime = UNSET
    started_at: Unset | datetime.datetime = UNSET
    finished_at: Unset | datetime.datetime = UNSET
    parent: Union["RunnerJobParentType0", None, Unset] = UNSET
    runner: Union[Unset, "RunnerJobRunner"] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        from peertube.models.runner_job_parent_type_0 import RunnerJobParentType0
        from peertube.models.vod_web_video_transcoding import VODWebVideoTranscoding
        from peertube.models.vodhls_transcoding import VODHLSTranscoding

        uuid: Unset | str = UNSET
        if not isinstance(self.uuid, Unset):
            uuid = str(self.uuid)

        type_: Unset | str = UNSET
        if not isinstance(self.type_, Unset):
            type_ = self.type_.value

        state: Unset | dict[str, Any] = UNSET
        if not isinstance(self.state, Unset):
            state = self.state.to_dict()

        payload: Unset | dict[str, Any]
        if isinstance(self.payload, Unset):
            payload = UNSET
        elif isinstance(self.payload, (VODWebVideoTranscoding, VODHLSTranscoding)):
            payload = self.payload.to_dict()
        else:
            payload = self.payload.to_dict()

        failures = self.failures

        error: None | Unset | str
        if isinstance(self.error, Unset):
            error = UNSET
        else:
            error = self.error

        progress = self.progress

        priority = self.priority

        updated_at: Unset | str = UNSET
        if not isinstance(self.updated_at, Unset):
            updated_at = self.updated_at.isoformat()

        created_at: Unset | str = UNSET
        if not isinstance(self.created_at, Unset):
            created_at = self.created_at.isoformat()

        started_at: Unset | str = UNSET
        if not isinstance(self.started_at, Unset):
            started_at = self.started_at.isoformat()

        finished_at: Unset | str = UNSET
        if not isinstance(self.finished_at, Unset):
            finished_at = self.finished_at.isoformat()

        parent: None | Unset | dict[str, Any]
        if isinstance(self.parent, Unset):
            parent = UNSET
        elif isinstance(self.parent, RunnerJobParentType0):
            parent = self.parent.to_dict()
        else:
            parent = self.parent

        runner: Unset | dict[str, Any] = UNSET
        if not isinstance(self.runner, Unset):
            runner = self.runner.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if uuid is not UNSET:
            field_dict["uuid"] = uuid
        if type_ is not UNSET:
            field_dict["type"] = type_
        if state is not UNSET:
            field_dict["state"] = state
        if payload is not UNSET:
            field_dict["payload"] = payload
        if failures is not UNSET:
            field_dict["failures"] = failures
        if error is not UNSET:
            field_dict["error"] = error
        if progress is not UNSET:
            field_dict["progress"] = progress
        if priority is not UNSET:
            field_dict["priority"] = priority
        if updated_at is not UNSET:
            field_dict["updatedAt"] = updated_at
        if created_at is not UNSET:
            field_dict["createdAt"] = created_at
        if started_at is not UNSET:
            field_dict["startedAt"] = started_at
        if finished_at is not UNSET:
            field_dict["finishedAt"] = finished_at
        if parent is not UNSET:
            field_dict["parent"] = parent
        if runner is not UNSET:
            field_dict["runner"] = runner

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        """Create from dictionary."""
        from peertube.models.runner_job_parent_type_0 import RunnerJobParentType0
        from peertube.models.runner_job_runner import RunnerJobRunner
        from peertube.models.runner_job_state_constant import RunnerJobStateConstant
        from peertube.models.vod_audio_merge_transcoding import VODAudioMergeTranscoding
        from peertube.models.vod_web_video_transcoding import VODWebVideoTranscoding
        from peertube.models.vodhls_transcoding import VODHLSTranscoding

        d = dict(src_dict)
        _uuid = d.pop("uuid", UNSET)
        uuid: Unset | UUID
        if isinstance(_uuid, Unset):
            uuid = UNSET
        else:
            uuid = UUID(_uuid)

        _type_ = d.pop("type", UNSET)
        type_: Unset | RunnerJobType
        if isinstance(_type_, Unset):
            type_ = UNSET
        else:
            type_ = RunnerJobType(_type_)

        _state = d.pop("state", UNSET)
        state: Unset | RunnerJobStateConstant
        if isinstance(_state, Unset):
            state = UNSET
        else:
            state = RunnerJobStateConstant.from_dict(_state)

        def _parse_payload(
            data: object,
        ) -> Union[
            "VODAudioMergeTranscoding",
            "VODHLSTranscoding",
            "VODWebVideoTranscoding",
            Unset,
        ]:
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError
                componentsschemas_runner_job_payload_vod_web_video_transcoding = (
                    VODWebVideoTranscoding.from_dict(data)
                )

                return componentsschemas_runner_job_payload_vod_web_video_transcoding
            except:  # noqa: E722
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError
                componentsschemas_runner_job_payload_vod_hls_transcoding = (
                    VODHLSTranscoding.from_dict(data)
                )

                return componentsschemas_runner_job_payload_vod_hls_transcoding
            except:  # noqa: E722
                pass
            if not isinstance(data, dict):
                raise TypeError
            componentsschemas_runner_job_payload_vod_audio_merge_transcoding = (
                VODAudioMergeTranscoding.from_dict(data)
            )

            return componentsschemas_runner_job_payload_vod_audio_merge_transcoding

        payload = _parse_payload(d.pop("payload", UNSET))

        failures = d.pop("failures", UNSET)

        def _parse_error(data: object) -> None | Unset | str:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast("None | Unset | str", data)

        error = _parse_error(d.pop("error", UNSET))

        progress = d.pop("progress", UNSET)

        priority = d.pop("priority", UNSET)

        _updated_at = d.pop("updatedAt", UNSET)
        updated_at: Unset | datetime.datetime
        if isinstance(_updated_at, Unset):
            updated_at = UNSET
        else:
            updated_at = isoparse(_updated_at)

        _created_at = d.pop("createdAt", UNSET)
        created_at: Unset | datetime.datetime
        if isinstance(_created_at, Unset):
            created_at = UNSET
        else:
            created_at = isoparse(_created_at)

        _started_at = d.pop("startedAt", UNSET)
        started_at: Unset | datetime.datetime
        if isinstance(_started_at, Unset):
            started_at = UNSET
        else:
            started_at = isoparse(_started_at)

        _finished_at = d.pop("finishedAt", UNSET)
        finished_at: Unset | datetime.datetime
        if isinstance(_finished_at, Unset):
            finished_at = UNSET
        else:
            finished_at = isoparse(_finished_at)

        def _parse_parent(data: object) -> Union["RunnerJobParentType0", None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError
                parent_type_0 = RunnerJobParentType0.from_dict(data)

                return parent_type_0
            except:  # noqa: E722
                pass
            return cast("RunnerJobParentType0 | None | Unset", data)

        parent = _parse_parent(d.pop("parent", UNSET))

        _runner = d.pop("runner", UNSET)
        runner: Unset | RunnerJobRunner
        if isinstance(_runner, Unset):
            runner = UNSET
        else:
            runner = RunnerJobRunner.from_dict(_runner)

        runner_job = cls(
            uuid=uuid,
            type_=type_,
            state=state,
            payload=payload,
            failures=failures,
            error=error,
            progress=progress,
            priority=priority,
            updated_at=updated_at,
            created_at=created_at,
            started_at=started_at,
            finished_at=finished_at,
            parent=parent,
            runner=runner,
        )

        runner_job.additional_properties = d
        return runner_job

    @property
    def additional_keys(self) -> list[str]:
        """Get additional keys."""
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
