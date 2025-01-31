import os,sys
from tkinter import Tk

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

def is_window_maximized():
    if check_os_platform()!="windows": return

    import win32gui,win32con
    hwnd = win32gui.GetForegroundWindow()

    # Получаем информацию о размещении окна
    placement = win32gui.GetWindowPlacement(hwnd)

    # placement[1] содержит состояние окна
    return placement[1] == win32con.SW_MAXIMIZE

def typeof(your_var):
    if (isinstance(your_var, int)):
        return 'int'
    elif (isinstance(your_var, float)):
        return 'float'
    elif (isinstance(your_var, list)) or (isinstance(your_var, tuple)):
        return 'list'
    elif (isinstance(your_var, dict)):
        return 'dict'
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

def parse_parameters(input_string):
    # рекурсивно обрабатывает строку со вложенным списком и возвращает в виде вложенного массива
    result, current_param, depth = [], "", 0
    for char in input_string:
        if char == ',' and depth == 0:
            current_param = current_param.strip()
            if current_param: result.append(current_param.strip())
            current_param = ""
        else:
            current_param += char
            if char == '(':
                depth += 1
            elif char == ')':
                depth -= 1
    current_param = current_param.strip()
    if current_param: result.append(current_param.strip())

    # Обработка вложенных параметров
    def parse_nested(params):
        parsed = []
        for param in params:
            if param.startswith('(') and param.endswith(')'):
                inner_params = parse_parameters(param[1:-1])  # Убираем внешние скобки
                parsed.append(inner_params)
            else:
                parsed.append(param)
        return parsed

    return parse_nested(result)

def parse_cycle(param_mas, depth = 1):
    # рекурсивно обрабатывает массив, и разворачивает конструкции вида (1,2,3),Х
    while True:
        nn, res_mas = 0, []
        while nn<len(param_mas):
            par1=param_mas[nn]
            if typeof(par1)=="list":
                param_mas[nn] = par1 = parse_cycle(par1, depth+1)
                if nn+1<=len(param_mas)-1:
                    par2 = param_mas[nn+1]
                    if typeof(par1)=="list" and is_number(par2) and depth>1:
                        count, par0 = int(par2), []
                        for _ in range(count):
                            par0.extend(par1)
                        res_mas.extend(par0)
                        nn += 2
                        continue
            res_mas.append(par1)
            nn += 1
        if len(param_mas) == len(res_mas): break
        param_mas = res_mas

    return res_mas

def parse_list(param_mas):
    # рекурсивно обрабатывает массив, и разворачивает конструкции вида 1..10
    nn, res_mas = 0, []
    while nn<len(param_mas):
        par=param_mas[nn]
        if typeof(par)=="list":
            param_mas[nn] = par = parse_list(par)
        elif typeof(par) == "str":
            pos = par.find("..")
            if pos >= 0:
                par_str = par
                str1, str2, str_ = par_str[:pos], par_str[pos + 2:], ""
                res_mas.append(str1)
                str_ = int(str1)
                while str(str_) != str2:
                    str_ += 1
                    res_mas.append(str(str_))
                nn += 1
                continue
        res_mas.append(par)
        nn += 1

    return res_mas
