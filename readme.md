This Code is Experimental and Unfinished. It works enough to output a website (include OBS.Ninja streams) into an NDI Video output

# macOS Build
python3 build_stagecast.py pack
python3 build chromicast.py pack

# Windows Build
pyinstaller --onefile --hidden-import='pkg_resources.py2_warn' --icon=chromicast.ico chromicast.py

# find the location of CEF on macOS
sudo find / | grep "Chromium Embedded Framework"
