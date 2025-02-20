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
