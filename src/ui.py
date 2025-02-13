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
                with VerticalGroup(id="LosslessSwitch"):
                    yield Label("Lossless audio", id="LosslessLabel", variant="primary")
                    yield Static("Use lossless audio")
                    yield Switch(id="lossless", value=True)
            yield ChannelSelector(id="ChannelSelectGroup")
            yield ChannelList(id="ChannelGroup")  # .data_bind(ConfigScreen.channels)
            yield AudioList(id="AudioGroup")  # .data_bind(ConfigScreen.channels)
        yield Footer(id="Footer", show_command_palette=False)
