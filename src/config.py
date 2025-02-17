from collections import defaultdict

# Constants
SETTINGS_FILE = "settings.json"

PAIR_CHANNEL_NAMES = {
    "Back Dolby": "BDL/BDR",
    "Center": "C",
    "Center Height": "CH",
    "Front Dolby": "FDL/FDR",
    "Front Height": "FHL/FHR",
    "Front": "FL/FR",
    "Front Wide": "FWL/FWR",
    "Rear Height": "RHL/RHR",
    "Surround Back (single)": "SB",
    "Surround Back": "SBL/SBR",
    "Surround Dolby": "SDL/SDR",
    "Surround Height": "SHL/SHR",
    "Surround": "SLA/SRA",
    "Top Front": "TFL/TFR",
    "Top Middle": "TML/TMR",
    "Top Rear": "TRL/TRR",
    "Top Surround": "TS",
    "Subwoofer 1": "SW1",
    "Subwoofer 2": "SW2",
    "Subwoofer 3": "SW3",
    "Subwoofer 4": "SW4",
}

ALL_CHANNEL_NAMES = {
    "BDL": "Back Dolby Left",
    "BDR": "Back Dolby Right",
    "C": "Center",
    "CH": "Center Height (Auro-3D)",
    "FDL": "Front Dolby Left",
    "FDR": "Front Dolby Right",
    "FHL": "Front Height Left",
    "FHR": "Front Height Right",
    "FL": "Front Left",
    "FR": "Front Right",
    "FWL": "Front Wide Left",
    "FWR": "Front Wide Right",
    "RHL": "Rear Height Left",
    "RHR": "Rear Height Right",
    "SB": "Surround Back (single)",
    "SBL": "Surround Back Left",
    "SBR": "Surround Back Right",
    "SDL": "Surround Dolby Left",
    "SDR": "Surround Dolby Right",
    "SHL": "Surround Height Left",
    "SHR": "Surround Height Right",
    "SLA": "Surround Left",
    "SRA": "Surround Right",
    "TFL": "Top Front Left",
    "TFR": "Top Front Right",
    "TML": "Top Middle Left",
    "TMR": "Top Middle Right",
    "TRL": "Top Rear Left",
    "TRR": "Top Rear Right",
    "TS": "Top Surround (Auro-3D)",
    "SW1": "Subwoofer 1",
    "SW2": "Subwoofer 2",
    "SW3": "Subwoofer 3",
    "SW4": "Subwoofer 4",
}


# Global variables
def default_channel_config():
    return {"audio": None, "status": None}


selected_channels = defaultdict(default_channel_config)

utility_steps: dict[str] = {
    "checkSettings": "Not started",
    "measureFR": "Not started",
    "measureFL": "Not started",
    "checkMic": "Not started",
}

# lossless_audio: bool = True

measure_mic_position: bool = True

measure_reference: bool = True

measure_iterations: int = 1

measure_position_name: str = "Reference"

# REW endpoints
WARNING_ENDPOINT = "http://localhost:4735/application/warnings"
ERROR_ENDPOINT = "http://localhost:4735/application/errors"
MEASUREMENT_UUID_ENDPOINT = "http://localhost:4735/measurements/selected-uuid"
MEASUREMENT_ENDPOINT = "http://localhost:4735/measurements"
VERSION_ENDPOINT = "http://localhost:4735/version"
BASE_URL_ENDPOINT = "http://localhost:4735"

# Pyautogui positions
REW_NAME_OFFSET = (-560, -642)
REW_NOTES_OFFSET = (-560, -470)
