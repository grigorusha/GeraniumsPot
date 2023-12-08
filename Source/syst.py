import win32gui
from tkinter import Tk
import os

import pygame

def window_front(win_caption):
    def windowEnumerationHandler(hwnd, windows):
        windows.append((hwnd, win32gui.GetWindowText(hwnd)))

    windows = []
    win32gui.EnumWindows(windowEnumerationHandler, windows)
    # hwnd = win32gui.GetForegroundWindow()

    for w in windows:
        if w[1] == win_caption:
            win32gui.ShowWindow(w[0], 5)
            try:
                win32gui.SetForegroundWindow(w[0])
            except:
                pass
            Tk().withdraw()
            break

def typeof(your_var):
    if (isinstance(your_var, int)):
        return 'int'
    elif (isinstance(your_var, float)):
        return 'float'
    elif (isinstance(your_var, list)) or (isinstance(your_var, tuple)):
        return 'list'
    elif (isinstance(your_var, bool)):
        return 'bool'
    elif (isinstance(your_var, str)):
        return 'str'
    else:
        return "type is unknown"

def is_number(s):
    if typeof(s)!= "str": return False
    try:
        float(s) # for int, long and float
    except ValueError:
        try:
            complex(s) # for complex
        except ValueError:
            return False
    return True

def calc_param(elem, param_calc):
    if typeof(elem)!="list":
        elem = [elem]

    for nn,ev in enumerate(elem):
        for param in param_calc:
            if param[0] == ev:
                ev = param[1]
                break
            if ev.find(param[0]) >= 0:
                ev = ev.replace(param[0], str(param[1]))
        try:
            elem[nn] = eval(ev)
        except:
            elem[nn] = float(ev)
    if len(elem)==1:
        elem = elem[0]

    return elem

def find_photo(puzzle_name, PHOTO):
    photo_screen, photo_path = "", ""
    dir = os.path.abspath(os.curdir) + "\\Photo"
    if os.path.isdir(dir):
        for root, dirs, files in os.walk(dir):
            for fil in files:
                if (fil.lower() == puzzle_name.lower() + ".jpg") or (fil.lower() == puzzle_name.lower() + ".png"):
                    photo_path = root + "\\" + fil
                    break
            if photo_path != "": break
        if os.path.isfile(photo_path):
            photo_screen = pygame.image.load(photo_path)
            photo_rect = (photo_screen.get_rect().width, photo_screen.get_rect().height)
            if photo_rect[0] / photo_rect[1] <= PHOTO[0] / PHOTO[1]:
                scale_ko = PHOTO[1] / photo_rect[1]
                new_width = int(scale_ko * photo_rect[0])
                PHOTO = (new_width, PHOTO[1])
            else:
                scale_ko = PHOTO[0] / photo_rect[0]
                new_height = int(scale_ko * photo_rect[1])
                PHOTO = (PHOTO[0], new_height)

            photo_screen = pygame.transform.scale(photo_screen, PHOTO)
    return photo_screen, PHOTO
