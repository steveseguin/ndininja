"""Run both entry points with real threads and stubbed CEF/NDI dependencies."""

import pathlib
import subprocess
import sys
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
HARNESS = r'''
import pathlib
import runpy
import sys
import threading
import types
from unittest.mock import patch

path, mode = sys.argv[1:]
waiting_for_next_frame = threading.Event()
cleanup = []

class FrameEvent:
    def __init__(self):
        self.event = threading.Event()

    def set(self):
        self.event.set()

    def clear(self):
        self.event.clear()

    def is_set(self):
        return self.event.is_set()

    def wait(self):
        if not self.event.is_set():
            waiting_for_next_frame.set()
        return self.event.wait()

class Image:
    def reshape(self, shape):
        return self

class Browser:
    def GetUserData(self, name):
        return b'frame'

    def SetClientHandler(self, handler):
        pass

    def SendFocusEvent(self, value):
        pass

    def WasResized(self):
        pass

    def CloseBrowser(self):
        cleanup.append('close-browser')

class WindowInfo:
    def SetAsOffscreen(self, handle):
        pass

def message_loop():
    assert waiting_for_next_frame.wait(3), 'Worker did not wait for a second paint'
    if mode == 'interrupt':
        raise KeyboardInterrupt
    if mode == 'error':
        raise RuntimeError('CEF message-loop error')

cef = types.SimpleNamespace(
    Initialize=lambda **kwargs: None,
    WindowInfo=WindowInfo,
    CreateBrowserSync=lambda **kwargs: Browser(),
    MessageLoop=message_loop,
    QuitMessageLoop=lambda: cleanup.append('quit-loop'),
    Shutdown=lambda: cleanup.append('shutdown'),
)
ndi = types.SimpleNamespace(
    initialize=lambda: True,
    SendCreate=types.SimpleNamespace,
    send_create=lambda settings: object(),
    VideoFrameV2=types.SimpleNamespace,
    FOURCC_VIDEO_TYPE_RGBA=0,
    send_send_video_v2=lambda sender, frame: None,
)
modules = {
    'cefpython3': types.SimpleNamespace(cefpython=cef),
    'NDIlib': ndi,
    'numpy': types.SimpleNamespace(uint8=0, frombuffer=lambda *args, **kwargs: Image()),
    'threading': types.SimpleNamespace(Event=FrameEvent, Thread=threading.Thread),
    'time': types.SimpleNamespace(sleep=lambda seconds: None),
}

class ExitRequested(BaseException):
    pass

def intercepted_exit(code):
    assert code == 0
    raise ExitRequested

original_hook = sys.excepthook
try:
    with patch.dict(sys.modules, modules), patch.object(sys, 'argv', [path]), \
         patch('os._exit', intercepted_exit):
        try:
            runpy.run_path(path, run_name='__main__')
        except ExitRequested:
            assert mode != 'normal', 'Normal return unexpectedly forced process exit'
finally:
    sys.excepthook = original_hook

assert cleanup == ['quit-loop', 'close-browser', 'shutdown'], cleanup
assert threading.active_count() == 1, 'Draw thread survived shutdown'
print('cleanup complete')
'''


class InterruptedShutdownTests(unittest.TestCase):
    def run_entrypoint(self, filename, mode):
        result = subprocess.run(
            [sys.executable, '-c', HARNESS, str(ROOT / filename), mode],
            capture_output=True,
            text=True,
            timeout=5,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn('cleanup complete', result.stdout)

    def test_root_keyboard_interrupt(self):
        self.run_entrypoint('chromicast.py', 'interrupt')

    def test_packaged_keyboard_interrupt(self):
        self.run_entrypoint('src/chromicast.py', 'interrupt')

    def test_root_message_loop_error(self):
        self.run_entrypoint('chromicast.py', 'error')

    def test_packaged_message_loop_error(self):
        self.run_entrypoint('src/chromicast.py', 'error')

    def test_root_normal_return(self):
        self.run_entrypoint('chromicast.py', 'normal')

    def test_packaged_normal_return(self):
        self.run_entrypoint('src/chromicast.py', 'normal')


if __name__ == '__main__':
    unittest.main()
