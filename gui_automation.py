import os
import sys
import time

import pyautogui

from audio import play_sweep
from config import REW_NAME_OFFSET, REW_NOTES_OFFSET

pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.5


def get_button_position(image_name):
    # Determine the correct base path
    if getattr(sys, "frozen", False):
        base_path = os.path.join(
            sys._MEIPASS, "assets"
        )  # When running as an executable
    else:
        base_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "assets"
        )  # When running as a script

    image_path = os.path.join(base_path, image_name)

    # Locate the image on screen
    location = pyautogui.locateCenterOnScreen(image_path, confidence=0.9)
    return location


def get_relative_position(reference, offset):
    return reference[0] + offset[0], reference[1] + offset[1]


def run_sweep(channel, is_reference, iteration, position, audio_path):
    """Automate measurement process using Pyautogui."""

    # Get positions
    measure_button_rew = get_button_position("MeasureButton.png")
    pyautogui.click(*measure_button_rew, clicks=2)

    start_button_rew = get_button_position("StartButton.png")
    name_textbox_rew = get_relative_position(start_button_rew, REW_NAME_OFFSET)
    notes_textbox_rew = get_relative_position(start_button_rew, REW_NOTES_OFFSET)

    pyautogui.click(*name_textbox_rew, clicks=2)
    measurement_name = (
        f"{channel}"
        if is_reference
        else f"{channel}-position{position}-iteration{iteration}"
    )
    pyautogui.typewrite(measurement_name)
    pyautogui.click(*notes_textbox_rew)

    # Pause if the channel is SW2, SW3, or SW4
    if channel in {"SW2", "SW3", "SW4"}:
        input(
            f"You are measuring {channel}, please plug your {channel} into SW1 and press Enter to continue..."
        )

    pyautogui.click(*start_button_rew)
    play_sweep(
        os.path.join(
            audio_path, f"{'SWx' if channel.startswith('SW') else channel}.mlp"
        )
    )
    time.sleep(13)  # Wait for measurement to complete

    # Clicking OK to get rid of dialog boxes
    pyautogui.press("enter")
    pyautogui.press("enter")
    pyautogui.press("enter")
