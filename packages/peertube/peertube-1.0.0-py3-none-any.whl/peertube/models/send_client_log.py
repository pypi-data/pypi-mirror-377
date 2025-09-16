from collections.abc import Mapping
from typing import (
    Any,
    TypeVar,
)

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from typing_extensions import Self

from peertube.models.send_client_log_level import SendClientLogLevel
from peertube.types import UNSET, Unset

T = TypeVar("T", bound="SendClientLog")


@_attrs_define
class SendClientLog:
    """Attributes:
    message (str):
    url (str): URL of the current user page
    level (SendClientLogLevel):
    stack_trace (Union[Unset, str]): Stack trace of the error if there is one
    user_agent (Union[Unset, str]): User agent of the web browser that sends the message
    meta (Union[Unset, str]): Additional information regarding this log
    """

    message: str
    url: str
    level: SendClientLogLevel
    stack_trace: Unset | str = UNSET
    user_agent: Unset | str = UNSET
    meta: Unset | str = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert instance to dictionary."""
        message = self.message

        url = self.url

        level = self.level.value

        stack_trace = self.stack_trace

        user_agent = self.user_agent

        meta = self.meta

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "message": message,
                "url": url,
                "level": level,
            }
        )
        if stack_trace is not UNSET:
            field_dict["stackTrace"] = stack_trace
        if user_agent is not UNSET:
            field_dict["userAgent"] = user_agent
        if meta is not UNSET:
            field_dict["meta"] = meta

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        """Create instance from dictionary."""
        d = dict(src_dict)
        message = d.pop("message")

        url = d.pop("url")

        level = SendClientLogLevel(d.pop("level"))

        stack_trace = d.pop("stackTrace", UNSET)

        user_agent = d.pop("userAgent", UNSET)

        meta = d.pop("meta", UNSET)

        send_client_log = cls(
            message=message,
            url=url,
            level=level,
            stack_trace=stack_trace,
            user_agent=user_agent,
            meta=meta,
        )

        send_client_log.additional_properties = d
        return send_client_log

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
