from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import (
    Placeholder,
    Header,
    Footer,
    ProgressBar,
    Log,
    Button,
)
from textual.containers import VerticalGroup, HorizontalGroup, VerticalScroll
from textual.message import Message

class MeasurementProgressUpdate(Message):
    """Custom event to send progress updates to the UI."""

    def __init__(self, progress: float):
        self.progress = progress  # A float between 0 and 1
        super().__init__()

# A custom event that main.py can handle
class CommandSelected(Message):
    def __init__(self, command_id: str):
        self.command_id = command_id
        super().__init__()

class MeasurementProgress(ProgressBar):
    """A progress bar widget for displaying measurement progress."""

    def on_mount(self) -> None:
        """Event handler for when the widget is mounted."""
        self.update_progress_bar = self.set_interval(
            1 / 60, self.update_progress, pause=True
        )

    def update_progress(self, steps: float | None = 1) -> None:
        """Update the progress bar value."""
        self.advance(steps)

    def start(self) -> None:
        """Start the progress bar."""
        self.update_progress_bar.resume()

    def pause(self) -> None:
        """Pause the progress bar."""
        self.update_progress_bar.pause()

    def stop(self) -> None:
        """Stop the progress bar."""
        self.update_progress_bar.pause()
        self.update(progress=0)


class DefaultScreen(Screen):
    def compose(self) -> ComposeResult:
        yield Header(id="Header")
        with HorizontalGroup(id="MainArea"):
            with VerticalGroup(id="Commands"):
                yield Button(label="Configure measurement", id="configure", variant="default")
                yield Button(label="Start measurement", id="start", variant="success")
                yield Button(label="Pause measurement", id="pause", variant="warning")
                yield Button(label="Stop measurement", id="stop", variant="error")
            yield Placeholder(name="Overview", id="Overview")
        with HorizontalGroup(id="Info"):
            yield Log(id="ConsoleLog", auto_scroll=True, max_lines=10)
            with VerticalGroup(id="ProgressBars"):
                yield MeasurementProgress(
                        id="TotalProgress", total=(11 * 60), show_eta=False
                    )
                yield MeasurementProgress(
                        id="PositionProgress", total=(2 * 60), show_eta=False
                    )
                yield MeasurementProgress(
                        id="IterationProgress", total=(2 * 60), show_eta=False
                    )
                yield MeasurementProgress(
                        id="SweepProgress", total=(2 * 60), show_eta=False
                    )
        yield Footer(id="Footer", show_command_palette=False)