# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from .._models import BaseModel

__all__ = ["PinterestConfigurationDto", "Media"]


class Media(BaseModel):
    url: str
    """Public URL of the media"""

    thumbnail_timestamp_ms: Optional[object] = None
    """Timestamp in milliseconds of frame to use as thumbnail for the media"""

    thumbnail_url: Optional[object] = None
    """Public URL of the thumbnail for the media"""


class PinterestConfigurationDto(BaseModel):
    board_ids: Optional[List[str]] = None
    """Pinterest board IDs"""

    caption: Optional[object] = None
    """Overrides the `caption` from the post"""

    link: Optional[str] = None
    """Pinterest post link"""

    media: Optional[List[Media]] = None
    """Overrides the `media` from the post"""
