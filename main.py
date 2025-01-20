import time

import pyautogui
import os
import json

# You have the create a VLC playlist and set the settings to the following:
# Open tools -> settings. Select "show advanced". Go to playlist.
# Under general playlist behavor: Only enable "start paused"

pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.5

# The channels you want to measure. The order needs to match the VLC playlist
channels = ["C", "FL", "FR", "SLA", "SRA", "TFL", "TFR", "TRL", "TRR", "SW1", "SW2"]


# Set to true for when you want to measure the MLP
createReference = False

# Number of measurements in each position
numIterations = 2

# Position which you are measuring
positionNumber = 0


# Pyautogui positions
# We assume that VLC playlist is smallest size and in top right corner
# We assume that REW window is in top left corner
measureButtonREW = 37, 57
nameTextboxREW = 275, 106
notesTextboxREW = 140, 279
startButtonREW = 754, 747
playButtonVLC = 1451, 371
backButtonVLC = 1492, 367

def measure(channel, reference, iteration, position):
    pyautogui.click(measureButtonREW[0], measureButtonREW[1], 2)
    # Click text box 2 times to select existing
    pyautogui.click(nameTextboxREW[0], nameTextboxREW[1], 2)
    if reference is True:
        pyautogui.typewrite(f"{channel}")
    else:
        pyautogui.typewrite(f"{channel}p{position}i{iteration}")
    # Click in notes box to make it commit the name change
    pyautogui.click(notesTextboxREW[0], notesTextboxREW[1])
    pyautogui.click(startButtonREW[0], startButtonREW[1])
    pyautogui.click(playButtonVLC[0], playButtonVLC[1])
    time.sleep(15)
    return

SETTINGS_FILE = "settings.json"
audio_path = None
selected_channels = None

def save_settings(path, channels):
    """Save user settings to a JSON file."""
    settings = {"audio_path": path, "channels": list(channels)}
    with open(SETTINGS_FILE, "w") as f:
        json.dump(settings, f)
    print("Settings saved successfully.")

def load_settings():
    """Load settings from a JSON file if available and valid."""
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            print("Warning: Settings file is corrupted. Ignoring it.")
    return None

def get_audio_files():
    """Prompt the user for an audio file path and validate the existence of .mlp files."""
    while True:
        path = input("Enter the path to the lossless audio files (or type 'exit' to quit): ")
        
        if path.lower() == 'exit':
            print("Exiting program.")
            return None, None
        
        if not os.path.isdir(path):
            print("Error: The provided path is not a valid directory. Please try again.")
            continue
        
        mlp_files = [f for f in os.listdir(path) if f.endswith('.mlp')]
        
        if not mlp_files:
            print("Error: No .mlp files found in the directory. Please try again.")
            continue
        
        print(f"Found {len(mlp_files)} .mlp files in the directory.")
        return path, mlp_files

def get_audio_channels(mlp_files):
    """Prompt the user to select audio channels based on available .mlp files."""
    available_channels = {os.path.splitext(f)[0] for f in mlp_files}
    
    while True:
        print("Available channels:", ", ".join(available_channels))
        channels = input("Enter the audio channels you want to measure (comma-separated): ")
        selected_channels = {ch.strip().upper() for ch in channels.split(',')}
        
        if not selected_channels.issubset(available_channels):
            print("Error: One or more entered channels are invalid. Please try again.")
            continue
        
        print("Selected channels:", ", ".join(selected_channels))
        return selected_channels

def setup ():
    settings = load_settings()
    # audio_path = None
    # selected_channels = None
    
    if settings:
        use_saved = input("Saved settings found. Do you want to load them? (y/n): ").strip().lower()
        if use_saved in ("y", "yes"):
            print("Loaded saved settings.")
            audio_path = settings["audio_path"]
            selected_channels = set(settings["channels"])
    
    if not audio_path or not selected_channels:
        audio_path, mlp_files = get_audio_files()
        if audio_path and mlp_files:
            selected_channels = get_audio_channels(mlp_files)
            save_choice = input("Do you want to save these settings for future use? (y/n): ").strip().lower()
            if save_choice in ("y", "yes"):
                save_settings(audio_path, selected_channels)
    
    print("Processing files in:", audio_path)
    print("Measuring channels:", selected_channels)





def run (channels, createReference, numIterations, positionNumber, backButtonVLC):
    # for channel in channels:
    for channel in channels:
        if createReference is True:
            print("Creating reference measurements")
            measure(channel, createReference, 0, 0)
        else:
            print(
                f"Creating {numIterations} iterations for channel {channel} at position {positionNumber}"
            )
            for i in range(1, numIterations + 1):
                print(f"Iteration {i} of {numIterations}")
                measure(channel, createReference, i, positionNumber)
                if i < numIterations:
                    pyautogui.click(backButtonVLC[0], backButtonVLC[1])
    print(f"Finished with {len(channels) + numIterations} measurements")

setup()
run(selected_channels, createReference, numIterations, positionNumber, backButtonVLC)
