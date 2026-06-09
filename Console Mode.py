# Built-in Python libraries:
import subprocess
import ctypes
import json
import os
import sys

#Third party Libraries (pip installs):
import wmi
import customtkinter as ctk
from screeninfo import get_monitors 
from pycaw.pycaw import AudioUtilities

# Set path to save settings:
if getattr(sys,'frozen', False):
    # Runs only if compiled as an .exe file
    BASE_DIR = os.path.dirname(sys.executable)
else:
    # Runs only as .py code
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SAVE_PATH = os.path.join(BASE_DIR, 'settings.json')
MULTIMONITOR_PATH = os.path.join(BASE_DIR, 'MultiMonitorTool.exe')
SOUNDVOLUMEVIEW_PATH = os.path.join(BASE_DIR, 'SoundVolumeView.exe')

class DISPLAY_DEVICE(ctypes.Structure):
    _fields_ = [
        ('cb', ctypes.c_uint32),
        ('DeviceName', ctypes.c_wchar*32),
        ('DeviceString', ctypes.c_wchar*128),
        ('StateFlags', ctypes.c_uint32),
        ('DeviceID', ctypes.c_wchar*128),
        ('DeviceKey', ctypes.c_wchar*128)
    ]
# Functions:
def apply():
    """Applies target display and audio settings using MultiMonitorTool and SoundVolumeView, saves preferences in a json file, and launches Steam."""
    target_display = display_dropdown.get()
    target_speaker = speaker_dropdown.get()
    current_display_label.configure(text=f'Current Display:\n{target_display}')
    current_speaker_label.configure(text=f'Current Speaker:\n{target_speaker}')

    if os.path.exists(MULTIMONITOR_PATH):
        raw_display = display_map[target_display]
        subprocess.run([MULTIMONITOR_PATH, '/SetPrimary', raw_display])
    if os.path.exists(SOUNDVOLUMEVIEW_PATH):
        raw_speaker = speaker_map[target_speaker]
        subprocess.run([SOUNDVOLUMEVIEW_PATH, '/SetDefault', raw_speaker, 'all'])
    
    # Remember choices logic:
    if remember_var.get() == 'on':
        settings = {
            'display': target_display,
            'speaker': target_speaker,
            'remember': 'on',
            'steam': steam_var.get()
        }
        with open(SAVE_PATH, 'w') as f:
            json.dump(settings, f)
    else:
        if os.path.exists(SAVE_PATH):
            os.remove(SAVE_PATH)

    if steam_var.get() == 'on':
        subprocess.run(['cmd', '/c', 'start', 'steam://open/bigpicture'])

def revert():
    """Restores the original system display and default audio endpoint, effectively reverting the changes made in the current session"""
    current_display_label.configure(text=f'Current Display:\n{current_display}')
    current_speaker_label.configure(text=f'Current Speaker:\n{current_speaker}')

    if os.path.exists(MULTIMONITOR_PATH):
        subprocess.run([MULTIMONITOR_PATH, '/SetPrimary', current_display_raw])
    if os.path.exists(SOUNDVOLUMEVIEW_PATH):
        subprocess.run([SOUNDVOLUMEVIEW_PATH, '/SetDefault', current_speaker_raw, 'all'])

# Create hardware lists:
system_wmi = wmi.WMI(namespace='root\\WMI') # Connects to Windows monitor hardware database
monitors = get_monitors()

# Grab the user friendly names and their HID from WMI:
wmi_names = {}
for w in system_wmi.WmiMonitorID():
    clean_name = ''.join([chr(c) for c in w.UserFriendlyName if c != 0])
    pnp_id = w.InstanceName.split('\\')[1] # Extracts the unique hardware ID
    wmi_names[pnp_id] = clean_name

monitor_options = []
display_map = {}
current_display = 'Placeholder'
current_display_raw = 'Placeholder'

for index, m in enumerate(monitors, start=1):
    device = DISPLAY_DEVICE()
    device.cb = ctypes.sizeof(device)
    ctypes.windll.user32.EnumDisplayDevicesW(m.name, 0, ctypes.byref(device), 0)

    try:
        pnp_id = device.DeviceID.split('\\')[1]
        display_name = wmi_names.get(pnp_id, f'Display {index}')
    except IndexError:
        display_name = f'Display {index}'

    display_entry = f'{display_name} [Display {index}] ({m.width}x{m.height})'
    monitor_options.append(display_entry)
    display_map[display_entry] = m.name

    if m.is_primary:
        current_display = display_entry
        current_display_raw = m.name

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

# System skin:
ctk.set_appearance_mode('dark')
ctk.set_default_color_theme('blue')

# Main window:
app = ctk.CTk()
app.geometry('700x450')
app.title('Console Mode')
app.resizable(False, False)

# Show current output on top:
status_frame = ctk.CTkFrame(app)
status_frame.pack(pady=20, padx=20, fill='x') # fill='x'  makes it stretch across the window

status_frame.grid_columnconfigure(0, weight=1, uniform='status_cols')
status_frame.grid_columnconfigure(1, weight=1, uniform='status_cols') # Configures grid so both sides are equal

current_display_label = ctk.CTkLabel(status_frame, text=f'Current Display:\n{current_display}', justify='center')
current_display_label.grid(row=0, column=0, padx=10, pady=10)
current_speaker_label = ctk.CTkLabel(status_frame, text=f'Current Speaker:\n{current_speaker}', justify='center')
current_speaker_label.grid(row=0, column=1, padx=10, pady=10)

# Target output selector:
target_display_label = ctk.CTkLabel(app, text= 'Select target display:')
target_display_label.pack(pady=(15, 10))
display_dropdown = ctk.CTkComboBox(app, values=monitor_options, width=300, state='readonly')
display_dropdown.pack(pady=10)
display_dropdown.set(monitor_options[0])

target_speaker_label = ctk.CTkLabel(app, text='Select target speaker:')
target_speaker_label.pack(pady=(15, 10))
speaker_dropdown = ctk.CTkComboBox(app, values=speaker_options, width=300, state='readonly')
speaker_dropdown.pack(pady=10)
speaker_dropdown.set(speaker_options[0])

# Checkboxes:
remember_var = ctk.StringVar(value='off')
steam_var = ctk.StringVar(value='off')
remember_checkbox = ctk.CTkCheckBox(app, text='Remember choices', variable=remember_var, onvalue='on', offvalue='off')
remember_checkbox.pack(pady=(15, 5))
steam_checkbox = ctk.CTkCheckBox(app, text='Open Steam Big Picture in target screen', variable=steam_var, onvalue='on', offvalue='off')
steam_checkbox.pack(pady=5)

# Buttons:
button_frame = ctk.CTkFrame(app, fg_color='transparent')
button_frame.pack(side='bottom', fill='x', padx=20, pady=20)

revert_btn = ctk.CTkButton(button_frame, text='Revert', fg_color='gray', command=revert)
revert_btn.pack(side='left')
apply_btn = ctk.CTkButton(button_frame, text='Apply', fg_color='gray', command=apply)
apply_btn.pack(side='right')

# Load saved settings:
if os.path.exists(SAVE_PATH):
    try:
        with open(SAVE_PATH, 'r') as f:
            saved = json.load(f)
        if saved.get('display') in monitor_options:
            display_dropdown.set(saved['display'])
        if saved.get('speaker') in speaker_options:
            speaker_dropdown.set(saved['speaker'])

        remember_var.set(saved.get('remember', 'off'))
        steam_var.set(saved.get('steam', 'off'))

    # Delete config file if app fails to read it:
    except Exception:
        if os.path.exists(SAVE_PATH):
            os.remove(SAVE_PATH)

# Start:
if __name__ == '__main__':
    app.mainloop()