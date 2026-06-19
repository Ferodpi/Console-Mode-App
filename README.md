## CONSOLE MODE APP

![Console Mode Screenshot](Screenshots/Screenshot_1.png)

A lightweight Windows utility that instantly switches your primary monitor, changes the default audio device, and optionally launches Steam Big Picture. Designed to make the transition from a desktop setup to couch gaming effortless.

## Requirements

Supported operating systems:
- Windows 10
- Windows 11

### Prebuilt release:

This application relies on NirSoft's utilities to modify display and audio settings.
- MultiMonitorTool: Handles display profile switching. [Download from NirSoft](https://www.nirsoft.net/utils/multi_monitor_tool.html).
- SoundVolumeView: Manages audio device routing. [Download from NirSoft](https://www.nirsoft.net/utils/sound_volume_view.html).

⚠️ **Both executables must be placed in the same folder as 'Console Mode.exe'**

### If running from source:  
- Python 3.13 (or newer)
- customtkinter
- screeninfo
- pycaw
- comtypes
- wmi

## Usage
- Launch the app and select your target gaming display and audio output.
- Toggle whether to remember your choices or auto-launch Steam.
- Click 'Apply' to switch hardware, then 'Revert' to restore your previous desktop setup.

## Features

- Automatically detects connected monitors.
- Automatically detects playback devices.
- Switches the primary display.
- Changes the default audio device.
- Saves user preferences.
- Optionally launches Steam Big Picture.
- Restores the previous display and audio configuration with a single click.
