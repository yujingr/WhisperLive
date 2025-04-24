@echo off
echo Installing WhisperLive client...
python install_client.py

echo Building executable...
python build_exe.py

echo.
echo If the build was successful, you can find the executable in the 'dist' folder.
echo.
pause 