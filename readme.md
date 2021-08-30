#### current status:  

August 2021: This project is sitting a bit idle at the moment, since my hopes of compiling it into an app didn't really work out. The code works of course, as it's very simliar to chromicast (based on it), except it outputs to NDI instead of the Virtualcam.  This repo is a bit of a mess, as it contains broken copies of attempts at compiling the code.

For the time being, Vingester.app also has an NDI output, and is available as an application. 

In the future, I'll be potentially adding NDI output to the Raspberry_Ninja project, where I can offer SD card images for a Raspberry Pi, with hardware-acceleration enabled, skipping the need for applications all together. I may add NDI/FFmpeg output to the Electron Capture app at some point as well, but that is very low-priority for me currently.

### NDI.Ninja

It works enough to output a website (include OBS.Ninja streams) into an NDI Video output. It can do this headlessly.

This Code is me tinkering around with ideas; it is unfinished. Audio isn't yet supported.

It is based on the chromicast repo I made. https://github.com/steveseguin/chromicam 

# macOS Build
python3 build chromicast.py pack

# Windows Build
pyinstaller --onefile --hidden-import='pkg_resources.py2_warn' --icon=chromicast.ico chromicast.py

# find the location of CEF on macOS
sudo find / | grep "Chromium Embedded Framework"

