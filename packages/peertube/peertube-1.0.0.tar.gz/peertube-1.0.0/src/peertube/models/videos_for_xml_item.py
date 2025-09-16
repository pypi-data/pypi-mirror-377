import datetime
from collections.abc import Mapping
from typing import (
    TYPE_CHECKING,
    Any,
    TypeVar,
    Union,
)

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse
from typing_extensions import Self

from peertube.models.videos_for_xml_item_mediarating import VideosForXMLItemMediarating
from peertube.types import UNSET, Unset

if TYPE_CHECKING:
    from peertube.models.mrss_group_content import MRSSGroupContent
    from peertube.models.mrss_peer_link import MRSSPeerLink
    from peertube.models.videos_for_xml_item_enclosure import VideosForXMLItemEnclosure
    from peertube.models.videos_for_xml_item_mediacommunity import (
        VideosForXMLItemMediacommunity,
    )
    from peertube.models.videos_for_xml_item_mediaembed import (
        VideosForXMLItemMediaembed,
    )
    from peertube.models.videos_for_xml_item_mediaplayer import (
        VideosForXMLItemMediaplayer,
    )
    from peertube.models.videos_for_xml_item_mediathumbnail import (
        VideosForXMLItemMediathumbnail,
    )


T = TypeVar("T", bound="VideosForXMLItem")


@_attrs_define
class VideosForXMLItem:
    """Attributes:
    link (Union[Unset, str]): video watch page URL
    guid (Union[Unset, str]): video canonical URL
    pub_date (Union[Unset, datetime.datetime]): video publication date
    description (Union[Unset, str]): video description
    contentencoded (Union[Unset, str]): video description
    dccreator (Union[Unset, str]): publisher user name
    mediacategory (Union[Unset, int]): video category (MRSS)
    mediacommunity (Union[Unset, VideosForXMLItemMediacommunity]): see
        [media:community](https://www.rssboard.org/media-rss#media-community) (MRSS)
    mediaembed (Union[Unset, VideosForXMLItemMediaembed]):
    mediaplayer (Union[Unset, VideosForXMLItemMediaplayer]):
    mediathumbnail (Union[Unset, VideosForXMLItemMediathumbnail]):
    mediatitle (Union[Unset, str]): see [media:title](https://www.rssboard.org/media-rss#media-title) (MRSS). We
        only use `plain` titles.
    mediadescription (Union[Unset, str]):
    mediarating (Union[Unset, VideosForXMLItemMediarating]): see [media:rating](https://www.rssboard.org/media-
        rss#media-rating) (MRSS)
    enclosure (Union[Unset, VideosForXMLItemEnclosure]): main streamable file for the video
    mediagroup (Union[Unset, list[Union['MRSSGroupContent', 'MRSSPeerLink']]]): list of streamable files for the
        video. see [media:peerLink](https://www.rssboard.org/media-rss#media-peerlink) and
        [media:content](https://www.rssboard.org/media-rss#media-content) or  (MRSS)
    """

    link: Unset | str = UNSET
    guid: Unset | str = UNSET
    pub_date: Unset | datetime.datetime = UNSET
    description: Unset | str = UNSET
    contentencoded: Unset | str = UNSET
    dccreator: Unset | str = UNSET
    mediacategory: Unset | int = UNSET
    mediacommunity: Union[Unset, "VideosForXMLItemMediacommunity"] = UNSET
    mediaembed: Union[Unset, "VideosForXMLItemMediaembed"] = UNSET
    mediaplayer: Union[Unset, "VideosForXMLItemMediaplayer"] = UNSET
    mediathumbnail: Union[Unset, "VideosForXMLItemMediathumbnail"] = UNSET
    mediatitle: Unset | str = UNSET
    mediadescription: Unset | str = UNSET
    mediarating: Unset | VideosForXMLItemMediarating = UNSET
    enclosure: Union[Unset, "VideosForXMLItemEnclosure"] = UNSET
    mediagroup: Unset | list[Union["MRSSGroupContent", "MRSSPeerLink"]] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert instance to dictionary."""
        from peertube.models.mrss_peer_link import MRSSPeerLink

        link = self.link

        guid = self.guid

        pub_date: Unset | str = UNSET
        if not isinstance(self.pub_date, Unset):
            pub_date = self.pub_date.isoformat()

        description = self.description

        contentencoded = self.contentencoded

        dccreator = self.dccreator

        mediacategory = self.mediacategory

        mediacommunity: Unset | dict[str, Any] = UNSET
        if not isinstance(self.mediacommunity, Unset):
            mediacommunity = self.mediacommunity.to_dict()

        mediaembed: Unset | dict[str, Any] = UNSET
        if not isinstance(self.mediaembed, Unset):
            mediaembed = self.mediaembed.to_dict()

        mediaplayer: Unset | dict[str, Any] = UNSET
        if not isinstance(self.mediaplayer, Unset):
            mediaplayer = self.mediaplayer.to_dict()

        mediathumbnail: Unset | dict[str, Any] = UNSET
        if not isinstance(self.mediathumbnail, Unset):
            mediathumbnail = self.mediathumbnail.to_dict()

        mediatitle = self.mediatitle

        mediadescription = self.mediadescription

        mediarating: Unset | str = UNSET
        if not isinstance(self.mediarating, Unset):
            mediarating = self.mediarating.value

        enclosure: Unset | dict[str, Any] = UNSET
        if not isinstance(self.enclosure, Unset):
            enclosure = self.enclosure.to_dict()

        mediagroup: Unset | list[dict[str, Any]] = UNSET
        if not isinstance(self.mediagroup, Unset):
            mediagroup = []
            for mediagroup_item_data in self.mediagroup:
                mediagroup_item: dict[str, Any]
                if isinstance(mediagroup_item_data, MRSSPeerLink):
                    mediagroup_item = mediagroup_item_data.to_dict()
                else:
                    mediagroup_item = mediagroup_item_data.to_dict()

                mediagroup.append(mediagroup_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if link is not UNSET:
            field_dict["link"] = link
        if guid is not UNSET:
            field_dict["guid"] = guid
        if pub_date is not UNSET:
            field_dict["pubDate"] = pub_date
        if description is not UNSET:
            field_dict["description"] = description
        if contentencoded is not UNSET:
            field_dict["content:encoded"] = contentencoded
        if dccreator is not UNSET:
            field_dict["dc:creator"] = dccreator
        if mediacategory is not UNSET:
            field_dict["media:category"] = mediacategory
        if mediacommunity is not UNSET:
            field_dict["media:community"] = mediacommunity
        if mediaembed is not UNSET:
            field_dict["media:embed"] = mediaembed
        if mediaplayer is not UNSET:
            field_dict["media:player"] = mediaplayer
        if mediathumbnail is not UNSET:
            field_dict["media:thumbnail"] = mediathumbnail
        if mediatitle is not UNSET:
            field_dict["media:title"] = mediatitle
        if mediadescription is not UNSET:
            field_dict["media:description"] = mediadescription
        if mediarating is not UNSET:
            field_dict["media:rating"] = mediarating
        if enclosure is not UNSET:
            field_dict["enclosure"] = enclosure
        if mediagroup is not UNSET:
            field_dict["media:group"] = mediagroup

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        """Create instance from dictionary."""
        from peertube.models.mrss_group_content import MRSSGroupContent
        from peertube.models.mrss_peer_link import MRSSPeerLink
        from peertube.models.videos_for_xml_item_enclosure import (
            VideosForXMLItemEnclosure,
        )
        from peertube.models.videos_for_xml_item_mediacommunity import (
            VideosForXMLItemMediacommunity,
        )
        from peertube.models.videos_for_xml_item_mediaembed import (
            VideosForXMLItemMediaembed,
        )
        from peertube.models.videos_for_xml_item_mediaplayer import (
            VideosForXMLItemMediaplayer,
        )
        from peertube.models.videos_for_xml_item_mediathumbnail import (
            VideosForXMLItemMediathumbnail,
        )

        d = dict(src_dict)
        link = d.pop("link", UNSET)

        guid = d.pop("guid", UNSET)

        _pub_date = d.pop("pubDate", UNSET)
        pub_date: Unset | datetime.datetime
        if isinstance(_pub_date, Unset):
            pub_date = UNSET
        else:
            pub_date = isoparse(_pub_date)

        description = d.pop("description", UNSET)

        contentencoded = d.pop("content:encoded", UNSET)

        dccreator = d.pop("dc:creator", UNSET)

        mediacategory = d.pop("media:category", UNSET)

        _mediacommunity = d.pop("media:community", UNSET)
        mediacommunity: Unset | VideosForXMLItemMediacommunity
        if isinstance(_mediacommunity, Unset):
            mediacommunity = UNSET
        else:
            mediacommunity = VideosForXMLItemMediacommunity.from_dict(_mediacommunity)

        _mediaembed = d.pop("media:embed", UNSET)
        mediaembed: Unset | VideosForXMLItemMediaembed
        if isinstance(_mediaembed, Unset):
            mediaembed = UNSET
        else:
            mediaembed = VideosForXMLItemMediaembed.from_dict(_mediaembed)

        _mediaplayer = d.pop("media:player", UNSET)
        mediaplayer: Unset | VideosForXMLItemMediaplayer
        if isinstance(_mediaplayer, Unset):
            mediaplayer = UNSET
        else:
            mediaplayer = VideosForXMLItemMediaplayer.from_dict(_mediaplayer)

        _mediathumbnail = d.pop("media:thumbnail", UNSET)
        mediathumbnail: Unset | VideosForXMLItemMediathumbnail
        if isinstance(_mediathumbnail, Unset):
            mediathumbnail = UNSET
        else:
            mediathumbnail = VideosForXMLItemMediathumbnail.from_dict(_mediathumbnail)

        mediatitle = d.pop("media:title", UNSET)

        mediadescription = d.pop("media:description", UNSET)

        _mediarating = d.pop("media:rating", UNSET)
        mediarating: Unset | VideosForXMLItemMediarating
        if isinstance(_mediarating, Unset):
            mediarating = UNSET
        else:
            mediarating = VideosForXMLItemMediarating(_mediarating)

        _enclosure = d.pop("enclosure", UNSET)
        enclosure: Unset | VideosForXMLItemEnclosure
        if isinstance(_enclosure, Unset):
            enclosure = UNSET
        else:
            enclosure = VideosForXMLItemEnclosure.from_dict(_enclosure)

        mediagroup = []
        _mediagroup = d.pop("media:group", UNSET)
        for mediagroup_item_data in _mediagroup or []:

            def _parse_mediagroup_item(
                data: object,
            ) -> Union["MRSSGroupContent", "MRSSPeerLink"]:
                try:
                    if not isinstance(data, dict):
                        raise TypeError
                    mediagroup_item_type_0 = MRSSPeerLink.from_dict(data)

                    return mediagroup_item_type_0
                except:  # noqa: E722
                    pass
                if not isinstance(data, dict):
                    raise TypeError
                mediagroup_item_type_1 = MRSSGroupContent.from_dict(data)

                return mediagroup_item_type_1

            mediagroup_item = _parse_mediagroup_item(mediagroup_item_data)

            mediagroup.append(mediagroup_item)

        videos_for_xml_item = cls(
            link=link,
            guid=guid,
            pub_date=pub_date,
            description=description,
            contentencoded=contentencoded,
            dccreator=dccreator,
            mediacategory=mediacategory,
            mediacommunity=mediacommunity,
            mediaembed=mediaembed,
            mediaplayer=mediaplayer,
            mediathumbnail=mediathumbnail,
            mediatitle=mediatitle,
            mediadescription=mediadescription,
            mediarating=mediarating,
            enclosure=enclosure,
            mediagroup=mediagroup,
        )

        videos_for_xml_item.additional_properties = d
        return videos_for_xml_item

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
