from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from typing_extensions import Self

from peertube.models.put_api_v1_videos_id_rate_body_rating import (
    PutApiV1VideosIdRateBodyRating,
)

T = TypeVar("T", bound="PutApiV1VideosIdRateBody")


@_attrs_define
class PutApiV1VideosIdRateBody:
    """Attributes:
    rating (PutApiV1VideosIdRateBodyRating):
    """

    rating: PutApiV1VideosIdRateBodyRating
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert instance to dictionary."""
        rating = self.rating.value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "rating": rating,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        """Create instance from dictionary."""
        d = dict(src_dict)
        rating = PutApiV1VideosIdRateBodyRating(d.pop("rating"))

        put_api_v1_videos_id_rate_body = cls(
            rating=rating,
        )

        put_api_v1_videos_id_rate_body.additional_properties = d
        return put_api_v1_videos_id_rate_body

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
