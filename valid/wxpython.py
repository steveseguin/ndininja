# python3 chromicam.py https://obs.ninja/?view=xxxxx 1280 720
import os
import sys
import numpy as np
import time
import threading
import NDIlib as ndi

from cefpython3 import cefpython as cef


import tkinter as tk

global URL
root= tk.Tk()
URL = "https://google.com"

VIEWPORT_SIZE = (1280, 720)
FRAMERATE = 30

def retrieve_input():
    global URL
    URL="https://s10.watch/"+textBox.get("1.0","end-1c")
    root.destroy()

textBox=tk.Text(root, height=1, width=50)
textBox.insert(tk.INSERT, "Paste the stream-token here then press Start", "a")
textBox.pack()
buttonCommit=tk.Button(root, height=1, width=20, text="Start", 
                    command=lambda: retrieve_input())
#command=lambda: retrieve_input() >>> just means do this when i press the button
buttonCommit.pack()

tk.mainloop()



def hello ():  

    global t, run_event, camera_ready
    print("EXITING");
    run_event.clear()
    cef.QuitMessageLoop()
    camera_ready.set()
    t.join()
    
    browser.CloseBrowser()
    cef.Shutdown()
    ndi.send_destroy(ndi_send)
    ndi.destroy()

def exit_button():
    root= tk.Tk()
    canvas1 = tk.Canvas(root, width = 200, height = 100, bg='grey')
    canvas1.pack()
    button1 = tk.Button(text='Quit',command=hello, bg='blue',fg='white')
    canvas1.create_window(100, 50, window=button1)
    root.mainloop()


    

t2 = threading.Thread(target=exit_button)
t2.start()



def command_line_arguments():
    if len(sys.argv) > 1:
        url = sys.argv[1]
        if url.startswith("http://") or url.startswith("https://"):
            global URL
            URL = url
        else:
            print("Error: Invalid url argument")
            sys.exit(1)
    if len(sys.argv) > 3:
        width = int(sys.argv[2])
        height = int(sys.argv[3])
        if width > 0 and height > 0:
            global VIEWPORT_SIZE
            VIEWPORT_SIZE = (width, height)
        else:
            print("Error: Invalid width and height")
            sys.exit(1)
    if len(sys.argv) > 4:
        global FRAMERATE
        FRAMERATE = int(sys.argv[4])
        
   

class LoadHandler(object):
    def OnLoadingStateChange(self, browser, is_loading, **_):
        pass

def drawFrame(browser, run_event, camera_ready):
    time.sleep(2)
    
    if not ndi.initialize():
            return 0
            
    send_settings = ndi.SendCreate()
    send_settings.ndi_name = "StageCast"

    ndi_send = ndi.send_create(send_settings)

    video_frame = ndi.VideoFrameV2()

    #video_frame.data = img
    video_frame.FourCC = ndi.FOURCC_VIDEO_TYPE_RGBA

    
    print("Starting Draw Routine..")
    while run_event.is_set():
        
        camera_ready.wait()
        buffer_string = browser.GetUserData("OnPaint.buffer_string")
        if (buffer_string):
            
            img = np.frombuffer(buffer_string, dtype=np.uint8, count=(VIEWPORT_SIZE[0]*VIEWPORT_SIZE[1]*4)).reshape((VIEWPORT_SIZE[1],VIEWPORT_SIZE[0],4))
            video_frame.data = img
            ndi.send_send_video_v2(ndi_send, video_frame)
            
            camera_ready.clear()
            #cam.sleep_until_next_frame()

class RenderHandler(object):
    def __init__(self):
        print('Starting to Render Frames')
        pass

    def GetViewRect(self, rect_out, **_):
        rect_out.extend([0, 0, VIEWPORT_SIZE[0], VIEWPORT_SIZE[1]])
        return True

    def OnPaint(self, browser, element_type, paint_buffer, **_):
        global camera_ready
        if element_type == cef.PET_VIEW:
            buffer_string = paint_buffer.GetString(mode="rgba", origin="top-left")
            browser.SetUserData("OnPaint.buffer_string", buffer_string)
            camera_ready.set();
        
global t,run_event, camera_ready

def endProgram(exctype, value, tb):
    global t, run_event, camera_ready
    print("EXITING");
    run_event.clear()
    camera_ready.set()
    t.join()
    cef.QuitMessageLoop()
    browser.CloseBrowser()
    cef.Shutdown()
    
    ndi.send_destroy(ndi_send)
    ndi.destroy()

    
    try:
        sys.exit(0)
    except SystemExit:
        os._exit(0)

try:
    sys.excepthook = endProgram  # To shutdown all CEF processes on error
   
    command_line_arguments()
    settings = {
        "windowless_rendering_enabled": True,
    }

    switches = {
        "disable-gpu": "",
        "disable-gpu-compositing": "",
        "enable-media-stream": "",
        "autoplay-policy":"no-user-gesture-required",
        "enable-begin-frame-scheduling": "",
        "disable-surfaces": "",  # This is required for PDF ext to work
    }
    browser_settings = {
        "windowless_frame_rate": 30,  # Default frame rate in CEF is 30
    }
    cef.Initialize(settings=settings, switches=switches)

    parent_window_handle = 0
    window_info = cef.WindowInfo()
    window_info.SetAsOffscreen(parent_window_handle)
    
    camera_ready = threading.Event()
    camera_ready.set()
    
    browser = cef.CreateBrowserSync(window_info=window_info, settings=browser_settings, url=URL)
    browser.SetClientHandler(RenderHandler())
    
    browser.SendFocusEvent(True)
    browser.WasResized()
    browser.SetClientHandler(LoadHandler())
    
    run_event = threading.Event()
    run_event.set()
    
    t = threading.Thread(target=drawFrame, args=(browser,run_event,camera_ready,))
    t.start()
    cef.MessageLoop()
    run_event.clear()
    camera_ready.set()
    
    t.join()
    
    cef.QuitMessageLoop()
    browser.CloseBrowser()
    cef.Shutdown()
   
except:
    print('Interrupted')
    run_event.clear()
    t.join()
    
    cef.QuitMessageLoop()
    browser.CloseBrowser()
    cef.Shutdown()
    try:
        sys.exit(0)
    except SystemExit:
        os._exit(0)
