from pygame import *
import os
from tkinter import filedialog as fd
from tkinter import messagebox as mb
import webbrowser
import random

from part import *
from syst import *

def read_puzzle_lines(lines):
    flip_y = flip_x = flip_rotate = skip_check_error = False
    puzzle_name, puzzle_author, puzzle_scale, puzzle_speed, auto_marker = "", "", 1, 2, 0
    puzzle_link, puzzle_rings, puzzle_arch, puzzle_parts, auto_cut_parts, auto_color_parts, set_color_parts, remove_parts = [], [], [], [], [], [], [], []

    part_num, param_calc = 0, []

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
        if pos == -1: continue
        if pos == len(stroka) - 1: continue

        command = stroka[0:pos].strip()
        params = stroka[pos + 1:].strip()

        param_mas = params.split(",")
        for num, par in enumerate(param_mas):
            par = par.strip()
            if par.find("(")>=0 and par.find(")")>=0 and par.find(";")>=0:
                par = par.replace("(","")
                par = par.replace(")","")
                param_mas2 = par.split(";")
                for num2, par2 in enumerate(param_mas2):
                    param_mas2[num2] = par2.strip()
                par = param_mas2
            param_mas[num] = par

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

        elif command == "AutoCutParts":
            auto_cut_parts += param_mas
        elif command == "RemoveParts":
            remove_parts += param_mas

        elif command == "AutoColorParts":
            auto_color_parts = param_mas
        elif command == "SetColorParts":
            set_color_parts += param_mas

        elif command == "AutoMarker":
            auto_marker = int(params)

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
            if len(param_mas) != 5: return ("Incorrect 'Ring' parameters. In str=" + str(str_nom))
            param_mas[1], param_mas[2] = calc_param(param_mas[1], param_calc), calc_param(param_mas[2], param_calc)
            param_mas[3], param_mas[4] = calc_param(param_mas[3], param_calc), calc_param(param_mas[4], param_calc)
            puzzle_rings.append([int(param_mas[0]), param_mas[1], param_mas[2], param_mas[3], param_mas[4], 0])
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

    return puzzle_name, puzzle_author, puzzle_link, puzzle_scale, puzzle_speed, puzzle_rings, puzzle_arch, puzzle_parts, auto_cut_parts, auto_color_parts, auto_marker, set_color_parts, remove_parts, flip_y, flip_x, flip_rotate, skip_check_error

def align_cordinates(puzzle_rings, puzzle_arch, puzzle_parts, puzzle_scale, flip_x, flip_y, flip_rotate, BORDER):
    # выровняем относительно осей. чтобы не было сильных сдвигов
    for nn, ring in enumerate(puzzle_rings):
        if nn == 0:
            min_x, min_y = ring[1] - ring[3], ring[2] - ring[3]
        else:
            min_x, min_y = min(min_x, ring[1] - ring[3]), min(min_y, ring[2] - ring[3])

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
            ring[1], ring[2] = ring[1] + min_x, ring[2] + min_y
        for arch in puzzle_arch:
            arch[1], arch[2] = arch[1] + min_x, arch[2] + min_y
        for part in puzzle_parts:
            for part_arch in part[2]:
                part_arch[2], part_arch[3] = part_arch[2] + min_x, part_arch[3] + min_y

    # изменим размеры окна
    WIN_WIDTH, WIN_HEIGHT = 0, 0
    for ring in puzzle_rings:
        xx = ring[1] + ring[3] + BORDER
        WIN_WIDTH = xx if xx > WIN_WIDTH else WIN_WIDTH
        yy = ring[2] + ring[3] + BORDER
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

    return WIN_WIDTH, WIN_HEIGHT, vek_mul

def mouse_move_click(mouse_xx, mouse_yy, mouse_x, mouse_y, mouse_left, mouse_right, puzzle_rings, ring_num, ring_select, direction):
    ring_pos = []
    for ring in puzzle_rings:
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
            puzzle_kol += len(files)
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

def events_check_read_puzzle(events, fl_break, fl_reset, BTN_CLICK, BTN_CLICK_STR, BORDER, WIN_WIDTH, WIN_HEIGHT, win_caption, file_ext, puzzle_link, puzzle_rings, puzzle_parts, help, photo, scramble_move, undo, moves, moves_stack, ring_num, direction, mouse_xx, mouse_yy, dirname, filename, PARTS_COLOR, auto_marker):
    mouse_x, mouse_y, mouse_left, mouse_right, fil = 0, 0, False, False, ""

    for ev in events:  # Обрабатываем события
        if (ev.type == QUIT):
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
        if (ev.type == KEYDOWN and ev.key == K_F11):
            BTN_CLICK = True
            BTN_CLICK_STR = "prev"
        if (ev.type == KEYDOWN and ev.key == K_F12):
            BTN_CLICK = True
            BTN_CLICK_STR = "next"
        if (ev.type == KEYDOWN and ev.key == K_SPACE):
            BTN_CLICK = True
            BTN_CLICK_STR = "undo"

        if BTN_CLICK_STR == "info" and help+photo == 0:
            for link in puzzle_link:
                if link != "":
                    webbrowser.open(link, new=2, autoraise=True)
        if BTN_CLICK_STR == "about" and help+photo == 0:
            webbrowser.open("https://twistypuzzles.com/forum/viewtopic.php?t=38581", new=2, autoraise=True)
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
                    puzzle_name, puzzle_author, puzzle_link, puzzle_scale, puzzle_speed, puzzle_rings, puzzle_arch, puzzle_parts, puzzle_kol, vek_mul, dirname, filename, WIN_WIDTH, WIN_HEIGHT, auto_marker, remove_parts = fil
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
                puzzle_name, puzzle_author, puzzle_link, puzzle_scale, puzzle_speed, puzzle_rings, puzzle_arch, puzzle_parts, puzzle_kol, vek_mul, dirname, filename, WIN_WIDTH, WIN_HEIGHT, auto_marker, remove_parts = fil
                file_ext = fl_break = True
                fl_reset = False
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
                puzzle_name, puzzle_author, puzzle_link, puzzle_scale, puzzle_speed, puzzle_rings, puzzle_arch, puzzle_parts, puzzle_kol, vek_mul, dirname, filename, WIN_WIDTH, WIN_HEIGHT, auto_marker, remove_parts = fil
                file_ext = fl_break = True
                fl_reset = False
            else:
                if fil != "-":
                    if fil == "":
                        fil = "Unknow error"
                    mb.showerror(message=("Bad puzzle-file: " + fil))
                    window_front(win_caption)

        if ev.type == MOUSEMOTION:
            mouse_xx, mouse_yy = ev.pos[0], ev.pos[1]

        if ev.type == MOUSEBUTTONUP:
            if ev.type == MOUSEBUTTONUP and (ev.button == 2 or ev.button == 6 or ev.button == 7):
                BTN_CLICK = True
                BTN_CLICK_STR = "undo"

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

        if BTN_CLICK_STR == "scramble" and help!=1:
            fl_break = False
            scramble_move = len(puzzle_rings)*len(puzzle_parts)
            if scramble_move<50: scramble_move *= 3
            random.seed()

        if BTN_CLICK_STR == "undo" and help+photo == 0:
            fl_break = False
            if len(moves_stack) > 0:
                undo = True
                moves -= 1
                ring_num, direction = moves_stack.pop()
                direction = -direction

        BTN_CLICK = False
        BTN_CLICK_STR = ""

    fil2 = fl_break, fl_reset, file_ext, BTN_CLICK, BTN_CLICK_STR, scramble_move, undo, moves, moves_stack, ring_num, direction, mouse_xx, mouse_yy, mouse_x, mouse_y, mouse_left, mouse_right, help, photo, mouse_xx, mouse_yy
    return fil, fil2

def init_puzzle(BORDER, PARTS_COLOR):
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
        SetColorParts: (1;3;7),6,   (15;18;22),3,   (2;6;9),5,  (17;21;23),4
    """.strip('\n')

    fil = read_file("", "", BORDER, PARTS_COLOR, "init", init)
    return fil

def read_file(dirname, filename, BORDER, PARTS_COLOR, fl, init=""):
    # загрузка файла
    lines, puzzle_kol, dirname, filename, error_str = load_puzzle(fl, init, dirname, filename)
    if error_str != "": return error_str

    # прочитаем строки файла
    fil = read_puzzle_lines(lines)
    if typeof(fil) == "str": return fil
    puzzle_name, puzzle_author, puzzle_link, puzzle_scale, puzzle_speed, puzzle_rings, puzzle_arch, puzzle_parts, auto_cut_parts, auto_color_parts, auto_marker, set_color_parts, remove_parts, flip_y, flip_x, flip_rotate, skip_check_error = fil

    mouse.set_cursor(SYSTEM_CURSOR_WAITARROW)
    win_caption = display.get_caption()
    display.set_caption("Please wait! Loading ...")

    # инициализация всех частей. запускаем скрамбл функцию с одновременной нарезкой. запускаем авто раскраску со смешиванием цветов
    if len(auto_cut_parts)>0:
        puzzle_arch,puzzle_parts = init_cut_all_ring_to_parts(puzzle_rings, auto_cut_parts, remove_parts)
    if len(auto_color_parts)>0 or len(set_color_parts)>0:
        init_color_all_parts(puzzle_parts, puzzle_rings, auto_color_parts, set_color_parts, PARTS_COLOR)
    if len(remove_parts)>0:
        remove_def_parts(puzzle_parts, remove_parts)

    # выравнивание, повороты и масштабирование всех координат
    WIN_WIDTH, WIN_HEIGHT, vek_mul = align_cordinates(puzzle_rings, puzzle_arch, puzzle_parts, puzzle_scale, flip_x, flip_y, flip_rotate, BORDER)

    # построение границ деталек
    calc_parts_countur(puzzle_parts,puzzle_arch)

    mouse.set_cursor(SYSTEM_CURSOR_ARROW)
    if typeof(win_caption)=="str":
        display.set_caption(win_caption)

    return puzzle_name, puzzle_author, puzzle_link, puzzle_scale, puzzle_speed, puzzle_rings, puzzle_arch, puzzle_parts, puzzle_kol, vek_mul, dirname, filename, WIN_WIDTH, WIN_HEIGHT, auto_marker, remove_parts

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
