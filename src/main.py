import sys
import threading

from textual.app import App
from textual.worker import Worker

from audio import get_audio_files
from measurement import run_measurements
from rew_api import ensure_rew_api, ensure_rew_settings
from serve import run_server
from ui import (
    Button,
    ConfigScreen,
    DefaultScreen,
    Link,
    MeasurementProgress,
    RichLog,
    ServeScreen,
    OptionList,
    RadioSet,
    RadioButton,
)
from utils import get_audio_channels, get_ip, load_settings, save_settings
from config import channel_mapping
from textual import log


class AutoSweepApp(App):
    CSS_PATH = "ui.tcss"

    SCREENS = {
        "DefaultScreen": DefaultScreen,
        "ServeScreen": ServeScreen,
        "ConfigScreen": ConfigScreen,
    }

    async def on_mount(self) -> None:
        self.title = "Automated Sweeps"
        self.sub_title = "Tool for automating REW measurements"
        self.push_screen(DefaultScreen())
        self.theme = "nord"

        self.total_progress = None
        self.position_progress = None
        self.iteration_progress = None
        self.sweep_progress = None
        self.main_console = None
        self.serve_url = None

        self.selected_channel = None

    # def on_command_selected(self, message: CommandSelected) -> None:

    def on_option_list_option_highlighted(
        self, message: OptionList.OptionSelected
    ) -> None:
        """Handle the highlighted option in the channel list."""

        self.selected_channel = message.option_id

        # Check if a mapping exists for the option_id
        mapped_option = channel_mapping.get(message.option_id, message.option_id)

        log.debug(
            f"Highlighted option: {message.option_id} (Mapped to: {mapped_option})"
        )

        # Use the mapped option_id to select the corresponding radio button
        self.radio_button = self.query_one(f"#{mapped_option}", RadioButton)
        self.radio_button.value = True

    def on_radio_set_changed(self, message: RadioSet.Changed) -> None:
        """Handle changes in the selected radio button (new channel mapping)."""
        log.debug(f"Radio button changed: {message.pressed.id}")
        original_channel = self.selected_channel  # The channel the user is mapping from
        new_mapping = message.pressed.id  # The channel the user selected as the mapping

        # Ensure both variables are valid
        if original_channel and new_mapping:
            # Update or create the mapping in CHANNEL_MAPPING
            channel_mapping[original_channel] = new_mapping
            log.info(f"Mapping updated: {original_channel} -> {new_mapping}")
        else:
            log.warning("Either original channel or new mapping is missing.")

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle measurement commands selected from the UI."""

        if event.button.id == "configure":
            await self.push_screen("ConfigScreen")
            # global channels, iterations, totalprogress
            # channels = 11
            # iterations = 2
            # totalprogress = channels * iterations

            # self.total_progress = self.query_one("#TotalProgress", MeasurementProgress)
            # self.iteration_progress = self.query_one(
            #     "#IterationProgress", MeasurementProgress
            # )
            # self.sweep_progress = self.query_one("#SweepProgress", MeasurementProgress)
            # self.total_label = self.query_one("#TotalLabel", Label)
            # self.iteration_label = self.query_one("#IterationLabel", Label)
            # self.main_console = self.query_one("#ConsoleLog", RichLog)

            # self.main_console.write("Configuring measurement...")
            # self.total_progress.update(total=totalprogress)
            # self.total_label.update(f"Total Progress ({totalprogress})")
            # self.iteration_label.update(f"Iteration Progress ({iterations})")
            # self.iteration_progress.update(total=iterations)

        elif event.button.id == "start":
            self.total_progress = self.query_one("#TotalProgress", MeasurementProgress)
            self.main_console = self.query_one("#ConsoleLog", RichLog)
            self.main_console.write("Starting measurement...")
            self.total_progress.advance(1)

            # Run measurement in a background worker
            self.run_worker(self.run_measurement, thread=True, exclusive=True)

        elif event.button.id == "pause":
            self.main_console.write("Pausing measurement...")
            self.total_progress.pause()

        elif event.button.id == "stop":
            self.main_console.write("Stopping measurement...")
            self.total_progress.stop()

        elif event.button.id == "back":
            await self.push_screen("DefaultScreen")

        elif event.button.id == "serve":
            self.main_console = self.query_one("#ConsoleLog", RichLog)
            self.main_console.write("Starting server...")
            thread = threading.Thread(target=run_server, daemon=True)
            thread.start()
            await self.push_screen("ServeScreen")
            self.serve_url = self.query_one("#ServeUrl", Link)
            self.serve_url.update("http://" + get_ip() + ":8000")

        elif event.button.id == "quit":
            self.main_console.write("Stopping server...")
            await self.action_quit()

    def on_worker_state_changed(self, event: Worker.StateChanged) -> None:
        """Handles worker completion and updates the UI."""
        if event.state.name == "SUCCESS":
            self.complete_measurement()

    def run_measurement(self):
        """Runs the measurement process in a worker thread."""
        # worker = get_current_worker()
        self.main_console.write("Running measurement...")
        # main()

    def complete_measurement(self):
        """Handles completion of the measurement process."""
        self.main_console.write("Measurement completed!")

    async def on_ready(self) -> None:
        # RichLog = self.query_one("#RichLog", RichLog)
        # for _ in range(10):
        #     RichLog.write("This is a RichLog message.")
        #     await asyncio.sleep(1)
        ...


def setup():
    """Handle setup process for loading settings and selecting audio files."""
    settings = load_settings()
    audio_path = None
    selected_channels = None

    if settings:
        use_saved = input("Saved settings found. Load them? (y/n): ").strip().lower()
        if use_saved in ("y", "yes"):
            print("Loaded saved settings.")
            audio_path = settings["audio_path"]
            selected_channels = sorted(set(settings["channels"]))

    if not audio_path or not selected_channels:
        audio_path, mlp_files = get_audio_files()
        if audio_path and mlp_files:
            selected_channels = get_audio_channels(mlp_files)
            save_choice = (
                input("Save these settings for future use? (y/n): ").strip().lower()
            )
            if save_choice in ("y", "yes"):
                save_settings(audio_path, selected_channels)

    if audio_path and selected_channels:
        print("Processing files in:", audio_path)
        print("Measuring channels:", selected_channels)

        is_reference = input(
            "Are you measuring the Main Listening Position (MLP)? (y/n): "
        ).strip().lower() in ("y", "yes")
        position_number = (
            0
            if is_reference
            else int(input("Enter the position number (starting from 0): "))
        )
        num_iterations = (
            1 if is_reference else int(input("How many measurements per position?: "))
        )

    return audio_path, selected_channels, is_reference, num_iterations, position_number


def main():
    print("Starting measurement script")
    if not ensure_rew_api():
        print("ERROR: REW API is not running. Exiting")
        return
    # Checking for errors in setup
    errors = ensure_rew_settings()
    if errors:
        print("Errors detected in REW settings:")
        for error in errors:
            print(error)
        return

    # Setup and run
    audio_path, selected_channels, is_reference, num_iterations, position_number = (
        setup()
    )
    if selected_channels:
        run_measurements(
            selected_channels, is_reference, num_iterations, position_number, audio_path
        )


if __name__ == "__main__":
    for arg in sys.argv:
        print(arg)
    app = AutoSweepApp()
    app.run()
