import time
from utils import get_correct_path
import config
from threading import Event

import pyautogui

from audio import play_sweep

pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.5


def get_button_position(image_name):
    image_path = get_correct_path(image_name, "assets")

    # Locate the image on screen
    location = pyautogui.locateCenterOnScreen(image_path, confidence=0.9)
    return location


def get_relative_position(reference, offset):
    return reference[0] + offset[0], reference[1] + offset[1]


def run_sweep(channel, iteration, position, audio_file, notify_ui, pause_event: Event):
    """Automate measurement process using Pyautogui."""

    # Get positions
    measure_button_rew = get_button_position("MeasureButton.png")
    pyautogui.click(*measure_button_rew, clicks=2)

    start_button_rew = get_button_position("StartButton.png")
    name_textbox_rew = get_relative_position(start_button_rew, config.REW_NAME_OFFSET)
    notes_textbox_rew = get_relative_position(start_button_rew, config.REW_NOTES_OFFSET)

    pyautogui.click(*name_textbox_rew, clicks=2)
    measurement_name = (
        f"{channel}"
        if config.measure_reference
        else f"{channel} (Pos: {position} - Iter: {iteration})"
    )
    pyautogui.typewrite(measurement_name)
    pyautogui.click(*notes_textbox_rew)

    # Pause if the channel is SW2, SW3, or SW4
    if channel is audio_file and channel in {"SW2", "SW3", "SW4"}:
        # Use notify_ui to inform the user to switch cables
        notify_ui(
            {
                "type": "info",
                "contents": f"Please plug your {channel} into SW1 and press Enter to continue...",
            }
        )
        # Pause until the user is ready to measure
        pause_event.clear()
        pause_event.wait()

    if not pause_event.is_set():
        notify_ui.info("Paused inside sweep_and_check_problems")
        pause_event.wait()

    pyautogui.click(*start_button_rew)
    play_sweep(f"{'SWx' if audio_file.startswith('SW') else audio_file}")
    time.sleep(2)  # Wait for measurement to complete

    # Clicking OK to get rid of dialog boxes
    pyautogui.press("enter")
    pyautogui.press("enter")
    pyautogui.press("enter")
