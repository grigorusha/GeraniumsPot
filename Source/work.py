from part import *
from syst import *

from pygame import *

import os,webbrowser,ptext

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
            fl_inner,pos = False,-1
            for inner in ring[7]:
                for nn,ring_info in enumerate(ring_pos):
                    if inner[0]==ring_info[0]:
                        fl_inner = True
                    if ring[0]==ring_info[0]:
                        pos=nn
            if fl_inner and pos>=0:
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

def draw_all_text(screen, font, font2, puzzle_kol, rings_kol, parts_kol, moves, solved, button_Save, button_Help, toggle_Marker, toggle_Circle, button_y2, button_y3, button_y4):
    WHITE_COLOR, RED_COLOR, GREEN_COLOR, BLUE_COLOR, YELLOW_COLOR = "#FFFFFF", "#FF0000", "#008000", "#0000FF", "#FFFF00"

    # 2
    # Пишем количество уровней
    text_puzzles = font2.render(str(puzzle_kol) + ' puzzles', True, WHITE_COLOR)
    text_puzzles_place = text_puzzles.get_rect(topleft=(button_Save.textRect.right + 10, button_y2 + 1))
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
    if check_os_platform()=="windows":
        user_profile = 'LOCALAPPDATA'
    else:
        user_profile = 'HOME'

    command_mas = []
    command_mas.append(["", "# Geraniums Pot - Intersecting Circles Puzzles Simulator. Ini-file:" + "\n", []])
    command_mas.append(["", "\n", []])
    command_mas.append(["DirName", dirname, []])
    command_mas.append(["PuzzleFile", filename, []])

    app_folder = os.path.join(os.getenv(user_profile),'Geraniums Pot '+VERSION)
    if not os.path.isdir(app_folder):
        try:
            os.mkdir(app_folder)
        except: return
        if not os.path.isdir(app_folder):
            return

    app_ini = os.path.join(app_folder,'Geraniums Pot.ini')
    save_file(app_ini, command_mas)

def save_puzzle(dirname, filename, puzzle_name, puzzle_author, puzzle_web_link, puzzle_speed, puzzle_rings, puzzle_arch, puzzle_parts, moves_stack):
    save_puzzle_file = os.path.splitext(filename)[0]+'.save'
    filetypes = (("Puzzle file", "*.save"), ("Any file", "*"))
    save_puzzle_file = fd.asksaveasfilename(title="Save Puzzle", initialdir=dirname, initialfile=os.path.basename(save_puzzle_file), filetypes=filetypes, confirmoverwrite=True)
    if save_puzzle_file == "": return
    #########################################################################################

    command_mas = []
    command_mas.append(["", "# Geraniums Pot - Intersecting Circles Puzzles Simulator. Save-file:" + "\n", []])
    command_mas.append(["", "\n", []])
    command_mas.append(["DirName", "\""+dirname+"\"", []])
    command_mas.append(["PuzzleFile", "\""+filename+"\"", []])
    command_mas.append(["", "\n", []])
    command_mas.append(["Name", puzzle_name, []])
    command_mas.append(["Author", puzzle_author, []])
    for link in puzzle_web_link:
        command_mas.append(["Link", link, []])
    command_mas.append(["", "\n", []])

    command_mas.append(["Speed", puzzle_speed, []])
    command_mas.append(["Scale", 1, []])
    command_mas.append(["", "\n", []])

    if len(moves_stack)>0:
        command_mas.append(["", "# ring number, direction"+"\n", []])
        command_mas.append(["MovesStack", "", moves_stack])
        command_mas.append(["", "\n", []])

    fl_linked = False
    command_mas.append(["", "# ring number, center coordinates x y, radius, angle, type, gear ratio"+"\n", []])
    for ring in puzzle_rings:
        angle_mas_str = ring[4]
        if typeof(ring[4]) == "list":
            angle_mas, angle_pos, angle_mas_str = ring[4], ring[5], "("
            for nn in range(len(angle_mas)):
                angle_mas_str += str(mas_pos(angle_mas,nn+angle_pos))
                if nn<len(angle_mas)-1:
                    angle_mas_str += ","
            angle_mas_str += ")"
        ring_mas = [ ring[0],ring[1],ring[2],ring[3],angle_mas_str ]
        if ring[6]!=0 and (len(ring[8]) == 0 or len(ring[8][1]) == 0):
            ring_mas.append(ring[6])
        if not (len(ring[8]) == 0 or len(ring[8][1]) == 0):
            ring_mas.append(ring[6])
            ring_mas.append(ring[8][0])
            fl_linked = True

        command_mas.append(["Ring", "", ring_mas])
    command_mas.append(["", "\n", []])

    if fl_linked:
        def check_linked_mass(ring_num, linked_mass):
            if len(linked_mass)==0: False
            for linked in linked_mass:
                if (ring_num in linked) or (-ring_num in linked):
                    return True
            return False

        linked_mass = []
        for ring in puzzle_rings:
            if len(ring[8]) == 0 or len(ring[8][1]) == 0: continue
            if not check_linked_mass(ring[0], linked_mass):
                linked = []
                for link in ring[8][1]:
                    linked.append(link[0]*link[1])
                linked_mass.append(linked)

        command_mas.append(["", "# specify linked rings. if the number is negative, then the rotation will be in the opposite direction"+"\n", []])
        command_mas.append(["Linked", "", linked_mass])
        command_mas.append(["", "\n", []])

    command_mas.append(["", "# arch number, center coordinates x y, radius"+"\n", []])
    for arch in puzzle_arch:
        command_mas.append(["Arch", "", [ arch[0],arch[1],arch[2],arch[3] ]])
    command_mas.append(["", "\n", []])

    command_mas.append(["", "# part number, color, visible"+"\n", []])
    command_mas.append(["", "#   marker text, angle, size, shift horizontal vertical"+"\n", []])
    command_mas.append(["", "#   arch number, type, direction, start x y"+"\n", []])
    for part in puzzle_parts:
        command_mas.append(["Part", "", [part[0], part[1], part[2]]])

        part_marker = part[3]
        if len(part_marker)>0:
            command_mas.append(["PartMarker", "", [part_marker[0], part_marker[1], part_marker[2], part_marker[3], part_marker[4]]])
        for part_arch in part[5]:
            command_mas.append(["PartArch", "", [part_arch[0], part_arch[1], part_arch[2], part_arch[3], part_arch[4]]])

    command_mas.append(["", "\n", []])

    save_file(save_puzzle_file, command_mas)

def save_file(filename, command_mas):
    with open(filename, encoding='utf-8', mode='w') as f:
        for command,params,param_mas in command_mas:
            if command=="":
                stroka = str(params)
            else:
                stroka = "" + command + ": "
                if len(param_mas)==0:
                    stroka += str(params)+"\n"
                else:
                    for nn,par in enumerate(param_mas):
                        if typeof(par)=="list":
                            stroka += "("
                            for mm in range(len(par)):
                                stroka += str(par[mm])
                                if mm < len(par) - 1:
                                    stroka += ","
                            stroka += ")"
                        else:
                            stroka += str(par)
                        if nn<len(param_mas)-1:
                            stroka += ", "
                    stroka += "\n"
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
    fl_load_save, puzzle_kol, lines = False, 0, []

    dir = os.path.abspath(os.curdir)
    if os.path.isdir(os.path.join(dir,"Garden")):
        dir = os.path.join(dir,"Garden")
    if dir != "":
        for root, dirs, files in os.walk(dir):
            for fil in files:
                if os.path.splitext(fil)[1].lower()==".txt":
                    puzzle_kol += 1
    puzzle_kol = 1 if puzzle_kol==0 else puzzle_kol

    ###################################################################################
    if dirname == "":
        dirname = os.path.abspath(os.curdir)
        if os.path.isdir(os.path.join(dirname,"Garden")):
            dirname = os.path.join(dirname,"Garden")
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
            filetypes = (("Puzzle files", "*.txt;*.save"), ("Puzzles", "*.txt"), ("Saves", "*.save"), ("Any files", "*"))
            if check_os_platform() != "windows":
                filetypes = (("Puzzles", "*.txt"), ("Saves", "*.save"), ("Any files", "*"))
            f_name = fd.askopenfilename(title="Open Puzzle", initialdir=dirname, filetypes=filetypes)
            if f_name == "":
                return [],0,"","", False, "-"
            filename = f_name
            dirname = os.path.dirname(filename)
        elif fl == "drop" and filename != "":
            dirname = os.path.dirname(filename)

        _, file_extension = os.path.splitext(filename)
        if file_extension.lower()==".save":
            fl_load_save = True

        try:
            with open(filename, encoding = 'utf-8', mode = 'r') as f:
                lines = f.readlines()
        except:
            try:
                with open(filename, mode='r') as f:
                    lines = f.readlines()
            except:
                return [],0,"","", False, "Can not open the file"
    return lines, puzzle_kol, dirname, filename,  fl_load_save, ""

def dir_test(dir_garden = "", dir_screenshots = ""):
    mas_files = []
    if dir_screenshots == "":
        dir_screenshots = os.path.abspath(os.curdir)
        if os.path.isdir(os.path.join(dir_screenshots,"ScreenShots")):
            dir_screenshots = os.path.join(dir_screenshots,"ScreenShots")

    if dir_garden == "":
        dir = os.path.abspath(os.curdir)
        if os.path.isdir(os.path.join(dir,"Garden")):
            dir = os.path.join(dir,"Garden")
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
    if check_os_platform()=="windows":
        user_profile = 'LOCALAPPDATA'
    else:
        user_profile = 'HOME'

    fl_init = file_ext = True
    dirname = filename = ""
    if not fl_esc:
        app_folder = os.path.join(os.getenv(user_profile),'Geraniums Pot '+VERSION)
        app_ini = os.path.join(app_folder,'Geraniums Pot.ini')
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

def resize_puzzle(new_win_width, new_win_height, puzzle_width, puzzle_height, BORDER, PANEL, puzzle_rings, puzzle_arch, puzzle_parts, puzzle_lines):
    puzzle_width_, puzzle_height_ = puzzle_width - BORDER * 2, puzzle_height - BORDER * 2
    original_scale = puzzle_width_ / puzzle_height_
    width, height = new_win_width - BORDER * 2, new_win_height - PANEL - BORDER * 2
    screen_scale = width / height

    new_scale = 1
    if original_scale > screen_scale:
        new_scale = width / puzzle_width_
    elif original_scale < screen_scale:
        new_scale = height / puzzle_height_

    if new_scale != 1:
        vek_mul, puzzle_width, puzzle_height = align_cordinates(puzzle_rings, puzzle_arch, puzzle_parts, puzzle_lines, new_scale, False, False, False, BORDER)
        calc_all_spline(puzzle_rings, puzzle_arch, puzzle_parts)
    else:
        vek_mul = -1

    WIN_WIDTH, WIN_HEIGHT = new_win_width, new_win_height - PANEL
    return puzzle_width, puzzle_height, WIN_WIDTH, WIN_HEIGHT, vek_mul

def events_check_read_puzzle(events, fl_break, fl_reset, fl_test, VERSION, BTN_CLICK, BTN_CLICK_STR, BORDER, WIN_WIDTH, WIN_HEIGHT, puzzle_width, puzzle_height, PANEL, win_caption, file_ext, puzzle_name, puzzle_author, puzzle_web_link, puzzle_speed, puzzle_rings, puzzle_arch, puzzle_parts, puzzle_lines, puzzle_points, help, photo, undo, moves, moves_stack, redo_stack, ring_num, direction, mouse_xx, mouse_yy, dirname, filename, PARTS_COLOR, auto_marker, auto_marker_ring, ctrl_pressed, shift_pressed, resized):
    mouse_x, mouse_y, mouse_left, mouse_right, fil = 0, 0, False, False, ""
    fl_resize = fl_screenshot = False

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

        if (ev.type == KEYDOWN):
            key_mas     = [K_F1,   K_F2,    K_F3,   K_F4,       K_F5,    K_F6,     K_F7,         K_F8,            K_F9,   K_F11,  K_F12,  K_SPACE, K_BACKSPACE]
            cammand_mas = ["help", "reset", "open", "scramble", "photo", "marker", "screenshot", "superscramble", "save", "prev", "next", "undo",  "redo"]
            try: pos = key_mas.index(ev.key)
            except: pos = -1
            if pos>=0:
                BTN_CLICK = True
                BTN_CLICK_STR = cammand_mas[pos]
            if (ev.key == pygame.K_o and ctrl_pressed): # Ctrl-O
                BTN_CLICK,BTN_CLICK_STR = True, "open"

        if (ev.type == KEYDOWN):
            if (ev.key == K_LCTRL or ev.key == K_RCTRL):
                ctrl_pressed = True
            elif (ev.key == K_LSHIFT or ev.key == K_RSHIFT):
                shift_pressed = True
        if (ev.type == KEYUP):
            if (ev.key == K_LCTRL or ev.key == K_RCTRL):
                ctrl_pressed = False
            elif (ev.key == K_LSHIFT or ev.key == K_RSHIFT):
                shift_pressed = False

        if BTN_CLICK_STR == "info" and help+photo == 0:
            for link in puzzle_web_link:
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
        if BTN_CLICK_STR == "marker":
            auto_marker = 1 - auto_marker
        if BTN_CLICK_STR == "screenshot":
            fl_screenshot = True

        if (BTN_CLICK_STR == "open" or ev.type == DROPFILE or BTN_CLICK_STR == "prev" or BTN_CLICK_STR == "next" or BTN_CLICK_STR == "reset") and help+photo == 0:
            if BTN_CLICK_STR == "reset" and (not file_ext):
                fl_break = fl_reset = True
            else:
                if BTN_CLICK_STR == "reset":
                    old_width, old_height = WIN_WIDTH, WIN_HEIGHT
                    fil = read_file(dirname, filename, BORDER, PARTS_COLOR, "reset")
                elif ev.type == DROPFILE:
                    fl_break = False
                    fil = read_file("", ev.file, BORDER, PARTS_COLOR, "drop")
                else:
                    fl_break = False
                    fil = read_file(dirname, filename, BORDER, PARTS_COLOR, BTN_CLICK_STR)

                if not fl_test:
                    window_front(win_caption)

                if typeof(fil) != "str":
                    puzzle_name, puzzle_author, puzzle_web_link, puzzle_scale, puzzle_speed, puzzle_rings, puzzle_arch, puzzle_parts, puzzle_lines, puzzle_points, puzzle_kol, vek_mul, dirname, filename, puzzle_width, puzzle_height, auto_marker, auto_marker_ring, remove_parts, copy_parts, show_hidden_circles, moves, moves_stack, fl_load_save = fil
                    if BTN_CLICK_STR == "reset":
                        file_ext, fl_break, fl_reset = True, True, True
                        if old_width != WIN_WIDTH or old_height != WIN_HEIGHT:
                            fl_reset = False
                        else:
                            puzzle_width,puzzle_height,WIN_WIDTH,WIN_HEIGHT,vek_mul = resize_puzzle(WIN_WIDTH, WIN_HEIGHT+PANEL, puzzle_width,puzzle_height, BORDER,PANEL, puzzle_rings,puzzle_arch,puzzle_parts,puzzle_lines)
                            # fl_resize = True
                    else:
                        file_ext, fl_break, fl_reset = True, True, False
                        if file_ext:
                            save_state(dirname, filename, VERSION)
                else:
                    if fil == "break":
                        fl_break, fl_reset, file_ext = True, False, False
                    elif fil != "-":
                        if fil == "":
                            fil = "Unknow error"
                        mb.showerror(message=("Bad puzzle-file: " + fil))
                        if not fl_test:
                            window_front(win_caption)

        if (BTN_CLICK_STR == "save") and help+photo == 0:
            fl_break = False
            save_puzzle(dirname, filename, puzzle_name, puzzle_author, puzzle_web_link, puzzle_speed, puzzle_rings, puzzle_arch, puzzle_parts, moves_stack)

        if ev.type == VIDEORESIZE:
            puzzle_width,puzzle_height,WIN_WIDTH,WIN_HEIGHT,vek_mul = resize_puzzle(ev.w,ev.h, puzzle_width,puzzle_height, BORDER,PANEL, puzzle_rings,puzzle_arch,puzzle_parts,puzzle_lines)

            # root = Tk() # 2 if root.state() == 'zoomed' else 1
            resized = 1
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

    fil2 = fl_break, fl_reset, file_ext, fl_resize, resized, BTN_CLICK, BTN_CLICK_STR, undo, moves, moves_stack, redo_stack, ring_num, direction, mouse_xx, mouse_yy, mouse_x, mouse_y, mouse_left, mouse_right, help, photo, WIN_WIDTH, WIN_HEIGHT, puzzle_width, puzzle_height, auto_marker, fl_screenshot, ctrl_pressed, shift_pressed
    return fil, fil2

def read_puzzle_script_and_init_puzzle(lines, dirname, filename, PARTS_COLOR):
    flip_y = flip_x = flip_rotate = skip_check_error = show_hidden_circles = False
    puzzle_name, puzzle_author, puzzle_scale, puzzle_speed, auto_marker, auto_marker_ring, auto_renumbering, first_cut, first_coloring, first_arch = "", "", 1, 2, 0, 0, 1, True, True, True
    puzzle_web_link, puzzle_rings, puzzle_arch, puzzle_parts, puzzle_lines, puzzle_points, auto_cut_parts, auto_color_parts, set_color_parts, remove_parts, copy_parts = [], [], [], [], [], [], [], [], [], [], []
    part_num, param_calc, ring_num, line_num = 0, [], 1, 1
    moves, moves_stack = 0, []

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
            puzzle_web_link.append(params)
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
            if not (len(param_mas) >= 5 or len(param_mas) <= 7): return ("Incorrect 'Ring' parameters. In str=" + str(str_nom))
            param_mas[1], param_mas[2] = calc_param(param_mas[1], param_calc), calc_param(param_mas[2], param_calc)
            param_mas[3], param_mas[4] = calc_param(param_mas[3], param_calc), calc_param(param_mas[4], param_calc)
            param_mas5 = int(param_mas[5]) if len(param_mas)>=6 else 0
            param_mas6 = int(param_mas[6]) if len(param_mas)>=7 else 0
            puzzle_rings.append([ring_num, param_mas[1], param_mas[2], param_mas[3], param_mas[4], 0, param_mas5, [], [param_mas6, []], []])
            ring_num += 1

            arch_num = len(puzzle_arch)+1
            puzzle_arch.append([arch_num, param_mas[1], param_mas[2], param_mas[3]])
            check_all_rings(puzzle_rings)

        elif command == "CopyRing".lower():
            if not (len(param_mas) >= 5 or len(param_mas) <= 7): return ("Incorrect 'CopyRing' parameters. In str=" + str(str_nom))
            param_mas[3], param_mas[4] = calc_param(param_mas[3], param_calc), calc_param(param_mas[4], param_calc)
            param_mas5 = int(param_mas[5]) if len(param_mas)>=6 else 0
            param_mas6 = int(param_mas[6]) if len(param_mas)>=7 else 0
            center_x, center_y = copy_ring(int(param_mas[1]),param_mas[2],puzzle_rings)
            puzzle_rings.append([ring_num, center_x, center_y, param_mas[3], param_mas[4], 0, param_mas5, [], [param_mas6, []], []])
            ring_num += 1

            arch_num = len(puzzle_arch)+1
            puzzle_arch.append([arch_num, center_x, center_y, param_mas[3]])
            check_all_rings(puzzle_rings)

        elif command == "Linked".lower():
            linked_mas = param_mas
            link_rings(puzzle_rings, linked_mas)

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
            init_cut_all_ring_to_parts(puzzle_rings, puzzle_arch, puzzle_parts, puzzle_points, auto_cut_parts, auto_renumbering, first_cut)
            first_cut = False

        elif command == "MakeCircles".lower():
            make_circles = param_mas
            make_def_circles(puzzle_rings, puzzle_arch, puzzle_parts, make_circles, True)
            first_cut = False

        elif command == "RotateCircles".lower():
            rotate_circles = param_mas
            rotate_def_circles(puzzle_rings, puzzle_arch, puzzle_parts, puzzle_points, rotate_circles, auto_renumbering)

        elif command == "CutCircles".lower():
            cut_circles = param_mas
            cut_def_circles(puzzle_rings, puzzle_arch, puzzle_parts, cut_circles, auto_renumbering)

        elif command == "CutLines".lower():
            cut_lines = param_mas
            cut_def_lines(puzzle_lines, puzzle_parts, puzzle_arch, cut_lines, auto_renumbering)

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
        elif command == "AutoRenumbering".lower():
            auto_renumbering = int(params) if is_number(params) else 1

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

        elif command == "DirName".lower():
            dirname = params.replace("\"","")
        elif command == "PuzzleFile".lower():
            filename = params.replace("\"","")

        elif command == "MovesStack".lower():
            for move in param_mas:
                moves_stack.append([int(move[0]),int(move[1])])
            moves = len(moves_stack)

        elif command == "Arch".lower():
            if first_arch:
                puzzle_arch, first_arch = [], False
            if len(param_mas) != 4: return ("Incorrect 'Arch' parameters. In str=" + str(str_nom))
            puzzle_arch.append([int(param_mas[0]), float(param_mas[1]), float(param_mas[2]), float(param_mas[3])])
        elif command == "Part".lower():
            if len(param_mas) == 3:
                part_num = int(param_mas[0])
                puzzle_parts.append([part_num, int(param_mas[1]), int(param_mas[2]), [], [], [], [], [], 0])
            else:
                return ("Incorrect 'Part' parameters. In str=" + str(str_nom))
        elif command == "PartMarker".lower():
            if len(param_mas) == 5 and part_num > 0:
                part = find_element(part_num, puzzle_parts)
                part[3] = [param_mas[0], float(param_mas[1]), float(param_mas[2]), float(param_mas[3]), float(param_mas[4]), ""]
            else:
                return ("Incorrect 'PartArch' parameters. In str=" + str(str_nom))
        elif command == "PartArch".lower():
            if len(param_mas) == 5 and part_num > 0:
                part = find_element(part_num, puzzle_parts)
                part_arch = part[5]
                part_arch.append([int(param_mas[0]), int(param_mas[1]), int(param_mas[2]), float(param_mas[3]), float(param_mas[4]), 0])
            else:
                return ("Incorrect 'PartArch' parameters. In str=" + str(str_nom))

    return puzzle_name, puzzle_author, puzzle_web_link, puzzle_scale, puzzle_speed, puzzle_rings, puzzle_arch, puzzle_parts, puzzle_lines, puzzle_points, auto_cut_parts, auto_color_parts, auto_marker, auto_marker_ring, set_color_parts, remove_parts, copy_parts, flip_y, flip_x, flip_rotate, skip_check_error, show_hidden_circles, dirname, filename, moves, moves_stack

def test_mode_screenshot(game_scr, puzzle_name,puzzle_rings,puzzle_arch,puzzle_parts,puzzle_points, fl_test, fl_test_photo, fl_test_scramble, fl_screenshot, count_test_scramble, photo_screen, dir_screenshots, sub_folder, GAME, PHOTO, BORDER):
    if fl_test:
        if count_test_scramble == 0:
            # сохраним скрин решенной головоломки
            if sub_folder != "":
                if not os.path.isdir(dir_screenshots + sub_folder):
                    os.mkdir(dir_screenshots + sub_folder)
            screenshot = os.path.join(dir_screenshots + sub_folder, puzzle_name + ".jpg")
            pygame.image.save(game_scr, screenshot)

            # сохраним скрин с открытым фото реальной головоломки
            if fl_test_photo and photo_screen != "":
                game_scr.blit(photo_screen, (GAME[0] - PHOTO[0] - BORDER // 3, BORDER // 3))
                draw.rect(game_scr, Color("#B88800"), (GAME[0] - PHOTO[0] - 2 * (BORDER // 3), 0, PHOTO[0] + 2 * (BORDER // 3), PHOTO[1] + 2 * (BORDER // 3)), BORDER // 3)
                screenshot2 = os.path.join(dir_screenshots + sub_folder, puzzle_name + " (photo).jpg")
                pygame.image.save(game_scr, screenshot2)

        if fl_test_scramble > 0:
            # сохраним скрин запутанной головоломки
            if count_test_scramble > 0:
                screenshot = os.path.join(dir_screenshots + sub_folder, puzzle_name + " (scramble " + str(count_test_scramble) + ").jpg")
                pygame.image.save(game_scr, screenshot)
            if count_test_scramble < fl_test_scramble:
                scramble_puzzle(puzzle_rings, puzzle_arch, puzzle_parts, puzzle_points, "scramble")
                count_test_scramble += 1
                return True
        return False
    elif fl_screenshot:
        # сохраним скрин решенной головоломки
        if not os.path.isdir(dir_screenshots):
            os.mkdir(dir_screenshots)
        screenshot = os.path.join(dir_screenshots, puzzle_name + ".jpg")
        pygame.image.save(game_scr, screenshot)

        # скопируем скрин в буфер обмена
        send_to_clipboard(screenshot)
    return True

def draw_all_markers(game_scr, puzzle_parts,puzzle_rings, auto_marker,auto_marker_ring, BLACK_COLOR,WHITE_COLOR,RED_COLOR):
    for nn, part in enumerate(puzzle_parts):
        marker_sprite = ""
        marker_color = BLACK_COLOR if part[1] != 1 else WHITE_COLOR
        center_x, center_y, area, max_radius = part[4]
        if auto_marker:
            marker_sprite, _ = ptext.draw(str(part[0]), (0, 0), color=marker_color, fontsize=10, sysfontname='Verdana', align="center")
        elif len(part[3]) != 0:
            marker_text, marker_angle, marker_size, marker_horizontal_shift, marker_vertical_shift, marker_sprite = part[3]
            center_x += marker_horizontal_shift
            center_y -= marker_vertical_shift
            if marker_sprite == "":
                if marker_size == 0:
                    marker_size = int(area / 200)
                fontname = 'Verdana'
                if "↑↓→←".find(marker_text) >= 0:
                    fontname = 'Arial'
                    marker_sprite, _ = ptext.draw(marker_text, (0, 0), color=marker_color, fontsize=marker_size, fontname="fonts/arialn.ttf", align="center")
                else:
                    marker_sprite, _ = ptext.draw(marker_text, (0, 0), color=marker_color, fontsize=marker_size, sysfontname=fontname, align="center")
                part[3][5] = marker_sprite
            marker_sprite = pygame.transform.rotate(marker_sprite, marker_angle)
        if marker_sprite != "":
            text_marker_place = marker_sprite.get_rect(center=(center_x, center_y))
            game_scr.blit(marker_sprite, text_marker_place)  # Пишем маркер
    if auto_marker_ring:
        for nn, ring in enumerate(puzzle_rings):
            if ring[6] != 0: continue
            center_x, center_y = ring[1], ring[2]
            text_marker, _ = ptext.draw(str(ring[0]), (0, 0), color=RED_COLOR, fontsize=20, sysfontname='Verdana', align="center", owidth=1, ocolor="blue")
            text_marker_place = text_marker.get_rect(center=(center_x, center_y))
            game_scr.blit(text_marker, text_marker_place)  # Пишем маркер

def calc_all_spline(puzzle_rings, puzzle_arch, puzzle_parts):
    # построение границ деталек
    calc_parts_countur(puzzle_parts, puzzle_arch)
    calc_all_centroids(puzzle_parts)

    # вычисление плавного контура кругов
    for ring in puzzle_rings:
        shift = 4
        arch_mas = [[ring[1], ring[2] + ring[3] + shift], [ring[1], ring[2] + ring[3] + shift]]
        ring[9], _ = calc_arch_spline(arch_mas, ring[1], ring[2], ring[3] + shift, 1)

def read_file(dirname, filename, BORDER, PARTS_COLOR, fl, init=""):
    # загрузка файла
    lines, puzzle_kol, dirname, filename, fl_load_save, error_str = load_puzzle(fl, init, dirname, filename)
    if error_str != "": return error_str

    mouse.set_cursor(SYSTEM_CURSOR_WAITARROW)
    win_caption = display.get_caption()
    display.set_caption("Please wait! Loading ...")

    # прочитаем строки файла
    fil = read_puzzle_script_and_init_puzzle(lines, dirname, filename, PARTS_COLOR)
    if typeof(fil) == "str": return fil
    puzzle_name, puzzle_author, puzzle_web_link, puzzle_scale, puzzle_speed, puzzle_rings, puzzle_arch, puzzle_parts, puzzle_lines, puzzle_points, auto_cut_parts, auto_color_parts, auto_marker, auto_marker_ring, set_color_parts, remove_parts, copy_parts, flip_y, flip_x, flip_rotate, skip_check_error, show_hidden_circles, dirname, filename, moves, moves_stack = fil

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

    return puzzle_name, puzzle_author, puzzle_web_link, puzzle_scale, puzzle_speed, puzzle_rings, puzzle_arch, puzzle_parts, puzzle_lines, puzzle_points, puzzle_kol, vek_mul, dirname, filename, puzzle_width, puzzle_height, auto_marker, auto_marker_ring, remove_parts, copy_parts, show_hidden_circles, moves, moves_stack, fl_load_save
