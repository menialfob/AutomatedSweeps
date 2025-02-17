import sys

from textual.app import ComposeResult
from textual.containers import HorizontalGroup, VerticalGroup, VerticalScroll
from textual.message import Message
from textual.screen import Screen
from textual.reactive import reactive
from textual.widgets import (
    Button,
    Footer,
    Header,
    Label,
    Link,
    OptionList,
    ProgressBar,
    RichLog,
    RadioSet,
    RadioButton,
    SelectionList,
    Static,
    Switch,
    Input,
)

from textual import log

from rich.table import Table
from textual.binding import Binding, BindingType

from textual.widgets.option_list import Option
from textual.widgets.selection_list import Selection

import config

import threading

from textual.app import App
from textual.worker import Worker

from serve import run_server
from utils import get_ip, load_settings, save_settings
from collections import OrderedDict


class MeasurementSchedule(Static):
    """A list of measurement steps."""

    def populate_table(self) -> None:
        """Populate the table with the measurement steps."""
        self.table = None
        self.table = Table(title="Measurement Schedule", expand=True)
        self.step_count = 1
        self.table.add_column("Step", no_wrap=True)
        self.table.add_column("Description", style="cyan", no_wrap=True)
        self.table.add_column("Channel", no_wrap=True)
        self.table.add_column("Audio played", no_wrap=True)
        self.table.add_column("Iteration", no_wrap=True)
        self.table.add_column("Position", no_wrap=True)
        self.table.add_column("Status", no_wrap=True)

        log.debug(f"initial table: {self.table}")

        # Always check settings first
        self.table.add_row(
            f"#{self.step_count}",
            "Check REW settings",
            "---",
            "---",
            "Utility",
            "---",
            config.utility_steps["checkSettings"],
        )

        if config.measure_mic_position:
            self.table.add_row(
                f"#{self.step_count}",
                "Measure FL Distance",
                "FL",
                "FL",
                "Utility",
                "Reference",
                config.utility_steps["measureFL"],
            )
            self.step_count += 1

            self.table.add_row(
                f"#{self.step_count}",
                "Measure FR Distance",
                "FR",
                "FR",
                "Utility",
                "Reference",
                config.utility_steps["measureFR"],
            )
            self.step_count += 1

            self.table.add_row(
                f"#{self.step_count}",
                "Check microphone position",
                "---",
                "---",
                "Utility",
                "Reference",
                config.utility_steps["checkMic"],
            )
            self.step_count += 1

        for i in range(config.measure_iterations):
            for channel, mapping in config.selected_channels.items():
                self.table.add_row(
                    f"#{self.step_count}",
                    "Measure sweep",
                    channel,
                    mapping["audio"],
                    "Reference" if config.measure_reference and i == 0 else f"{i + 1}",
                    config.measure_position_name,
                    mapping["status"],
                )
                self.step_count += 1
            self.table.add_section()
        self.update(self.table)
        log.debug(f"self.table: {self.table}")


class ChannelSelector(VerticalGroup):
    """A radio set widget for selecting audio channels."""

    def compose(self) -> ComposeResult:
        self.channel_options: list = [
            Selection(
                prompt=f"{ch} ({config.PAIR_CHANNEL_NAMES[ch]})",
                value=config.PAIR_CHANNEL_NAMES[ch],
                id=config.PAIR_CHANNEL_NAMES[ch],
                initial_state=any(
                    channel in config.PAIR_CHANNEL_NAMES[ch]
                    for channel in config.selected_channels.keys()
                ),
            )
            for ch in config.PAIR_CHANNEL_NAMES
        ]
        yield Label("Channels to measure", id="ChannelOptionsLabel")
        yield SelectionList[str](*self.channel_options, id="ChannelOptionsList")


class ChannelList(VerticalGroup):
    """A radio set widget for selecting audio channels."""

    def compose(self) -> ComposeResult:
        self.channel_options: list = [
            Option(prompt=f"{config.ALL_CHANNEL_NAMES[ch]} ({ch})", id=ch)
            for ch in config.selected_channels.keys()
        ]
        yield Label("When measuring...", id="ChannelLabel")
        yield OptionList(*self.channel_options, id="ChannelOptionsList")


class AudioList(VerticalGroup):
    """A radio set widget for selecting audio channels."""

    def compose(self) -> ComposeResult:
        self.audio_buttons: list = [
            RadioButton(label=f"{config.ALL_CHANNEL_NAMES[ch]} ({ch})", id=ch)
            for ch in config.selected_channels.keys()
        ]
        yield Label("...then play this audio file", id="AudioLabel")
        yield RadioSet(*self.audio_buttons, id="AudioOptionsList")


class MeasurementProgressUpdate(Message):
    """Custom event to send progress updates to the UI."""

    def __init__(self, progress: float):
        self.progress = progress  # A float between 0 and 1
        super().__init__()


class MeasurementProgress(ProgressBar):
    """A progress bar widget for displaying measurement progress."""

    def on_mount(self) -> None:
        """Event handler for when the widget is mounted."""

    def update_progress(self, steps: float | None = 1) -> None:
        """Update the progress bar value."""
        self.advance(steps)

    def start(self) -> None:
        """Start the progress bar."""
        # self.update_progress_bar.resume()

    def pause(self) -> None:
        """Pause the progress bar."""
        # self.update_progress_bar.pause()

    def stop(self) -> None:
        """Stop the progress bar."""
        # self.update_progress_bar.pause()
        self.update(progress=0)


class DefaultScreen(Screen):
    BINDINGS: list[BindingType] = [
        Binding("q", "app.quit", "Quit the application", show=True, priority=True),
        Binding("s", "app.stop", "Stop the measurement", show=True, priority=True),
        Binding("p", "app.pause", "Pause the measurement", show=True, priority=True),
        Binding("down", "app.focus_next", "Next button", show=True, priority=True),
        Binding(
            "up", "app.focus_previous", "Previous button", show=True, priority=True
        ),
    ]

    def compose(self) -> ComposeResult:
        yield Header(id="Header")
        with HorizontalGroup(id="MainArea"):
            with VerticalGroup(id="Commands"):
                yield Button(
                    label="Start measurement",
                    id="start",
                    variant="success",
                    name="start",
                )
                yield Button(
                    label="Stop measurement", id="stop", variant="error", disabled=True
                )
                yield Button(label="Setup", id="configure", variant="default")
                yield Button(label="Load settings", id="load", variant="default")
                if "--serve" not in sys.argv:
                    yield Button(label="Serve remotely", id="serve", variant="default")
            with VerticalGroup(id="Overview"):
                with VerticalGroup(id="Selections"):
                    with HorizontalGroup(classes="SetupRow"):
                        with VerticalGroup(id="ReferenceSwitch", classes="SetupField"):
                            yield Label(
                                "Reference position",
                                id="ReferenceLabel",
                                variant="primary",
                            )
                            yield Static("Measure reference position")
                            yield Switch(id="reference", value=True)
                        with VerticalGroup(id="CenteringSwitch", classes="SetupField"):
                            yield Label(
                                "Center microphone",
                                id="CenteringLabel",
                                variant="primary",
                            )
                            yield Static(
                                "Measure the microphone center position as a reference"
                            )
                            yield Switch(id="centering", value=True)
                    with HorizontalGroup(classes="SetupRow"):
                        with VerticalGroup(id="Iterations", classes="SetupField"):
                            yield Label(
                                "Iterations per position",
                                id="IterationsLabel",
                                variant="primary",
                            )
                            yield Static(
                                "Input the number of measurements that you want to perform at this position"
                            )
                            yield Input(
                                id="iterations",
                                value="1",
                                placeholder="1 to 99",
                                type="integer",
                            )
                        with VerticalGroup(id="Positions", classes="SetupField"):
                            yield Label(
                                "Position name",
                                id="PositionsLabel",
                                variant="primary",
                            )
                            yield Static(
                                "Enter a custom name for your position such as 'couch 1' or simply a number"
                            )
                            yield Input(
                                id="position",
                                value="",
                                placeholder="Position name",
                                type="text",
                                disabled=True,
                            )
                with VerticalScroll(id="ScheduleArea"):
                    yield MeasurementSchedule(id="MeasurementSchedule")
        with HorizontalGroup(id="Info"):
            yield RichLog(id="ConsoleLog", auto_scroll=True, markup=True, wrap=True)
        yield Footer(id="Footer", show_command_palette=False)


class ServeScreen(Screen):
    BINDINGS: list[BindingType] = [
        Binding("q", "app.quit", "Quit the application", show=True, priority=True),
    ]

    # A screen showing the user that the app is currently being served at a remote IP
    def compose(self) -> ComposeResult:
        yield Header(id="Header")
        with HorizontalGroup(id="ServeMainArea"):
            with VerticalGroup(id="Commands"):
                yield Button(label="Stop serving & quit", id="quit", variant="default")
            with VerticalGroup(id="ServeInfo"):
                yield Label("Serving automated sweeps app at:")
                yield Link("", id="ServeUrl")
                yield Label(
                    "Go to the url on another device to do the measurements remotely."
                )
        with HorizontalGroup(id="Info"):
            yield RichLog(id="ConsoleLog", auto_scroll=True, max_lines=10)
        yield Footer(id="Footer", show_command_palette=False)


class ConfigScreen(Screen):
    # A channel mapping configuration screen
    BINDINGS: list[BindingType] = [
        Binding("q", "app.quit", "Quit the application", show=True, priority=True),
        Binding("right", "app.focus_next", "Next button", show=True, priority=True),
        Binding(
            "left", "app.focus_previous", "Previous button", show=True, priority=True
        ),
    ]

    channels = reactive(config.selected_channels, recompose=True, layout=True)

    def compose(self) -> ComposeResult:
        yield Header(id="Header")
        with HorizontalGroup(id="ConfigMainArea"):
            with VerticalGroup(id="Commands"):
                yield Button(label="Back", id="back", variant="default")
                yield Button(label="Save settings", id="save", variant="default")
                # with VerticalGroup(id="LosslessSwitch"):
                #     yield Label("Lossless audio", id="LosslessLabel", variant="primary")
                #     yield Static("Use lossless audio")
                #     yield Switch(id="lossless", value=True)
            yield ChannelSelector(id="ChannelSelectGroup")
            yield ChannelList(id="ChannelGroup")  # .data_bind(ConfigScreen.channels)
            yield AudioList(id="AudioGroup")  # .data_bind(ConfigScreen.channels)
        yield Footer(id="Footer", show_command_palette=False)


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
        self.channels_list.refresh(recompose=True, layout=True)
        self.audio_list = self.query_one(AudioList)
        self.audio_list.refresh(recompose=True, layout=True)

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

        if event.switch.id == "reference":
            config.measure_reference = self.switch_value

            # Disable centering switch if reference is False since you can only center at the reference position
            self.centering_switch = self.query_one("#centering", Switch)
            self.centering_switch.value = self.switch_value
            self.centering_switch.disabled = not self.switch_value

            # Set position name to 'Reference' if measuring reference and disable changing
            self.position_input = self.query_one("#position", Input)
            self.position_input.value = "Reference" if self.switch_value else ""
            self.position_input.disabled = self.switch_value

        elif event.switch.id == "centering":
            config.measure_mic_position = self.switch_value

        # elif event.switch.id == "lossless":
        #     config.lossless_audio = event.switch.value

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
            self.start_button = self.query_one("#start", Button)
            self.stop_button = self.query_one("#stop", Button)

            # Enable stop button
            self.stop_button.disabled = False

            # if button is green it must be started
            if event.button.variant == "success":
                log.debug(f"---{event.button.label}---")
                self.main_console.write("Starting measurement...")

                # Run measurement in a background worker
                self.run_measurement_schedule()

                # Set button to pause
                self.start_button.variant = "warning"
                self.start_button.label = "Pause measurement"
            # If button is yellow it must be paused
            elif event.button.variant == "warning":
                self.main_console.write("Resuming measurement...")

                # Set button to resume
                self.start_button.variant = "success"
                self.start_button.label = "Resume"

        elif event.button.id == "stop":
            self.stop_button = self.query_one("#stop", Button)

            # Disable stop button
            self.stop_button.disabled = True

            self.start_button = self.query_one("#start", Button)
            self.start_button.variant = "success"
            self.start_button.label = "Start measurement"

            self.main_console.write("Stopping measurement...")

            self.worker.cancel()

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
        self.start_button = self.query_one("#start", Button)
        self.stop_button = self.query_one("#stop", Button)
        if event.state.name == "SUCCESS":
            self.stop_button.disabled = True
            self.start_button.variant = "success"
            self.start_button.label = "Start measurement"
            self.complete_measurement()
        elif event.state.name == "CANCELLED":
            self.main_console.write("Measurement cancelled.")
            self.stop_button.disabled = True
            self.start_button.variant = "success"
            self.start_button.label = "Start measurement"

    def run_measurement_schedule(self):
        """Runs the measurement schedule in a worker thread."""
        from workflow import run_positioning_check

        # self.worker: Worker = get_current_worker()

        # Define a thread-safe UI writer function
        def notify_ui(message: dict[str]):
            if message["type"] == "info":
                self.call_from_thread(self.main_console.write, message["contents"])
            if message["type"] == "update":
                self.call_from_thread(self.measurement_schedule.populate_table)

        # Run the workflow as a background task
        self.run_worker(
            lambda: run_positioning_check(notify_ui), thread=True, exclusive=True
        )

        # # If worker is not cancelled, continuously check if REW is running with ensure_rew_api(). If not, wait 2 seconds and try again for a maximum of 30 times.
        # rew_api_offline = False

        # for _ in range(30):
        #     if _ == 1:
        #         self.call_from_thread(
        #             self.main_console.write, "REW API is not running, please start it."
        #         )
        #     if self.worker.is_cancelled:
        #         break
        #     if ensure_rew_api():
        #         self.call_from_thread(self.main_console.write, "REW API is running.")
        #         break
        #     time.sleep(2)
        # if rew_api_offline:
        #     self.call_from_thread(
        #         self.main_console.write, "Timed out waiting for REW API to run."
        #     )

    def complete_measurement(self):
        """Handles completion of the measurement process."""
        self.main_console.write("Measurement completed!")
