from PyInstaller.utils.hooks import get_package_paths
import subprocess

subprocess.Popen([
      "pyinstaller", "--clean", "-F", "src/stagecast.py",
      "--onefile",
      "--icon","stagecast.ico",
      "--add-data", f"{get_package_paths('cefpython3')[1]}:cefpython3",
      "--hidden-import", "pkg_resources.py2_warn", "-n", "Stagecast"
])
