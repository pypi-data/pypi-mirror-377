# Remote Video Player

A simple Python CLI tool for playing video files on remote HPC clusters via SSH.

## Problem

Users working on HPC clusters need to preview video files but lack GUI access to run video players directly.

## Solution

This tool uses OpenCV to display video files in a new window, with optional playback speed control, pause and backward/forward skip buttons.

## Installation

From PyPI:
```bash
pip install remote-video-player
```
Requires: X11 forwarding enabled in SSH connection (`ssh -X` or `ssh -Y`)

## Usage

```bash
# Play a video file
dvplayer video.mp4

# Play with custom speed (0.5x to 2.0x)
dvplayer video.mp4 --speed 1.5

# Play specific formats
dvplayer movie.mkv
```
## Supported Formats

MP4, MKV, AVI - any video format supported by OpenCV.

## Development

### Requirements

- Python 3.7+
- OpenCV (`opencv-python`)

### Building the Package

To build the distribution packages:

```bash
# Install build tools
pip install build twine

# Build the package
python -m build
```

This creates distribution files in the `dist/` directory:
- `.whl` file (wheel distribution)
- `.tar.gz` file (source distribution)

### Publishing to PyPI

```bash
# Upload to PyPI (requires account and API token)
twine upload dist/*

# Upload to test PyPI first (recommended)
twine upload --repository testpypi dist/*
```

