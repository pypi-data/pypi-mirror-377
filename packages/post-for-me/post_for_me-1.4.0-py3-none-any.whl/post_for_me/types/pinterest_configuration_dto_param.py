# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable, Optional
from typing_extensions import Required, TypedDict

from .._types import SequenceNotStr

__all__ = ["PinterestConfigurationDtoParam", "Media"]


class Media(TypedDict, total=False):
    url: Required[str]
    """Public URL of the media"""

    thumbnail_timestamp_ms: Optional[object]
    """Timestamp in milliseconds of frame to use as thumbnail for the media"""

    thumbnail_url: Optional[object]
    """Public URL of the thumbnail for the media"""


class PinterestConfigurationDtoParam(TypedDict, total=False):
    board_ids: Optional[SequenceNotStr[str]]
    """Pinterest board IDs"""

    caption: Optional[object]
    """Overrides the `caption` from the post"""

    link: Optional[str]
    """Pinterest post link"""

    media: Optional[Iterable[Media]]
    """Overrides the `media` from the post"""
