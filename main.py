from rew_api import ensure_rew_api, ensure_rew_settings, get_selected_measurement, delete_measurement, check_new_problems
from gui_automation import run_sweep
from audio import get_audio_files
from utils import save_settings, load_settings, get_audio_channels


def run_measure(
    channel,
    is_reference,
    iteration,
    position,
    audio_path,
    max_attempts=3,
):
    """Runs MeasureSweep() and checks for new problems, retrying up to max_attempts times."""

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
        delete_measurement(
            get_selected_measurement()
        )

        # Update initial_times to avoid detecting the same problem in the next iteration
        previous_problem_times.update(new_problem_times)

        if attempts < max_attempts:
            print(f"Retrying sweep... Attempt {attempts + 1}")
        else:
            print("Max attempts reached. Exiting with problem.")
            return


def setup():
    """Handle setup process for loading settings and selecting audio files."""
    settings = load_settings()
    audio_path = None
    selected_channels = None

    if settings:
        use_saved = input("Saved settings found. Load them? (y/n): ").strip().lower()
        if use_saved in ("y", "yes"):
            print("Loaded saved settings.")
            audio_path = settings["audio_path"]
            selected_channels = sorted(set(settings["channels"]))

    if not audio_path or not selected_channels:
        audio_path, mlp_files = get_audio_files()
        if audio_path and mlp_files:
            selected_channels = get_audio_channels(mlp_files)
            save_choice = (
                input("Save these settings for future use? (y/n): ").strip().lower()
            )
            if save_choice in ("y", "yes"):
                save_settings(audio_path, selected_channels)

    if audio_path and selected_channels:
        print("Processing files in:", audio_path)
        print("Measuring channels:", selected_channels)

        is_reference = input(
            "Are you measuring the Main Listening Position (MLP)? (y/n): "
        ).strip().lower() in ("y", "yes")
        position_number = (
            0
            if is_reference
            else int(input("Enter the position number (starting from 0): "))
        )
        num_iterations = (
            1 if is_reference else int(input("How many measurements per position?: "))
        )

    return audio_path, selected_channels, is_reference, num_iterations, position_number


def run_measurements(channels, is_reference, num_iterations, position_number, audio_path):
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
                run_measure(
                    channel,
                    is_reference,
                    i,
                    position_number,
                    audio_path
                )
    print(f"Completed {len(channels) * num_iterations} measurements.")

def main():
    print("Starting measurement script")
    if not ensure_rew_api():
        print("ERROR: REW API is not running. Exiting")
        return
    # Checking for errors in setup
    errors = ensure_rew_settings()
    if errors:
        print("Errors detected in REW settings:")
        for error in errors:
            print(error)
        return
    
    # Setup and run
    audio_path, selected_channels, is_reference, num_iterations, position_number = (
        setup()
    )
    if selected_channels:
        run_measurements(
            selected_channels, is_reference, num_iterations, position_number, audio_path
        )


if __name__ == "__main__":
    main()
