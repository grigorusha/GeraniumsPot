from pygame import *

import os
from tkinter import filedialog as fd
from tkinter import messagebox as mb
import webbrowser
import random

from part import *
from syst import *

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
            photo_screen = image.load(photo_path)
            photo_rect = (photo_screen.get_rect().width, photo_screen.get_rect().height)
            if photo_rect[0] / photo_rect[1] <= PHOTO[0] / PHOTO[1]:
                scale_ko = PHOTO[1] / photo_rect[1]
                new_width = int(scale_ko * photo_rect[0])
                PHOTO = (new_width, PHOTO[1])
            else:
                scale_ko = PHOTO[0] / photo_rect[0]
                new_height = int(scale_ko * photo_rect[1])
                PHOTO = (PHOTO[0], new_height)

            photo_screen = transform.scale(photo_screen, PHOTO)
    return photo_screen, PHOTO

def draw_all_text(screen, font, font2, puzzle_kol, moves, solved, button_Open, button_Help, button_y2, button_y3):
    WHITE_COLOR, RED_COLOR, GREEN_COLOR, BLUE_COLOR = "#FFFFFF", "#FF0000", "#008000", "#0000FF"

    # Пишем количество уровней
    text_puzzles = font2.render(str(puzzle_kol) + ' puzzles', True, WHITE_COLOR)
    text_puzzles_place = text_puzzles.get_rect(topleft=(button_Open.textRect.right + 10, button_y2 + 1))
    screen.blit(text_puzzles, text_puzzles_place)
    # Пишем количество перемещений
    text_moves = font.render('Moves: ' + str(moves), True, RED_COLOR)
    text_moves_place = text_moves.get_rect(topleft=(button_Help.textRect.right + 18, button_y2 - 3))
    screen.blit(text_moves, text_moves_place)
    # Пишем статус
    text_solved = font.render('Solved', True, WHITE_COLOR) if solved else font.render('not solved', True, RED_COLOR)
    text_solved_place = text_solved.get_rect(topleft=(text_moves_place.right + 10, button_y2 - 3))
    screen.blit(text_solved, text_solved_place)
    # Пишем подсказку
    text_info = font2.render('Use: mouse wheel - ring rotate, space button - undo, F11/F12 - prev/next file', True, GREEN_COLOR)
    text_info_place = text_solved.get_rect(topleft=(10, button_y3 - 3))
    screen.blit(text_info, text_info_place)

def save_state(dirname, filename):
    command_mas = []
    command_mas.append(["DirName", dirname, []])
    command_mas.append(["PuzzleFile", filename, []])

    app_folder = os.getenv('LOCALAPPDATA')+'\\Geraniums Pot\\'
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

        if params == "":
            param_mas = []
        else:
            param_mas = params.split(",")
            for num, par in enumerate(param_mas):
                par = par.strip()
                if par == "": continue
                if par.find("(") >= 0 and par.find(")") >= 0 and par.find(";") >= 0:
                    par = par.replace("(", "")
                    par = par.replace(")", "")
                    param_mas2 = par.split(";")
                    for num2, par2 in enumerate(param_mas2):
                        param_mas2[num2] = par2.strip()
                    par = param_mas2
                elif par[0] == "(" and par[len(par) - 1] == ")":
                    par = par.replace("(", "")
                    par = par.replace(")", "")
                    par = [par]
                param_mas[num] = par

        command_mas.append([command, params, param_mas, str_nom])

    return command_mas

def rotate_all_parts(puzzle_rings, puzzle_arch, puzzle_parts, rotate_parts_param):
    center_x,center_y,angle = float(rotate_parts_param[0]),float(rotate_parts_param[1]),float(rotate_parts_param[2])
    angle = -radians(angle)

    for ring in puzzle_rings:
        ring[1],ring[2] = rotate_point(center_x,center_y, ring[1],ring[2], -angle) # разворачиваем direction, тк центр координат вверху
    for arch in puzzle_arch:
        arch[1],arch[2] = rotate_point(center_x,center_y, arch[1],arch[2], -angle)
    for part in puzzle_parts:
        for part_arch in part[2]:
            part_arch[2], part_arch[3] = rotate_point(center_x,center_y, part_arch[2], part_arch[3], -angle)

    calc_parts_countur(puzzle_parts, puzzle_arch, True)

def read_puzzle_script_and_init_puzzle(lines,PARTS_COLOR):
    flip_y = flip_x = flip_rotate = skip_check_error = False
    puzzle_name, puzzle_author, puzzle_scale, puzzle_speed, auto_marker, auto_marker_ring, first_cut = "", "", 1, 2, 0, 0, True
    puzzle_link, puzzle_rings, puzzle_arch, puzzle_parts, auto_cut_parts, auto_color_parts, set_color_parts, remove_parts, copy_parts = [], [], [], [], [], [], [], [], []
    part_num, param_calc, ring_num = 0, [], 1

    command_mas = expand_script(lines)

    step,step_total = 0,1
    for command, params, param_mas, _ in command_mas:
        if ["Ring","CopyRing","Renumbering","AutoColorParts","SetColorParts","RotateAllParts","RemoveMicroParts","RemoveSmallParts","HideAllParts","ShowAllParts","InvertAllParts"].count(command)>0:
            step_total += 1
        elif ["MakeCircles","CutCircles","RemoveParts","HideParts","ShowParts","RotateAllParts","RemoveMicroParts","RemoveSmallParts"].count(command)>0:
            step_total += len(param_mas)
        elif ["AutoCutParts","CopyParts","MoveParts"].count(command)>0:
            step_total += len(param_mas)

    ##################################################################
    # инициализация параметров

    for command, params, param_mas, str_nom in command_mas:
        if ["Ring","CopyRing","Renumbering","AutoColorParts","SetColorParts","RotateAllParts","RemoveMicroParts","RemoveSmallParts","HideAllParts","ShowAllParts","InvertAllParts"].count(command)>0:
            step += 1
        elif ["MakeCircles","CutCircles","RemoveParts","HideParts","ShowParts","RotateAllParts","RemoveMicroParts","RemoveSmallParts"].count(command)>0:
            step += len(param_mas)
        elif ["AutoCutParts","CopyParts","MoveParts"].count(command)>0:
            step += len(param_mas)

        percent = int(100 * step / step_total)
        if percent%5==0 and percent!=0:
            try:
                display.set_caption("Please wait! Loading ... " + str(percent) + "%")
                display.update()
            except: pass

        if command == "Name":
            puzzle_name = params
        elif command == "Author":
            puzzle_author = params
        elif command == "SkipCheckError":
            if int(params) == 1:
                skip_check_error = True
        elif command == "Link":
            puzzle_link.append(params)
        elif command == "Scale":
            puzzle_scale = float(params)
        elif command == "Speed":
            puzzle_speed = float(params)
        elif command == "Flip":
            if params.lower().find("y") >= 0:
                flip_y = True
            if params.lower().find("x") >= 0:
                flip_x = True
            if params.lower().find("rotate") >= 0:
                flip_rotate = True

        #########################################################################
        # инициализация кругов головоломки
        elif command == "Param":
            if len(param_mas) != 2: return ("Incorrect 'Param' parameters. In str=" + str(str_nom))
            for param in param_calc:
                if param_mas[1].find(param[0]) != -1:
                    param_mas[1] = param_mas[1].replace(param[0], str(param[1]))
            try:
                param_mas[1] = eval(param_mas[1])
            except:
                return ("Error in 'Param' calculation. In str=" + str(str_nom))
            param_calc.append([param_mas[0], param_mas[1]])
        elif command == "Ring":
            if not (len(param_mas) == 5 or len(param_mas) == 6): return ("Incorrect 'Ring' parameters. In str=" + str(str_nom))
            param_mas[1], param_mas[2] = calc_param(param_mas[1], param_calc), calc_param(param_mas[2], param_calc)
            param_mas[3], param_mas[4] = calc_param(param_mas[3], param_calc), calc_param(param_mas[4], param_calc)
            param_mas5 = param_mas[5] if len(param_mas)==6 else 0
            puzzle_rings.append([ring_num, param_mas[1], param_mas[2], param_mas[3], param_mas[4], 0, param_mas5])
            ring_num += 1

            arch_num = len(puzzle_arch)+1
            puzzle_arch.append([arch_num, param_mas[1], param_mas[2], param_mas[3]])

        elif command == "CopyRing":
            if not (len(param_mas) == 5 or len(param_mas) == 6): return ("Incorrect 'CopyRing' parameters. In str=" + str(str_nom))
            param_mas[3], param_mas[4] = calc_param(param_mas[3], param_calc), calc_param(param_mas[4], param_calc)
            param_mas5 = param_mas[5] if len(param_mas)==6 else 0
            center_x, center_y = copy_ring(int(param_mas[1]),param_mas[2],puzzle_rings)
            puzzle_rings.append([ring_num, center_x, center_y, param_mas[3], param_mas[4], 0, param_mas5])
            ring_num += 1

            arch_num = len(puzzle_arch)+1
            puzzle_arch.append([arch_num, center_x, center_y, param_mas[3]])

        ###############################################################################################################################
        # инициализация всех частей. запускаем скрамбл функцию с одновременной нарезкой. запускаем авто раскраску со смешиванием цветов

        elif command == "AutoCutParts":
            auto_cut_parts = param_mas
            init_cut_all_ring_to_parts(puzzle_rings, puzzle_arch, puzzle_parts, auto_cut_parts, first_cut)
            first_cut = False

        elif command == "MakeCircles":
            make_circles = param_mas
            make_def_circles(puzzle_rings, puzzle_arch, puzzle_parts, make_circles)
            first_cut = False

        elif command == "CutCircles":
            cut_circles = param_mas
            cut_def_circles(puzzle_rings, puzzle_arch, puzzle_parts, cut_circles)

        elif command == "RemoveParts":
            remove_parts = param_mas
            remove_def_parts(puzzle_parts, remove_parts)

        elif command == "RemoveMicroParts" or command == "RemoveSmallParts":
            area_param = param_mas
            remove_micro_parts(puzzle_parts, area_param)

        elif command == "CopyParts":
            copy_parts = param_mas
            copy_def_parts(copy_parts, puzzle_rings, puzzle_arch, puzzle_parts)
        elif command == "MoveParts":
            copy_parts = param_mas
            copy_def_parts(copy_parts, puzzle_rings, puzzle_arch, puzzle_parts, True)

        elif command == "Renumbering":
            sort_and_renum_all_parts(puzzle_parts)

        elif command == "HideParts":
            hide_parts = param_mas
            hide_show_def_parts(puzzle_parts, hide_parts, -1, False)
        elif command == "ShowParts":
            hide_parts = param_mas
            hide_show_def_parts(puzzle_parts, hide_parts, 1, False)
        elif command == "HideAllParts":
            hide_show_def_parts(puzzle_parts, [], -1, True)
        elif command == "ShowAllParts":
            hide_show_def_parts(puzzle_parts, [], 1, True)
        elif command == "InvertAllParts":
            hide_show_def_parts(puzzle_parts, [], 0, True)

        elif command == "AutoColorParts":
            auto_color_parts = param_mas
            init_color_all_parts(puzzle_parts, puzzle_rings, auto_color_parts, PARTS_COLOR)
        elif command == "SetColorParts":
            set_color_parts = param_mas
            set_color_all_parts(puzzle_parts, set_color_parts)

        elif command == "RotateAllParts":
            param_mas[0], param_mas[1], param_mas[2] = calc_param(param_mas[0], param_calc), calc_param(param_mas[1], param_calc), calc_param(param_mas[2], param_calc)
            rotate_parts_param = param_mas
            rotate_all_parts(puzzle_rings, puzzle_arch, puzzle_parts, rotate_parts_param)

        elif command == "AutoMarker":
            if is_number(params):
                auto_marker = int(params)
            else:
                auto_marker =1
        elif command == "AutoMarkerRing":
            if is_number(params):
                auto_marker_ring = int(params)
            else:
                auto_marker_ring =1

        elif command == "End" or command == "Stop" or command == "Exit" or command == "Quit":
            break

        ########################################################################################
        # блок для загрузки скомпилированной головоломки. загружаем координаты всех частей
        elif command == "Arch":
            if len(param_mas) != 4: return ("Incorrect 'Arch' parameters. In str=" + str(str_nom))
            param_mas[1], param_mas[2], param_mas[3] = calc_param(param_mas[1], param_calc), calc_param(param_mas[2], param_calc), calc_param(param_mas[3], param_calc)
            puzzle_arch.append([int(param_mas[0]), param_mas[1], param_mas[2], param_mas[3]])
        elif command == "Part":
            if len(param_mas) == 2:
                part_num = int(param_mas[0])
                puzzle_parts.append([part_num, int(param_mas[1]), []])
            else:
                return ("Incorrect 'Part' parameters. In str=" + str(str_nom))
        elif command == "PartArch":
            if len(param_mas) == 4 and part_num > 0:
                part = find_element(part_num, puzzle_parts)
                param_mas[2], param_mas[3] = calc_param(param_mas[2], param_calc), calc_param(param_mas[3], param_calc)
                part_arch = part[2]
                part_arch.append([int(param_mas[0]), int(param_mas[1]), param_mas[2], param_mas[3]])
            else:
                return ("Incorrect 'PartArch' parameters. In str=" + str(str_nom))

    return puzzle_name, puzzle_author, puzzle_link, puzzle_scale, puzzle_speed, puzzle_rings, puzzle_arch, puzzle_parts, auto_cut_parts, auto_color_parts, auto_marker, auto_marker_ring, set_color_parts, remove_parts, copy_parts, flip_y, flip_x, flip_rotate, skip_check_error

def resize_window(puzzle_rings, puzzle_arch, puzzle_parts, puzzle_scale, BORDER):
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
            for part_arch in part[2]:
                part_arch[2] = part_arch[2] * puzzle_scale + shift
                part_arch[3] = part_arch[3] * puzzle_scale + shift

    # изменим размеры окна
    WIN_WIDTH, WIN_HEIGHT = 0, 0
    for ring in puzzle_rings:
        if ring[6]!= 0: continue
        xx = ring[1] + ring[3] + BORDER
        WIN_WIDTH = xx if xx > WIN_WIDTH else WIN_WIDTH
        yy = ring[2] + ring[3] + BORDER
        WIN_HEIGHT = yy if yy > WIN_HEIGHT else WIN_HEIGHT

    return WIN_WIDTH, WIN_HEIGHT

def align_cordinates(puzzle_rings, puzzle_arch, puzzle_parts, puzzle_scale, flip_x, flip_y, flip_rotate, BORDER):
    # выровняем относительно осей. чтобы не было сильных сдвигов
    for nn, ring in enumerate(puzzle_rings):
        if ring[6] != 0: continue
        if nn == 0:
            min_x, min_y = ring[1] - ring[3], ring[2] - ring[3]
        else:
            min_x, min_y = min(min_x, ring[1] - ring[3]), min(min_y, ring[2] - ring[3])
    for part in puzzle_parts: # отдельные части могут быть за пределами колец
        for part_xy in part[4]:
            min_x, min_y = min(min_x, part_xy[0]), min(min_y, part_xy[1])

    for ring in puzzle_rings:
        ring[1], ring[2] = ring[1] - min_x, ring[2] - min_y
    for arch in puzzle_arch:
        arch[1], arch[2] = arch[1] - min_x, arch[2] - min_y
    for part in puzzle_parts:
        for part_arch in part[2]:
            part_arch[2], part_arch[3] = part_arch[2] - min_x, part_arch[3] - min_y

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
            for part_arch in part[2]:
                part_arch[2] = part_arch[2] * puzzle_scale + shift
                part_arch[3] = part_arch[3] * puzzle_scale + shift

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
            for part_arch in part[2]:
                part_arch[2], part_arch[3] = part_arch[2] + min_x, part_arch[3] + min_y

    # изменим размеры окна
    WIN_WIDTH, WIN_HEIGHT = 0, 0
    for ring in puzzle_rings:
        if ring[6]!= 0: continue
        xx = ring[1] + ring[3] + BORDER
        WIN_WIDTH = xx if xx > WIN_WIDTH else WIN_WIDTH
        yy = ring[2] + ring[3] + BORDER
        WIN_HEIGHT = yy if yy > WIN_HEIGHT else WIN_HEIGHT

    calc_parts_countur(puzzle_parts, puzzle_arch, True)
    for part in puzzle_parts: # отдельные части могут быть за пределами колец
        for part_xy in part[4]:
            xx = part_xy[0] + BORDER
            WIN_WIDTH = xx if xx > WIN_WIDTH else WIN_WIDTH
            yy = part_xy[1] + BORDER
            WIN_HEIGHT = yy if yy > WIN_HEIGHT else WIN_HEIGHT

    # учтем повороты
    vek_mul = -1
    if flip_x:
        vek_mul = -1 * vek_mul
        for ring in puzzle_rings:
            ring[1] = WIN_WIDTH - ring[1]
        for arch in puzzle_arch:
            arch[1] = WIN_WIDTH - arch[1]
        for part in puzzle_parts:
            for part_arch in part[2]:
                part_arch[2] = WIN_WIDTH - part_arch[2]
    if flip_y:
        vek_mul = -vek_mul
        for ring in puzzle_rings:
            ring[2] = WIN_HEIGHT - ring[2]
        for arch in puzzle_arch:
            arch[2] = WIN_HEIGHT - arch[2]
        for part in puzzle_parts:
            for part_arch in part[2]:
                part_arch[3] = WIN_HEIGHT - part_arch[3]
    if flip_rotate:
        vek_mul = -vek_mul
        for ring in puzzle_rings:
            ring[1], ring[2] = ring[2], ring[1]
        for arch in puzzle_arch:
            arch[1], arch[2] = arch[2], arch[1]
        for part in puzzle_parts:
            for part_arch in part[2]:
                part_arch[2], part_arch[3] = part_arch[3], part_arch[2]

        WIN_WIDTH, WIN_HEIGHT = WIN_HEIGHT, WIN_WIDTH

    if vek_mul == 1:
        for part in puzzle_parts:
            for part_arch in part[2]:
                part_arch[1] = -part_arch[1]

    # размер головоломки
    puzzle_width, puzzle_height = WIN_WIDTH-2*BORDER, WIN_HEIGHT-2*BORDER

    return WIN_WIDTH, WIN_HEIGHT, vek_mul, puzzle_width, puzzle_height

def mouse_move_click(mouse_xx, mouse_yy, mouse_x, mouse_y, mouse_left, mouse_right, puzzle_rings, ring_num, ring_select, direction):
    ring_pos = []
    for ring in puzzle_rings:
        if ring[6]!= 0: continue
        pos = check_circle(ring[1], ring[2], mouse_xx, mouse_yy, ring[3])
        if pos[0]:
            ring_pos.append((ring[0], pos[1]))

    if len(ring_pos) > 0:  # есть внутри круга
        rr = 999999
        for ring_info in ring_pos:
            if ring_info[1] < rr:
                rr = ring_info[1]
                ring_select = ring_info[0]

        if mouse_x + mouse_y > 0:  # есть клик
            direction = -1 if mouse_left else 1 if mouse_right else 0
            ring_num = ring_select

    return ring_num, ring_select, direction

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

def events_check_read_puzzle(events, fl_break, fl_reset, VERSION, BTN_CLICK, BTN_CLICK_STR, BORDER, WIN_WIDTH, WIN_HEIGHT, win_caption, file_ext, puzzle_link, puzzle_rings, puzzle_arch, puzzle_parts, help, photo, undo, moves, moves_stack, redo_stack, ring_num, direction, mouse_xx, mouse_yy, dirname, filename, PARTS_COLOR, auto_marker, auto_marker_ring):
    mouse_x, mouse_y, mouse_left, mouse_right, fil = 0, 0, False, False, ""
    fl_resize = False

    for ev in events:  # Обрабатываем события
        if (ev.type == QUIT):
            if file_ext:
                save_state(dirname, filename)
            return SystemExit, "QUIT"
        if (ev.type == KEYDOWN and ev.key == K_ESCAPE):
            help = 0 if help == 1 else help
            photo = 0 if photo == 1 else photo
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
                window_front(win_caption)

                if typeof(fil) != "str":
                    puzzle_name, puzzle_author, puzzle_link, puzzle_scale, puzzle_speed, puzzle_rings, puzzle_arch, puzzle_parts, puzzle_kol, vek_mul, dirname, filename, WIN_WIDTH, WIN_HEIGHT, puzzle_width, puzzle_height, auto_marker, auto_marker_ring, remove_parts, copy_parts = fil
                    file_ext = fl_break = fl_reset = True
                    if old_width != WIN_WIDTH or old_height != WIN_HEIGHT:
                        fl_reset = False
                else:
                    if fil != "-":
                        if fil == "":
                            fil = "Unknow error"
                        mb.showerror(message=("Bad puzzle-file: " + fil))
                        window_front(win_caption)
        if (BTN_CLICK_STR == "open" or BTN_CLICK_STR == "prev" or BTN_CLICK_STR == "next") and help+photo == 0:
            fl_break = False
            fil = read_file(dirname, filename, BORDER, PARTS_COLOR, BTN_CLICK_STR)
            window_front(win_caption)

            if typeof(fil) != "str":
                puzzle_name, puzzle_author, puzzle_link, puzzle_scale, puzzle_speed, puzzle_rings, puzzle_arch, puzzle_parts, puzzle_kol, vek_mul, dirname, filename, WIN_WIDTH, WIN_HEIGHT, puzzle_width, puzzle_height, auto_marker, auto_marker_ring, remove_parts, copy_parts = fil
                file_ext = fl_break = True
                fl_reset = False
                if file_ext:
                    save_state(dirname, filename)
            else:
                if fil != "-":
                    if fil == "":
                        fil = "Unknow error"
                    mb.showerror(message=("Bad puzzle-file: " + fil))
                    window_front(win_caption)
        if ev.type == DROPFILE and help+photo == 0:
            fl_break = False
            fil = read_file("", ev.file, BORDER, PARTS_COLOR, "drop")
            window_front(win_caption)

            if typeof(fil) != "str":
                puzzle_name, puzzle_author, puzzle_link, puzzle_scale, puzzle_speed, puzzle_rings, puzzle_arch, puzzle_parts, puzzle_kol, vek_mul, dirname, filename, WIN_WIDTH, WIN_HEIGHT, puzzle_width, puzzle_height, auto_marker, auto_marker_ring, remove_parts, copy_parts = fil
                file_ext = fl_break = True
                fl_reset = False
                if file_ext:
                    save_state(dirname, filename)
            else:
                if fil != "-":
                    if fil == "":
                        fil = "Unknow error"
                    mb.showerror(message=("Bad puzzle-file: " + fil))
                    window_front(win_caption)

        if ev.type == VIDEORESIZE:
            # k_wh = WIN_WIDTH/WIN_HEIGHT
            # if k_wh<=ev.w/ev.h:
            #
            # WIN_WIDTH = ev.w
            # WIN_HEIGHT = ev.h




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
            scramble_puzzle(puzzle_rings,puzzle_arch,puzzle_parts,BTN_CLICK_STR)
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

    fil2 = fl_break, fl_reset, file_ext, fl_resize, BTN_CLICK, BTN_CLICK_STR, undo, moves, moves_stack, redo_stack, ring_num, direction, mouse_xx, mouse_yy, mouse_x, mouse_y, mouse_left, mouse_right, help, photo, mouse_xx, mouse_yy
    return fil, fil2

def scramble_puzzle(puzzle_rings,puzzle_arch,puzzle_parts,type):
    # обработка рандома для Скрамбла
    random.seed()
    mouse.set_cursor(SYSTEM_CURSOR_WAITARROW)
    win_caption = display.get_caption()
    display.set_caption("Please wait! Scrambling ...")

    scramble_mul = 1 if type=="scramble" else 10
    for ring in puzzle_rings:
        if typeof(ring[4]) == "list":
            scramble_mul *= 2
            break
    scramble_move = len_puzzle_rings(puzzle_rings) * len(puzzle_parts) * scramble_mul * 3

    step = ring_num_pred = 0
    while step<=scramble_move:
        percent = int(100 * step / scramble_move)
        if percent % 5 == 0:
            try:
                display.set_caption("Please wait! Scrambling ... " + str(percent) + "%")
                display.update()
            except:
                pass

        # поворот круга
        direction = random.choice([-1, 1])
        while True:
            ring_num = random.randint(1, len(puzzle_rings))
            ring = find_element(ring_num, puzzle_rings)
            if ring[6]!=0 : continue
            if ring_num_pred != ring_num: break
        ring_num_pred = ring_num

        # 1. найдем все части внутри круга
        part_mas, part_mas_other = find_parts_in_circle(ring, puzzle_parts)
        if (part_mas) == 0: continue

        # 2. повернем все части внутри круга
        if len(part_mas) > 0:
            angle_rotate = find_angle_rotate(ring, direction)
            rotate_part(ring, part_mas, puzzle_arch, radians(angle_rotate), direction)
            calc_parts_countur(part_mas, puzzle_arch, True)
        step += 1

    calc_parts_countur(puzzle_parts, puzzle_arch)

    mouse.set_cursor(SYSTEM_CURSOR_ARROW)
    if typeof(win_caption)=="str":
        display.set_caption(win_caption)
    elif typeof(win_caption)=="list":
        display.set_caption(win_caption[0])

def init_puzzle(BORDER, PARTS_COLOR):
    fl_init = file_ext = True
    dirname = filename = ""
    app_folder = os.getenv('LOCALAPPDATA')+'\\Geraniums Pot\\'
    app_ini = app_folder+'Geraniums Pot.ini'
    if os.path.isfile(app_ini):
        lines = []
        try:
            with open(app_ini, encoding = 'utf-8', mode = 'r') as f:
                lines = f.readlines()
        except:
            try:
                with open(app_ini, mode='r') as f:
                    lines = f.readlines()
            except: pass

        ini_mas = expand_script(lines)
        for command, params, param_mas, str_nom in ini_mas:
            if command == "DirName":
                dirname = params
            elif command == "PuzzleFile":
                filename = params
                fl_init = False

    if dirname !="" and filename != "":
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
    puzzle_name, puzzle_author, puzzle_link, puzzle_scale, puzzle_speed, puzzle_rings, puzzle_arch, puzzle_parts, auto_cut_parts, auto_color_parts, auto_marker, auto_marker_ring, set_color_parts, remove_parts, copy_parts, flip_y, flip_x, flip_rotate, skip_check_error = fil

    # выравнивание, повороты и масштабирование всех координат
    WIN_WIDTH, WIN_HEIGHT, vek_mul, puzzle_width, puzzle_height = align_cordinates(puzzle_rings, puzzle_arch, puzzle_parts, puzzle_scale, flip_x, flip_y, flip_rotate, BORDER)

    # построение границ деталек
    remove_dublikate_parts(puzzle_parts)
    calc_parts_countur(puzzle_parts,puzzle_arch)

    for ring in puzzle_rings:
        ring[5]=0 # сбросим углы поворота для бермуд

    mouse.set_cursor(SYSTEM_CURSOR_ARROW)
    if typeof(win_caption)=="str":
        display.set_caption(win_caption)

    return puzzle_name, puzzle_author, puzzle_link, puzzle_scale, puzzle_speed, puzzle_rings, puzzle_arch, puzzle_parts, puzzle_kol, vek_mul, dirname, filename, WIN_WIDTH, WIN_HEIGHT, puzzle_width, puzzle_height, auto_marker, auto_marker_ring, remove_parts, copy_parts
