from part import *
from syst import *

from pygame import *

import os,webbrowser
from tkinter import filedialog as fd
from tkinter import messagebox as mb

def mouse_move_click(mouse_xx, mouse_yy, mouse_x, mouse_y, mouse_left, mouse_right, puzzle_rings, ring_num, ring_select, direction, puzzle_parts, show_hidden_circles):
    # обработка перемещения и нажатия в игровом поле
    # mouse_xx, mouse_yy - координаты мышки при перемещении. mouse_x, mouse_y - координаты точки клика
    # ring_select - координаты кольца над которым двигается курсор. ring_num - кольцо внутри которого был клик

    circle_area = 3  #  ширина линии круга в пикселях, для проверки касание мышкой

    ring_pos = []
    for ring in puzzle_rings:
        if ring[6]!= 0: continue
        pos = check_circle(ring[1], ring[2], mouse_xx, mouse_yy, ring[3], 2)
        # проверка попадает ли точка внутрь окружности, лежит ли она на окружности с небольшой погрешностью
        # return (length<=rad, compare_xy(in_ring, 1), in_ring, abs(rad-length)) ... length - расстояние до центра, in_ring = length/rad
        if pos[0]:
            if show_hidden_circles:
                ring_pos.append((ring[0], pos[1], pos[2], pos[3]))
            elif check_ring_intersecting_parts(ring, puzzle_parts):
                ring_pos.append((ring[0], pos[1], pos[2], pos[3]))

    if len(ring_pos) > 0:  # есть внутри круга
        # проверим концентрические круги
        for ring in puzzle_rings:
            if len(ring[7])==0: continue
            fl_link,pos = False,-1
            for linked in ring[7]:
                for nn,ring_info in enumerate(ring_pos):
                    if linked[0]==ring_info[0]:
                        fl_link = True
                    if ring[0]==ring_info[0]:
                        pos=nn
            if fl_link and pos>=0:
                ring_pos.pop(pos)

        # print(ring_pos)
        rr = 1
        for ring_info in ring_pos:
            if ring_info[3]<=circle_area: # касаемся круга
                ring_select = ring_info[0]
                break
            elif ring_info[2] < rr: # ищем круг - мышка ближе всего к центру
                rr = ring_info[2]
                ring_select = ring_info[0]

        if mouse_x + mouse_y > 0:  # есть клик
            direction = -1 if mouse_left else 1 if mouse_right else 0
            ring_num = ring_select

    return ring_num, ring_select, direction

def draw_all_text(screen, font, font2, puzzle_kol, rings_kol, parts_kol, moves, solved, button_Open, button_Help, toggle_Marker, toggle_Circle, button_y2, button_y3, button_y4):
    WHITE_COLOR, RED_COLOR, GREEN_COLOR, BLUE_COLOR, YELLOW_COLOR = "#FFFFFF", "#FF0000", "#008000", "#0000FF", "#FFFF00"

    # 2
    # Пишем количество уровней
    text_puzzles = font2.render(str(puzzle_kol) + ' puzzles', True, WHITE_COLOR)
    text_puzzles_place = text_puzzles.get_rect(topleft=(button_Open.textRect.right + 10, button_y2 + 1))
    screen.blit(text_puzzles, text_puzzles_place)
    # Пишем количество перемещений
    text_moves = font.render('Moves: ' + str(moves), True, RED_COLOR)
    text_moves_place = text_moves.get_rect(topleft=(button_Help.textRect.right + 18, button_y2 - 3))
    screen.blit(text_moves, text_moves_place)
    # Пишем статус
    # text_solved = font.render('Solved', True, WHITE_COLOR) if solved else font.render('not solved', True, RED_COLOR)
    # text_solved_place = text_solved.get_rect(topleft=(text_moves_place.right + 10, button_y2 - 3))
    # screen.blit(text_solved, text_solved_place)

    # 3
    # Пишем текст переключателей + инфо о головоломке
    marker_text = "On" if toggle_Marker.value else "Off"
    text_marker = font2.render('Marker ' + marker_text, True, WHITE_COLOR)
    text_marker_place = text_moves.get_rect(topleft=(40, button_y3-4))
    screen.blit(text_marker, text_marker_place)

    circle_text = "On" if toggle_Circle.value else "Off"
    text_circle = font2.render('Hidden circles ' + circle_text, True, WHITE_COLOR)
    text_circle_place = text_moves.get_rect(topleft=(145, button_y3-4))
    screen.blit(text_circle, text_circle_place)

    text_info = font2.render('Total parts: ' + str(parts_kol) + ", circles: "+str(rings_kol), True, YELLOW_COLOR)
    text_info_place = text_moves.get_rect(topleft=(text_circle_place.right + 30, button_y3-4))
    screen.blit(text_info, text_info_place)

    # 4
    # Пишем подсказку
    text_info = font2.render('Use: mouse wheel - ring rotate, space button - undo, F11/F12 - prev/next file', True, GREEN_COLOR)
    text_info_place = text_moves.get_rect(topleft=(10, button_y4 - 3))
    screen.blit(text_info, text_info_place)

def save_state(dirname, filename, VERSION):
    command_mas = []
    command_mas.append(["DirName", dirname, []])
    command_mas.append(["PuzzleFile", filename, []])

    app_folder = os.getenv('LOCALAPPDATA')+'\\Geraniums Pot '+VERSION+'\\'
    if not os.path.isdir(app_folder):
        try:
            os.mkdir(app_folder)
        except: return
        if not os.path.isdir(app_folder):
            return

    app_ini = app_folder+'Geraniums Pot.ini'
    save_file(app_ini, command_mas)

def save_file(filename, command_mas):
    with open(filename, encoding='utf-8', mode='w') as f:
        f.write("# Geraniums Pot - Intersecting Circles Puzzles Simulator"+"\n")
        for command,params,param_mas in command_mas:
            stroka = ""+command+": "+params+"\n"
            f.write(stroka)

def expand_script(lines):
    command_mas = []
    for nom, stroka in enumerate(lines):
        str_nom = nom + 1
        stroka = stroka.replace('\n', '')
        stroka = stroka.strip()
        if stroka == "": continue

        if stroka[0] == "#": continue
        pos = stroka.find("#")
        if pos >= 0:
            stroka = stroka[0:pos]

        pos = stroka.find(":")
        if pos == -1:
            command = stroka.strip()
            params = ""
        else:
            command = stroka[0:pos].strip()
            if pos == len(stroka) - 1:
                params = ""
            else:
                params = stroka[pos + 1:].strip()

        pos = 0
        while True:
            params_str = params[pos:]
            pos1, pos2 = params_str.find("("), params_str.find(")")
            if pos1 >= 0 and pos2 >= 0:
                new_par = params_str[pos1 + 1:pos2].replace(",", ";")
                params = params[0:pos + pos1 + 1] + new_par + params[pos + pos2:]
                pos += pos2 + 1
            else:
                break

        param_mas = []
        if params != "":
            param_mas_ = params.split(",")
            for num, par in enumerate(param_mas_):
                par = par.strip()
                if par == "": continue
                if par.find("(") >= 0 and par.find(")") >= 0 and par.find(";") >= 0:
                    par = par.replace("(", "")
                    par = par.replace(")", "")
                    param_mas2, param_mas2_ = [], par.split(";")
                    for num2, par2 in enumerate(param_mas2_):
                        if par2 == "": continue
                        param_mas2.append(par2.strip())
                    par = param_mas2
                elif par[0] == "(" and par[len(par) - 1] == ")":
                    par = par.replace("(", "")
                    par = par.replace(")", "")
                    par = [par]
                param_mas.append(par)

        command_mas.append([command, params, param_mas, str_nom])

    return command_mas

def align_cordinates(puzzle_rings, puzzle_arch, puzzle_parts, puzzle_lines, puzzle_scale, flip_x, flip_y, flip_rotate, BORDER):
    # выровняем относительно осей. чтобы не было сильных сдвигов
    for nn, ring in enumerate(puzzle_rings):
        if ring[6] != 0: continue
        if nn == 0:
            min_x, min_y = ring[1] - ring[3], ring[2] - ring[3]
        else:
            min_x, min_y = min(min_x, ring[1] - ring[3]), min(min_y, ring[2] - ring[3])
    for part in puzzle_parts: # отдельные части могут быть за пределами колец
        for part_xy in part[6]:
            min_x, min_y = min(min_x, part_xy[0]), min(min_y, part_xy[1])

    for ring in puzzle_rings:
        ring[1], ring[2] = ring[1] - min_x, ring[2] - min_y
    for arch in puzzle_arch:
        arch[1], arch[2] = arch[1] - min_x, arch[2] - min_y
    for part in puzzle_parts:
        for part_arch in part[5]:
            part_arch[3], part_arch[4] = part_arch[3] - min_x, part_arch[4] - min_y
    for line in puzzle_lines:
        line[1], line[2] = line[1] - min_x, line[2] - min_y
        line[3], line[4] = line[3] - min_x, line[4] - min_y

    # учтем масштаб
    if puzzle_scale != 0:
        shift = BORDER
        for ring in puzzle_rings:
            ring[1] = ring[1] * puzzle_scale + shift
            ring[2] = ring[2] * puzzle_scale + shift
            ring[3] = ring[3] * puzzle_scale
        for arch in puzzle_arch:
            arch[1] = arch[1] * puzzle_scale + shift
            arch[2] = arch[2] * puzzle_scale + shift
            arch[3] = arch[3] * puzzle_scale
        for part in puzzle_parts:
            for part_arch in part[5]:
                part_arch[3] = part_arch[3] * puzzle_scale + shift
                part_arch[4] = part_arch[4] * puzzle_scale + shift
            if len(part[3])>0:
                part[3][3] = part[3][3] * puzzle_scale
                part[3][4] = part[3][4] * puzzle_scale
        for line in puzzle_lines:
            line[1] = line[1] * puzzle_scale + shift
            line[2] = line[2] * puzzle_scale + shift
            line[3] = line[3] * puzzle_scale + shift
            line[4] = line[4] * puzzle_scale + shift

    # иногда контуры колец выходят за край
    min_x = min_y = 0
    for ring in puzzle_rings:
        if ring[6]!= 0: continue
        shift_xx = ring[1] - (ring[3] + BORDER)
        shift_yy = ring[2] - (ring[3] + BORDER)
        if shift_xx < 0:
            if min_x < (-shift_xx):
                min_x = -shift_xx
        if shift_yy < 0:
            if min_y < (-shift_yy):
                min_y = -shift_yy
    if min_x > 0 or min_y > 0:
        for ring in puzzle_rings:
            if ring[6] != 0: continue
            ring[1], ring[2] = ring[1] + min_x, ring[2] + min_y
        for arch in puzzle_arch:
            if arch[0] <= len_puzzle_rings(puzzle_rings):
                ring = find_element(arch[0],puzzle_rings)
                if ring[6] != 0: continue
            arch[1], arch[2] = arch[1] + min_x, arch[2] + min_y
        for part in puzzle_parts:
            for part_arch in part[5]:
                part_arch[3], part_arch[4] = part_arch[3] + min_x, part_arch[4] + min_y
        for line in puzzle_lines:
            line[1], line[2] = line[1] + min_x, line[2] + min_y
            line[3], line[4] = line[3] + min_x, line[4] + min_y

    # измерим размеры головоломки
    puzzle_width, puzzle_height = 0, 0
    for ring in puzzle_rings:
        if ring[6]!= 0: continue
        xx = ring[1] + ring[3] + BORDER
        puzzle_width = xx if xx > puzzle_width else puzzle_width
        yy = ring[2] + ring[3] + BORDER
        puzzle_height = yy if yy > puzzle_height else puzzle_height

    calc_parts_countur(puzzle_parts, puzzle_arch, True)
    for part in puzzle_parts: # отдельные части могут быть за пределами колец
        for part_xy in part[6]:
            xx = part_xy[0] + BORDER
            puzzle_width = xx if xx > puzzle_width else puzzle_width
            yy = part_xy[1] + BORDER
            puzzle_height = yy if yy > puzzle_height else puzzle_height

    # учтем повороты
    vek_mul = -1
    if flip_x:
        vek_mul = -1 * vek_mul
        for ring in puzzle_rings:
            ring[1] = puzzle_width - ring[1]
        for arch in puzzle_arch:
            arch[1] = puzzle_width - arch[1]
        for part in puzzle_parts:
            for part_arch in part[5]:
                part_arch[3] = puzzle_width - part_arch[3]
        for line in puzzle_lines:
            line[1] = puzzle_width - line[1]
            line[3] = puzzle_width - line[3]
    if flip_y:
        vek_mul = -vek_mul
        for ring in puzzle_rings:
            ring[2] = puzzle_height - ring[2]
        for arch in puzzle_arch:
            arch[2] = puzzle_height - arch[2]
        for part in puzzle_parts:
            for part_arch in part[5]:
                part_arch[4] = puzzle_height - part_arch[4]
        for line in puzzle_lines:
            line[2] = puzzle_height - line[2]
            line[4] = puzzle_height - line[4]
    if flip_rotate:
        vek_mul = -vek_mul
        for ring in puzzle_rings:
            ring[1], ring[2] = ring[2], ring[1]
        for arch in puzzle_arch:
            arch[1], arch[2] = arch[2], arch[1]
        for part in puzzle_parts:
            for part_arch in part[5]:
                part_arch[3], part_arch[4] = part_arch[4], part_arch[3]
        for line in puzzle_lines:
            line[1], line[2] = line[2], line[1]
            line[3], line[4] = line[4], line[3]

        puzzle_width, puzzle_height = puzzle_height, puzzle_width

    if vek_mul == 1:
        for part in puzzle_parts:
            for part_arch in part[5]:
                part_arch[2] = -part_arch[2]

    return vek_mul, puzzle_width, puzzle_height

def load_puzzle(fl, init, dirname,filename):
    puzzle_kol = 0
    lines = []

    dir = os.path.abspath(os.curdir)
    if os.path.isdir(dir + "\\Garden"):
        dir += "\\Garden"
    if dir != "":
        for root, dirs, files in os.walk(dir):
            for fil in files:
                if os.path.splitext(fil)[1].lower()==".txt":
                    puzzle_kol += 1
    puzzle_kol = 1 if puzzle_kol==0 else puzzle_kol

    ###################################################################################
    if dirname == "":
        dirname = os.path.abspath(os.curdir)
        if os.path.isdir(dirname + "\\Garden"):
            dirname += "\\Garden"
    if fl == "init":
        lines = init.split("\n")
    else:
        if (fl == "next" or fl == "prev") and filename != "" and dirname != "":
            for root, dirs, files in os.walk(dirname):
                f_name = os.path.basename(filename)
                if f_name in files:
                    pos = files.index(f_name)
                    if fl == "next":
                        pos += 1
                    else:
                        pos -= 1
                    if pos == len(files):
                        pos = 0
                    elif pos == -1:
                        pos = len(files)-1
                    f_name = files[pos]
                    filename = os.path.join(dirname, f_name)
        elif fl == "open" or filename == "":
            filetypes = (("Text file", "*.txt"), ("Any file", "*"))
            f_name = fd.askopenfilename(title="Open Puzzle", initialdir=dirname, filetypes=filetypes)
            if f_name == "":
                return [],0,"","", "-"
            filename = f_name
            dirname = os.path.dirname(filename)
        elif fl == "drop" and filename != "":
            dirname = os.path.dirname(filename)

        try:
            with open(filename, encoding = 'utf-8', mode = 'r') as f:
                lines = f.readlines()
        except:
            try:
                with open(filename, mode='r') as f:
                    lines = f.readlines()
            except:
                return [],0,"","", "Can not open the file"
    return lines, puzzle_kol, dirname, filename,  ""

def dir_test(dir_garden = "", dir_screenshots = ""):
    mas_files = []
    if dir_screenshots == "":
        dir_screenshots = os.path.abspath(os.curdir)
        if os.path.isdir(dir_screenshots + "\\ScreenShots"):
            dir_screenshots += "\\ScreenShots"

    if dir_garden == "":
        dir = os.path.abspath(os.curdir)
        if os.path.isdir(dir + "\\Garden"):
            dir += "\\Garden"
    else:
        dir = dir_garden
    if dir != "":
        for root, dirs, files in os.walk(dir):
            for fil in files:
                if os.path.splitext(fil)[1].lower()==".txt":
                    filename = os.path.join(root, fil)
                    mas_files.append( [root, filename] )
    return mas_files, dir, dir_screenshots

def init_test(file_num, mas_files, BORDER, PARTS_COLOR):
    if file_num>=len(mas_files):
        return "Quit",0
    dirname, filename = mas_files[file_num]
    fil = read_file(dirname, filename, BORDER, PARTS_COLOR, "reset")

    file_num += 1
    return fil,file_num

def init_puzzle(BORDER, PARTS_COLOR, VERSION, fl_reset_ini = False, fl_esc = False):
    fl_init = file_ext = True
    dirname = filename = ""
    if not fl_esc:
        app_folder = os.getenv('LOCALAPPDATA') + '\\Geraniums Pot '+VERSION+'\\'
        app_ini = app_folder + 'Geraniums Pot.ini'
        if os.path.isfile(app_ini):
            if fl_reset_ini:
                os.remove(app_ini)
            else:
                lines = []
                try:
                    with open(app_ini, encoding='utf-8', mode='r') as f:
                        lines = f.readlines()
                except:
                    try:
                        with open(app_ini, mode='r') as f:
                            lines = f.readlines()
                    except:
                        pass

                ini_mas = expand_script(lines)
                for command, params, param_mas, str_nom in ini_mas:
                    if command == "DirName":
                        dirname = params
                    elif command == "PuzzleFile":
                        filename = params
                        fl_init = False

    if dirname != "" and filename != "":
        fil = read_file(dirname, filename, BORDER, PARTS_COLOR, "reset")
        if typeof(fil) == "str":
            fl_init = True

    if fl_init:
        init = """
            Name: Avenger Puzzler
            Author: Douglas Engel
            Link: https://twistypuzzles.com/app/museum/museum_showitem.php?pkey=1550

            Scale: 3
            Speed: 4
            Flip: y

            # ring number, center coordinates x y, radius, angle
            Ring: 1,  50, 50, 50, 60
            Ring: 2, 115, 50, 50, 60

            AutoCutParts: 1R,1R,1R,1R,1R,1R, 2R,2R,2R,2R,2R,2R
            AutoColorParts: 0, 0, 7
            SetColorParts: (1,3,7),6,   (15,18,22),3,   (2,6,9),5,  (17,21,23),4
        """.strip('\n')

        fil = read_file("", "", BORDER, PARTS_COLOR, "init", init)
        file_ext = False

    return file_ext, fil

def events_check_read_puzzle(events, fl_break, fl_reset, fl_test, VERSION, BTN_CLICK, BTN_CLICK_STR, BORDER, WIN_WIDTH, WIN_HEIGHT, puzzle_width, puzzle_height, PANEL, win_caption, file_ext, puzzle_link, puzzle_rings, puzzle_arch, puzzle_parts, puzzle_lines, puzzle_points, help, photo, undo, moves, moves_stack, redo_stack, ring_num, direction, mouse_xx, mouse_yy, dirname, filename, PARTS_COLOR, auto_marker, auto_marker_ring):
    mouse_x, mouse_y, mouse_left, mouse_right, fil = 0, 0, False, False, ""
    fl_resize = False

    for ev in events:  # Обрабатываем события
        if (ev.type == QUIT):
            if file_ext:
                save_state(dirname, filename, VERSION)
            return SystemExit, "QUIT"
        if (ev.type == KEYDOWN and ev.key == K_ESCAPE):
            if fl_test:
                return SystemExit, "QUIT"
            help = 0 if help == 1 else help
            photo = 0 if photo == 1 else photo
        if fl_test: continue

        if (ev.type == KEYDOWN and ev.key == K_F1):
            BTN_CLICK = True
            BTN_CLICK_STR = "help"
        if (ev.type == KEYDOWN and ev.key == K_F2):
            BTN_CLICK = True
            BTN_CLICK_STR = "reset"
        if (ev.type == KEYDOWN and ev.key == K_F3):
            BTN_CLICK = True
            BTN_CLICK_STR = "open"
        if (ev.type == KEYDOWN and ev.key == K_F4):
            BTN_CLICK = True
            BTN_CLICK_STR = "scramble"
        if (ev.type == KEYDOWN and ev.key == K_F8):
            BTN_CLICK = True
            BTN_CLICK_STR = "superscramble"
        if (ev.type == KEYDOWN and ev.key == K_F5):
            BTN_CLICK = True
            BTN_CLICK_STR = "photo"
        if (ev.type == KEYDOWN and ev.key == K_F11):
            BTN_CLICK = True
            BTN_CLICK_STR = "prev"
        if (ev.type == KEYDOWN and ev.key == K_F12):
            BTN_CLICK = True
            BTN_CLICK_STR = "next"
        if (ev.type == KEYDOWN and ev.key == K_SPACE):
            BTN_CLICK = True
            BTN_CLICK_STR = "undo"
        if (ev.type == KEYDOWN and ev.key == K_BACKSPACE):
            BTN_CLICK = True
            BTN_CLICK_STR = "redo"

        if BTN_CLICK_STR == "info" and help+photo == 0:
            for link in puzzle_link:
                if link != "":
                    webbrowser.open(link, new=2, autoraise=True)
        if BTN_CLICK_STR == "about" and help+photo == 0:
            mb.showinfo("Geraniums Pot","Geraniums Pot - Intersecting Circles Puzzles Simulator\n"+
                             "Programmer: Evgeniy Grigoriev. Version "+VERSION)
            webbrowser.open("https://twistypuzzles.com/forum/viewtopic.php?p=424143#p424143", new=2, autoraise=True)
            webbrowser.open("https://github.com/grigorusha/GeraniumsPot", new=2, autoraise=True)
        if BTN_CLICK_STR == "help":
            help = 1 - help
        if BTN_CLICK_STR == "photo":
            photo = 1 - photo

        if BTN_CLICK_STR == "reset" and help+photo == 0:
            if not file_ext:
                fl_break = fl_reset = True
            else:
                old_width, old_height = WIN_WIDTH, WIN_HEIGHT
                fil = read_file(dirname, filename, BORDER, PARTS_COLOR, "reset")
                if not fl_test:
                    window_front(win_caption)

                if typeof(fil) != "str":
                    puzzle_name, puzzle_author, puzzle_link, puzzle_scale, puzzle_speed, puzzle_rings, puzzle_arch, puzzle_parts, puzzle_lines, puzzle_points, puzzle_kol, vek_mul, dirname, filename, puzzle_width, puzzle_height, auto_marker, auto_marker_ring, remove_parts, copy_parts, show_hidden_circles = fil
                    file_ext = fl_break = fl_reset = True
                    if old_width != WIN_WIDTH or old_height != WIN_HEIGHT:
                        fl_reset = False
                else:
                    if fil == "break":
                        fl_break, fl_reset, file_ext = True, False, False
                    elif fil != "-":
                        if fil == "":
                            fil = "Unknow error"
                        mb.showerror(message=("Bad puzzle-file: " + fil))
                        if not fl_test:
                            window_front(win_caption)
        if (BTN_CLICK_STR == "open" or BTN_CLICK_STR == "prev" or BTN_CLICK_STR == "next") and help+photo == 0:
            fl_break = False
            fil = read_file(dirname, filename, BORDER, PARTS_COLOR, BTN_CLICK_STR)
            if not fl_test:
                window_front(win_caption)

            if typeof(fil) != "str":
                puzzle_name, puzzle_author, puzzle_link, puzzle_scale, puzzle_speed, puzzle_rings, puzzle_arch, puzzle_parts, puzzle_lines, puzzle_points, puzzle_kol, vek_mul, dirname, filename, puzzle_width, puzzle_height, auto_marker, auto_marker_ring, remove_parts, copy_parts, show_hidden_circles = fil
                file_ext = fl_break = True
                fl_reset = False
                if file_ext:
                    save_state(dirname, filename, VERSION)
            else:
                if fil == "break":
                    fl_break, fl_reset, file_ext = True,False,False
                elif fil != "-":
                    if fil == "":
                        fil = "Unknow error"
                    mb.showerror(message=("Bad puzzle-file: " + fil))
                    if not fl_test:
                        window_front(win_caption)
        if ev.type == DROPFILE and help+photo == 0:
            fl_break = False
            fil = read_file("", ev.file, BORDER, PARTS_COLOR, "drop")
            window_front(win_caption)

            if typeof(fil) != "str":
                puzzle_name, puzzle_author, puzzle_link, puzzle_scale, puzzle_speed, puzzle_rings, puzzle_arch, puzzle_parts, puzzle_lines, puzzle_points, puzzle_kol, vek_mul, dirname, filename, puzzle_width, puzzle_height, auto_marker, auto_marker_ring, remove_parts, copy_parts, show_hidden_circles = fil
                file_ext = fl_break = True
                fl_reset = False
                if file_ext:
                    save_state(dirname, filename, VERSION)
            else:
                if fil == "break":
                    fl_break, fl_reset, file_ext = True,False,False
                elif fil != "-":
                    if fil == "":
                        fil = "Unknow error"
                    mb.showerror(message=("Bad puzzle-file: " + fil))
                    window_front(win_caption)

        if ev.type == VIDEORESIZE:
            puzzle_width_, puzzle_height_ = puzzle_width-BORDER*2, puzzle_height-BORDER*2
            original_scale = puzzle_width_/puzzle_height_
            width, height = ev.w-BORDER*2, ev.h-PANEL-BORDER*2
            screen_scale = width/height

            new_scale = 1
            if original_scale>screen_scale:
                new_scale = width / puzzle_width_
            elif original_scale<screen_scale:
                new_scale = height / puzzle_height_

            if new_scale != 1:
                vek_mul, puzzle_width, puzzle_height = align_cordinates(puzzle_rings, puzzle_arch, puzzle_parts, puzzle_lines, new_scale, False, False, False, BORDER)
                calc_all_spline(puzzle_rings, puzzle_arch, puzzle_parts)

            WIN_WIDTH, WIN_HEIGHT = ev.w, ev.h-PANEL
            fl_resize = True

        if ev.type == MOUSEMOTION:
            mouse_xx, mouse_yy = ev.pos[0], ev.pos[1]

        if ev.type == MOUSEBUTTONUP:
            if ev.type == MOUSEBUTTONUP and (ev.button == 2 or ev.button == 6):
                BTN_CLICK = True
                BTN_CLICK_STR = "undo"
            if ev.type == MOUSEBUTTONUP and (ev.button == 7):
                BTN_CLICK = True
                BTN_CLICK_STR = "redo"

            if ev.type == MOUSEBUTTONUP and (ev.button == 1 or ev.button == 4) and not BTN_CLICK:
                if help+photo == 0:
                    mouse_x, mouse_y = ev.pos[0], ev.pos[1]
                    mouse_left = True
                help = 0 if help == 1 else help
                photo = 0 if photo == 1 else photo
            if ev.type == MOUSEBUTTONUP and (ev.button == 3 or ev.button == 5) and not BTN_CLICK:
                if help+photo == 0:
                    mouse_x, mouse_y = ev.pos[0], ev.pos[1]
                    mouse_right = True
                help = 0 if help == 1 else help
                photo = 0 if photo == 1 else photo

        if (BTN_CLICK_STR == "scramble" or BTN_CLICK_STR == "superscramble") and help!=1:
            fl_break = False
            scramble_puzzle(puzzle_rings,puzzle_arch,puzzle_parts,puzzle_points,BTN_CLICK_STR)
            moves, moves_stack, redo_stack = 0, [], []

        if BTN_CLICK_STR == "undo" and help+photo == 0:
            fl_break = False
            if len(moves_stack) > 0:
                undo = True
                moves -= 1
                ring_num, direction = moves_stack.pop()
                direction = -direction
                redo_stack.append([ring_num, direction])

        if BTN_CLICK_STR == "redo" and help+photo == 0:
            fl_break = False
            if len(redo_stack) > 0:
                undo = True
                moves += 1
                ring_num, direction = redo_stack.pop()
                direction = -direction
                moves_stack.append([ring_num, direction])

        BTN_CLICK = False
        BTN_CLICK_STR = ""

    fil2 = fl_break, fl_reset, file_ext, fl_resize, BTN_CLICK, BTN_CLICK_STR, undo, moves, moves_stack, redo_stack, ring_num, direction, mouse_xx, mouse_yy, mouse_x, mouse_y, mouse_left, mouse_right, help, photo, WIN_WIDTH, WIN_HEIGHT, puzzle_width, puzzle_height
    return fil, fil2

def read_puzzle_script_and_init_puzzle(lines,PARTS_COLOR):
    flip_y = flip_x = flip_rotate = skip_check_error = show_hidden_circles = False
    puzzle_name, puzzle_author, puzzle_scale, puzzle_speed, auto_marker, auto_marker_ring, first_cut, first_coloring = "", "", 1, 2, 0, 0, True, True
    puzzle_link, puzzle_rings, puzzle_arch, puzzle_parts, puzzle_lines, puzzle_points, auto_cut_parts, auto_color_parts, set_color_parts, remove_parts, copy_parts = [], [], [], [], [], [], [], [], [], [], []
    part_num, param_calc, ring_num, line_num = 0, [], 1, 1

    command_mas = expand_script(lines)

    step,step_total = 0,1
    for command, params, param_mas, _ in command_mas:
        command = command.lower()
        if ["ring","copyring","line","renumbering","autocolorparts","setcolorcircles","setcolorparts","setmarkerparts","rotateallparts","removemicroparts","removesmallparts","hideallparts","showallparts","invertallparts"].count(command)>0:
            step_total += 1
        elif ["makecircles","cutcircles","removeparts","hideparts","showparts","rotateallparts","removemicroparts","removesmallparts"].count(command)>0:
            step_total += len(param_mas)
        elif ["autocutparts","mirrorparts","copyparts","moveparts","rotatecircles"].count(command)>0:
            step_total += len(param_mas)

    ##################################################################
    # инициализация параметров

    for command, params, param_mas, str_nom in command_mas:
        command = command.lower()
        if ["ring","copyring","line","renumbering","autocolorparts","setcolorcircles","setcolorparts","setmarkerparts","rotateallparts","removemicroparts","removesmallparts","hideallparts","showallparts","invertallparts"].count(command)>0:
            step += 1
        elif ["makecircles","cutcircles","removeparts","hideparts","showparts","rotateallparts","removemicroparts","removesmallparts"].count(command)>0:
            step += len(param_mas)
        elif ["autocutparts","mirrorparts","copyparts","moveparts","rotatecircles"].count(command)>0:
            step += len(param_mas)

        percent = int(100 * step / step_total)
        if percent%5==0 and percent!=0:
            try:
                events = pygame.event.get()
                # for ev in events:  # Обрабатываем события
                #     if (ev.type == KEYDOWN and ev.key == K_ESCAPE):
                #         return "break"

                display.set_caption(puzzle_name + ": Please wait! Loading ... " + str(percent) + "%")
                display.update()
            except: pass

        if command == "Name".lower():
            puzzle_name = params
        elif command == "Author".lower():
            puzzle_author = params
        elif command == "SkipCheckError".lower():
            if int(params) == 1:
                skip_check_error = True
        elif command == "ShowHiddenCircles".lower():
            show_hidden_circles = True
        elif command == "Link".lower():
            puzzle_link.append(params)
        elif command == "Scale".lower():
            puzzle_scale = float(params)
        elif command == "Speed".lower():
            puzzle_speed = float(params)
        elif command == "Flip".lower():
            if params.lower().find("y") >= 0:
                flip_y = True
            if params.lower().find("x") >= 0:
                flip_x = True
            if params.lower().find("rotate") >= 0:
                flip_rotate = True

        #########################################################################
        elif command == "Param".lower():
            if len(param_mas) != 2: return ("Incorrect 'Param' parameters. In str=" + str(str_nom))
            for param in param_calc:
                if param_mas[1].find(param[0]) != -1:
                    param_mas[1] = param_mas[1].replace(param[0], str(param[1]))
            try:
                param_mas[1] = eval(param_mas[1])
            except:
                return ("Error in 'Param' calculation. In str=" + str(str_nom))

            fl_ins = False
            for nn, param in enumerate(param_calc):
                if param_mas[0].find(param[0]) != -1:
                    param_calc.insert(nn,[param_mas[0], param_mas[1]])
                    fl_ins = True
                    break
            if not fl_ins:
                param_calc.append([param_mas[0], param_mas[1]])

        #########################################################################
        # инициализация кругов головоломки
        elif command == "Ring".lower():
            if not (len(param_mas) == 5 or len(param_mas) == 6): return ("Incorrect 'Ring' parameters. In str=" + str(str_nom))
            param_mas[1], param_mas[2] = calc_param(param_mas[1], param_calc), calc_param(param_mas[2], param_calc)
            param_mas[3], param_mas[4] = calc_param(param_mas[3], param_calc), calc_param(param_mas[4], param_calc)
            param_mas5 = int(param_mas[5]) if len(param_mas)==6 else 0
            puzzle_rings.append([ring_num, param_mas[1], param_mas[2], param_mas[3], param_mas[4], 0, param_mas5, [], []])
            ring_num += 1

            arch_num = len(puzzle_arch)+1
            puzzle_arch.append([arch_num, param_mas[1], param_mas[2], param_mas[3]])
            check_all_rings(puzzle_rings)

        elif command == "CopyRing".lower():
            if not (len(param_mas) == 5 or len(param_mas) == 6): return ("Incorrect 'CopyRing' parameters. In str=" + str(str_nom))
            param_mas[3], param_mas[4] = calc_param(param_mas[3], param_calc), calc_param(param_mas[4], param_calc)
            param_mas5 = int(param_mas[5]) if len(param_mas)==6 else 0
            center_x, center_y = copy_ring(int(param_mas[1]),param_mas[2],puzzle_rings)
            puzzle_rings.append([ring_num, center_x, center_y, param_mas[3], param_mas[4], 0, param_mas5, [], []])
            ring_num += 1

            arch_num = len(puzzle_arch)+1
            puzzle_arch.append([arch_num, center_x, center_y, param_mas[3]])
            check_all_rings(puzzle_rings)

        #########################################################################
        # инициализация линий головоломки
        elif command == "Line".lower():
            if not (len(param_mas) == 5): return ("Incorrect 'Line' parameters. In str=" + str(str_nom))
            param_mas[1], param_mas[2] = calc_param(param_mas[1], param_calc), calc_param(param_mas[2], param_calc)
            param_mas[3], param_mas[4] = calc_param(param_mas[3], param_calc), calc_param(param_mas[4], param_calc)
            puzzle_lines.append([line_num, param_mas[1], param_mas[2], param_mas[3], param_mas[4]])
            line_num += 1

        ###############################################################################################################################
        # инициализация всех частей. запускаем скрамбл функцию с одновременной нарезкой. запускаем авто раскраску со смешиванием цветов

        elif command == "AutoCutParts".lower():
            auto_cut_parts = param_mas
            init_cut_all_ring_to_parts(puzzle_rings, puzzle_arch, puzzle_parts, puzzle_points, auto_cut_parts, first_cut)
            first_cut = False

        elif command == "MakeCircles".lower():
            make_circles = param_mas
            make_def_circles(puzzle_rings, puzzle_arch, puzzle_parts, make_circles)
            first_cut = False

        elif command == "RotateCircles".lower():
            rotate_circles = param_mas
            rotate_def_circles(puzzle_rings, puzzle_arch, puzzle_parts, puzzle_points, rotate_circles)

        elif command == "CutCircles".lower():
            cut_circles = param_mas
            cut_def_circles(puzzle_rings, puzzle_arch, puzzle_parts, cut_circles)

        elif command == "CutLines".lower():
            cut_lines = param_mas
            cut_def_lines(puzzle_lines, puzzle_parts, puzzle_arch, cut_lines)

        elif command == "RemoveParts".lower():
            remove_parts = param_mas
            remove_def_parts(puzzle_parts, remove_parts)

        elif command == "RemoveMicroParts".lower() or command == "RemoveSmallParts".lower():
            area_param = param_mas
            remove_micro_parts(puzzle_parts, area_param)

        elif command == "CopyParts".lower():
            copy_parts = param_mas
            copy_def_parts(copy_parts, puzzle_rings, puzzle_arch, puzzle_parts, puzzle_points)
        elif command == "MoveParts".lower():
            copy_parts = param_mas
            copy_def_parts(copy_parts, puzzle_rings, puzzle_arch, puzzle_parts, puzzle_points, True)

        elif command == "MirrorParts".lower():
            for nn,mir in enumerate(param_mas):
                if nn%2==1: param_mas[nn] = calc_param(param_mas[nn], param_calc)
            mirror_parts = param_mas
            mirror_def_parts(mirror_parts, puzzle_arch, puzzle_parts, puzzle_points)

        elif command == "Renumbering".lower():
            sort_and_renum_all_parts(puzzle_parts)

        elif command == "HideParts".lower():
            hide_parts = param_mas
            hide_show_def_parts(puzzle_parts, hide_parts, -1, False)
        elif command == "ShowParts".lower():
            hide_parts = param_mas
            hide_show_def_parts(puzzle_parts, hide_parts, 1, False)
        elif command == "HideAllParts".lower():
            hide_show_def_parts(puzzle_parts, [], -1, True)
        elif command == "ShowAllParts".lower():
            hide_show_def_parts(puzzle_parts, [], 1, True)
        elif command == "InvertAllParts".lower():
            hide_show_def_parts(puzzle_parts, [], 0, True)

        elif command == "RotateAllParts".lower():
            param_mas[0], param_mas[1], param_mas[2] = calc_param(param_mas[0], param_calc), calc_param(param_mas[1], param_calc), calc_param(param_mas[2], param_calc)
            rotate_parts_param = param_mas
            rotate_all_parts(puzzle_rings, puzzle_arch, puzzle_parts, rotate_parts_param)
            puzzle_points = []

        elif command == "AutoColorParts".lower():
            auto_color_parts = param_mas
            init_color_all_parts(puzzle_parts, puzzle_rings, auto_color_parts, PARTS_COLOR)
            first_coloring = False
        elif command == "SetColorCircles".lower():
            auto_color_parts = param_mas
            init_color_all_circles(puzzle_parts, puzzle_rings, auto_color_parts, first_coloring)
            first_coloring = False
        elif command == "SetColorParts".lower():
            set_color_parts = param_mas
            set_color_all_parts(puzzle_parts, set_color_parts)
            first_coloring = False

        elif command == "SetMarkerParts".lower():
            set_marker_parts = param_mas
            set_marker_all_parts(puzzle_parts, set_marker_parts, puzzle_scale)
        elif command == "AutoMarker".lower():
            auto_marker = int(params) if is_number(params) else 1
        elif command == "AutoMarkerRing".lower():
            auto_marker_ring = int(params) if is_number(params) else 1

        elif command == "End".lower() or command == "Stop".lower() or command == "Exit".lower() or command == "Quit".lower():
            break

        ########################################################################################
        # блок для загрузки скомпилированной головоломки. загружаем координаты всех частей
        # elif command == "Arch":
        #     if len(param_mas) != 4: return ("Incorrect 'Arch' parameters. In str=" + str(str_nom))
        #     param_mas[1], param_mas[2], param_mas[3] = calc_param(param_mas[1], param_calc), calc_param(param_mas[2], param_calc), calc_param(param_mas[3], param_calc)
        #     puzzle_arch.append([int(param_mas[0]), param_mas[1], param_mas[2], param_mas[3]])
        # elif command == "Part":
        #     if len(param_mas) == 2:
        #         part_num = int(param_mas[0])
        #         puzzle_parts.append([part_num, int(param_mas[1]), 1, [], [], [], [], [], 0])
        #     else:
        #         return ("Incorrect 'Part' parameters. In str=" + str(str_nom))
        # elif command == "PartArch":
        #     if len(param_mas) == 4 and part_num > 0:
        #         part = find_element(part_num, puzzle_parts)
        #         param_mas[2], param_mas[3] = calc_param(param_mas[2], param_calc), calc_param(param_mas[3], param_calc)
        #         part_arch = part[5]
        #         part_arch.append([int(param_mas[0]), 1, int(param_mas[1]), param_mas[2], param_mas[3], 0])
        #     else:
        #         return ("Incorrect 'PartArch' parameters. In str=" + str(str_nom))

    return puzzle_name, puzzle_author, puzzle_link, puzzle_scale, puzzle_speed, puzzle_rings, puzzle_arch, puzzle_parts, puzzle_lines, puzzle_points, auto_cut_parts, auto_color_parts, auto_marker, auto_marker_ring, set_color_parts, remove_parts, copy_parts, flip_y, flip_x, flip_rotate, skip_check_error, show_hidden_circles

def calc_all_spline(puzzle_rings, puzzle_arch, puzzle_parts):
    # построение границ деталек
    calc_parts_countur(puzzle_parts, puzzle_arch)
    calc_all_centroids(puzzle_parts)

    # вычисление плавного контура кругов
    for ring in puzzle_rings:
        shift = 4
        arch_mas = [[ring[1], ring[2] + ring[3] + shift], [ring[1], ring[2] + ring[3] + shift]]
        ring[8], _ = calc_arch_spline(arch_mas, ring[1], ring[2], ring[3] + shift, 1)

def read_file(dirname, filename, BORDER, PARTS_COLOR, fl, init=""):
    # загрузка файла
    lines, puzzle_kol, dirname, filename, error_str = load_puzzle(fl, init, dirname, filename)
    if error_str != "": return error_str

    mouse.set_cursor(SYSTEM_CURSOR_WAITARROW)
    win_caption = display.get_caption()
    display.set_caption("Please wait! Loading ...")

    # прочитаем строки файла
    fil = read_puzzle_script_and_init_puzzle(lines, PARTS_COLOR)
    if typeof(fil) == "str": return fil
    puzzle_name, puzzle_author, puzzle_link, puzzle_scale, puzzle_speed, puzzle_rings, puzzle_arch, puzzle_parts, puzzle_lines, puzzle_points, auto_cut_parts, auto_color_parts, auto_marker, auto_marker_ring, set_color_parts, remove_parts, copy_parts, flip_y, flip_x, flip_rotate, skip_check_error, show_hidden_circles = fil

    remove_dublikate_parts(puzzle_parts)

    # выравнивание, повороты и масштабирование всех координат
    vek_mul, puzzle_width, puzzle_height = align_cordinates(puzzle_rings, puzzle_arch, puzzle_parts, puzzle_lines, puzzle_scale, flip_x, flip_y, flip_rotate, BORDER)
    calc_all_spline(puzzle_rings, puzzle_arch, puzzle_parts)

    # поиск ошибок
    # find_incorrect_parts(puzzle_parts)

    for ring in puzzle_rings:
        ring[5]=0 # сбросим углы поворота для бермуд
    puzzle_points = []

    mouse.set_cursor(SYSTEM_CURSOR_ARROW)
    if typeof(win_caption)=="str":
        display.set_caption(win_caption)

    return puzzle_name, puzzle_author, puzzle_link, puzzle_scale, puzzle_speed, puzzle_rings, puzzle_arch, puzzle_parts, puzzle_lines, puzzle_points, puzzle_kol, vek_mul, dirname, filename, puzzle_width, puzzle_height, auto_marker, auto_marker_ring, remove_parts, copy_parts, show_hidden_circles
