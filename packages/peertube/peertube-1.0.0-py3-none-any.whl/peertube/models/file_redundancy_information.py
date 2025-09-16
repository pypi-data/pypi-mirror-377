import datetime
from collections.abc import Mapping
from typing import (
    Any,
    TypeVar,
)

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse
from typing_extensions import Self

from peertube.models.file_redundancy_information_strategy import (
    FileRedundancyInformationStrategy,
)
from peertube.types import UNSET, Unset

T = TypeVar("T", bound="FileRedundancyInformation")


@_attrs_define
class FileRedundancyInformation:
    """Attributes:
    id (Union[Unset, int]):  Example: 42.
    file_url (Union[Unset, str]):
    strategy (Union[Unset, FileRedundancyInformationStrategy]):
    size (Union[Unset, int]):
    created_at (Union[Unset, datetime.datetime]):
    updated_at (Union[Unset, datetime.datetime]):
    expires_on (Union[Unset, datetime.datetime]):
    """

    id: Unset | int = UNSET
    file_url: Unset | str = UNSET
    strategy: Unset | FileRedundancyInformationStrategy = UNSET
    size: Unset | int = UNSET
    created_at: Unset | datetime.datetime = UNSET
    updated_at: Unset | datetime.datetime = UNSET
    expires_on: Unset | datetime.datetime = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert instance to dictionary."""
        id = self.id

        file_url = self.file_url

        strategy: Unset | str = UNSET
        if not isinstance(self.strategy, Unset):
            strategy = self.strategy.value

        size = self.size

        created_at: Unset | str = UNSET
        if not isinstance(self.created_at, Unset):
            created_at = self.created_at.isoformat()

        updated_at: Unset | str = UNSET
        if not isinstance(self.updated_at, Unset):
            updated_at = self.updated_at.isoformat()

        expires_on: Unset | str = UNSET
        if not isinstance(self.expires_on, Unset):
            expires_on = self.expires_on.isoformat()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if id is not UNSET:
            field_dict["id"] = id
        if file_url is not UNSET:
            field_dict["fileUrl"] = file_url
        if strategy is not UNSET:
            field_dict["strategy"] = strategy
        if size is not UNSET:
            field_dict["size"] = size
        if created_at is not UNSET:
            field_dict["createdAt"] = created_at
        if updated_at is not UNSET:
            field_dict["updatedAt"] = updated_at
        if expires_on is not UNSET:
            field_dict["expiresOn"] = expires_on

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        """Create instance from dictionary."""
        d = dict(src_dict)
        id = d.pop("id", UNSET)

        file_url = d.pop("fileUrl", UNSET)

        _strategy = d.pop("strategy", UNSET)
        strategy: Unset | FileRedundancyInformationStrategy
        if isinstance(_strategy, Unset):
            strategy = UNSET
        else:
            strategy = FileRedundancyInformationStrategy(_strategy)

        size = d.pop("size", UNSET)

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

        _expires_on = d.pop("expiresOn", UNSET)
        expires_on: Unset | datetime.datetime
        if isinstance(_expires_on, Unset):
            expires_on = UNSET
        else:
            expires_on = isoparse(_expires_on)

        file_redundancy_information = cls(
            id=id,
            file_url=file_url,
            strategy=strategy,
            size=size,
            created_at=created_at,
            updated_at=updated_at,
            expires_on=expires_on,
        )

        file_redundancy_information.additional_properties = d
        return file_redundancy_information

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
