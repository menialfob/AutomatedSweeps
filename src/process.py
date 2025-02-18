from gui_automation import run_sweep
from rew_api import (
    check_new_problems,
    delete_measurement,
    get_selected_measurement_uuid,
)
from utils import get_microphone_distance
import config
from threading import Event
from ui import MessageUI


def run_workflow(notify_ui: MessageUI, pause_event: Event, stop_event: Event):
    total_steps = len(config.measurement_schedule)
    current_step = 0
    successful_step = False
    uuids: dict = {}

    while current_step <= total_steps:
        # If the event is stopped, break the loop
        if stop_event.is_set():
            break

        # If the event is paused, wait for it to be cleared
        if not pause_event.is_set():
            notify_ui.info("Paused inside run_workflow")
            pause_event.wait()

        successful_step = False

        match config.measurement_schedule[current_step]["Description"]:
            case "Check REW settings":
                successful_step = True

            case "Measure distance":
                successful_step = sweep_and_check_problems(
                    config.measurement_schedule[current_step]["Channel"],
                    config.measurement_schedule[current_step]["Iteration"],
                    config.measurement_schedule[current_step]["Position"],
                    config.measurement_schedule[current_step]["Audio played"],
                    notify_ui,
                    pause_event,
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
                    notify_ui.info(
                        f"The microphone is positioned correctly within the error margin of 3 cm. (Distance from center: {abs(fr_fl_distance)} cm)"
                    )
                    successful_step = True
                else:
                    if fr_fl_distance < 0:
                        notify_ui.info(
                            f"Move the microphone {abs(fr_fl_distance)} cm ({round(abs(fr_fl_distance) / 2.54, 2)} in) to the right speaker"
                        )
                    else:
                        notify_ui.info(
                            f"Move the microphone {abs(fr_fl_distance)} cm ({round(abs(fr_fl_distance) / 2.54, 2)} in) to the left speaker"
                        )
                    notify_ui.info(
                        "Press any key to continue after moving the microphone..."
                    )

        if successful_step:
            config.measurement_schedule[current_step]["Status"] = (
                "[green]Completed[/green]"
            )
            notify_ui.update()
            current_step += 1
        else:
            config.measurement_schedule[current_step]["Status"] = (
                "[yellow]Retrying[/yellow]"
            )
            notify_ui.update()


def sweep_and_check_problems(
    channel: str,
    iteration,
    position,
    audio_file,
    notify_ui: MessageUI,
    pause_event: Event,
    max_attempts=3,
):
    """Runs sweep and checks for new problems, retrying up to max_attempts times."""

    # Track initial problem times
    initial_problem_times = set()
    previous_problem_times, _ = check_new_problems(initial_problem_times)

    attempts = 0

    while attempts < max_attempts:
        run_sweep(channel, iteration, position, audio_file, notify_ui, pause_event)
        attempts += 1

        if not pause_event.is_set():
            notify_ui.info("Paused inside sweep_and_check_problems")
            pause_event.wait()

        new_problem_times, problems = check_new_problems(previous_problem_times)

        if not new_problem_times:
            notify_ui.info("No new problems detected. Sweep successful.")
            return True
        notify_ui.info(f"New problem detected: {problems[-1]['title']}")

        # Deleting bad measurement
        delete_measurement(get_selected_measurement_uuid())

        # Update initial_times to avoid detecting the same problem in the next iteration
        previous_problem_times.update(new_problem_times)

        if attempts < max_attempts:
            notify_ui.info(f"Retrying sweep... Attempt {attempts + 1}")
        else:
            notify_ui.info("Max attempts reached. Exiting with problem.")
            return False
