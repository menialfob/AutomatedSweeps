import time
import pyautogui
import os
import json
import vlc

# Constants
SETTINGS_FILE = "settings.json"
DEFAULT_CHANNELS = ["C", "FL", "FR", "SLA", "SRA", "TFL", "TFR", "TRL", "TRR", "SW1", "SW2"]

# Pyautogui settings
pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.5

# Pyautogui positions
REW_NAME_OFFSET = (-560, -642)
REW_NOTES_OFFSET = (-560, -470)

# Initialize VLC instance
vlc_instance = vlc.Instance()
player = vlc_instance.media_player_new()

def play_sweep(source):
    """Play the audio sweep using VLC."""
    try:
        media = vlc_instance.media_new(source)
        player.set_media(media)
        player.play()
        time.sleep(2)  # Give time for VLC to initialize playback
        if player.get_state() == vlc.State.Error:
            print(f"Error: VLC could not play {source}. Check your audio output settings.")
    except Exception as e:
        print(f"VLC playback error: {e}")

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
    """Prompt user for an audio file directory and validate the existence of .mlp files."""
    while True:
        path = input("Enter the path to the lossless audio files (or type 'exit' to quit): ")
        if path.lower() == 'exit':
            print("Exiting program.")
            return None, None
        if not os.path.isdir(path):
            print("Error: Invalid directory. Please try again.")
            continue
        mlp_files = [f for f in os.listdir(path) if f.endswith('.mlp')]
        if not mlp_files:
            print("Error: No .mlp files found in the directory. Please try again.")
            continue
        print(f"Found {len(mlp_files)} .mlp files in the directory.")
        return path, mlp_files

def get_audio_channels(mlp_files):
    """Prompt user to select audio channels from available .mlp files."""
    available_channels = {os.path.splitext(f)[0] for f in mlp_files}
    while True:
        print("Available channels:", ", ".join(available_channels))
        channels = input("Enter the audio channels to measure (comma-separated): ")
        selected_channels = {ch.strip().upper() for ch in channels.split(',')}
        if not selected_channels.issubset(available_channels):
            print("Error: Invalid channels. Please try again.")
            continue
        print("Selected channels:", ", ".join(selected_channels))
        return selected_channels
    
def get_button_position(image):
    location = pyautogui.locateCenterOnScreen(image, confidence=0.9)
    return location

def get_relative_position(reference, offset):
    position = reference[0] + offset[0], reference[1] + offset[1]
    return position

def measure(channel, is_reference, iteration, position):
    """Automate measurement process using Pyautogui."""

    # Get positions
    measure_button_rew = get_button_position("MeasureButton.png")
    pyautogui.click(*measure_button_rew, clicks=2)
    
    start_button_rew = get_button_position("StartButton.png")
    name_textbox_rew = get_relative_position(start_button_rew, REW_NAME_OFFSET)
    notes_textbox_rew = get_relative_position(start_button_rew, REW_NOTES_OFFSET)

    pyautogui.click(*name_textbox_rew, clicks=2)
    measurement_name = f"{channel}" if is_reference else f"{channel}p{position}i{iteration}"
    pyautogui.typewrite(measurement_name)
    pyautogui.click(*notes_textbox_rew)
    pyautogui.click(*start_button_rew)
    play_sweep(os.path.join(audio_path, f"{channel}.mlp"))
    time.sleep(15)  # Wait for measurement to complete

def setup():
    """Handle setup process for loading settings and selecting audio files."""
    settings = load_settings()
    audio_path = None
    selected_channels = None
    
    if settings:
        use_saved = input("Saved settings found. Load them? (y/n): ").strip().lower()
        if use_saved in ("y", "yes"):
            print("Loaded saved settings.")
            audio_path = settings["audio_path"]
            selected_channels = set(settings["channels"])
    
    if not audio_path or not selected_channels:
        audio_path, mlp_files = get_audio_files()
        if audio_path and mlp_files:
            selected_channels = get_audio_channels(mlp_files)
            save_choice = input("Save these settings for future use? (y/n): ").strip().lower()
            if save_choice in ("y", "yes"):
                save_settings(audio_path, selected_channels)

    if audio_path and selected_channels:
        print("Processing files in:", audio_path)
        print("Measuring channels:", selected_channels)
        
        is_reference = input("Are you measuring the Main Listening Position (MLP)? (y/n): ").strip().lower() in ("y", "yes")
        position_number = 0 if is_reference else int(input("Enter the position number (starting from 0): "))
        num_iterations = 1 if is_reference else int(input("How many measurements per position?: "))
        
    return audio_path, selected_channels, is_reference, num_iterations, position_number

def run_measurements(channels, is_reference, num_iterations, position_number):
    """Run the measurement process for selected channels."""
    for channel in channels:
        if is_reference:
            print(f"Creating reference measurement for {channel}")
            measure(channel, is_reference, 0, 0)
        else:
            print(f"Measuring {channel} at position {position_number} for {num_iterations} iterations")
            for i in range(1, num_iterations + 1):
                print(f"Iteration {i} of {num_iterations}")
                measure(channel, is_reference, i, position_number)
                # if i < num_iterations:
                #     pyautogui.click(*BACK_BUTTON_VLC)
    print(f"Completed {len(channels) * num_iterations} measurements.")

if __name__ == "__main__":
    # Setup and run
    audio_path, selected_channels, is_reference, num_iterations, position_number = setup()
    if selected_channels:
        run_measurements(selected_channels, is_reference, num_iterations, position_number)
