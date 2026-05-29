# Libraries:
from screeninfo import get_monitors 
from pycaw.pycaw import AudioUtilities
from comtypes import CLSCTX_ALL
import customtkinter as ctk
import wmi
import subprocess
import time

# Functions:
def apply():
    target_display = display_dropdown.get()
    target_speaker = speaker_dropdown.get()
    current_display_label.configure(text=f'Current Display:\n{target_display}')
    current_speaker_label.configure(text=f'Current Speaker:\n{target_speaker}')
    if steam_var.get() == 'on':
        subprocess.run(['cmd', '/c', 'start', 'steam://open/bigpicture'])

def revert():
    current_display_label.configure(text=f'Current Display:\n{current_display}')
    current_speaker_label.configure(text=f'Current Speaker:\n{current_speaker}')

# Create hardware lists:
system_wmi = wmi.WMI(namespace='root\\WMI') # Connects to Windows monitor hardware database
wmi_monitorlist = system_wmi.WmiMonitorID()
monitors = get_monitors()
monitor_options = []

hardware_names = []
for w in wmi_monitorlist:
    # Convert the names WMI shows as numbers to text:
    clean_name = ''.join([chr(c) for c in w.UserFriendlyName if c != 0])
    hardware_names.append(clean_name)

# Create dropdown lists:
current_display = 'Placeholder'
for i, m in enumerate(monitors): # Adds each display info to the list
    try:
        display_name = hardware_names[i] # Gets name assigned by Windows 
    except IndexError:
        display_name = f'Display {i+1}'

    display_entry = f'{display_name} ({m.width}x{m.height})'
    monitor_options.append(display_entry)
    # Check for primary:
    if i == 0 or m.is_primary:
        current_display = display_entry

devices = AudioUtilities.GetDeviceEnumerator() # Tool to list audio devices
enumerator = AudioUtilities.GetDeviceEnumerator()
devices = enumerator.EnumAudioEndpoints(0, 1) # First number is output/input, second is state

speaker_options= []
for i in range(devices.GetCount()):
    device = devices.Item(i)
    friendly_name = AudioUtilities.CreateDevice(device).FriendlyName
    speaker_options.append(friendly_name)
# Check for primary:
default_speaker = enumerator.GetDefaultAudioEndpoint(0,1)
current_speaker = AudioUtilities.CreateDevice(default_speaker).FriendlyName

# System skin:
ctk.set_appearance_mode('dark')
ctk.set_default_color_theme('blue')

# Main window:
app = ctk.CTk()
app.geometry('700x450')
app.title('Gaming Mode')
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

# Start:
app.mainloop()