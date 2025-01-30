# from audio import get_audio_files
# from measurement import run_measurements
# from rew_api import ensure_rew_api, ensure_rew_settings
from utils import get_audio_channels, load_settings, save_settings
from ui import DefaultScreen, CommandSelected, MeasurementProgress, Log
from textual.binding import Binding
from textual.app import App
from textual.worker import Worker, get_current_worker
import time

class AutoSweepApp(App):
    CSS_PATH = "ui.tcss"
    BINDINGS = [
        Binding("q", "quit", "Quit the application", show=True, priority=True),
        Binding("s", "stop", "Stop the measurement", show=True, priority=True),
        Binding("p", "pause", "Pause the measurement", show=True, priority=True),
    ]

    def on_mount(self) -> None:
        self.title = "Automated Sweeps"
        self.sub_title = "Tool for automating REW measurements"
        self.push_screen(DefaultScreen())

    def on_command_selected(self, message: CommandSelected) -> None:
        """Handle measurement commands selected from the UI."""
        log = self.query_one("#Log")
        progress = self.query_one("#TotalProgress", MeasurementProgress)

        if message.command_id == "configure":
            log.write_line("Configuring measurement...")

        elif message.command_id == "start":
            log.write_line("Starting measurement...")
            # progress.start()

            # Run measurement in a background worker
            self.run_worker(self.run_measurement, thread=True, exclusive=True)

        elif message.command_id == "pause":
            log.write_line("Pausing measurement...")
            progress.pause()

        elif message.command_id == "stop":
            log.write_line("Stopping measurement...")
            progress.stop()

    def on_worker_state_changed(self, event: Worker.StateChanged) -> None:
        """Handles worker completion and updates the UI."""
        if event.state.name == "SUCCESS":
            self.complete_measurement()


    def run_measurement(self):
        """Runs the measurement process in a worker thread."""
        # worker = get_current_worker()
        start_measurement()


    def complete_measurement(self):
        """Handles completion of the measurement process."""
        log = self.query_one("#Log", Log)
        progress = self.query_one("#TotalProgress", MeasurementProgress)
        log.write_line("Measurement completed!")
        progress.stop()

    async def on_ready(self) -> None:
        # log = self.query_one("#Log", Log)
        # for _ in range(10):
        #     log.write_line("This is a log message.")
        #     await asyncio.sleep(1)
        ...

def start_measurement():
    progress = app.query_one("#TotalProgress", MeasurementProgress)
    for _ in range(11*60):
        progress.update_progress()
        time.sleep(0.01)

# def setup():
#     """Handle setup process for loading settings and selecting audio files."""
#     settings = load_settings()
#     audio_path = None
#     selected_channels = None

#     if settings:
#         use_saved = input("Saved settings found. Load them? (y/n): ").strip().lower()
#         if use_saved in ("y", "yes"):
#             print("Loaded saved settings.")
#             audio_path = settings["audio_path"]
#             selected_channels = sorted(set(settings["channels"]))

#     if not audio_path or not selected_channels:
#         audio_path, mlp_files = get_audio_files()
#         if audio_path and mlp_files:
#             selected_channels = get_audio_channels(mlp_files)
#             save_choice = (
#                 input("Save these settings for future use? (y/n): ").strip().lower()
#             )
#             if save_choice in ("y", "yes"):
#                 save_settings(audio_path, selected_channels)

#     if audio_path and selected_channels:
#         print("Processing files in:", audio_path)
#         print("Measuring channels:", selected_channels)

#         is_reference = input(
#             "Are you measuring the Main Listening Position (MLP)? (y/n): "
#         ).strip().lower() in ("y", "yes")
#         position_number = (
#             0
#             if is_reference
#             else int(input("Enter the position number (starting from 0): "))
#         )
#         num_iterations = (
#             1 if is_reference else int(input("How many measurements per position?: "))
#         )

#     return audio_path, selected_channels, is_reference, num_iterations, position_number


# def main():
#     print("Starting measurement script")
#     if not ensure_rew_api():
#         print("ERROR: REW API is not running. Exiting")
#         return
#     # Checking for errors in setup
#     errors = ensure_rew_settings()
#     if errors:
#         print("Errors detected in REW settings:")
#         for error in errors:
#             print(error)
#         return

#     # Setup and run
#     audio_path, selected_channels, is_reference, num_iterations, position_number = (
#         setup()
#     )
#     if selected_channels:
#         run_measurements(
#             selected_channels, is_reference, num_iterations, position_number, audio_path
#         )


if __name__ == "__main__":
    # main()
    app = AutoSweepApp()
    app.run()
