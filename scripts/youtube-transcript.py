#!/usr/bin/env python3
"""
Download YouTube transcript and save to ./youtube-transcript directory
Usage: python youtube-transcript.py <youtube_url>
"""

import sys
import os
from pathlib import Path
from urllib.parse import urlparse, parse_qs
from youtube_transcript_api import (
    YouTubeTranscriptApi,
    NoTranscriptFound,
    TranscriptsDisabled,
    VideoUnavailable,
    CouldNotRetrieveTranscript,
)
from typing import Iterable

def extract_video_id(url: str) -> str:
    """Extract video ID from various YouTube URL formats"""
    parsed = urlparse(url)

    # youtu.be/VIDEO_ID
    if parsed.netloc == 'youtu.be':
        return parsed.path[1:]

    # youtube.com/watch?v=VIDEO_ID
    if parsed.netloc in ['youtube.com', 'www.youtube.com']:
        return parse_qs(parsed.query).get('v', [None])[0]

    # Direct video ID
    if len(url) == 11 and url.replace('-', '').replace('_', '').isalnum():
        return url

    raise ValueError(f"Invalid YouTube URL: {url}")

def get_transcript(video_id: str, languages: Iterable[str] | None = None) -> list[dict]:
    """Fetch transcript from YouTube using latest API (1.x)"""
    languages = languages or ("en", "en-US", "en-GB")
    api = YouTubeTranscriptApi()
    try:
        transcript = api.fetch(video_id, languages=languages)
        return transcript.to_raw_data()
    except (NoTranscriptFound, TranscriptsDisabled) as e:
        print(f"No transcript available: {e}")
        sys.exit(2)
    except VideoUnavailable as e:
        print(f"Video unavailable: {e}")
        sys.exit(3)
    except CouldNotRetrieveTranscript as e:
        print(f"Could not retrieve transcript: {e}")
        sys.exit(4)
    except Exception as e:
        print(f"Unexpected error fetching transcript: {e}")
        sys.exit(1)

def format_transcript(transcript: list[dict]) -> str:
    """Format transcript into readable text"""
    lines = []
    for entry in transcript:
        lines.append(entry['text'])
    return ' '.join(lines)

def main():
    if len(sys.argv) < 2:
        print("Usage: python youtube-transcript.py <youtube_url>")
        print("Example: python youtube-transcript.py https://www.youtube.com/watch?v=dQw4w9WgXcQ")
        sys.exit(1)

    url = sys.argv[1]

    # Extract video ID
    try:
        video_id = extract_video_id(url)
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)

    # Create output directory
    output_dir = Path('./youtube-transcript')
    output_dir.mkdir(exist_ok=True)

    # Fetch transcript
    print(f"Fetching transcript for video: {video_id}")
    transcript = get_transcript(video_id)

    # Format and save
    formatted = format_transcript(transcript)
    output_file = output_dir / f"{video_id}.txt"

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(formatted)

    print(f"✓ Transcript saved to {output_file}")
    print(f"  ({len(formatted)} characters)")

if __name__ == '__main__':
    main()
