# Built-in Python libraries:
import json
import os
import sys

# Third party Libraries (pip installs):
import customtkinter as ctk # Creates GUI

# Backend Import:
if sys.platform == 'win32':
    import Windows_backend as backend
elif sys.platform == 'linux':
    import Linux_backend as backend

# Set path to save settings:
if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SAVE_PATH = os.path.join(BASE_DIR, 'settings.json')

# Functions:
def apply():
    """Applies the selected display and audio settings, saves preferences if requested, and optionally launches Steam."""
    target_display = display_dropdown.get()
    target_speaker = speaker_dropdown.get()
    current_display_label.configure(text=f'Current Display:\n{target_display}')
    current_speaker_label.configure(text=f'Current Speaker:\n{target_speaker}')

    backend.set_display(display_map[target_display])
    backend.set_speaker(speaker_map[target_speaker])
    
    # Remember choices logic:
    if remember_var.get() == 'on':
        settings = {
            'display': target_display,
            'speaker': target_speaker,
            'remember': 'on',
            'steam': steam_var.get()
        }
        with open(SAVE_PATH, 'w', encoding='utf-8') as f:
            json.dump(settings, f, indent=4)
    else:
        if os.path.exists(SAVE_PATH):
            os.remove(SAVE_PATH)

    if steam_var.get() == 'on':
        backend.launch_steam()

def revert():
    """Restores the original system display and default audio endpoint."""
    current_display_label.configure(text=f'Current Display:\n{current_display}')
    current_speaker_label.configure(text=f'Current Speaker:\n{current_speaker}')

    backend.set_display(current_display_raw)
    backend.set_speaker(current_speaker_raw)

# Create hardware lists:
monitors = backend.get_displays() 

# Build display options and mappings:
monitor_options = []
display_map = {}
current_display = 'Unknown'
current_display_raw = 'Unknown'

for index, m in enumerate(monitors, start=1):
    display_name = backend.get_display_name(m, index)

    display_entry = f'{display_name} [Display {index}] ({m.width}x{m.height})'
    monitor_options.append(display_entry)
    display_map[display_entry] = m.name

    if m.is_primary:
        current_display = display_entry
        current_display_raw = m.name

# Get audio devices:
speaker_options, speaker_map, current_speaker, current_speaker_raw = backend.get_audio_devices()

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
        with open(SAVE_PATH, 'r', encoding='utf-8') as f:
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