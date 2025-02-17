import os
import time

import vlc
from utils import get_correct_path


def play_sweep(channel):
    """
    Plays an audio sweep using VLC.

    Args:
        source (str): Path or URL of the audio file.
    """

    audio_file_path = get_correct_path(f"{channel}.mlp", "assets/Lossless")
    # if config.lossless_audio:
    #     audio_file_path = get_correct_path(f"{channel}.mlp", "assets/Lossless")
    # else:
    #     audio_file_path = get_correct_path(f"{channel}.mp4", "assets/Lossy")

    # Initialize VLC instance and media player
    global player  # Keep reference to avoid garbage collection
    vlc_instance = vlc.Instance("--quiet")
    player = vlc_instance.media_player_new()

    try:
        # Load media
        media = vlc_instance.media_new(audio_file_path)
        player.set_media(media)

        # Start playback
        player.play()
        time.sleep(1)  # Allow time for VLC to start playing

        # Wait for playback to complete
        while player.get_state() in {
            vlc.State.Opening,
            vlc.State.Buffering,
            vlc.State.Playing,
        }:
            time.sleep(1)

        # Check for errors
        if player.get_state() == vlc.State.Error:
            print(
                f"Error: VLC could not play {audio_file_path}. Check your audio output settings."
            )

    except Exception as e:
        print(f"VLC playback error: {e}")


def get_audio_files():
    """Prompt user for an audio file directory and validate the existence of .mlp files."""
    while True:
        path = input(
            "Enter the path to the lossless audio files (or type 'exit' to quit): "
        )
        if path.lower() == "exit":
            print("Exiting program.")
            return None, None
        if not os.path.isdir(path):
            print("Error: Invalid directory. Please try again.")
            continue
        mlp_files = [f for f in os.listdir(path) if f.endswith(".mlp")]
        if not mlp_files:
            print("Error: No .mlp files found in the directory. Please try again.")
            continue
        print(f"Found {len(mlp_files)} .mlp files in the directory.")
        return path, mlp_files
