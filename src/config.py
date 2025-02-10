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

ALL_CHANNELS = [
    "FL",
    "FR",
    "C",
    "SLA",
    "SRA",
    "SBL",
    "SBR",
    "SB",
    "FHL",
    "FHR",
    "FWL",
    "FWR",
    "TFL",
    "TFR",
    "TML",
    "TMR",
    "TRL",
    "TRR",
    "RHL",
    "RHR",
    "FDL",
    "FDR",
    "SDL",
    "SDR",
    "BDL",
    "BDR",
    "SHL",
    "SHR",
    "TS",
    "CH",
    "SW1",
    "SW2",
    "SW3",
    "SW4",
]

channel_mapping: dict = {}

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
