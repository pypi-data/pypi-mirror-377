# DaVinci Remote Video Player

A simple Python CLI tool for playing video files on remote HPC clusters via SSH.

## Problem

Users working on HPC clusters need to preview video files but lack GUI access to run video players directly.

## Solution

This tool uses OpenCV to display video files in a new window, with optional playback speed control.

## Usage

```bash
# Play a video file
dvplayer video.mp4

# Play with custom speed (0.5x to 2.0x)
dvplayer video.mp4 --speed 1.5

# Play specific formats
dvplayer movie.mkv
```

## Requirements

- Python 3.7+
- OpenCV (`opencv-python`)
- X11 forwarding enabled in SSH connection (`ssh -X` or `ssh -Y`)

## Installation

From PyPI:
```bash
pip install davinci-remote-video-player
```

From source:
```bash
pip install -e .
```

## Development

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

## Supported Formats

MP4, MKV, AVI - any video format supported by OpenCV.