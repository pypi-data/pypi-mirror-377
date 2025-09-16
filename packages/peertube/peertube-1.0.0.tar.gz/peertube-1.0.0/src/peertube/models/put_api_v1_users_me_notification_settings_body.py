from collections.abc import Mapping
from typing import (
    Any,
    TypeVar,
)

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from typing_extensions import Self

from peertube.types import UNSET, Unset

T = TypeVar("T", bound="PutApiV1UsersMeNotificationSettingsBody")


@_attrs_define
class PutApiV1UsersMeNotificationSettingsBody:
    """Attributes:
    abuse_as_moderator (Union[Unset, int]): Notification type. One of the following values, or a sum of multiple
        values:
        - `0` NONE
        - `1` WEB
        - `2` EMAIL
    video_auto_blacklist_as_moderator (Union[Unset, int]): Notification type. One of the following values, or a sum
        of multiple values:
        - `0` NONE
        - `1` WEB
        - `2` EMAIL
    new_user_registration (Union[Unset, int]): Notification type. One of the following values, or a sum of multiple
        values:
        - `0` NONE
        - `1` WEB
        - `2` EMAIL
    new_video_from_subscription (Union[Unset, int]): Notification type. One of the following values, or a sum of
        multiple values:
        - `0` NONE
        - `1` WEB
        - `2` EMAIL
    blacklist_on_my_video (Union[Unset, int]): Notification type. One of the following values, or a sum of multiple
        values:
        - `0` NONE
        - `1` WEB
        - `2` EMAIL
    my_video_published (Union[Unset, int]): Notification type. One of the following values, or a sum of multiple
        values:
        - `0` NONE
        - `1` WEB
        - `2` EMAIL
    my_video_import_finished (Union[Unset, int]): Notification type. One of the following values, or a sum of
        multiple values:
        - `0` NONE
        - `1` WEB
        - `2` EMAIL
    comment_mention (Union[Unset, int]): Notification type. One of the following values, or a sum of multiple
        values:
        - `0` NONE
        - `1` WEB
        - `2` EMAIL
    new_comment_on_my_video (Union[Unset, int]): Notification type. One of the following values, or a sum of
        multiple values:
        - `0` NONE
        - `1` WEB
        - `2` EMAIL
    new_follow (Union[Unset, int]): Notification type. One of the following values, or a sum of multiple values:
        - `0` NONE
        - `1` WEB
        - `2` EMAIL
    new_instance_follower (Union[Unset, int]): Notification type. One of the following values, or a sum of multiple
        values:
        - `0` NONE
        - `1` WEB
        - `2` EMAIL
    auto_instance_following (Union[Unset, int]): Notification type. One of the following values, or a sum of
        multiple values:
        - `0` NONE
        - `1` WEB
        - `2` EMAIL
    abuse_state_change (Union[Unset, int]): Notification type. One of the following values, or a sum of multiple
        values:
        - `0` NONE
        - `1` WEB
        - `2` EMAIL
    abuse_new_message (Union[Unset, int]): Notification type. One of the following values, or a sum of multiple
        values:
        - `0` NONE
        - `1` WEB
        - `2` EMAIL
    new_peer_tube_version (Union[Unset, int]): Notification type. One of the following values, or a sum of multiple
        values:
        - `0` NONE
        - `1` WEB
        - `2` EMAIL
    new_plugin_version (Union[Unset, int]): Notification type. One of the following values, or a sum of multiple
        values:
        - `0` NONE
        - `1` WEB
        - `2` EMAIL
    my_video_studio_edition_finished (Union[Unset, int]): Notification type. One of the following values, or a sum
        of multiple values:
        - `0` NONE
        - `1` WEB
        - `2` EMAIL
    my_video_transcription_generated (Union[Unset, int]): Notification type. One of the following values, or a sum
        of multiple values:
        - `0` NONE
        - `1` WEB
        - `2` EMAIL
    """

    abuse_as_moderator: Unset | int = UNSET
    video_auto_blacklist_as_moderator: Unset | int = UNSET
    new_user_registration: Unset | int = UNSET
    new_video_from_subscription: Unset | int = UNSET
    blacklist_on_my_video: Unset | int = UNSET
    my_video_published: Unset | int = UNSET
    my_video_import_finished: Unset | int = UNSET
    comment_mention: Unset | int = UNSET
    new_comment_on_my_video: Unset | int = UNSET
    new_follow: Unset | int = UNSET
    new_instance_follower: Unset | int = UNSET
    auto_instance_following: Unset | int = UNSET
    abuse_state_change: Unset | int = UNSET
    abuse_new_message: Unset | int = UNSET
    new_peer_tube_version: Unset | int = UNSET
    new_plugin_version: Unset | int = UNSET
    my_video_studio_edition_finished: Unset | int = UNSET
    my_video_transcription_generated: Unset | int = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert instance to dictionary."""
        abuse_as_moderator = self.abuse_as_moderator

        video_auto_blacklist_as_moderator = self.video_auto_blacklist_as_moderator

        new_user_registration = self.new_user_registration

        new_video_from_subscription = self.new_video_from_subscription

        blacklist_on_my_video = self.blacklist_on_my_video

        my_video_published = self.my_video_published

        my_video_import_finished = self.my_video_import_finished

        comment_mention = self.comment_mention

        new_comment_on_my_video = self.new_comment_on_my_video

        new_follow = self.new_follow

        new_instance_follower = self.new_instance_follower

        auto_instance_following = self.auto_instance_following

        abuse_state_change = self.abuse_state_change

        abuse_new_message = self.abuse_new_message

        new_peer_tube_version = self.new_peer_tube_version

        new_plugin_version = self.new_plugin_version

        my_video_studio_edition_finished = self.my_video_studio_edition_finished

        my_video_transcription_generated = self.my_video_transcription_generated

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if abuse_as_moderator is not UNSET:
            field_dict["abuseAsModerator"] = abuse_as_moderator
        if video_auto_blacklist_as_moderator is not UNSET:
            field_dict["videoAutoBlacklistAsModerator"] = (
                video_auto_blacklist_as_moderator
            )
        if new_user_registration is not UNSET:
            field_dict["newUserRegistration"] = new_user_registration
        if new_video_from_subscription is not UNSET:
            field_dict["newVideoFromSubscription"] = new_video_from_subscription
        if blacklist_on_my_video is not UNSET:
            field_dict["blacklistOnMyVideo"] = blacklist_on_my_video
        if my_video_published is not UNSET:
            field_dict["myVideoPublished"] = my_video_published
        if my_video_import_finished is not UNSET:
            field_dict["myVideoImportFinished"] = my_video_import_finished
        if comment_mention is not UNSET:
            field_dict["commentMention"] = comment_mention
        if new_comment_on_my_video is not UNSET:
            field_dict["newCommentOnMyVideo"] = new_comment_on_my_video
        if new_follow is not UNSET:
            field_dict["newFollow"] = new_follow
        if new_instance_follower is not UNSET:
            field_dict["newInstanceFollower"] = new_instance_follower
        if auto_instance_following is not UNSET:
            field_dict["autoInstanceFollowing"] = auto_instance_following
        if abuse_state_change is not UNSET:
            field_dict["abuseStateChange"] = abuse_state_change
        if abuse_new_message is not UNSET:
            field_dict["abuseNewMessage"] = abuse_new_message
        if new_peer_tube_version is not UNSET:
            field_dict["newPeerTubeVersion"] = new_peer_tube_version
        if new_plugin_version is not UNSET:
            field_dict["newPluginVersion"] = new_plugin_version
        if my_video_studio_edition_finished is not UNSET:
            field_dict["myVideoStudioEditionFinished"] = (
                my_video_studio_edition_finished
            )
        if my_video_transcription_generated is not UNSET:
            field_dict["myVideoTranscriptionGenerated"] = (
                my_video_transcription_generated
            )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        """Create instance from dictionary."""
        d = dict(src_dict)
        abuse_as_moderator = d.pop("abuseAsModerator", UNSET)

        video_auto_blacklist_as_moderator = d.pop(
            "videoAutoBlacklistAsModerator", UNSET
        )

        new_user_registration = d.pop("newUserRegistration", UNSET)

        new_video_from_subscription = d.pop("newVideoFromSubscription", UNSET)

        blacklist_on_my_video = d.pop("blacklistOnMyVideo", UNSET)

        my_video_published = d.pop("myVideoPublished", UNSET)

        my_video_import_finished = d.pop("myVideoImportFinished", UNSET)

        comment_mention = d.pop("commentMention", UNSET)

        new_comment_on_my_video = d.pop("newCommentOnMyVideo", UNSET)

        new_follow = d.pop("newFollow", UNSET)

        new_instance_follower = d.pop("newInstanceFollower", UNSET)

        auto_instance_following = d.pop("autoInstanceFollowing", UNSET)

        abuse_state_change = d.pop("abuseStateChange", UNSET)

        abuse_new_message = d.pop("abuseNewMessage", UNSET)

        new_peer_tube_version = d.pop("newPeerTubeVersion", UNSET)

        new_plugin_version = d.pop("newPluginVersion", UNSET)

        my_video_studio_edition_finished = d.pop("myVideoStudioEditionFinished", UNSET)

        my_video_transcription_generated = d.pop("myVideoTranscriptionGenerated", UNSET)

        put_api_v1_users_me_notification_settings_body = cls(
            abuse_as_moderator=abuse_as_moderator,
            video_auto_blacklist_as_moderator=video_auto_blacklist_as_moderator,
            new_user_registration=new_user_registration,
            new_video_from_subscription=new_video_from_subscription,
            blacklist_on_my_video=blacklist_on_my_video,
            my_video_published=my_video_published,
            my_video_import_finished=my_video_import_finished,
            comment_mention=comment_mention,
            new_comment_on_my_video=new_comment_on_my_video,
            new_follow=new_follow,
            new_instance_follower=new_instance_follower,
            auto_instance_following=auto_instance_following,
            abuse_state_change=abuse_state_change,
            abuse_new_message=abuse_new_message,
            new_peer_tube_version=new_peer_tube_version,
            new_plugin_version=new_plugin_version,
            my_video_studio_edition_finished=my_video_studio_edition_finished,
            my_video_transcription_generated=my_video_transcription_generated,
        )

        put_api_v1_users_me_notification_settings_body.additional_properties = d
        return put_api_v1_users_me_notification_settings_body

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
