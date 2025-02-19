import time
from utils import get_correct_path, check_control_events
import config
from threading import Event

import pyautogui

from audio import play_sweep

pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.5


def get_button_position(
    image_name, message_ui, pause_event: Event, stop_event: Event
) -> tuple:
    """Get the position of a button on screen using Pyautogui."""
    image_path = get_correct_path(image_name, "assets")

    while True:
        if check_control_events(pause_event, stop_event, message_ui):
            break
        try:
            # Locate the image on screen
            location = pyautogui.locateCenterOnScreen(image_path, confidence=0.9)
            return location
        except pyautogui.ImageNotFoundException:
            message_ui.input(
                f"Could not find {image_name} on screen. Please move the window to the correct position and press OK."
            )
            pause_event.wait()


def get_relative_position(reference, offset):
    return reference[0] + offset[0], reference[1] + offset[1]


def run_sweep(
    channel,
    iteration,
    position,
    audio_file,
    message_ui,
    pause_event: Event,
    stop_event: Event,
):
    """Automate measurement process using Pyautogui."""

    # Check for control events and return if stop_event is set.
    if check_control_events(pause_event, stop_event, message_ui):
        return

    # Get positions
    measure_button_rew = get_button_position(
        "MeasureButton.png", message_ui, pause_event, stop_event
    )
    # Check for control events and return if stop_event is set.
    if check_control_events(pause_event, stop_event, message_ui):
        return

    pyautogui.click(*measure_button_rew, clicks=2)

    start_button_rew = get_button_position(
        "StartButton.png", message_ui, pause_event, stop_event
    )

    # Check for control events and return if stop_event is set.
    if check_control_events(pause_event, stop_event, message_ui):
        return

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
        # Use message_ui to inform the user to switch cables
        message_ui.info(
            f"Please plug your {channel} into SW1 and press Enter to continue..."
        )
        # Pause until the user is ready to measure
        pause_event.clear()
        pause_event.wait()

    # Check for control events and return if stop_event is set.
    if check_control_events(pause_event, stop_event, message_ui):
        return

    pyautogui.click(*start_button_rew)
    play_sweep(f"{'SWx' if audio_file.startswith('SW') else audio_file}")
    time.sleep(2)  # Wait for measurement to complete

    # Check for control events and return if stop_event is set.
    if check_control_events(pause_event, stop_event, message_ui):
        return

    # Clicking OK to get rid of dialog boxes
    pyautogui.click(*notes_textbox_rew)
    pyautogui.press("enter")
    pyautogui.press("enter")
    pyautogui.press("enter")
