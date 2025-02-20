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
    "checkMic": "Not started",
}

measurement_schedule: list[dict] = []

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

# Instructions markdown
INSTRUCTIONS = """
# AutomatedSweeps Instructions

## Overview
AutomatedSweeps is an application designed to help you configure and run measurement schedules for your audio setup. It integrates with **REW (Room EQ Wizard)** to conduct automated sweep measurements and utilizes **Atmos audio files** to ensure correct speaker output.

## System Requirements
- **Operating System**: Windows (Currently the only supported OS)
- **Required Software**:
  - **REW (Room EQ Wizard)** (Must be running with the "Measure" button visible)
  - **VLC Media Player** (Required for playing lossless Atmos audio files)
- **AVR Setup**:
  - Needs to be configured for measurement.
  - Use the `ODD.wtf` file from the **OCA A1 Neuron Folder** for setting your AVR in measurement mode.

## Getting Started
### 1. Initial Setup
Before starting any measurements, configure your setup:
- Open **Settings** in AutomatedSweeps.
- Select the channels you want to measure.
- Configure channel remapping if necessary (typically used for **LFE channel measurements** via AVR pre-outs).
- Save your setup for future use.

### 2. Measurement Schedule
- Define your **measurement schedule**.
- Choose the number of iterations to run the schedule multiple times.
- Assign a **position name** (e.g., "Couch Left" or "Position 2") to organize your measurements.
- Toggle the **Reference Position** switch for your main listening position (**mandatory** for the OCA A1 EVO Neuron script).

### 3. Running the Measurement
- Ensure REW API is running and "Measure" button is visible on the **main screen**.
- Start the measurement schedule.
- **Do not move your mouse or interact with the system** unless pausing or stopping the process.

## Tools
### 1. Check REW Settings (Mandatory)
- This tool runs automatically to verify REW settings before starting measurements.

### 2. Center Microphone Position (Optional)
- This tool measures **Front Left (FL) and Front Right (FR)** speakers and suggests microphone adjustments for centering.

## Important Notes
- **Lossless Audio**: The application only supports **lossless** Atmos audio files.
- **AVR Configuration**: Ensure proper setup using `ODD.wtf` from the **OCA library**.
- **Reference Position**: At least one measurement at this position is required for the **OCA A1 EVO Neuron script** to function.

## Troubleshooting
- **Audio not playing?** Ensure VLC is installed and selected as the default media player.
- **Measurement not starting?** Confirm REW is running and the "Measure" button is visible.
- **Incorrect microphone placement?** Use the **Center Microphone Position** tool to assist with alignment.
"""
