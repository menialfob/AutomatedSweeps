from gui_automation import run_sweep
from rew_api import (
    check_new_problems,
    delete_measurement,
    get_selected_measurement_uuid,
)
from utils import get_microphone_distance, check_control_events
import config
from threading import Event
from ui import MessageUI
from gui_automation import get_button_position
from rew_api import ensure_rew_api, ensure_rew_settings


def run_workflow(message_ui: MessageUI, pause_event: Event, stop_event: Event):
    total_steps = len(config.measurement_schedule)
    current_step = 0
    successful_step = False
    uuids: dict = {}

    while current_step < total_steps:
        # Check for control events and break if stop_event is set.
        if check_control_events(pause_event, stop_event, message_ui):
            break

        successful_step = False

        match config.measurement_schedule[current_step]["Description"]:
            case "Check REW settings":
                # Checking if REW API is running
                while not ensure_rew_api():
                    # Check for control events and break if stop_event is set.
                    if check_control_events(pause_event, stop_event, message_ui):
                        break
                    message_ui.input(
                        "REW API is not running. Please start REW and press OK."
                    )
                    pause_event.wait()

                # Checking if some of the REW settings are correct
                while True:
                    # Check for control events and break if stop_event is set.
                    if check_control_events(pause_event, stop_event, message_ui):
                        break

                    errors = ensure_rew_settings()  # Get the list of errors
                    if not errors:
                        break  # Exit loop if settings are correct

                    # Show errors to the user
                    error_message = "REW settings are incorrect:\n" + "\n".join(errors)
                    message_ui.input(
                        error_message + "\n\nPlease adjust settings and press OK."
                    )

                    pause_event.wait()

                # Checking if measure button is visible. This already contains a loop to inform user move window if necessary.
                get_button_position(
                    "MeasureButton.png", message_ui, pause_event, stop_event
                )

                successful_step = True

            case "Measure distance":
                successful_step = sweep_and_check_problems(
                    config.measurement_schedule[current_step]["Channel"],
                    config.measurement_schedule[current_step]["Iteration"],
                    config.measurement_schedule[current_step]["Position"],
                    config.measurement_schedule[current_step]["Audio played"],
                    message_ui,
                    pause_event,
                    stop_event,
                    max_attempts=3,
                )
                uuids[config.measurement_schedule[current_step]["Channel"]] = (
                    get_selected_measurement_uuid()
                )

            case "Check microphone position":
                # Get the distance needed to move the microphone
                # A negative number means it needs to move to the right speaker, while a positive number means it needs to move to the left speaker.
                fr_fl_distance = get_microphone_distance(uuids["FR"], uuids["FL"])
                if abs(fr_fl_distance) < 4:
                    message_ui.info(
                        f"The microphone is positioned correctly within the error margin of 3 cm. (Distance from center: {abs(fr_fl_distance)} cm)"
                    )
                    successful_step = True
                else:
                    if fr_fl_distance < 0:
                        message_ui.input(
                            f"Move the microphone {abs(fr_fl_distance)} cm ({round(abs(fr_fl_distance) / 2.54, 2)} in) to the right speaker"
                        )
                    else:
                        message_ui.input(
                            f"Move the microphone {abs(fr_fl_distance)} cm ({round(abs(fr_fl_distance) / 2.54, 2)} in) to the left speaker"
                        )
                    pause_event.wait()
                    current_step -= 2
        # Check for control events and break if stop_event is set.
        if check_control_events(pause_event, stop_event, message_ui):
            break

        if successful_step:
            config.measurement_schedule[current_step]["Status"] = (
                "[green]Completed[/green]"
            )
            message_ui.update()
            current_step += 1
        else:
            config.measurement_schedule[current_step]["Status"] = (
                "[yellow]Retrying[/yellow]"
            )
            message_ui.update()
    # Check for control events and break if stop_event is set.
    if check_control_events(pause_event, stop_event, message_ui):
        return
    message_ui.complete()


def sweep_and_check_problems(
    channel: str,
    iteration,
    position,
    audio_file,
    message_ui: MessageUI,
    pause_event: Event,
    stop_event: Event,
    max_attempts=3,
):
    """Runs sweep and checks for new problems, retrying up to max_attempts times."""

    # Track initial problem times
    initial_problem_times = set()
    previous_problem_times, _ = check_new_problems(initial_problem_times)

    attempts = 0

    while attempts < max_attempts:
        # Check for control events and break if stop_event is set.
        if check_control_events(pause_event, stop_event, message_ui):
            break

        run_sweep(
            channel,
            iteration,
            position,
            audio_file,
            message_ui,
            pause_event,
            stop_event,
        )
        attempts += 1

        # Check for control events and break if stop_event is set.
        if check_control_events(pause_event, stop_event, message_ui):
            break

        new_problem_times, problems = check_new_problems(previous_problem_times)

        if not new_problem_times:
            message_ui.info("No new problems detected. Sweep successful.")
            return True
        message_ui.info(f"New problem detected: {problems[-1]['title']}")

        # Deleting bad measurement
        delete_measurement(get_selected_measurement_uuid())

        # Check for control events and break if stop_event is set.
        if check_control_events(pause_event, stop_event, message_ui):
            break

        # Update initial_times to avoid detecting the same problem in the next iteration
        previous_problem_times.update(new_problem_times)

        if attempts < max_attempts:
            message_ui.info(f"Retrying sweep... Attempt {attempts + 1}")
        else:
            message_ui.input(
                f"Reached max attempts of {max_attempts}. Do you want to continue trying or abort?"
            )
            return False
