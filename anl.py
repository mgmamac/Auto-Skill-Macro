import ctypes
from ctypes import wintypes
import time
from random import randrange
import pystray
from PIL import Image, ImageDraw
import threading
from pynput.keyboard import Key, Listener

user32 = ctypes.WinDLL('user32', use_last_error=True)
INPUT_KEYBOARD = 1
KEYEVENTF_EXTENDEDKEY = 0x0001
KEYEVENTF_KEYUP       = 0x0002
KEYEVENTF_UNICODE     = 0x0004
MAPVK_VK_TO_VSC = 0
# msdn.microsoft.com/en-us/library/dd375731
wintypes.ULONG_PTR = wintypes.WPARAM
class MOUSEINPUT(ctypes.Structure):
    _fields_ = (("dx",          wintypes.LONG),
                ("dy",          wintypes.LONG),
                ("mouseData",   wintypes.DWORD),
                ("dwFlags",     wintypes.DWORD),
                ("time",        wintypes.DWORD),
                ("dwExtraInfo", wintypes.ULONG_PTR))
class KEYBDINPUT(ctypes.Structure):
    _fields_ = (("wVk",         wintypes.WORD),
                ("wScan",       wintypes.WORD),
                ("dwFlags",     wintypes.DWORD),
                ("time",        wintypes.DWORD),
                ("dwExtraInfo", wintypes.ULONG_PTR))
    def __init__(self, *args, **kwds):
        super(KEYBDINPUT, self).__init__(*args, **kwds)
        if not self.dwFlags & KEYEVENTF_UNICODE:
            self.wScan = user32.MapVirtualKeyExW(self.wVk,
                                                 MAPVK_VK_TO_VSC, 0)
class HARDWAREINPUT(ctypes.Structure):
    _fields_ = (("uMsg",    wintypes.DWORD),
                ("wParamL", wintypes.WORD),
                ("wParamH", wintypes.WORD))
class INPUT(ctypes.Structure):
    class _INPUT(ctypes.Union):
        _fields_ = (("ki", KEYBDINPUT),
                    ("mi", MOUSEINPUT),
                    ("hi", HARDWAREINPUT))
    _anonymous_ = ("_input",)
    _fields_ = (("type",   wintypes.DWORD),
                ("_input", _INPUT))
LPINPUT = ctypes.POINTER(INPUT)
def PressKey(hexKeyCode):
    x = INPUT(type=INPUT_KEYBOARD,
              ki=KEYBDINPUT(wVk=hexKeyCode))
    user32.SendInput(1, ctypes.byref(x), ctypes.sizeof(x))
def ReleaseKey(hexKeyCode):
    x = INPUT(type=INPUT_KEYBOARD,
              ki=KEYBDINPUT(wVk=hexKeyCode,
                            dwFlags=KEYEVENTF_KEYUP))
    user32.SendInput(1, ctypes.byref(x), ctypes.sizeof(x))

def Press(hexKeyCode):
    PressKey(hexKeyCode)
    time.sleep(randrange(5,10)/100)
    ReleaseKey(hexKeyCode)
    time.sleep(randrange(5,10)/100)

def AltTab():
    PressKey(0xA4)
    time.sleep(randrange(5,10)/100)
    PressKey(0x09)
    time.sleep(randrange(5,10)/100)
    ReleaseKey(0xA4)
    ReleaseKey(0x09)

autoRun = True

def auto():
    global autoRun
    while(autoRun):
        Press(0x31)
        Press(0x32)
        Press(0x33)
        Press(0x34)
        Press(0x35)
        Press(0x36)
        Press(0x37)
        Press(0x38)
        Press(0x39)
        Press(0x30)

        #for i in range(5):
        #    Press(0x20)
        
        # you can change 0x30 to any key you want. For more info look at :
        # msdn.microsoft.com/en-us/library/dd375731

# Create a simple image for the icon
def create_image(width, height, color1, color2):
    image = Image.new('RGB', (width, height), color1)
    dc = ImageDraw.Draw(image)
    dc.rectangle((width // 2, 0, width, height // 2), fill=color2)
    dc.rectangle((0, height // 2, width // 2, height), fill=color2)
    return image

# Define menu actions
def on_pause(icon, item):
    global autoRun
    if(autoRun == False):
        autoRun = True
        t = threading.Thread(target = auto, daemon = True)
        t.start()
    else:
        autoRun = False

def on_quit(icon, item):
    global autoRun
    autoRun = False
    icon.stop()

# Create the icon
icon = pystray.Icon(
    'my_app',
    icon=create_image(64, 64, 'blue', 'white'),
    menu=pystray.Menu(
        pystray.MenuItem('Resume/Pause', on_pause),
        pystray.MenuItem('Quit', on_quit)
    )
)

def on_release(key):
    global autoRun
    if key == Key.f7:
        if(autoRun == False):
            autoRun = True
            t = threading.Thread(target = auto, daemon = True)
            t.start()
        else:
            autoRun = False
        time.sleep(2)


listener = Listener(on_release=on_release, daemon = True)
listener.start()

# Run the icon
icon.run()