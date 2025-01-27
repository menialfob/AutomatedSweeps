import json
import os
import time
import sys

import pyautogui
import requests
import vlc

# Constants
SETTINGS_FILE = "settings.json"
DEFAULT_CHANNELS = [
    "C",
    "FL",
    "FR",
    "SLA",
    "SRA",
    "TFL",
    "TFR",
    "TRL",
    "TRR",
    "SW1",
    "SW2",
]

# REW endpoints
WARNING_ENDPOINT = "http://localhost:4735/application/warnings"
ERROR_ENDPOINT = "http://localhost:4735/application/errors"
MEASUREMENT_UUID_ENDPOINT = "http://localhost:4735/measurements/selected-uuid"
MEASUREMENT_ENDPOINT = "http://localhost:4735/measurements"
VERSION_ENDPOINT = "http://localhost:4735/version"
BASE_URL_ENDPOINT = "http://localhost:4735"

# Pyautogui settings
pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.5

# Pyautogui positions
REW_NAME_OFFSET = (-560, -642)
REW_NOTES_OFFSET = (-560, -470)

# Initialize VLC instance
vlc_options = "--mmdevice-passthrough=2 --no-video"
# --force-dolby-surround=1
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
            print(
                f"Error: VLC could not play {source}. Check your audio output settings."
            )
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
        path = input(
            "Enter the path to the lossless audio files (or type 'exit' to quit): "
        )
        if path.lower() == "exit":
            print("Exiting program.")
            return None, None
        if not os.path.isdir(path):
            print("Error: Invalid directory. Please try again.")
            continue
        mlp_files = [f for f in os.listdir(path) if f.endswith(".mlp")]
        if not mlp_files:
            print("Error: No .mlp files found in the directory. Please try again.")
            continue
        print(f"Found {len(mlp_files)} .mlp files in the directory.")
        return path, mlp_files


def get_audio_channels(mlp_files):
    """Prompt user to select audio channels from available .mlp files."""
    available_channels = {os.path.splitext(f)[0] for f in mlp_files}

    # If "SWx" is found, replace it with "SW1" to "SW4"
    if "SWx" in available_channels:
        available_channels.remove("SWx")
        available_channels.update({"SW1", "SW2", "SW3", "SW4"})
    while True:
        sorted_channels = sorted(available_channels)  # Sort alphabetically
        print("Available channels:", ", ".join(sorted_channels))
        channels = input("Enter the audio channels to measure (comma-separated): ")
        selected_channels = {ch.strip().upper() for ch in channels.split(",")}
        if not selected_channels.issubset(sorted_channels):
            print("Error: Invalid channels. Please try again.")
            continue
        sorted_selected_channels = sorted(selected_channels)
        print("Selected channels:", ", ".join(sorted_selected_channels))
        return sorted_selected_channels


def get_button_position(image):
    if getattr(sys, 'frozen', False):
        image_location = os.path.join(sys._MEIPASS, image)
    else:
        image_location = image
    location = pyautogui.locateCenterOnScreen(image_location, confidence=0.9)
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
    measurement_name = (
        f"{channel}" if is_reference else f"{channel}-position{position}-iteration{iteration}"
    )
    pyautogui.typewrite(measurement_name)
    pyautogui.click(*notes_textbox_rew)

    # Pause if the channel is SW2, SW3, or SW4
    if channel in {"SW2", "SW3", "SW4"}:
        input(f"You are measuring {channel}, please plug your {channel} into SW1 and press Enter to continue...")

    pyautogui.click(*start_button_rew)
    play_sweep(os.path.join(audio_path, f"{'SWx' if channel.startswith('SW') else channel}.mlp"))
    time.sleep(15)  # Wait for measurement to complete
    
    # Clicking OK to get rid of dialog boxes
    pyautogui.press("enter")
    pyautogui.press("enter")
    pyautogui.press("enter")

def ensure_rew_api(endpoint):
    """Checks if the REW API is running by sending a request to the endpoint."""
    try:
        response = requests.get(endpoint, timeout=3)  # Timeout to prevent long waits
        if response.status_code == 200:
            return True
        else:
            return False
    except requests.exceptions.RequestException:
        return False
    
def ensure_rew_settings(base_url):
    """
    Fetches and checks endpoint responses for correctness based on predefined expected values.
    Returns a list of error descriptions if any values are incorrect.
    """
    
    ENDPOINTS = [
        "/measure/naming",
        "/measure/playback-mode"
    ]
    
    EXPECTED_VALUES = {
        "/measure/naming": {
            "namingOption": "Use as entered",
            "prefixMeasNameWithOutput": False
        },
        "/measure/playback-mode": {
            "message": "From file"
        }
    }
    
    errors = []
    
    for endpoint in ENDPOINTS:
        try:
            response = requests.get(f"{base_url}{endpoint}").json()
        except Exception as e:
            errors.append(f"Failed to fetch {endpoint}: {str(e)}")
            continue
        
        expected_values = EXPECTED_VALUES.get(endpoint, {})
        
        for key, expected_value in expected_values.items():
            if response.get(key) != expected_value:
                errors.append(f"{endpoint}: {key} should be {expected_value}, but got {response.get(key)}")
    
    return errors
    



def get_measure_problems(endpoint):
    """Fetch the latest problem from the endpoint."""
    try:
        response = requests.get(endpoint)
        response.raise_for_status()
        data = response.json()
        return (
            data if isinstance(data, list) else []
        )  # Ensure it handles empty problems
    except requests.RequestException as e:
        print(f"Error fetching problems: {e}")
        return []


def get_selected_measurement(endpoint):
    """Get the id of the selected measurement. Assumption is that selected measurement is the latest one."""
    try:
        response = requests.get(endpoint)
        response.raise_for_status()
        data = response.json()
        uuid = data["message"]
        return uuid
    except requests.RequestException as e:
        print(f"Error fetching problems: {e}")
        return {}


def delete_measurement(endpoint, uuid):
    """Get the id of the selected measurement. Assumption is that selected measurement is the latest one."""
    try:
        response = requests.delete(endpoint + "/" + uuid)
        response.raise_for_status()
        data = response.json()
        return data
    except requests.RequestException as e:
        print(f"Error fetching problems: {e}")
        return {}


def check_and_run_measure(
    channel,
    is_reference,
    iteration,
    position,
    warning_endpoint,
    error_endpoint,
    max_attempts=3,
):
    """Runs MeasureSweep() and checks for new problems, retrying up to max_attempts times."""
    initial_problems = get_measure_problems(warning_endpoint) + get_measure_problems(error_endpoint)
    initial_times = {
        problem.get("time", "") for problem in initial_problems
    }  # Track initial problem timestamps
    attempts = 0

    while attempts < max_attempts:
        measure(channel, is_reference, iteration, position)
        attempts += 1

        latest_problems = get_measure_problems(warning_endpoint) + get_measure_problems(error_endpoint)
        latest_times = {
            problem.get("time", "") for problem in latest_problems
        }  # Get latest problem timestamps

        new_problems = (
            latest_times - initial_times
        )  # Check for truly new problems based on time

        if not new_problems:
            print("No new problems detected. Sweep successful.")
            return

        print(f"New problem detected: {latest_problems[-1]['title']}")

        # Deleting bad measurement
        delete_measurement(
            MEASUREMENT_ENDPOINT,
            get_selected_measurement(MEASUREMENT_UUID_ENDPOINT),
        )

        # Update initial_times to avoid detecting the same problem in the next iteration
        initial_times.update(new_problems)

        if attempts < max_attempts:
            print(f"Retrying sweep... Attempt {attempts + 1}")
        else:
            print("Max attempts reached. Exiting with problem.")
            return


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
            selected_channels = sorted(set(settings["channels"]))

    if not audio_path or not selected_channels:
        audio_path, mlp_files = get_audio_files()
        if audio_path and mlp_files:
            selected_channels = get_audio_channels(mlp_files)
            save_choice = (
                input("Save these settings for future use? (y/n): ").strip().lower()
            )
            if save_choice in ("y", "yes"):
                save_settings(audio_path, selected_channels)

    if audio_path and selected_channels:
        print("Processing files in:", audio_path)
        print("Measuring channels:", selected_channels)

        is_reference = input(
            "Are you measuring the Main Listening Position (MLP)? (y/n): "
        ).strip().lower() in ("y", "yes")
        position_number = (
            0
            if is_reference
            else int(input("Enter the position number (starting from 0): "))
        )
        num_iterations = (
            1 if is_reference else int(input("How many measurements per position?: "))
        )

    return audio_path, selected_channels, is_reference, num_iterations, position_number


def run_measurements(channels, is_reference, num_iterations, position_number):
    """Run the measurement process for selected channels."""
    for channel in channels:
        if is_reference:
            print(f"Creating reference measurement for {channel}")
            check_and_run_measure(
                channel, is_reference, 0, 0, WARNING_ENDPOINT, ERROR_ENDPOINT
            )
        else:
            print(
                f"Measuring {channel} at position {position_number} for {num_iterations} iterations"
            )
            for i in range(1, num_iterations + 1):
                print(f"Iteration {i} of {num_iterations}")
                check_and_run_measure(
                    channel,
                    is_reference,
                    i,
                    position_number,
                    WARNING_ENDPOINT,
                    ERROR_ENDPOINT,
                )
    print(f"Completed {len(channels) * num_iterations} measurements.")


if __name__ == "__main__":
    print("Starting measurement script")
    if not ensure_rew_api(VERSION_ENDPOINT):
        print("ERROR: REW API is not running. Exiting")
    else:
        # Checking for errors in setup
        errors = ensure_rew_settings(BASE_URL_ENDPOINT)
        if errors:
            print("Errors detected in REW settings:")
            for error in errors:
                print(error)
        else:
            # Setup and run
            audio_path, selected_channels, is_reference, num_iterations, position_number = (
                setup()
            )
            if selected_channels:
                run_measurements(
                    selected_channels, is_reference, num_iterations, position_number
                )
