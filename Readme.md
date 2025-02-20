
![Product Name Screen Shot][application-logo]
# AutomatedSweeps

AutomatedSweeps is an automation engine and UI for measuring speaker responses in REW.

## Description

The tool is intended to be used to measure speaker responses in REW for use with OCA's A1 EVO "Nexus".

### Features

* Friendly terminal based user interface
* Configuration of any speaker setup
* Serving the application on your local network to control in a web browser (For example to measure on your computer, but controlling on your phone in another room)
* Automatic checks and retries of bad measurements
* Microphone-centering tool

### Preview
Frontpage of the application running in windows terminal

![Product Name Screen Shot][application-screenshot]

## Getting Started

### Dependencies

- Windows (For now)
- VLC (For now)
- REW beta 68 or higher

### Installing

* Download and install [VLC](https://www.videolan.org/)
* Download and install [REW](https://www.avnirvana.com/threads/rew-api-beta-releases.12981/)
* [Download the exe from this project](https://github.com/menialfob/AutomatedSweeps/releases/latest)

### Executing program

* Set up REW and adjust device output
* Set up your AVR to be in 'measurement mode' ([Easiest to use odd.wtf from here](https://drive.google.com/drive/folders/1Jb3PTQug_Anh8vQp482W7OB25G900rPK))
* Run the AutomatedSweeps.exe
* (Optional) Serve the application on your local network for controlling in a web browser
* Configure your speaker setup
* Run the measurement schedule

## Help

If you encounter any issues, then submit an [issue in this repository](https://github.com/menialfob/AutomatedSweeps/issues).


## License

This project is licensed under the MIT License.

## Acknowledgments

Created for
* ["A1 EVO Neuron" - Next Gen Room EQ by OCA](https://www.avsforum.com/threads/a1-evo-neuron-next-gen-room-eq-by-oca.3316571/)

<!-- MARKDOWN LINKS & IMAGES -->
[application-logo]: assets/AutomatedSweeps.ico
[application-screenshot]: ApplicationFrontpage.png