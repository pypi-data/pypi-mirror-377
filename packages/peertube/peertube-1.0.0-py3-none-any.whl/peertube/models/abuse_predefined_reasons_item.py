from enum import Enum


class AbusePredefinedReasonsItem(str, Enum):
    """Predefined abuse reason categories."""

    CAPTIONS = "captions"
    HATEFULORABUSIVE = "hatefulOrAbusive"
    PRIVACY = "privacy"
    RIGHTS = "rights"
    SERVERRULES = "serverRules"
    SPAMORMISLEADING = "spamOrMisleading"
    THUMBNAILS = "thumbnails"
    VIOLENTORABUSIVE = "violentOrAbusive"

    def __str__(self) -> str:
        return str(self.value)
