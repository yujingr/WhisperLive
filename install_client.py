import subprocess
import sys
import os


def install_client():
    """Install the client-only portion of whisper-live"""
    print("Installing WhisperLive client...")

    # First install the requirements
    subprocess.check_call([sys.executable, "-m", "pip",
                          "install", "-r", "requirements.txt"])

    # Install whisper-live client only
    subprocess.check_call([
        sys.executable, "-m", "pip", "install",
        "--no-deps",  # Don't install dependencies
        "whisper-live"
    ])

    # Install needed client dependencies individually
    client_deps = [
        "PyAudio",
        "av",
        "scipy",
        "websocket-client"
    ]

    for dep in client_deps:
        subprocess.check_call([sys.executable, "-m", "pip", "install", dep])

    print("\nWhisperLive client successfully installed!")
    print("You can now run the GUI with: python whisper_live_gui.py")
    print("Or build the executable with: python build_exe.py")


if __name__ == "__main__":
    install_client()
