import os
import sys
import subprocess


def build_executable():
    """Build standalone executable using PyInstaller"""
    print("Building WhisperLive GUI executable...")

    # PyInstaller command
    pyinstaller_cmd = [
        "python -m pyinstaller",
        "--name=WhisperLiveGUI",
        "--onefile",  # Create a single executable file
        "--windowed",  # Don't open console window when app starts
        "--add-data=README.md;.",  # Include README file
        "--icon=NONE",  # No icon for now
        "whisper_live_gui.py"
    ]

    # Run PyInstaller
    try:
        subprocess.run(pyinstaller_cmd, check=True)
        print("\nBuild completed successfully!")
        print(
            f"Executable is located at: {os.path.join('dist', 'WhisperLiveGUI.exe')}")
    except subprocess.CalledProcessError as e:
        print(f"Error building executable: {e}")
        sys.exit(1)


if __name__ == "__main__":
    build_executable()
