import pyautogui
import time

def get_button_position(image):
    location = pyautogui.locateCenterOnScreen(image, confidence=0.9)
    print(image, location)
    return location

def get_relative_position(reference, offset):
    position = reference[0] + offset[0], reference[1] + offset[1]
    return position

# location = get_button_position("MeasureButton.png")
location_measure = get_button_position("MeasureButton.png")
# pyautogui.click(*location_measure)
location_start = get_button_position("StartButton.png")
REW_NAME_OFFSET = -560, -642
REW_NOTES_OFFSET = -560, -470
location_name = get_relative_position(location_start, REW_NAME_OFFSET)

location_notes = get_relative_position(location_start, REW_NOTES_OFFSET)

pyautogui.moveTo(location_name, duration=1.0)
time.sleep(5)
pyautogui.moveTo(location_notes, duration=1.0)