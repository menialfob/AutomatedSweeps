from gui_automation import run_sweep
from rew_api import check_new_problems, delete_measurement, get_selected_measurement


def run_measure(
    channel,
    is_reference,
    iteration,
    position,
    audio_path,
    max_attempts=3,
):
    """Runs sweep and checks for new problems, retrying up to max_attempts times."""

    # Track initial problem times
    initial_problem_times = set()
    previous_problem_times, _ = check_new_problems(initial_problem_times)

    attempts = 0

    while attempts < max_attempts:
        run_sweep(channel, is_reference, iteration, position, audio_path)
        attempts += 1

        new_problem_times, problems = check_new_problems(previous_problem_times)

        if not new_problem_times:
            print("No new problems detected. Sweep successful.")
            return
        print(f"New problem detected: {problems[-1]['title']}")

        # Deleting bad measurement
        delete_measurement(get_selected_measurement())

        # Update initial_times to avoid detecting the same problem in the next iteration
        previous_problem_times.update(new_problem_times)

        if attempts < max_attempts:
            print(f"Retrying sweep... Attempt {attempts + 1}")
        else:
            print("Max attempts reached. Exiting with problem.")
            return


def run_measurements(
    channels, is_reference, num_iterations, position_number, audio_path
):
    """Run the measurement process for selected channels."""
    for channel in channels:
        if is_reference:
            print(f"Creating reference measurement for {channel}")
            iteration_number = 0
            position_number = 0
            run_measure(
                channel, is_reference, iteration_number, position_number, audio_path
            )
        else:
            print(
                f"Measuring {channel} at position {position_number} for {num_iterations} iterations"
            )
            for i in range(1, num_iterations + 1):
                print(f"Iteration {i} of {num_iterations}")
                run_measure(channel, is_reference, i, position_number, audio_path)
    print(f"Completed {len(channels) * num_iterations} measurements.")
