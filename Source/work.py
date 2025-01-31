import os,webbrowser
from tkinter import filedialog as fd
from tkinter import messagebox as mb
import pygame

import glob as var
from part import *
from syst import *

def mouse_move_click(mouse_xx, mouse_yy, mouse_x, mouse_y, mouse_left, mouse_right, puzzle_rings, ring_num, ring_select, direction, puzzle_parts):
    # обработка перемещения и нажатия в игровом поле
    # mouse_xx, mouse_yy - координаты мышки при перемещении. mouse_x, mouse_y - координаты точки клика
    # ring_select - координаты кольца над которым двигается курсор. ring_num - кольцо внутри которого был клик

    circle_area = 3  #  ширина линии круга в пикселях, для проверки касание мышкой

    ring_pos = []
    for ring in puzzle_rings:
        if ring["type"]!= 0: continue
        pos = check_circle(ring["center_x"], ring["center_y"], mouse_xx, mouse_yy, ring["radius"], 2)
        # проверка попадает ли точка внутрь окружности, лежит ли она на окружности с небольшой погрешностью
        # return (length<=rad, compare_xy(in_ring, 1), in_ring, abs(rad-length)) ... length - расстояние до центра, in_ring = length/rad
        if pos["in_circle"]:
            if var.show_hidden_circles:
                ring_pos.append((ring["num"], pos["on_ring"], pos["proporce_cent"], pos["distance_ring"]))
            elif check_ring_intersecting_parts(ring, puzzle_parts):
                ring_pos.append((ring["num"], pos["on_ring"], pos["proporce_cent"], pos["distance_ring"]))

    if len(ring_pos) > 0:  # есть внутри круга
        # проверим концентрические круги
        for ring in puzzle_rings:
            if len(ring["inner"])==0: continue
            fl_inner,pos = False,-1
            for inner in ring["inner"]:
                for nn,ring_info in enumerate(ring_pos):
                    if inner["num"]==ring_info[0]:
                        fl_inner = True
                    if ring["num"]==ring_info[0]:
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

def save_puzzle(BTN_CLICK_STR, dirname, filename, puzzle_name, puzzle_author, puzzle_web_link, puzzle_speed, puzzle_rings, puzzle_arch, puzzle_parts):
    if BTN_CLICK_STR == "savemove" and len(var.moves_stack) > 0:
        save_puzzle_file = os.path.splitext(filename)[0]+'.move'
        filetypes = (("Move file", "*.move"), ("Any file", "*"))
        save_puzzle_file = fd.asksaveasfilename(title="Save Moves", initialdir=dirname, initialfile=os.path.basename(save_puzzle_file), filetypes=filetypes, confirmoverwrite=True)
        if save_puzzle_file == "": return
        #########################################################################################

        command_mas = []
        command_mas.append(["", "# Geraniums Pot - Intersecting Circles Puzzles Simulator. Moves-file:" + "\n", []])
        command_mas.append(["", "\n", []])
        command_mas.append(["Name", puzzle_name, []])
        command_mas.append(["", "\n", []])

        command_mas.append(["", "# ring number, direction" + "\n", []])
        command_mas.append(["MovesStack", "", var.moves_stack])
        command_mas.append(["", "\n", []])

    elif BTN_CLICK_STR == "save":
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

        if len(var.moves_stack)>0:
            command_mas.append(["", "# ring number, direction"+"\n", []])
            command_mas.append(["MovesStack", "", var.moves_stack])
            command_mas.append(["", "\n", []])

        fl_linked = False
        command_mas.append(["", "# ring number, center coordinates x y, radius, angle, type, gear ratio"+"\n", []])
        for ring in puzzle_rings:
            angle_mas_str = ring["angle"]
            if typeof(ring["angle"]) == "list":
                angle_mas, angle_pos, angle_mas_str = ring["angle"], ring["angle_pos"], "("
                for nn in range(len(angle_mas)):
                    angle_mas_str += str(mas_pos(angle_mas,nn+angle_pos))
                    if nn<len(angle_mas)-1:
                        angle_mas_str += ","
                angle_mas_str += ")"
            ring_mas = [ ring["num"],ring["center_x"],ring["center_y"],ring["radius"],angle_mas_str ]
            if ring["type"]!=0 and (len(ring["linked"]) == 0 or len(ring["linked"]["link_mas"]) == 0):
                ring_mas.append(ring["type"])
            if not (len(ring["linked"]) == 0 or len(ring["linked"]["link_mas"]) == 0):
                ring_mas.append(ring["type"])
                ring_mas.append(ring["linked"]["gears"])
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
                if len(ring["linked"]) == 0 or len(ring["linked"]["link_mas"]) == 0: continue
                if not check_linked_mass(ring["num"], linked_mass):
                    linked = []
                    for link in ring["linked"]["link_mas"]:
                        linked.append(link["ring_num"]*link["direction"])
                    linked_mass.append(linked)

            command_mas.append(["", "# specify linked rings. if the number is negative, then the rotation will be in the opposite direction"+"\n", []])
            command_mas.append(["Linked", "", linked_mass])
            command_mas.append(["", "\n", []])

        command_mas.append(["", "# arch number, center coordinates x y, radius"+"\n", []])
        for arch in puzzle_arch:
            command_mas.append(["Arch", "", [ arch["num"],arch["center_x"],arch["center_y"],arch["radius"] ]])
        command_mas.append(["", "\n", []])

        command_mas.append(["", "# part number, color, visible"+"\n", []])
        command_mas.append(["", "#   marker text, angle, size, shift horizontal vertical"+"\n", []])
        command_mas.append(["", "#   arch number, type, direction, start x y"+"\n", []])
        for part in puzzle_parts:
            command_mas.append(["Part", "", [part["num"], part["color"], part["visible"]]])

            part_marker = part["marker"]
            if len(part_marker):
                command_mas.append(["PartMarker", "", [part_marker["text"], part_marker["angle"], part_marker["font_size"], part_marker["horizontal_shift"], part_marker["vertical_shift"]]])
            for part_arch in part["arch_lines"]:
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
    command_depth1 = ["setcolorcircles","setcolorparts","copyparts","moveparts","ring","copyring","line","linked","latch","makecircles","setmarkerparts",
                      "cutcircles","autocolorparts","cutlines","removeparts","removemicroparts","hideparts","showparts","rotateallparts,display"]
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

        param_mas = []
        if params != "":
            depth = 1 if command_depth1.count(command.lower())==1 else 2
            if command.lower()=="param":
                param_mas = params.split(",")
            else:
                param_mas = parse_parameters(params)
                param_mas = parse_cycle(param_mas,depth)
                param_mas = parse_list(param_mas)

        command_mas.append([command, params, param_mas, str_nom])

    return command_mas

def align_cordinates(puzzle_rings, puzzle_arch, puzzle_parts, puzzle_lines, puzzle_scale, flip_x, flip_y, flip_rotate):
    if len(var.puzzle_display):
        min_x, min_y = var.puzzle_display["x1"],var.puzzle_display["y1"]

        for ring in puzzle_rings:
            ring["center_x"], ring["center_y"] = ring["center_x"] - min_x, ring["center_y"] - min_y
        for arch in puzzle_arch:
            arch["center_x"], arch["center_y"] = arch["center_x"] - min_x, arch["center_y"] - min_y
        for part in puzzle_parts:
            for part_arch in part["arch_lines"]:
                part_arch[3], part_arch[4] = part_arch[3] - min_x, part_arch[4] - min_y
        for line in puzzle_lines:
            line[1], line[2] = line[1] - min_x, line[2] - min_y
            line[3], line[4] = line[3] - min_x, line[4] - min_y
        var.puzzle_display["x1"], var.puzzle_display["y1"], var.puzzle_display["x2"],var.puzzle_display["y2"] = 0,0, var.puzzle_display["x2"]-min_x,var.puzzle_display["y2"]-min_y
    else:
        # выровняем относительно осей. чтобы не было сильных сдвигов - подвинем влево
        min_x = None
        for nn, ring in enumerate(puzzle_rings):
            if ring["type"] != 0: continue
            if min_x == None:
                min_x, min_y = ring["center_x"] - ring["radius"], ring["center_y"] - ring["radius"]
            else:
                min_x, min_y = min(min_x, ring["center_x"] - ring["radius"]), min(min_y, ring["center_y"] - ring["radius"])
        for part in puzzle_parts: # отдельные части могут быть за пределами колец
            for part_xy in part["polygon"]:
                min_x, min_y = min(min_x, part_xy[0]), min(min_y, part_xy[1])

        for ring in puzzle_rings:
            ring["center_x"], ring["center_y"] = ring["center_x"] - min_x, ring["center_y"] - min_y
        for arch in puzzle_arch:
            arch["center_x"], arch["center_y"] = arch["center_x"] - min_x, arch["center_y"] - min_y
        for part in puzzle_parts:
            for part_arch in part["arch_lines"]:
                part_arch[3], part_arch[4] = part_arch[3] - min_x, part_arch[4] - min_y
        for line in puzzle_lines:
            line[1], line[2] = line[1] - min_x, line[2] - min_y
            line[3], line[4] = line[3] - min_x, line[4] - min_y

    # учтем масштаб
    if puzzle_scale != 0:
        shift = var.BORDER
        for ring in puzzle_rings:
            ring["center_x"] = ring["center_x"] * puzzle_scale + shift
            ring["center_y"] = ring["center_y"] * puzzle_scale + shift
            ring["radius"] = ring["radius"] * puzzle_scale
        for arch in puzzle_arch:
            arch["center_x"] = arch["center_x"] * puzzle_scale + shift
            arch["center_y"] = arch["center_y"] * puzzle_scale + shift
            arch["radius"] = arch["radius"] * puzzle_scale
        for part in puzzle_parts:
            for part_arch in part["arch_lines"]:
                part_arch[3] = part_arch[3] * puzzle_scale + shift
                part_arch[4] = part_arch[4] * puzzle_scale + shift
            if len(part["marker"]):
                part["marker"]["horizontal_shift"] = part["marker"]["horizontal_shift"] * puzzle_scale
                part["marker"]["vertical_shift"] = part["marker"]["vertical_shift"] * puzzle_scale
        for line in puzzle_lines:
            line[1] = line[1] * puzzle_scale + shift
            line[2] = line[2] * puzzle_scale + shift
            line[3] = line[3] * puzzle_scale + shift
            line[4] = line[4] * puzzle_scale + shift
        if len(var.puzzle_display):
            var.puzzle_display["x1"], var.puzzle_display["y1"] = var.puzzle_display["x1"] * puzzle_scale, var.puzzle_display["y1"] * puzzle_scale
            var.puzzle_display["x2"], var.puzzle_display["y2"] = var.puzzle_display["x2"] * puzzle_scale + shift*2, var.puzzle_display["y2"] * puzzle_scale + shift*2

    if not len(var.puzzle_display):
        # иногда контуры колец выходят за край - подвинем вправо. а также отступ Бордюра
        min_x = min_y = 0
        for ring in puzzle_rings:
            if ring["type"]!= 0: continue
            shift_xx = ring["center_x"] - (ring["radius"] + var.BORDER)
            shift_yy = ring["center_y"] - (ring["radius"] + var.BORDER)
            if shift_xx < 0:
                if min_x < (-shift_xx):
                    min_x = -shift_xx
            if shift_yy < 0:
                if min_y < (-shift_yy):
                    min_y = -shift_yy
        if min_x > 0 or min_y > 0:
            for ring in puzzle_rings:
                if ring["type"] != 0: continue
                ring["center_x"], ring["center_y"] = ring["center_x"] + min_x, ring["center_y"] + min_y
            for arch in puzzle_arch:
                if arch["num"] <= len_puzzle_rings(puzzle_rings):
                    ring = find_element(arch["num"],puzzle_rings)
                    if ring != "":
                        if ring["type"] != 0: continue
                arch["center_x"], arch["center_y"] = arch["center_x"] + min_x, arch["center_y"] + min_y
            for part in puzzle_parts:
                for part_arch in part["arch_lines"]:
                    part_arch[3], part_arch[4] = part_arch[3] + min_x, part_arch[4] + min_y
            for line in puzzle_lines:
                line[1], line[2] = line[1] + min_x, line[2] + min_y
                line[3], line[4] = line[3] + min_x, line[4] + min_y

    # измерим размеры головоломки
    calc_parts_countur(puzzle_parts, puzzle_arch, True)
    if len(var.puzzle_display):
        puzzle_width, puzzle_height = var.puzzle_display["x2"]-var.puzzle_display["x1"],var.puzzle_display["y2"]-var.puzzle_display["y1"]
    else:
        puzzle_width, puzzle_height = 0, 0
        for ring in puzzle_rings:
            if ring["type"]!= 0: continue
            xx = ring["center_x"] + ring["radius"] + var.BORDER
            puzzle_width = xx if xx > puzzle_width else puzzle_width
            yy = ring["center_y"] + ring["radius"] + var.BORDER
            puzzle_height = yy if yy > puzzle_height else puzzle_height
        for part in puzzle_parts: # отдельные части могут быть за пределами колец
            for part_xy in part["polygon"]:
                xx = part_xy[0] + var.BORDER
                puzzle_width = xx if xx > puzzle_width else puzzle_width
                yy = part_xy[1] + var.BORDER
                puzzle_height = yy if yy > puzzle_height else puzzle_height

    # учтем повороты
    vek_mul = -1
    if flip_x:
        vek_mul = -1 * vek_mul
        for ring in puzzle_rings:
            ring["center_x"] = puzzle_width - ring["center_x"]
        for arch in puzzle_arch:
            arch["center_x"] = puzzle_width - arch["center_x"]
        for part in puzzle_parts:
            for part_arch in part["arch_lines"]:
                part_arch[3] = puzzle_width - part_arch[3]
        for line in puzzle_lines:
            line[1] = puzzle_width - line[1]
            line[3] = puzzle_width - line[3]
    if flip_y:
        vek_mul = -vek_mul
        for ring in puzzle_rings:
            ring["center_y"] = puzzle_height - ring["center_y"]
        for arch in puzzle_arch:
            arch["center_y"] = puzzle_height - arch["center_y"]
        for part in puzzle_parts:
            for part_arch in part["arch_lines"]:
                part_arch[4] = puzzle_height - part_arch[4]
        for line in puzzle_lines:
            line[2] = puzzle_height - line[2]
            line[4] = puzzle_height - line[4]
    if flip_rotate:
        vek_mul = -vek_mul
        for ring in puzzle_rings:
            ring["center_x"], ring["center_y"] = ring["center_y"], ring["center_x"]
        for arch in puzzle_arch:
            arch["center_x"], arch["center_y"] = arch["center_y"], arch["center_x"]
        for part in puzzle_parts:
            for part_arch in part["arch_lines"]:
                part_arch[3], part_arch[4] = part_arch[4], part_arch[3]
        for line in puzzle_lines:
            line[1], line[2] = line[2], line[1]
            line[3], line[4] = line[4], line[3]

        puzzle_width, puzzle_height = puzzle_height, puzzle_width

    if vek_mul == 1:
        for part in puzzle_parts:
            for part_arch in part["arch_lines"]:
                part_arch[2] = -part_arch[2]

    return vek_mul, puzzle_width, puzzle_height

def load_puzzle(fl, init, dirname,filename):
    fl_load_save, fl_load_move, puzzle_kol, lines = False, False, 0, []

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
            filetypes = (("Puzzle files", "*.txt;*.save;*.move"), ("Puzzles", "*.txt"), ("Saves", "*.save"), ("Moves", "*.move"), ("Any files", "*"))
            if check_os_platform() != "windows":
                filetypes = (("Puzzles", "*.txt"), ("Saves", "*.save"), ("Moves", "*.move"), ("Any files", "*"))
            f_name = fd.askopenfilename(title="Open Puzzle", initialdir=dirname, filetypes=filetypes)
            if f_name == "":
                return [],0,"","", False, False, "-"
            filename = f_name
            dirname = os.path.dirname(filename)
        elif fl == "drop" and filename != "":
            dirname = os.path.dirname(filename)

        _, file_extension = os.path.splitext(filename)
        if file_extension.lower()==".save":
            fl_load_save = True
        elif file_extension.lower()==".move":
            fl_load_move = True

        try:
            with open(filename, encoding = 'utf-8', mode = 'r') as f:
                lines = f.readlines()
        except:
            try:
                with open(filename, mode='r') as f:
                    lines = f.readlines()
            except:
                return [],0,"","", False, False, "Can not open the file"
    return lines, puzzle_kol, dirname, filename,  fl_load_save, fl_load_move, ""

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

def init_test(file_num, mas_files):
    if file_num>=len(mas_files):
        return "Quit",0
    dirname, filename = mas_files[file_num]
    fil = read_file(dirname, filename, "reset")

    file_num += 1
    return fil,file_num

def init_puzzle(VERSION, fl_reset_ini = False, fl_esc = False):
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
        fil = read_file(dirname, filename, "reset")
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

        fil = read_file("", "", "init", init)
        file_ext = False

    return file_ext, fil

def resize_puzzle(new_win_width, new_win_height, puzzle_width, puzzle_height, puzzle_rings, puzzle_arch, puzzle_parts, puzzle_lines):
    puzzle_width_, puzzle_height_ = puzzle_width - var.BORDER * 2, puzzle_height - var.BORDER * 2
    original_scale = puzzle_width_ / puzzle_height_
    width, height = new_win_width - var.BORDER * 2, new_win_height - var.PANEL - var.BORDER * 2
    screen_scale = width / height

    new_scale = 1
    if original_scale > screen_scale:
        new_scale = width / puzzle_width_
    elif original_scale < screen_scale:
        new_scale = height / puzzle_height_

    if new_scale != 1:
        vek_mul, puzzle_width, puzzle_height = align_cordinates(puzzle_rings, puzzle_arch, puzzle_parts, puzzle_lines, new_scale, False, False, False)
        calc_all_spline(puzzle_rings, puzzle_arch, puzzle_parts)
    else:
        vek_mul = -1

    var.WIN_WIDTH, var.WIN_HEIGHT = new_win_width, new_win_height - var.PANEL
    return puzzle_width, puzzle_height, vek_mul

def toggle_marker_check(toggle_Marker, toggle_Circle):
    if var.auto_marker != toggle_Marker.value:
        toggle_Marker.value = var.auto_marker
        if var.auto_marker:
            toggle_Marker.colour, toggle_Marker.handleColour = toggle_Marker.onColour, toggle_Marker.handleOnColour
        else:
            toggle_Marker.colour, toggle_Marker.handleColour = toggle_Marker.offColour, toggle_Marker.handleOffColour
    if var.show_hidden_circles != toggle_Circle.value:
        toggle_Circle.value = var.show_hidden_circles
        if var.show_hidden_circles:
            toggle_Circle.colour, toggle_Circle.handleColour = toggle_Circle.onColour, toggle_Circle.handleOnColour
        else:
            toggle_Circle.colour, toggle_Circle.handleColour = toggle_Circle.offColour, toggle_Circle.handleOffColour

def events_check_read_puzzle(events, fl_break, fl_test, VERSION, BTN_CLICK, BTN_CLICK_STR, puzzle_width, puzzle_height, win_caption, file_ext, puzzle_name, puzzle_author, puzzle_web_link, puzzle_speed, puzzle_rings, puzzle_arch, puzzle_parts, puzzle_lines, help, photo, ring_num, direction, mouse_xx, mouse_yy, dirname, filename, ctrl_pressed, shift_pressed, SCREEN,game_scr,shift_width,shift_height):
    mouse_x, mouse_y, mouse_left, mouse_right, fil = 0, 0, False, False, ""
    var.fl_resize = fl_screenshot = fl_event = False

    fl_stop = False
    for ev in events:  # Обрабатываем события
        if (ev.type == pygame.QUIT):
            if file_ext:
                save_state(dirname, filename, VERSION)
            return False, SystemExit, "QUIT"
        if (ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE):
            if fl_test:
                return False, SystemExit, "QUIT"
            help = 0 if help == 1 else help
            photo = 0 if photo == 1 else photo
            fl_event = True
        if fl_test: continue

        if (ev.type == pygame.KEYDOWN):
            pos = -1
            if ctrl_pressed:
                key_mas     = [pygame.K_o, pygame.K_F6, pygame.K_F9]
                cammand_mas = ["open",     "markerring","savemove"]
                try: pos = key_mas.index(ev.key)
                except: pos = -1
            elif shift_pressed:
                key_mas     = [pygame.K_F6]
                cammand_mas = ["hiddencircles"]
                try: pos = key_mas.index(ev.key)
                except: pos = -1
            else:
                key_mas     = [pygame.K_F1, pygame.K_F2, pygame.K_F3, pygame.K_F4, pygame.K_F5, pygame.K_F6, pygame.K_F7,  pygame.K_F8,     pygame.K_F9, pygame.K_F11, pygame.K_F12, pygame.K_SPACE, pygame.K_BACKSPACE]
                cammand_mas = ["help",     "reset",      "open",      "scramble",  "photo",     "marker",    "screenshot", "superscramble", "save",      "prev",       "next",       "undo",         "redo"]
                try: pos = key_mas.index(ev.key)
                except: pos = -1
            if pos>=0:
                BTN_CLICK = True
                BTN_CLICK_STR = cammand_mas[pos]

        if (ev.type == pygame.KEYDOWN):
            if (ev.key == pygame.K_LCTRL or ev.key == pygame.K_RCTRL):
                ctrl_pressed = True
            elif (ev.key == pygame.K_LSHIFT or ev.key == pygame.K_RSHIFT):
                shift_pressed = True
        if (ev.type == pygame.KEYUP):
            if (ev.key == pygame.K_LCTRL or ev.key == pygame.K_RCTRL):
                ctrl_pressed = False
            elif (ev.key == pygame.K_LSHIFT or ev.key == pygame.K_RSHIFT):
                shift_pressed = False

        if BTN_CLICK_STR == "info" and help+photo == 0:
            for link in puzzle_web_link:
                if link != "":
                    webbrowser.open(link, new=2, autoraise=True)
            fl_event = True
        if BTN_CLICK_STR == "about" and help+photo == 0:
            mb.showinfo("Geraniums Pot","Geraniums Pot - Intersecting Circles Puzzles Simulator\n"+
                             "Programmer: Evgeniy Grigoriev. Version "+VERSION)
            webbrowser.open("https://twistypuzzles.com/forum/viewtopic.php?p=424143#p424143", new=2, autoraise=True)
            webbrowser.open("https://github.com/grigorusha/GeraniumsPot", new=2, autoraise=True)
            fl_event = True
        if BTN_CLICK_STR == "help":
            help = 1 - help
            fl_event = True
        if BTN_CLICK_STR == "photo":
            photo = 1 - photo
            fl_event = True
        if BTN_CLICK_STR == "marker":
            var.auto_marker = 1 - var.auto_marker
            fl_event = True
        if BTN_CLICK_STR == "markerring":
            var.auto_marker_ring = 1 - var.auto_marker_ring
            fl_event = True
        if BTN_CLICK_STR == "hiddencircles":
            var.show_hidden_circles = 1 - var.show_hidden_circles
            fl_event = True
        if BTN_CLICK_STR == "screenshot":
            fl_screenshot = True
            fl_event = True

        if (BTN_CLICK_STR == "open" or ev.type == pygame.DROPFILE or BTN_CLICK_STR == "prev" or BTN_CLICK_STR == "next" or BTN_CLICK_STR == "reset") and help+photo == 0:
            if BTN_CLICK_STR == "reset" and (not file_ext):
                fl_break = var.fl_reset = True
            else:
                if BTN_CLICK_STR == "reset":
                    old_width, old_height = var.WIN_WIDTH, var.WIN_HEIGHT
                    fil = read_file(dirname, filename, "reset")
                elif ev.type == pygame.DROPFILE:
                    fl_break = False
                    fil = read_file("", ev.file, "drop")
                else:
                    fl_break = False
                    fil = read_file(dirname, filename, BTN_CLICK_STR)

                if not fl_test:
                    window_front(win_caption)

                if typeof(fil) != "str":
                    puzzle_name, puzzle_author, puzzle_web_link, puzzle_scale, puzzle_speed, puzzle_rings, puzzle_arch, puzzle_parts, puzzle_lines, puzzle_kol, vek_mul, dirname, filename, puzzle_width, puzzle_height, remove_parts, copy_parts, fl_load_save = fil
                    if BTN_CLICK_STR == "reset":
                        file_ext, fl_break, var.fl_reset = True, True, True
                        if old_width != var.WIN_WIDTH or old_height != var.WIN_HEIGHT:
                            var.fl_reset = False
                        else:
                            puzzle_width,puzzle_height,vek_mul = resize_puzzle(var.WIN_WIDTH, var.WIN_HEIGHT+var.PANEL, puzzle_width,puzzle_height, puzzle_rings,puzzle_arch,puzzle_parts,puzzle_lines)
                            # var.fl_resize = True
                    else:
                        file_ext, fl_break, var.fl_reset = True, True, False
                        if file_ext:
                            save_state(dirname, filename, VERSION)
                else:
                    if fil == "break":
                        fl_break, var.fl_reset, file_ext = True, False, False
                    elif fil != "-":
                        if fil == "":
                            fil = "Unknow error"
                        mb.showerror(message=("Bad puzzle-file: " + fil))
                        if not fl_test:
                            window_front(win_caption)

            if BTN_CLICK_STR != "reset":
                if var.resized==2:
                    puzzle_width, puzzle_height, vek_mul = resize_puzzle(var.WIN_WIDTH, var.WIN_HEIGHT+var.PANEL, puzzle_width, puzzle_height, puzzle_rings, puzzle_arch, puzzle_parts, puzzle_lines)
                    var.fl_resize = False
                else:
                    var.resized, var.fl_resize = 0, False
            fl_event = True

        if ev.type == pygame.VIDEORESIZE:
            puzzle_width,puzzle_height,vek_mul = resize_puzzle(ev.w,ev.h, puzzle_width,puzzle_height, puzzle_rings,puzzle_arch,puzzle_parts,puzzle_lines)

            # проверим максимизированно ли окно
            var.resized = 2 if is_window_maximized() else 1
            var.fl_resize = fl_event = True

        if ( (BTN_CLICK_STR == "save") or (BTN_CLICK_STR == "savemove") ) and help+photo == 0:
            fl_break = False
            save_puzzle(BTN_CLICK_STR, dirname, filename, puzzle_name, puzzle_author, puzzle_web_link, puzzle_speed, puzzle_rings, puzzle_arch, puzzle_parts)
            fl_event = True

        if ev.type == pygame.MOUSEMOTION:
            mouse_xx, mouse_yy = ev.pos[0], ev.pos[1]
            fl_event = True

        if ev.type == pygame.MOUSEBUTTONUP:
            if ev.type == pygame.MOUSEBUTTONUP and (ev.button == 2 or ev.button == 6):
                BTN_CLICK = True
                BTN_CLICK_STR = "undo"
                fl_event = True
            if ev.type == pygame.MOUSEBUTTONUP and (ev.button == 7):
                BTN_CLICK = True
                BTN_CLICK_STR = "redo"
                fl_event = True

            if ev.type == pygame.MOUSEBUTTONUP and (ev.button == 1 or ev.button == 4) and not BTN_CLICK:
                if help+photo == 0:
                    mouse_x, mouse_y = ev.pos[0], ev.pos[1]
                    mouse_left = True
                help = 0 if help == 1 else help
                photo = 0 if photo == 1 else photo
                fl_event = True
            if ev.type == pygame.MOUSEBUTTONUP and (ev.button == 3 or ev.button == 5) and not BTN_CLICK:
                if help+photo == 0:
                    mouse_x, mouse_y = ev.pos[0], ev.pos[1]
                    mouse_right = True
                help = 0 if help == 1 else help
                photo = 0 if photo == 1 else photo
                fl_event = True

        if (BTN_CLICK_STR == "scramble" or BTN_CLICK_STR == "superscramble") and help!=1:
            fl_break = False
            scramble_puzzle(puzzle_rings,puzzle_arch,puzzle_parts,BTN_CLICK_STR, True, SCREEN,game_scr,shift_width,shift_height)
            var.moves, var.moves_stack, var.redo_stack = 0, [], []
            fl_event = True

        if BTN_CLICK_STR == "undo" and help+photo == 0:
            fl_break = False
            if len(var.moves_stack) > 0:
                var.undo = True
                var.moves -= 1
                ring_num, direction = var.moves_stack.pop()
                direction = -direction
                var.redo_stack.append([ring_num, direction])
            fl_event = fl_stop = True

        if BTN_CLICK_STR == "redo" and help+photo == 0:
            fl_break = False
            if len(var.redo_stack) > 0:
                var.undo = True
                var.moves += 1
                ring_num, direction = var.redo_stack.pop()
                direction = -direction
                var.moves_stack.append([ring_num, direction])
            fl_event = fl_stop = True

        BTN_CLICK = False
        BTN_CLICK_STR = ""

        if fl_stop: break

    fil2 = fl_break, file_ext, BTN_CLICK, BTN_CLICK_STR, ring_num, direction, mouse_xx, mouse_yy, mouse_x, mouse_y, mouse_left, mouse_right, help, photo, puzzle_width, puzzle_height, fl_screenshot, ctrl_pressed, shift_pressed
    return fl_event, fil, fil2

def read_puzzle_script_and_init_puzzle(lines, dirname, filename, fl_load_move):
    if not fl_load_move:
        flip_y = flip_x = flip_rotate = skip_check_error = var.show_hidden_circles = False
        puzzle_name, puzzle_author, puzzle_scale, puzzle_speed, var.auto_marker, var.auto_marker_ring, auto_renumbering, first_cut, first_coloring, first_arch = "", "", 1, 2, 0, 0, 1, True, True, True
        puzzle_web_link, puzzle_rings, puzzle_arch, puzzle_parts, puzzle_lines, auto_cut_parts, auto_color_parts, set_color_parts, remove_parts, copy_parts, var.puzzle_display = [], [], [], [], [], [], [], [], [], [], dict()
        part_num, param_calc, ring_num, line_num = 0, [], 1, 1
        var.moves, var.moves_stack = 0, []

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

                pygame.display.set_caption(puzzle_name + ": Please wait! Loading ... " + str(percent) + "%")
                pygame.display.update()
            except: pass

        if command == "Name".lower():
            puzzle_name = params
        elif command == "Author".lower():
            puzzle_author = params
        elif command == "SkipCheckError".lower():
            if int(params) == 1:
                skip_check_error = True
        elif command == "ShowHiddenCircles".lower():
            var.show_hidden_circles = True
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

            linked_dict = dict(gears=param_mas6,link_mas=[])
            ring_dict = dict(num=ring_num, center_x=param_mas[1], center_y=param_mas[2], radius=param_mas[3], angle=param_mas[4], angle_pos=0, type=param_mas5, inner=[], linked=linked_dict, spline=[])
            puzzle_rings.append(ring_dict)
            # puzzle_rings.append([ring_num, param_mas[1], param_mas[2], param_mas[3], param_mas[4], 0, param_mas5, [], [param_mas6, []], []])
            ring_num += 1

            arch_num = len(puzzle_arch)+1
            arch_dict = dict(num=arch_num, center_x=param_mas[1], center_y=param_mas[2], radius=param_mas[3])
            puzzle_arch.append(arch_dict)
            # puzzle_arch.append([arch_num, param_mas[1], param_mas[2], param_mas[3]])
            check_all_rings(puzzle_rings)

        elif command == "CopyRing".lower():
            if not (len(param_mas) >= 5 or len(param_mas) <= 7): return ("Incorrect 'CopyRing' parameters. In str=" + str(str_nom))
            param_mas[3], param_mas[4] = calc_param(param_mas[3], param_calc), calc_param(param_mas[4], param_calc)
            param_mas5 = int(param_mas[5]) if len(param_mas)>=6 else 0
            param_mas6 = int(param_mas[6]) if len(param_mas)>=7 else 0
            center_x, center_y = copy_ring(int(param_mas[1]),param_mas[2],puzzle_rings)

            linked_dict = dict(gears=param_mas6,link_mas=[])
            ring_dict = dict(num=ring_num, center_x=center_x, center_y=center_y, radius=param_mas[3], angle=param_mas[4], angle_pos=0, type=param_mas5, inner=[], linked=linked_dict, spline=[])
            puzzle_rings.append(ring_dict)
            # puzzle_rings.append([ring_num, center_x, center_y, param_mas[3], param_mas[4], 0, param_mas5, [], [param_mas6, []], []])
            ring_num += 1

            arch_num = len(puzzle_arch)+1
            arch_dict = dict(num=arch_num, center_x=center_x, center_y=center_y, radius=param_mas[3])
            puzzle_arch.append(arch_dict)
            # puzzle_arch.append([arch_num, center_x, center_y, param_mas[3]])
            check_all_rings(puzzle_rings)

        elif command == "RemoveRings".lower():
            remove_ring_mas = param_mas
            remove_ring(puzzle_rings, remove_ring_mas)

        elif command == "Linked".lower():
            linked_mas = param_mas
            link_rings(puzzle_rings, linked_mas)

        elif command == "Latch".lower():
            latch_mas = param_mas
            latch_parts(puzzle_parts, latch_mas)

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
            init_cut_all_ring_to_parts(puzzle_rings, puzzle_arch, puzzle_parts, auto_cut_parts, auto_renumbering, first_cut)
            first_cut = False

        elif command == "MakeCircles".lower():
            make_circles = param_mas
            make_def_circles(puzzle_rings, puzzle_arch, puzzle_parts, make_circles, True)
            first_cut = False

        elif command == "RotateCircles".lower():
            rotate_circles = param_mas
            rotate_def_circles(puzzle_rings, puzzle_arch, puzzle_parts, rotate_circles, auto_renumbering)

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
            copy_def_parts(copy_parts, puzzle_rings, puzzle_arch, puzzle_parts)
        elif command == "MoveParts".lower():
            copy_parts = param_mas
            copy_def_parts(copy_parts, puzzle_rings, puzzle_arch, puzzle_parts, True)

        elif command == "MirrorParts".lower():
            for nn,mir in enumerate(param_mas):
                if nn%2==1: param_mas[nn] = calc_param(param_mas[nn], param_calc)
            mirror_parts = param_mas
            mirror_def_parts(mirror_parts, puzzle_arch, puzzle_parts)

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
            if len(param_mas) == 3:
                param_mas[0], param_mas[1], param_mas[2] = calc_param(param_mas[0], param_calc), calc_param(param_mas[1], param_calc), calc_param(param_mas[2], param_calc)
                rotate_parts_param = param_mas
            else:
                param_mas[0] = calc_param(param_mas[0], param_calc)
                rotate_parts_param = [ 0,0,param_mas[0] ]
            rotate_all_parts(puzzle_rings, puzzle_arch, puzzle_parts, rotate_parts_param)

        elif command == "AutoColorParts".lower():
            auto_color_parts = param_mas
            init_color_all_parts(puzzle_parts, puzzle_rings, auto_color_parts)
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
            var.auto_marker = int(params) if is_number(params) else 1
        elif command == "AutoMarkerRing".lower():
            var.auto_marker_ring = int(params) if is_number(params) else 1

        elif command == "Display".lower():
            if len(param_mas) != 4: return ("Incorrect 'Display' parameters. In str=" + str(str_nom))
            param_mas[0], param_mas[1], param_mas[2], param_mas[3] = calc_param(param_mas[0], param_calc), calc_param(param_mas[1], param_calc), calc_param(param_mas[2], param_calc), calc_param(param_mas[3], param_calc)
            var.puzzle_display = dict(x1=int(param_mas[0]),y1=int(param_mas[1]),x2=int(param_mas[2]),y2=int(param_mas[3]))
            var.puzzle_display["x1"],var.puzzle_display["x2"] = min(var.puzzle_display["x1"],var.puzzle_display["x2"]),max(var.puzzle_display["x1"],var.puzzle_display["x2"])
            var.puzzle_display["y1"],var.puzzle_display["y2"] = min(var.puzzle_display["y1"],var.puzzle_display["y2"]),max(var.puzzle_display["y1"],var.puzzle_display["y2"])

        ########################################################################################
        # блок для загрузки скомпилированной головоломки. загружаем координаты всех частей

        elif command == "DirName".lower():
            dirname = params.replace("\"","")
        elif command == "PuzzleFile".lower():
            filename = params.replace("\"","")

        elif command == "MovesStack".lower():
            for move in param_mas:
                var.moves_stack.append([int(move[0]),int(move[1])])
            var.moves = len(var.moves_stack)

        elif command == "Arch".lower():
            if first_arch:
                puzzle_arch, first_arch = [], False
            if len(param_mas) != 4: return ("Incorrect 'Arch' parameters. In str=" + str(str_nom))

            arch_dict = dict(num=int(param_mas[0]), center_x=float(param_mas[1]), center_y=float(param_mas[2]), radius=float(param_mas[3]))
            puzzle_arch.append(arch_dict)
            # puzzle_arch.append([int(param_mas[0]), float(param_mas[1]), float(param_mas[2]), float(param_mas[3])])
        elif command == "Part".lower():
            if len(param_mas) == 3:
                part_num = int(param_mas[0])
                part_dict = dict(num=part_num, color=int(param_mas[1]), visible=int(param_mas[2]), latch=0, marker=dict(), centroid=dict(), arch_lines=[], polygon=[], spline=[], fl_error=0)
                puzzle_parts.append(part_dict)
                # puzzle_parts.append([part_num, int(param_mas[1]), int(param_mas[2]), [], [], [], [], [], 0])
            else:
                return ("Incorrect 'Part' parameters. In str=" + str(str_nom))
        elif command == "PartMarker".lower():
            if len(param_mas) == 5 and part_num > 0:
                part = find_element(part_num, puzzle_parts)
                marker_dict = dict(text=param_mas[0], angle=float(param_mas[1]), font_size=float(param_mas[2]), horizontal_shift=float(param_mas[3]), vertical_shift=float(param_mas[4]), sprite="")
                part["marker"] = marker_dict
                # part["marker"] = [param_mas[0], float(param_mas[1]), float(param_mas[2]), float(param_mas[3]), float(param_mas[4]), ""]
                # "text", "angle", "font_size", "horizontal_shift", "vertical_shift", "sprite"
            else:
                return ("Incorrect 'PartArch' parameters. In str=" + str(str_nom))
        elif command == "PartArch".lower():
            if len(param_mas) == 5 and part_num > 0:
                part = find_element(part_num, puzzle_parts)
                part_arch = part["arch_lines"]
                part_arch.append([int(param_mas[0]), int(param_mas[1]), int(param_mas[2]), float(param_mas[3]), float(param_mas[4]), 0])
            else:
                return ("Incorrect 'PartArch' parameters. In str=" + str(str_nom))

        ########################################################################################
        elif command == "End".lower() or command == "Stop".lower() or command == "Exit".lower() or command == "Quit".lower():
            break


    return puzzle_name, puzzle_author, puzzle_web_link, puzzle_scale, puzzle_speed, puzzle_rings, puzzle_arch, puzzle_parts, puzzle_lines, auto_cut_parts, auto_color_parts, set_color_parts, remove_parts, copy_parts, flip_y, flip_x, flip_rotate, skip_check_error, dirname, filename

def calc_all_spline(puzzle_rings, puzzle_arch, puzzle_parts):
    # построение границ деталек
    calc_parts_countur(puzzle_parts, puzzle_arch)
    calc_all_centroids(puzzle_parts)

    # вычисление плавного контура кругов
    for ring in puzzle_rings:
        shift = 4
        arch_mas = [[ring["center_x"], ring["center_y"] + ring["radius"] + shift], [ring["center_x"], ring["center_y"] + ring["radius"] + shift]]
        ring["spline"], _ = calc_arch_spline(arch_mas, ring["center_x"], ring["center_y"], ring["radius"] + shift, 1)

def read_file(dirname, filename, fl, init=""):
    # загрузка файла
    lines, puzzle_kol, dirname, filename, fl_load_save, fl_load_move, error_str = load_puzzle(fl, init, dirname, filename)
    if error_str != "": return error_str

    pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_WAITARROW)
    win_caption = pygame.display.get_caption()
    pygame.display.set_caption("Please wait! Loading ...")

    var.moves, var.moves_stack = 0, []

    # прочитаем строки файла
    fil = read_puzzle_script_and_init_puzzle(lines, dirname, filename, fl_load_move)
    if typeof(fil) == "str": return fil
    puzzle_name, puzzle_author, puzzle_web_link, puzzle_scale, puzzle_speed, puzzle_rings, puzzle_arch, puzzle_parts, puzzle_lines, auto_cut_parts, auto_color_parts, set_color_parts, remove_parts, copy_parts, flip_y, flip_x, flip_rotate, skip_check_error, dirname, filename = fil

    remove_dublikate_parts(puzzle_parts)

    # выравнивание, повороты и масштабирование всех координат
    vek_mul, puzzle_width, puzzle_height = align_cordinates(puzzle_rings, puzzle_arch, puzzle_parts, puzzle_lines, puzzle_scale, flip_x, flip_y, flip_rotate)
    calc_all_spline(puzzle_rings, puzzle_arch, puzzle_parts)

    # поиск ошибок
    # find_incorrect_parts(puzzle_parts)

    for ring in puzzle_rings:
        ring["angle_pos"]=0 # сбросим углы поворота для бермуд

    pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
    if typeof(win_caption)=="str":
        pygame.display.set_caption(win_caption)

    return puzzle_name, puzzle_author, puzzle_web_link, puzzle_scale, puzzle_speed, puzzle_rings, puzzle_arch, puzzle_parts, puzzle_lines, puzzle_kol, vek_mul, dirname, filename, puzzle_width, puzzle_height, remove_parts, copy_parts, fl_load_save
