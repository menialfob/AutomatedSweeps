pyinstaller --clean --onefile --icon assets/AutomatedSweeps.ico -y -n  "AutomatedSweeps" --add-data "assets;assets" --add-data "src/ui.tcss:." src/main.py

[https://stackoverflow.com/questions/53587322/how-do-i-include-files-with-pyinstaller](https://stackoverflow.com/questions/53587322/how-do-i-include-files-with-pyinstaller)