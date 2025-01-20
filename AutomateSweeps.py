import pyautogui
import time

# You have the create a VLC playlist and set the settings to the following:
# Open tools -> settings. Select "show advanced". Go to playlist. 
# Under general playlist behavor: Only enable "start paused"

pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.5

# The channels you want to measure. The order needs to match the VLC playlist
channels = ["C","FL","FR","SLA","SRA","TFL","TFR","TRL","TRR","SW1","SW2"]


# Set to true for when you want to measure the MLP
createReference = False

# Number of measurements in each position
numIterations = 2

# Position which you are measuring
positionNumber = 0


# Pyautogui positions
# We assume that VLC playlist is smallest size and in top right corner
# We assume that REW window is in top left corner
measureButtonREW = 37, 57
nameTextboxREW = 275, 106
notesTextboxREW = 140, 279
startButtonREW = 754, 747
playButtonVLC = 1451, 371
backButtonVLC = 1492, 367

def measure(channel, reference, iteration, position):
    pyautogui.click(measureButtonREW[0],measureButtonREW[1],2)
    # Click text box 2 times to select existing
    pyautogui.click(nameTextboxREW[0],nameTextboxREW[1],2)
    if reference == True:
        pyautogui.typewrite(f'{channel}')
    else:
        pyautogui.typewrite(f'{channel}p{position}i{iteration}')
    # Click in notes box to make it commit the name change
    pyautogui.click(notesTextboxREW[0],notesTextboxREW[1])
    pyautogui.click(startButtonREW[0],startButtonREW[1])
    pyautogui.click(playButtonVLC[0],playButtonVLC[1])
    time.sleep(15)
    return

# for channel in channels:
for channel in channels:
    if createReference == True:
        print("Creating reference measurements")
        measure(channel, createReference, 0, 0)
    else:
        print(f'Creating {numIterations} iterations for channel {channel} at position {positionNumber}')
        for i in range(1, numIterations + 1):
            print(f'Iteration {i} of {numIterations}')
            measure(channel, createReference, i, positionNumber)
            if i < numIterations:
                pyautogui.click(backButtonVLC[0],backButtonVLC[1])
print(f'Finished with {len(channels)+numIterations} measurements')