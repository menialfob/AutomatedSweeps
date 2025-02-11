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
    RichLog,
    ServeScreen,
    OptionList,
    RadioSet,
    RadioButton,
    SelectionList,
    ChannelList,
    AudioList,
    ChannelSelector,
    MeasurementSchedule,
    Switch,
    Input,
)
from utils import get_audio_channels, get_ip, load_settings, save_settings
import config
from textual import log
from collections import OrderedDict


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
        await self.push_screen(DefaultScreen())
        self.theme = "nord"

        self.selected_channel = None

        # Update measurement schedule
        self.measurement_schedule = self.query_one(
            "#MeasurementSchedule", MeasurementSchedule
        )
        self.measurement_schedule.populate_table()

        # Write welcome message
        self.main_console = self.query_one("#ConsoleLog", RichLog)
        self.main_console.write("[green]Welcome to Automated Sweeps![/green]")
        self.main_console.write(
            "This program uses a combination of APIs and screen interaction to automate sweep measurements as much as possible. It is designed to be used in conjunction with ObsessiveCompulsiveAudiophile's A1 Neuron Room Audio Optimization script."
        )
        self.main_console.write(
            "Start by going to setup and configure your measurement setup or use Load settings to load a previous configuration."
        )
        self.main_console.write(
            "It is important that you have the following settings: 1) REW open on your main monitor with the 'Measure' button visible. 2) Set REW measurement sweep file. 3) Select 'Use as entered' and deselect 'Prefix with output'"
        )
        self.main_console.write(
            "[italic]Note that the position name 'Reference' carries a special significance and should be used for your first measurements of the Main Listening Position (MLP) / reference position.[/italic]"
        )

    def on_selection_list_selected_changed(
        self, message: SelectionList.SelectedChanged
    ) -> None:
        """Handle the selected option in the channel list."""

        config.selected_channels.clear()

        for item in message.selection_list.selected:
            log.debug(f"Selected option: {item}")
            for ch in item.split("/"):
                config.selected_channels[ch] = {"audio": ch, "status": "Not started"}

        # Sort config.selected_channels according to the order in ALL_CHANNEL_NAMES
        sorted_selected_channels = OrderedDict(
            (k, config.selected_channels[k])
            for k in config.ALL_CHANNEL_NAMES
            if k in config.selected_channels
        )

        # Replace the original dict with the sorted one
        config.selected_channels.clear()
        config.selected_channels.update(sorted_selected_channels)

        log.debug(f"Selected options: {config.selected_channels}")

        self.channels_list = self.query_one(ChannelList)
        self.channels_list.refresh(recompose=True)
        self.audio_list = self.query_one(AudioList)
        self.audio_list.refresh(recompose=True)

    def on_option_list_option_highlighted(
        self, message: OptionList.OptionSelected
    ) -> None:
        """Handle the highlighted option in the channel list."""

        self.selected_channel = message.option_id

        # Check if a mapping exists for the option_id
        mapped_option = config.selected_channels[message.option_id]["audio"]

        log.debug(
            f"Highlighted option: {message.option_id} (Mapped to: {mapped_option})"
        )

        # Use the mapped option_id to select the corresponding radio button
        self.radio_button = self.query_one(f"#{mapped_option}", RadioButton)
        self.radio_button.value = True

    def on_radio_set_changed(self, message: RadioSet.Changed) -> None:
        """Handle changes in the selected radio button (new channel mapping)."""
        original_channel = self.selected_channel  # The channel the user is mapping from
        new_mapping = message.pressed.id  # The channel the user selected as the mapping

        # Ensure both variables are valid
        if original_channel and new_mapping:
            # Update or create the mapping in config.channel_mapping
            config.selected_channels[original_channel]["audio"] = new_mapping
            log.debug(f"Mapping updated: {original_channel} -> {new_mapping}")
        else:
            log.warning("Either original channel or new mapping is missing.")

    def on_switch_changed(self, event: Switch.Changed) -> None:
        """Handle changes in the switch."""
        log.debug(f"Switch changed: {event.switch.id} -> {event.switch.value}")

        self.switch_value = event.switch.value

        if event.switch.id == "lossless":
            config.lossless_audio = event.switch.value

        elif event.switch.id == "centering":
            config.measure_mic_position = self.switch_value

        # Update measurement schedule
        self.measurement_schedule.populate_table()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle changes in the input field."""
        log.debug(f"Input submitted: {event.input.id} -> {event.input.value}")

        if event.input.id == "position":
            config.measure_position_name = event.input.value

        elif event.input.id == "iterations":
            config.measure_iterations = int(event.input.value)

        # Update measurement schedule
        self.measurement_schedule.populate_table()

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle measurement commands selected from the UI."""

        if event.button.id == "configure":
            await self.push_screen("ConfigScreen")
            self.channels_overview = self.query_one(
                "#ChannelSelectGroup", ChannelSelector
            )
            self.channels_overview.refresh(recompose=True)
            self.channels_list = self.query_one(ChannelList)
            self.channels_list.refresh(recompose=True)
            self.audio_list = self.query_one(AudioList)
            self.audio_list.refresh(recompose=True)

        elif event.button.id == "load":
            self.settings = load_settings()
            if self.settings:
                config.selected_channels = self.settings
                log.debug(f"Loaded settings: {config.selected_channels}")

                # Update measurement schedule
                self.measurement_schedule.populate_table()
            log.info("No settings file found.")

        elif event.button.id == "start":
            self.main_console.write("Starting measurement...")

            # Run measurement in a background worker
            self.run_worker(self.run_measurement, thread=True, exclusive=True)

        elif event.button.id == "pause":
            self.main_console.write("Pausing measurement...")

        elif event.button.id == "stop":
            self.main_console.write("Stopping measurement...")

        elif event.button.id == "back":
            await self.pop_screen()
            self.measurement_schedule = self.query_one(
                "#MeasurementSchedule", MeasurementSchedule
            )
            self.measurement_schedule.populate_table()

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

        elif event.button.id == "save":
            save_settings(config.selected_channels)

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
