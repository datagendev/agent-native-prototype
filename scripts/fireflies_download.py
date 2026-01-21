#!/usr/bin/env python3
"""
Download Fireflies meeting transcript and summary.

Usage:
    python scripts/fireflies_download.py <meeting_id>
    python scripts/fireflies_download.py --url <fireflies_url>

Examples:
    python scripts/fireflies_download.py 01KB8EFR4YVD6TVS4B2XZV3S5N
    python scripts/fireflies_download.py --url "https://app.fireflies.ai/view/Meeting-Name::01KB8EFR4YVD6TVS4B2XZV3S5N"

Output:
    transcript/{meeting_id}_summary.json
    transcript/{meeting_id}_transcript.json
"""

import argparse
import json
import os
import re
import sys


def extract_meeting_id(url_or_id: str) -> str:
    """Extract meeting ID from URL or return as-is if already an ID."""
    # If it's a URL, extract the ID after ::
    if "fireflies.ai" in url_or_id:
        match = re.search(r"::([A-Z0-9]+)", url_or_id)
        if match:
            return match.group(1)
        # Try to get ID from end of path
        match = re.search(r"/view/[^/]+::([A-Z0-9]+)", url_or_id)
        if match:
            return match.group(1)
        raise ValueError(f"Could not extract meeting ID from URL: {url_or_id}")
    return url_or_id


def download_meeting(meeting_id: str, output_dir: str = "transcript") -> tuple[dict, str]:
    """
    Download meeting summary and transcript from Fireflies.

    Returns:
        (result_dict, error_string) - error is empty string on success
    """
    try:
        from datagen_sdk import DatagenClient
    except ImportError:
        return {}, "datagen_sdk not installed. Run: pip install datagen-sdk"

    try:
        client = DatagenClient()

        print(f"Fetching summary for {meeting_id}...")
        summary = client.execute_tool(
            "mcp_Fireflies_fireflies_get_summary",
            {"transcriptId": meeting_id}
        )

        print(f"Fetching transcript for {meeting_id}...")
        transcript = client.execute_tool(
            "mcp_Fireflies_fireflies_get_transcript",
            {"transcriptId": meeting_id}
        )

        # Create output directory
        os.makedirs(output_dir, exist_ok=True)

        # Save summary
        summary_path = os.path.join(output_dir, f"{meeting_id}_summary.json")
        with open(summary_path, "w") as f:
            json.dump(summary, f, indent=2)
        print(f"Saved: {summary_path}")

        # Save transcript
        transcript_path = os.path.join(output_dir, f"{meeting_id}_transcript.json")
        with open(transcript_path, "w") as f:
            json.dump(transcript, f, indent=2)
        print(f"Saved: {transcript_path}")

        # Extract metadata for return
        result = {
            "meeting_id": meeting_id,
            "summary_path": summary_path,
            "transcript_path": transcript_path,
            "summary": summary,
            "transcript": transcript,
        }

        # Try to extract participant info
        if isinstance(transcript, list) and len(transcript) > 0:
            transcript_text = transcript[0] if isinstance(transcript[0], str) else str(transcript[0])

            # Extract participants
            participants_match = re.search(r"Participants: ([^\n]+)", transcript_text)
            if participants_match:
                result["participants"] = [p.strip() for p in participants_match.group(1).split(",")]

            # Extract title
            title_match = re.search(r"Title: ([^\n]+)", transcript_text)
            if title_match:
                result["title"] = title_match.group(1).strip()

            # Extract date
            date_match = re.search(r"DateString: ([^\n]+)", transcript_text)
            if date_match:
                result["date"] = date_match.group(1).strip()

            # Extract duration
            duration_match = re.search(r"Duration: ([^\n]+)", transcript_text)
            if duration_match:
                result["duration_minutes"] = float(duration_match.group(1).strip())

        return result, ""

    except Exception as e:
        return {}, f"Failed to download meeting: {e}"


def main():
    parser = argparse.ArgumentParser(
        description="Download Fireflies meeting transcript and summary",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    parser.add_argument(
        "meeting_id",
        nargs="?",
        help="Meeting ID (e.g., 01KB8EFR4YVD6TVS4B2XZV3S5N)"
    )
    parser.add_argument(
        "--url",
        help="Fireflies meeting URL to extract ID from"
    )
    parser.add_argument(
        "--output-dir", "-o",
        default="transcript",
        help="Output directory (default: transcript)"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output result as JSON"
    )

    args = parser.parse_args()

    # Get meeting ID from args
    if args.url:
        meeting_id = extract_meeting_id(args.url)
    elif args.meeting_id:
        meeting_id = extract_meeting_id(args.meeting_id)
    else:
        parser.print_help()
        sys.exit(1)

    # Download
    result, err = download_meeting(meeting_id, args.output_dir)

    if err:
        print(f"Error: {err}", file=sys.stderr)
        sys.exit(1)

    if args.json:
        # Output minimal JSON (without full content)
        output = {
            "meeting_id": result["meeting_id"],
            "title": result.get("title", "Unknown"),
            "date": result.get("date", "Unknown"),
            "duration_minutes": result.get("duration_minutes", 0),
            "participants": result.get("participants", []),
            "summary_path": result["summary_path"],
            "transcript_path": result["transcript_path"],
        }
        print(json.dumps(output, indent=2))
    else:
        print(f"\nDownload complete!")
        print(f"  Title: {result.get('title', 'Unknown')}")
        print(f"  Date: {result.get('date', 'Unknown')}")
        print(f"  Duration: {result.get('duration_minutes', 0):.1f} minutes")
        print(f"  Participants: {', '.join(result.get('participants', []))}")


if __name__ == "__main__":
    main()
