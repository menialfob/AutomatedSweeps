import sys

from textual.app import ComposeResult
from textual.containers import HorizontalGroup, VerticalGroup, VerticalScroll, Grid
from textual.screen import Screen
from textual.reactive import reactive
from textual.screen import ModalScreen
from textual.widgets import (
    Button,
    Footer,
    Label,
    Link,
    OptionList,
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

from serve import run_server
from utils import get_ip, load_settings, save_settings
from collections import OrderedDict


class MeasurementSchedule(Static):
    """A list of measurement steps."""

    def populate_table(self) -> None:
        """Populate the table with the measurement steps."""
        self.table = None
        self.table = Table(title="Measurement Schedule", expand=True)
        # self.step_count = 1
        self.table.add_column("Step", no_wrap=True)
        self.table.add_column("Description", style="cyan", no_wrap=True)
        self.table.add_column("Channel", no_wrap=True)
        self.table.add_column("Audio played", no_wrap=True)
        self.table.add_column("Iteration", no_wrap=True)
        self.table.add_column("Position", no_wrap=True)
        self.table.add_column("Status", no_wrap=True)

        log.debug(f"initial table: {self.table}")

        for index, step in enumerate(config.measurement_schedule):
            self.table.add_row(
                f"#{index + 1}",
                step["Description"],
                step["Channel"],
                step["Audio played"],
                step["Iteration"],
                step["Position"],
                step["Status"],
            )
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


class DefaultScreen(Screen):
    BINDINGS: list[BindingType] = [
        Binding(
            "q", "app.quit_safely", "Quit the application", show=True, priority=True
        ),
        Binding(
            "s",
            "app.stop_measurement_schedule",
            "Stop the measurement",
            show=True,
            priority=True,
        ),
        Binding(
            "p",
            "app.pause_measurement_schedule",
            "Pause the measurement",
            show=True,
            priority=True,
        ),
        Binding("down", "app.focus_next", "Next button", show=True, priority=True),
        Binding(
            "up", "app.focus_previous", "Previous button", show=True, priority=True
        ),
    ]

    def compose(self) -> ComposeResult:
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
        Binding(
            "q", "app.quit_safely", "Quit the application", show=True, priority=True
        ),
    ]

    # A screen showing the user that the app is currently being served at a remote IP
    def compose(self) -> ComposeResult:
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
        Binding(
            "q", "app.quit_safely", "Quit the application", show=True, priority=True
        ),
        Binding("right", "app.focus_next", "Next button", show=True, priority=True),
        Binding(
            "left", "app.focus_previous", "Previous button", show=True, priority=True
        ),
    ]

    channels = reactive(config.selected_channels, recompose=True, layout=True)

    def compose(self) -> ComposeResult:
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


class QuitScreen(ModalScreen[bool]):
    """Screen with a dialog to quit."""

    def __init__(self, input_text: str) -> None:
        super().__init__()
        self.input_text = input_text  # Store input_text as an instance variable

    def compose(self) -> ComposeResult:
        yield Grid(
            Label(f"{self.input_text}", id="question"),
            Button("OK", variant="primary", id="proceed"),
            Button("Abort", variant="error", id="stop"),
            id="dialog",
        )

    def on_button_pressed(self, event: Button.Pressed | None) -> None:
        self.app.pop_screen()


class AutoSweepApp(App):
    CSS_PATH = "ui.tcss"

    SCREENS = {
        "DefaultScreen": DefaultScreen,
        "ServeScreen": ServeScreen,
        "ConfigScreen": ConfigScreen,
    }

    ENABLE_COMMAND_PALETTE = False

    async def on_mount(self) -> None:
        self.title = "Automated Sweeps"
        self.sub_title = "Tool for automating REW measurements"
        await self.push_screen(DefaultScreen())
        self.theme = "nord"

        self.selected_channel = None

        self.generate_measurement_schedule()

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

    def generate_measurement_schedule(self):
        """Generates the measurement schedule based on the current configuration."""

        # Clear the measurement schedule
        config.measurement_schedule.clear()

        # We always need the check settings step
        check_settings = {
            "Description": "Check REW settings",
            "Channel": "---",
            "Audio played": "---",
            "Iteration": "Utility",
            "Position": "---",
            "Status": "Not started",
        }

        config.measurement_schedule.append(check_settings)

        if config.measure_mic_position:
            check_mic_schedule = [
                {
                    "Description": "Measure distance",
                    "Channel": "FL",
                    "Audio played": "FL",
                    "Iteration": "Utility",
                    "Position": "Reference",
                    "Status": "Not started",
                },
                {
                    "Description": "Measure distance",
                    "Channel": "FR",
                    "Audio played": "FR",
                    "Iteration": "Utility",
                    "Position": "Reference",
                    "Status": "Not started",
                },
                {
                    "Description": "Check microphone position",
                    "Channel": "---",
                    "Audio played": "---",
                    "Iteration": "Utility",
                    "Position": "Reference",
                    "Status": "Not started",
                },
            ]

            config.measurement_schedule.extend(check_mic_schedule)
        for i in range(config.measure_iterations):
            for channel, mapping in config.selected_channels.items():
                step = {
                    "Description": "Measure sweep",
                    "Channel": channel,
                    "Audio played": mapping["audio"],
                    "Iteration": "Reference"
                    if config.measure_reference and i == 0
                    else f"{i + 1}",
                    "Position": config.measure_position_name,
                    "Status": "Not started",
                }
                config.measurement_schedule.append(step)

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

        # Update measurement schedule
        self.generate_measurement_schedule()

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

        # Update measurement schedule
        self.generate_measurement_schedule()

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

        # Update measurement schedule
        self.generate_measurement_schedule()

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
        self.generate_measurement_schedule()

        # Refresh measurement table
        self.measurement_schedule.populate_table()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle changes in the input field."""
        log.debug(f"Input submitted: {event.input.id} -> {event.input.value}")

        if event.input.id == "position":
            config.measure_position_name = event.input.value

        elif event.input.id == "iterations":
            config.measure_iterations = int(event.input.value)

        # Update measurement schedule
        self.generate_measurement_schedule()

        # Refresh measurement table
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
                self.generate_measurement_schedule()

                # Refresh measurement table
                self.measurement_schedule.populate_table()
            log.info("No settings file found.")

        elif event.button.id == "start":
            self.start_button = self.query_one("#start", Button)
            self.stop_button = self.query_one("#stop", Button)

            # Enable stop button
            self.stop_button.disabled = False

            # if button is green it must be started
            if event.button.variant == "success":
                # Run measurement in a background worker
                self.start_measurement_schedule()

                # Set button to pause
                self.start_button.variant = "warning"
                self.start_button.label = "Pause measurement"

            # If button is yellow it must be paused
            elif event.button.variant == "warning":
                # Pause measurement schedule
                self.action_pause_measurement_schedule()

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

            self.action_stop_measurement_schedule()

        elif event.button.id == "proceed":
            self.start_measurement_schedule()

        elif event.button.id == "back":
            await self.pop_screen()

            # Update measurement schedule
            self.generate_measurement_schedule()

            # Refresh measurement table
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
            await self.action_quit_safely()

        elif event.button.id == "save":
            save_settings(config.selected_channels)

    # def on_worker_state_changed(self, event: Worker.StateChanged) -> None:
    #     """Handles worker completion and updates the UI."""
    #     self.start_button = self.query_one("#start", Button)
    #     self.stop_button = self.query_one("#stop", Button)
    #     if event.state.name == "SUCCESS":
    #         self.stop_button.disabled = True
    #         self.start_button.variant = "success"
    #         self.start_button.label = "Start measurement"
    #         self.complete_measurement()
    #     elif event.state.name == "CANCELLED":
    #         self.main_console.write("Measurement cancelled.")
    #         self.stop_button.disabled = True
    #         self.start_button.variant = "success"
    #         self.start_button.label = "Start measurement"

    def start_measurement_schedule(self):
        """Runs the measurement schedule in a worker thread."""

        # If a worker is running, resume it
        if hasattr(self, "worker") and self.worker is not None:
            self.pause_event.set()  # Unpause the worker
            self.main_console.write("Resuming measurement schedule...")
            return  # Exit, no need to start a new one

        self.main_console.write("[green]Starting measurement schedule...[/green]")

        self.stop_event = threading.Event()  # Used to stop the thread
        self.pause_event = threading.Event()  # Used to pause execution
        self.pause_event.set()  # Start as unpaused

        # Define a thread-safe UI writer function
        # Initialize NotifyUI instance
        self.message_ui = MessageUI(
            self.main_console,
            self.measurement_schedule,
            self.action_wait_input_measurement_schedule,
            self.action_complete_measurement_schedule,
            self.call_from_thread,
        )

        # Run the workflow as a background task
        from process import run_workflow

        self.worker = self.run_worker(
            lambda: run_workflow(self.message_ui, self.pause_event, self.stop_event),
            thread=True,
            exclusive=True,
        )

    def action_stop_measurement_schedule(self):
        """Stops the measurement schedule."""

        self.main_console.write("[red]Stopping measurement schedule...[/red]")
        if hasattr(self, "stop_event") and hasattr(self, "pause_event"):
            self.stop_event.set()  # Tell the thread to exit
            self.pause_event.set()  # Unpause to allow clean exit

        # Wait for worker thread to finish
        if hasattr(self, "worker") and self.worker is not None:
            self.worker.cancel()  # Ensure the worker is fully stopped
            self.worker = None  # Reset worker to allow restart

        # Clear the measurement schedule
        self.generate_measurement_schedule()

        # Refresh measurement table
        self.measurement_schedule.populate_table()

    def action_pause_measurement_schedule(self):
        """Pauses the measurement schedule."""
        self.main_console.write("[yellow]Pausing measurement schedule...[/yellow]")
        self.pause_event.clear()

    def action_wait_input_measurement_schedule(self, input: str) -> None:
        """Waits for input from the user to continue the measurement schedule."""

        # Pause the measurement schedule by clearing the pause event
        self.action_pause_measurement_schedule()

        self.push_screen(QuitScreen(input))

    def action_complete_measurement_schedule(self):
        """Completes the measurement schedule."""

        self.main_console.write("[green]Completed measurement schedule.[/green]")
        if hasattr(self, "stop_event") and hasattr(self, "pause_event"):
            self.stop_event.set()  # Tell the thread to exit
            self.pause_event.set()  # Unpause to allow clean exit

        # Wait for worker thread to finish
        if hasattr(self, "worker") and self.worker is not None:
            self.worker.cancel()  # Ensure the worker is fully stopped
            self.worker = None  # Reset worker to allow restart

        # Set buttons to default state
        self.stop_button = self.query_one("#stop", Button)

        # Disable stop button
        self.stop_button.disabled = True

        self.start_button = self.query_one("#start", Button)
        self.start_button.variant = "success"
        self.start_button.label = "Start measurement"

    async def action_quit_safely(self):
        """Quits the application."""
        self.main_console.write("Quitting safely...")

        self.action_stop_measurement_schedule()
        # Check if worker exists and cancel it
        if hasattr(self, "worker") and self.worker is not None:
            self.worker.cancel()
        await self.action_quit()


class MessageUI:
    def __init__(
        self,
        main_console: RichLog,
        measurement_schedule: MeasurementSchedule,
        action_wait_input_measurement_schedule,
        action_complete_measurement_schedule,
        call_from_thread,
    ):
        self.main_console = main_console
        self.measurement_schedule = measurement_schedule
        self.action_wait_input_measurement_schedule = (
            action_wait_input_measurement_schedule
        )
        self.action_complete_measurement_schedule = action_complete_measurement_schedule
        self.call_from_thread = call_from_thread

    def info(self, contents: str):
        """Send an informational message to the UI."""
        self.call_from_thread(self.main_console.write, contents)

    def update(self):
        """Trigger a UI update for the measurement schedule."""
        self.call_from_thread(self.measurement_schedule.populate_table)

    def input(self, contents: str):
        """Indicate that input is required from the user."""
        self.call_from_thread(self.action_wait_input_measurement_schedule, contents)

    def complete(self):
        """Indicate that the measurement schedule is complete."""
        self.call_from_thread(self.action_complete_measurement_schedule)
