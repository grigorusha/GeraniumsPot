import pygame

from tkinter import Tk
import os,sys

from math import pi, sqrt, cos, sin, tan, acos, asin, atan, atan2, exp, pow, radians, degrees, hypot
from calc import mas_pos,calc_spline

def check_os_platform():
    import platform
    return platform.system().lower()

def check_linux_wine():
    if check_os_platform()!="windows":
        return False

    import winreg
    fl_wine1 = fl_wine2 = False
    aReg = winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE)
    try:
        aKey = winreg.OpenKey(aReg, r'SOFTWARE\Wine')
        fl_wine1 = True
    except: pass
    aReg = winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER)
    try:
        aKey = winreg.OpenKey(aReg, r'SOFTWARE\Wine')
        fl_wine2 = True
    except: pass
    return (fl_wine1 or fl_wine2)

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

def draw_smooth_gear(screen, color, cir_x, cir_y, radius, teeth):
    def draw_arc(screen, color, center, start, end, radius):
        angle_start = degrees(atan2(start[1] - center[1], start[0] - center[0]))
        angle_end = degrees(atan2(end[1] - center[1], end[0] - center[0]))
        if angle_end < angle_start:
            angle_end += 360
        pygame.draw.arc(screen, color, (center[0] - radius, center[1] - radius, radius * 2, radius * 2), radians(angle_start), radians(angle_end), 2)

    for i in range(teeth):
        angle0 = (i-1) * 2*pi / teeth
        angle1 = i * 2*pi / teeth
        angle2 = (i+1) * 2*pi / teeth
        x0 = int(cir_x + radius * cos(angle0))
        y0 = int(cir_y + radius * sin(angle0))
        x1 = int(cir_x + radius * cos(angle1))
        y1 = int(cir_y + radius * sin(angle1))
        x2 = int(cir_x + radius * cos(angle2))
        y2 = int(cir_y + radius * sin(angle2))
        draw_arc(screen, color, (x1,y1), (x0,y0), (x2,y2), radius)
        # pygame.draw.circle(screen, color, (x_i, y_i), 3, 2)

def draw_smoth_polygon(surface, color, polygon, width):
    # рисуем плавную кривую с пиксельным сглаживанием
    # заменяем pygame.draw.polygon - тк там грубая пиксельная ступенька
    for nn, p1 in enumerate(polygon):
        p2 = mas_pos(polygon, nn + 1)

        # delta vector
        d = (p2[0] - p1[0], p2[1] - p1[1])
        # distance between the points
        dis = hypot(*d)
        # scaled perpendicular vector (vector from p1 & p2 to the polygon's points)
        if dis != 0:
            sp = (-d[1] * width / (2 * dis), d[0] * width / (2 * dis))
        else:
            sp = (0,0)

        # points
        p1_1 = (p1[0] - sp[0], p1[1] - sp[1])
        p1_2 = (p1[0] + sp[0], p1[1] + sp[1])
        p2_1 = (p2[0] - sp[0], p2[1] - sp[1])
        p2_2 = (p2[0] + sp[0], p2[1] + sp[1])

        # draw two line
        pygame.draw.aaline(surface, color, p1_1, p1_2, 1)
        pygame.draw.aaline(surface, color, p2_1, p2_2, 1)

def keyboard_press(key):
    if check_os_platform()!="windows": return

    import keyboard
    keyboard.press_and_release(key)  # странный трюк, чтобы вернуть фокус после сплаш скрина

def send_to_clipboard(screenshot):
    if check_os_platform()!="windows": return

    from io import BytesIO
    from PIL import Image
    import winclip32

    image = Image.open(screenshot)
    output = BytesIO()
    image.convert("RGB").save(output, "BMP")
    data = output.getvalue()[14:]
    output.close()
    winclip32.set_clipboard_data(winclip32.BITMAPINFO_STD_STRUCTURE, data)

def window_front(win_caption):
    if check_os_platform()!="windows": return

    import win32gui
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

def find_photo(puzzle_name, PHOTO):
    photo_screen, photo_path = "", ""
    dir = os.path.join(os.path.abspath(os.curdir),"Photo")
    if os.path.isdir(dir):
        for root, dirs, files in os.walk(dir):
            for fil in files:
                if (fil.lower() == puzzle_name.lower() + ".jpg") or (fil.lower() == puzzle_name.lower() + ".jpeg") or (fil.lower() == puzzle_name.lower() + ".png"):
                    photo_path = os.path.join(root,fil)
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

def close_spalsh_screen():
    if check_os_platform() != "windows": return

    try:  # pyinstaller spalsh screen
        import pyi_splash
        pyi_splash.close()
    except:
        pass

def purge_dir(parent, ext_str):
    # удалить файлы в папке
    ext_mas = ext_str.split(",")
    for ext in ext_mas:
        for root, dirs, files in os.walk(parent):
            for item in files:
                # Delete subordinate files
                filespec = os.path.join(root, item)
                if filespec.endswith('.'+ext) or (item.lower()=="thumbs.db"):
                    try:
                        os.remove(filespec)
                    except: pass
            for item in dirs:
                # Recursively perform this operation for subordinate directories
                purge_dir(os.path.join(root, item), ext)
                try:
                    os.rmdir(os.path.join(root, item))
                except: pass

def arg_param_check():
    fl_reset_ini, fl_test, fl_test_photo, fl_test_scramble = False, False, False, 0
    for param in os.environ:
        param = param.lower()
        if param.find("geraniumreset")>=0:
            fl_reset_ini,fl_test = True,False
            break
        if param.find("geraniumtest")>=0: fl_test = True
        if fl_test:
            if param.find("photo")>=0: fl_test_photo = True
            if param.find("scramble")>=0:
                fl_test_scramble = os.environ[param.upper()]
                count = int(fl_test_scramble) if is_number(fl_test_scramble) else 1
                fl_test_scramble = count

    dir_garden, dir_screenshots = "", ""
    arg_param = sys.argv[1:]
    if len(arg_param)>0:
        param = arg_param[0].lower()
        if param=="reset":
            fl_reset_ini = True
        elif param[:4]=="test":
            fl_test = True
        if fl_test:
            if param.find("photo")>=0: fl_test_photo = True
            if param.find("scramble")>=0:
                pos = param.find("scramble")+8
                count = param[pos:]
                count = int(count) if is_number(count) else 1
                fl_test_scramble = count
    if len(arg_param)>1:
        dir_garden = arg_param[1]
    if len(arg_param)>2:
        dir_screenshots = arg_param[2]
    if fl_test_scramble==1: fl_test = True

    return fl_reset_ini, fl_test, fl_test_photo, fl_test_scramble, dir_garden, dir_screenshots