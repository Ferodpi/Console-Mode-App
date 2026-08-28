# Built-in Python libraries:
import ctypes
import os
import subprocess # Runs external calls (.exe)
import sys

# Third party Libraries (pip installs):
import wmi
from screeninfo import get_monitors as screeninfo_get_monitors
from pycaw.pycaw import AudioUtilities

# Set path to dependencies:
if getattr(sys,'frozen', False):
    # Runs only if compiled as an .exe file
    BASE_DIR = os.path.dirname(sys.executable)
else:
    # Runs only as .py code
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Dependencies path:
MULTIMONITOR_PATH = os.path.join(BASE_DIR, 'MultiMonitorTool.exe')
SOUNDVOLUMEVIEW_PATH = os.path.join(BASE_DIR, 'SoundVolumeView.exe')

# Windows API structures:
class DISPLAY_DEVICE(ctypes.Structure):
    _fields_ = [
        ('cb', ctypes.c_uint32),
        ('DeviceName', ctypes.c_wchar*32),
        ('DeviceString', ctypes.c_wchar*128),
        ('StateFlags', ctypes.c_uint32),
        ('DeviceID', ctypes.c_wchar*128),
        ('DeviceKey', ctypes.c_wchar*128)
    ]

# Windows WMI connection:
system_wmi = wmi.WMI(namespace='root\\WMI') # Connects to Windows monitor hardware database

# Monitor functions:
def get_wmi_names():
    wmi_names = {}
    for w in system_wmi.WmiMonitorID():
        clean_name = ''.join([chr(c) for c in w.UserFriendlyName if c != 0])
        pnp_id = w.InstanceName.split('\\')[1] # Extracts the unique hardware ID
        wmi_names[pnp_id] = clean_name
    return wmi_names

def get_displays():
    return screeninfo_get_monitors()

def get_display_device(monitor):
    device = DISPLAY_DEVICE()
    device.cb = ctypes.sizeof(device)
    ctypes.windll.user32.EnumDisplayDevicesW(
        monitor.name,
        0,
        ctypes.byref(device),
        0
    )
    return device

def get_display_name(device, wmi_names, index):
    try:
        pnp_id = device.DeviceID.split('\\')[1]
        return wmi_names.get(pnp_id, f'Display {index}')
    except IndexError:
        return f'Display {index}'
    
# Speaker functions:
def get_audio_devices():
    enumerator = AudioUtilities.GetDeviceEnumerator()
    AUDIO_RENDER = 0
    AUDIO_ACTIVE = 1
    devices = enumerator.EnumAudioEndpoints(AUDIO_RENDER, AUDIO_ACTIVE)

    speaker_options = []
    speaker_map = {} # Dictionary to map UI names to SoundVolumeView Hardware IDs
    for i in range(devices.GetCount()):
        device = devices.Item(i)
        friendly_name = AudioUtilities.CreateDevice(device).FriendlyName
        device_id = device.GetId()

        # Failsafe in case of duplicate speaker names:
        original_name = friendly_name
        counter = 1
        while friendly_name in speaker_map:
            friendly_name = f'{original_name} ({counter})'
            counter += 1

        speaker_options.append(friendly_name)
        speaker_map[friendly_name] = device_id

    # Check for primary:
    default_speaker = enumerator.GetDefaultAudioEndpoint(AUDIO_RENDER, AUDIO_ACTIVE)
    current_speaker_raw = default_speaker.GetId()
    # Reverse lookup the disctionary to get UI name:
    current_speaker = next(name for name, id in speaker_map.items() if id == current_speaker_raw)
    return speaker_options, speaker_map, current_speaker, current_speaker_raw

def set_display(display):
    if os.path.exists(MULTIMONITOR_PATH):
        subprocess.run([MULTIMONITOR_PATH, '/SetPrimary', display])

def set_speaker(speaker):
     if os.path.exists(SOUNDVOLUMEVIEW_PATH):
        subprocess.run([SOUNDVOLUMEVIEW_PATH, '/SetDefault', speaker, 'all'])

def launch_steam():
    subprocess.run(['cmd', '/c', 'start', 'steam://open/bigpicture'])