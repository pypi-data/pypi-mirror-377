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

from peertube.types import UNSET, Unset

if TYPE_CHECKING:
    from peertube.models.user_registration_state import UserRegistrationState
    from peertube.models.user_registration_user_type_0 import UserRegistrationUserType0


T = TypeVar("T", bound="UserRegistration")


@_attrs_define
class UserRegistration:
    """Attributes:
    id (Union[Unset, int]):  Example: 42.
    state (Union[Unset, UserRegistrationState]):
    registration_reason (Union[Unset, str]):
    moderation_response (Union[None, Unset, str]):
    username (Union[Unset, str]):
    email (Union[Unset, str]):
    email_verified (Union[Unset, bool]):
    account_display_name (Union[Unset, str]):
    channel_handle (Union[Unset, str]):
    channel_display_name (Union[Unset, str]):
    created_at (Union[Unset, datetime.datetime]):
    updated_at (Union[Unset, datetime.datetime]):
    user (Union['UserRegistrationUserType0', None, Unset]): If the registration has been accepted, this is a partial
        user object created by the registration
    """

    id: Unset | int = UNSET
    state: Union[Unset, "UserRegistrationState"] = UNSET
    registration_reason: Unset | str = UNSET
    moderation_response: None | Unset | str = UNSET
    username: Unset | str = UNSET
    email: Unset | str = UNSET
    email_verified: Unset | bool = UNSET
    account_display_name: Unset | str = UNSET
    channel_handle: Unset | str = UNSET
    channel_display_name: Unset | str = UNSET
    created_at: Unset | datetime.datetime = UNSET
    updated_at: Unset | datetime.datetime = UNSET
    user: Union["UserRegistrationUserType0", None, Unset] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert instance to dictionary."""
        from peertube.models.user_registration_user_type_0 import (
            UserRegistrationUserType0,
        )

        id = self.id

        state: Unset | dict[str, Any] = UNSET
        if not isinstance(self.state, Unset):
            state = self.state.to_dict()

        registration_reason = self.registration_reason

        moderation_response: None | Unset | str
        if isinstance(self.moderation_response, Unset):
            moderation_response = UNSET
        else:
            moderation_response = self.moderation_response

        username = self.username

        email = self.email

        email_verified = self.email_verified

        account_display_name = self.account_display_name

        channel_handle = self.channel_handle

        channel_display_name = self.channel_display_name

        created_at: Unset | str = UNSET
        if not isinstance(self.created_at, Unset):
            created_at = self.created_at.isoformat()

        updated_at: Unset | str = UNSET
        if not isinstance(self.updated_at, Unset):
            updated_at = self.updated_at.isoformat()

        user: None | Unset | dict[str, Any]
        if isinstance(self.user, Unset):
            user = UNSET
        elif isinstance(self.user, UserRegistrationUserType0):
            user = self.user.to_dict()
        else:
            user = self.user

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if id is not UNSET:
            field_dict["id"] = id
        if state is not UNSET:
            field_dict["state"] = state
        if registration_reason is not UNSET:
            field_dict["registrationReason"] = registration_reason
        if moderation_response is not UNSET:
            field_dict["moderationResponse"] = moderation_response
        if username is not UNSET:
            field_dict["username"] = username
        if email is not UNSET:
            field_dict["email"] = email
        if email_verified is not UNSET:
            field_dict["emailVerified"] = email_verified
        if account_display_name is not UNSET:
            field_dict["accountDisplayName"] = account_display_name
        if channel_handle is not UNSET:
            field_dict["channelHandle"] = channel_handle
        if channel_display_name is not UNSET:
            field_dict["channelDisplayName"] = channel_display_name
        if created_at is not UNSET:
            field_dict["createdAt"] = created_at
        if updated_at is not UNSET:
            field_dict["updatedAt"] = updated_at
        if user is not UNSET:
            field_dict["user"] = user

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        """Create instance from dictionary."""
        from peertube.models.user_registration_state import UserRegistrationState
        from peertube.models.user_registration_user_type_0 import (
            UserRegistrationUserType0,
        )

        d = dict(src_dict)
        id = d.pop("id", UNSET)

        _state = d.pop("state", UNSET)
        state: Unset | UserRegistrationState
        if isinstance(_state, Unset):
            state = UNSET
        else:
            state = UserRegistrationState.from_dict(_state)

        registration_reason = d.pop("registrationReason", UNSET)

        def _parse_moderation_response(data: object) -> None | Unset | str:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast("None | Unset | str", data)

        moderation_response = _parse_moderation_response(
            d.pop("moderationResponse", UNSET)
        )

        username = d.pop("username", UNSET)

        email = d.pop("email", UNSET)

        email_verified = d.pop("emailVerified", UNSET)

        account_display_name = d.pop("accountDisplayName", UNSET)

        channel_handle = d.pop("channelHandle", UNSET)

        channel_display_name = d.pop("channelDisplayName", UNSET)

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

        def _parse_user(
            data: object,
        ) -> Union["UserRegistrationUserType0", None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError
                user_type_0 = UserRegistrationUserType0.from_dict(data)

                return user_type_0
            except:  # noqa: E722
                pass
            return cast("UserRegistrationUserType0 | None | Unset", data)

        user = _parse_user(d.pop("user", UNSET))

        user_registration = cls(
            id=id,
            state=state,
            registration_reason=registration_reason,
            moderation_response=moderation_response,
            username=username,
            email=email,
            email_verified=email_verified,
            account_display_name=account_display_name,
            channel_handle=channel_handle,
            channel_display_name=channel_display_name,
            created_at=created_at,
            updated_at=updated_at,
            user=user,
        )

        user_registration.additional_properties = d
        return user_registration

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
