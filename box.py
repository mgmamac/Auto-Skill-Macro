import ctypes
from ctypes import wintypes
import time
from random import randrange
import pystray
from PIL import Image, ImageDraw
import threading
from pynput.keyboard import Key, Listener
import pyautogui
from PIL import Image
import numpy as np

boxActive = False
buffActive = False
autoRun = True
boxInterval = 0
buffInterval = 0

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
    ReleaseKey(0x09)
    ReleaseKey(0xA4)
    time.sleep(0.5)
    
def ss():
    # Take a screenshot of the entire screen
    screenshot = pyautogui.screenshot()

    # Save the screenshot to a file
    screenshot.save("ss.png")
    
def downscale(input_path, output_path, new_width):
    """
    Downscales an image using Pillow, maintaining aspect ratio.

    Args:
        input_path (str): Path to the input image.
        output_path (str): Path to save the downscaled image.
        new_width (int): Desired width for the downscaled image.
    """
    try:
        img = Image.open(input_path)
        original_width, original_height = img.size
        
        # Calculate new height to maintain aspect ratio
        aspect_ratio = original_height / original_width
        new_height = int(new_width * aspect_ratio)

        # Resize the image
        downscaled_img = img.resize((new_width, new_height), Image.LANCZOS)
        downscaled_img.save(output_path)
        #print(f"Image downscaled and saved to {output_path}")
    except FileNotFoundError:
        pass
        #print(f"Error: Input file not found at {input_path}")
    except Exception as e:
        pass
        #print(f"An error occurred: {e}")

def crop(training = False):
    # Open the image
    img = Image.open("ds.png")

    # Define the cropping box (left, upper, right, lower)
    # These coordinates define the rectangular region to keep.
    crop_box = (466, 260, 476, 270) 

    # Crop the image
    cropped_img = img.crop(crop_box)
    
    # Grayscale
    cropped_img = cropped_img.convert("L")

    # Save the cropped image
    if(training == True):
        cropped_img.save("ref.png")
    else:
        cropped_img.save("crop.png")
    
def is_box_active():
    img1 = np.array(Image.open('ref.png'))
    img2 = np.array(Image.open('crop.png'))
    
    sim = calculate_similarity(img1, img2)
    
    if sim >= 70:
        #print("Lucky Box!")
        return True
    else:
        #print("Not Lucky Box!")
        return False
        
def grayscale():
    image = Image.open("lucky.png")
    grayscale_image = image.convert("L")
    grayscale_image.save("gslucky.png")
    
def calculate_similarity(arr1, arr2):
    number_of_equal_elements = np.sum(arr1==arr2)
    total_elements = np.multiply(*arr1.shape)
    percentage = (number_of_equal_elements/total_elements) * 100
    return percentage
    
def train():
    ss()
    downscale("ss.png", "ds.png", 480)
    crop(True)
    
def check_box():
    global boxActive
    ss()
    downscale("ss.png", "ds.png", 480)
    crop()
    
    if(is_box_active()):
        boxActive = True
        
        boxCountdown = threading.Thread(target = box_timer, daemon = True)
        boxCountdown.start()

def box_timer():
    global boxInterval
    global boxActive
    #print("Timer starts!")
    time.sleep(60*boxInterval)
    boxActive = False
    #print("Box expired!")
    
def buff_timer():
    global buffInterval
    global buffActive
    #print("Timer starts!")
    time.sleep(60*buffInterval)
    buffActive = False
    #print("Box expired!")

def auto():
    global autoRun
    global boxActive
    global buffActive
    lootCounter = 0
    
    while(autoRun):
        if not buffActive:
            Press(0x71)
            Press(0x38)
            Press(0x39)
            Press(0x30)
            Press(0x70)
            
            buffActive = True
            buffCountdown = threading.Thread(target = buff_timer, daemon = True)
            buffCountdown.start()

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
            
        lootCounter+=1

        if(lootCounter == 10):
            if(not boxActive):
                time.sleep(2)
                for i in range(3):
                    if(not boxActive):
                        Press(0x20)
                        time.sleep(0.5)
                        check_box()
            lootCounter = 0
        
        # you can change 0x30 to any key you want. For more info look at :
        # msdn.microsoft.com/en-us/library/dd375731
        
def read_boxInterval():
    global boxInterval
    f = open("boxInterval.txt")
    boxInterval = float(f.read())
    
def read_buffInterval():
    global buffInterval
    f = open("buffInterval.txt")
    buffInterval = float(f.read())

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
    global boxActive
    global buffActive
    
    if key == Key.f7:
        if(autoRun == False):
            autoRun = True
            t = threading.Thread(target = auto, daemon = True)
            t.start()
        else:
            autoRun = False
            boxActive = False
            buffActive = False
        time.sleep(2)
        
    if key == Key.f8:
        train()

read_boxInterval()
read_buffInterval()
listener = Listener(on_release=on_release, daemon = True)
listener.start()

# Run the icon
icon.run()