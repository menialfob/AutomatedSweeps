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

# Pyautogui positions
REW_NAME_OFFSET = (-560, -642)
REW_NOTES_OFFSET = (-560, -470)
