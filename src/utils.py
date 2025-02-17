import json
import os
import socket
from rew_api import get_measurement_summary
import sys

from config import SETTINGS_FILE


def save_settings(settings):
    """Save user settings to a JSON file."""
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


def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(0)
    try:
        # doesn't even have to be reachable
        s.connect(("10.254.254.254", 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = "127.0.0.1"
    finally:
        s.close()
    return IP


local_ip = get_ip()


def get_microphone_distance(
    fr_uuid: str,
    fl_uuid: str,
) -> int:
    """Get the distance in cm needed to move the microphone to align the IR peaks of the FR and FL measurements.
    A negative number means it needs to move to the right speaker, and a positive number means it needs to move to the left speaker."""
    # Get the time of the IR peak for the FR measurement
    fr_data = get_measurement_summary(fr_uuid)

    # Get the time of the IR peak for the FL measurement
    fl_data = get_measurement_summary(fl_uuid)

    # Get the delta time of the IR peak for the FR and FL measurements
    delta_time = fl_data["timeOfIRPeakSeconds"] - fr_data["timeOfIRPeakSeconds"]

    # Get the distance needed to move the microphone to align the IR peaks
    speed_of_sound = 343  # m/s
    distance_meters = delta_time * speed_of_sound

    # Convert the distance to cm
    distance = int(distance_meters * 100)

    return distance


def get_correct_path(path, directory):
    """Get the correct path for the given file.
    Args:
        path (str): Path to the file.
        directory (str): Directory containing the file.

    Examples:
        get_correct_path("MeasureButton.png", "assets")
        get_correct_path("FR.mlp", "assets/Lossless")
    """
    if getattr(sys, "frozen", False):
        base_path = os.path.join(
            sys._MEIPASS, directory
        )  # When running as an executable
    else:
        base_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), f"../{directory}"
        )  # When running as a script

    return os.path.join(base_path, path)
