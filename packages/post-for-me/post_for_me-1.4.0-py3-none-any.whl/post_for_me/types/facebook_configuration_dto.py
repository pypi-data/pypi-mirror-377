# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from typing_extensions import Literal

from .._models import BaseModel

__all__ = ["FacebookConfigurationDto", "Media"]


class Media(BaseModel):
    url: str
    """Public URL of the media"""

    thumbnail_timestamp_ms: Optional[object] = None
    """Timestamp in milliseconds of frame to use as thumbnail for the media"""

    thumbnail_url: Optional[object] = None
    """Public URL of the thumbnail for the media"""


class FacebookConfigurationDto(BaseModel):
    caption: Optional[object] = None
    """Overrides the `caption` from the post"""

    media: Optional[List[Media]] = None
    """Overrides the `media` from the post"""

    placement: Optional[Literal["reels", "stories", "timeline"]] = None
    """Facebook post placement"""
