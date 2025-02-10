import sys

from textual.app import ComposeResult
from textual.containers import HorizontalGroup, VerticalGroup
from textual.message import Message
from textual.screen import Screen
from textual.widgets import (
    Button,
    Footer,
    Header,
    Label,
    Link,
    OptionList,
    Placeholder,
    ProgressBar,
    RichLog,
    RadioSet,
    RadioButton,
    SelectionList,
)
from textual.binding import Binding, BindingType

from textual.widgets.option_list import Option
from textual.widgets.selection_list import Selection

from config import DEFAULT_CHANNELS, ALL_CHANNEL_NAMES, PAIR_CHANNEL_NAMES


class ChannelSelector(VerticalGroup):
    """A radio set widget for selecting audio channels."""

    channel_options: list = [
        Selection(
            prompt=f"{ch} ({PAIR_CHANNEL_NAMES[ch]})",
            value=PAIR_CHANNEL_NAMES[ch],
            id=PAIR_CHANNEL_NAMES[ch],
        )
        for ch in PAIR_CHANNEL_NAMES
    ]

    def compose(self) -> ComposeResult:
        yield Label("Channels to measure", id="ChannelOptionsLabel")
        yield SelectionList[str](*self.channel_options, id="ChannelOptionsList")


class ChannelList(VerticalGroup):
    """A radio set widget for selecting audio channels."""

    channel_options: list = [
        Option(prompt=f"{ALL_CHANNEL_NAMES[ch]} ({ch})", id=ch)
        for ch in DEFAULT_CHANNELS
    ]

    def compose(self) -> ComposeResult:
        yield Label("When measuring...", id="ChannelLabel")
        yield OptionList(*self.channel_options, id="ChannelOptionsList")


class AudioList(VerticalGroup):
    """A radio set widget for selecting audio channels."""

    audio_buttons: list = [
        RadioButton(label=f"{ALL_CHANNEL_NAMES[ch]} ({ch})", id=ch)
        for ch in DEFAULT_CHANNELS
    ]

    def compose(self) -> ComposeResult:
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
        # self.update_progress_bar = self.set_interval(
        #     1 / 60, self.update_progress, pause=True
        # )

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
                yield Button(label="Start measurement", id="start", variant="success")
                # yield Button(label="Pause measurement", id="pause", variant="warning")
                yield Button(
                    label="Channel mapping config", id="configure", variant="default"
                )
                yield Button(
                    label="Stop measurement", id="stop", variant="error", disabled=True
                )
                if "--serve" not in sys.argv:
                    yield Button(label="Serve remotely", id="serve", variant="default")
            yield Placeholder(name="Overview", id="Overview")
        with HorizontalGroup(id="Info"):
            yield RichLog(id="ConsoleLog", auto_scroll=True, max_lines=10)
            with VerticalGroup(id="ProgressBars"):
                yield Label("Total Progress", id="TotalLabel")
                yield MeasurementProgress(
                    id="TotalProgress",
                    total=(11 * 60),
                    show_eta=False,
                    name="Total Progress",
                )
                yield Label("Iteration Progress", id="IterationLabel")
                yield MeasurementProgress(
                    id="IterationProgress",
                    total=(2 * 60),
                    show_eta=False,
                    name="Iteration Progress",
                )
                yield Label("Sweep Progress", id="SweepLabel")
                yield MeasurementProgress(
                    id="SweepProgress",
                    total=(2 * 60),
                    show_eta=False,
                    name="Sweep Progress",
                )
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

    def compose(self) -> ComposeResult:
        yield Header(id="Header")
        with HorizontalGroup(id="ConfigMainArea"):
            with VerticalGroup(id="Commands"):
                yield Button(label="Back", id="back", variant="default")
                yield Button(label="Save settings", id="save", variant="default")
            yield ChannelSelector(id="ChannelSelectGroup")
            with HorizontalGroup(id="ConfigInfo"):
                yield ChannelList(id="ChannelGroup")
                yield AudioList(id="AudioGroup")
        with HorizontalGroup(id="Info"):
            yield RichLog(id="ConsoleLog", auto_scroll=True, max_lines=10)
        yield Footer(id="Footer", show_command_palette=False)
