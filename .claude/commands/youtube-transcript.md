---
name: "YouTube Transcript Downloader"
description: "Download YouTube transcript and save to specified location (default: useful-resources/youtube-transcript/)"
---

# YouTube Transcript Downloader

You will help the user download a YouTube transcript using the youtube-transcript.py script.

## Prerequisites

Before using this command, ensure you have one of the following set up:

### Option 1: Using uv (Recommended)
```bash
# Install uv if not already installed
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install youtube_transcript_api
uv pip install youtube_transcript_api
```

### Option 2: Using Python Virtual Environment
```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate  # Windows

# Install dependencies
pip install youtube_transcript_api
```

Once set up, you can use the command below.

## What to do:

1. The user provides a YouTube URL via `/youtube-transcript <url> [output_dir]`
   - `<url>`: Required YouTube URL
   - `[output_dir]`: Optional output directory (defaults to `useful-resources/youtube-transcript/`)

2. Run the script:
   ```bash
   uv run --no-project python scripts/youtube-transcript.py "$URL"
   ```

3. Move the output file to the desired location:
   ```bash
   mv ./youtube-transcript/*.txt "$OUTPUT_DIR/"
   mkdir -p "$OUTPUT_DIR"
   mv ./youtube-transcript/*.txt "$OUTPUT_DIR/"
   ```

4. Report success with the file path

## Usage Examples:

- `/youtube-transcript https://www.youtube.com/watch?v=dQw4w9WgXcQ`
  - Saves to: `useful-resources/youtube-transcript/dQw4w9WgXcQ.txt`

- `/youtube-transcript https://youtu.be/dQw4w9WgXcQ my-transcripts/`
  - Saves to: `my-transcripts/dQw4w9WgXcQ.txt`

## Implementation:

Parse the arguments:
- $1 = YouTube URL (required)
- $2 = Output directory (optional, defaults to `useful-resources/youtube-transcript/`)

If URL is missing, ask the user for it.

## Important Notes

- **Dependency Check**: Before running, confirm the user has `youtube_transcript_api` installed (either via uv or venv).
- **Execution**: The command runs `uv run --no-project python scripts/youtube-transcript.py` by default. If the user is using venv instead, they should activate it first with `source venv/bin/activate` (macOS/Linux) or `venv\Scripts\activate` (Windows), then run `python scripts/youtube-transcript.py` without the uv prefix.
- **Output Directory**: The default output is `useful-resources/youtube-transcript/`. The directory is created automatically if it doesn't exist.
