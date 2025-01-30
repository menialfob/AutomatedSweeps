from textual.app import App, ComposeResult
from textual.screen import Screen
from textual.widgets import (
    Placeholder,
    Label,
    ListView,
    ListItem,
    Header,
    Footer,
    ProgressBar,
    Log,
)
from textual.binding import Binding
from textual.containers import VerticalGroup, HorizontalGroup, VerticalScroll


class Commands(ListView):
    """A container widget for a list of commands."""

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        """Handle the selection of a list item."""

        log = self.app.query_one("#Log", Log)
        progress = self.app.query_one("#TotalProgress", MeasurementProgress)
        if event.item.id == "configure":
            log.write_line("Configuring measurement...")
        elif event.item.id == "start":
            log.write_line("Starting measurement...")
            progress.start()
        elif event.item.id == "pause":
            log.write_line("Pausing measurement...")
            progress.pause()
        elif event.item.id == "stop":
            log.write_line("Stopping measurement...")
            progress.stop()
        else:
            log.write_line(event.item.id)

    def compose(self) -> ComposeResult:
        """Create child widgets for the list view."""

        yield ListItem(Label("Configure measurement"), id="configure")
        yield ListItem(Label("Start measurement"), id="start")
        yield ListItem(Label("Pause measurement"), id="pause")
        yield ListItem(Label("Stop measurement"), id="stop")


class MeasurementProgress(ProgressBar):
    """A progress bar widget for displaying measurement progress."""

    def on_mount(self) -> None:
        """Event handler for when the widget is mounted."""
        self.update_progress_bar = self.set_interval(
            1 / 60, self.update_progress, pause=True
        )

    def update_progress(self) -> None:
        """Update the progress bar value."""
        self.advance()

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
        yield Commands(id="Commands", name="Commands")
        yield Header(id="Header")
        yield Placeholder(name="Overview", id="Overview")
        with HorizontalGroup():
            with VerticalScroll():
                yield Log(id="Log", auto_scroll=True, max_lines=10)
            with VerticalGroup():
                yield MeasurementProgress(
                    id="TotalProgress", total=(11 * 60), show_eta=False
                )
            with VerticalGroup():
                yield MeasurementProgress(
                    id="CurrentProgress", total=(3 * 60), show_eta=False
                )
        yield Footer(id="Footer", show_command_palette=False)


class AutoSweepApp(App):
    CSS_PATH = "textual.tcss"
    BINDINGS = [
        Binding("q", "quit", "Quit the application", show=True, priority=True),
        Binding("s", "stop", "Stop the measurement", show=True, priority=True),
        Binding("p", "pause", "Pause the measurement", show=True, priority=True),
    ]

    def on_mount(self) -> None:
        self.title = "Automated Sweeps"
        self.sub_title = "Tool for automating REW measurements"
        self.push_screen(DefaultScreen())

    async def on_ready(self) -> None:
        # log = self.query_one("#Log", Log)
        # for _ in range(10):
        #     log.write_line("This is a log message.")
        #     await asyncio.sleep(1)
        ...


if __name__ == "__main__":
    app = AutoSweepApp()
    app.run()
