"""
Future Media Upload Support

TODO: Implement when upgrading to Pro/Enterprise plans
- Image upload (JPG, PNG, GIF)
- Video upload (MP4, MOV)
- Media processing and optimization
- Alt-text support for accessibility
"""

from pathlib import Path
from typing import Any, Dict, Optional


class MediaUploadError(Exception):
    """Custom exception for media upload operations"""

    pass


def upload_image(image_path: Path, alt_text: Optional[str] = None) -> str:
    """
    Upload image to X/Twitter

    Args:
        image_path: Path to image file
        alt_text: Alt text for accessibility

    Returns:
        Media ID for use in tweets

    TODO: Implement when Basic+ plan is available
    - Support JPG, PNG, GIF formats
    - Image resizing and optimization
    - Alt-text for accessibility
    - Media ID caching
    """
    raise NotImplementedError("Media upload requires Basic+ plan")


def upload_video(video_path: Path, thumbnail_path: Optional[Path] = None) -> str:
    """
    Upload video to X/Twitter

    Args:
        video_path: Path to video file
        thumbnail_path: Optional custom thumbnail

    Returns:
        Media ID for use in tweets

    TODO: Implement when Pro plan is available
    - Support MP4, MOV formats
    - Video transcoding and compression
    - Custom thumbnails
    - Progress tracking for large files
    """
    raise NotImplementedError("Video upload requires Pro plan")


def create_media_tweet(
    text: str, media_paths: list[Path], alt_texts: Optional[list[str]] = None
) -> Dict[str, Any]:
    """
    Create tweet with media attachments

    Args:
        text: Tweet text
        media_paths: List of media file paths
        alt_texts: Optional alt texts for each media

    Returns:
        Tweet data with media IDs

    TODO: Implement media tweet composition
    - Multiple media support (up to 4 images)
    - Mixed media types
    - Media validation
    - Size limit checks
    """
    raise NotImplementedError("Media tweets require Basic+ plan")
