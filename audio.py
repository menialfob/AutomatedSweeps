import vlc
import time
import os

# Initialize VLC instance
vlc_options = "--mmdevice-passthrough=2 --no-video"
# --force-dolby-surround=1
vlc_instance = vlc.Instance()
player = vlc_instance.media_player_new()

def play_sweep(source):
    """Play the audio sweep using VLC."""
    try:
        media = vlc_instance.media_new(source)
        player.set_media(media)
        player.play()
        time.sleep(2)  # Give time for VLC to initialize playback
        if player.get_state() == vlc.State.Error:
            print(
                f"Error: VLC could not play {source}. Check your audio output settings."
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
