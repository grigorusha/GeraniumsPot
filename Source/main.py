import os,copy,time
from tkinter import Tk
import pygame, pygame_widgets, ptext
from math import pi, sqrt, cos, sin, tan, acos, asin, atan, exp, pow, radians, degrees, hypot
# import Pillow - for pyinstaller splash-screen

import glob as var
from work import *
from draw import *
from syst import *

VERSION = "1.9.2"

# + TODO 0. Латч головоломки: простые +/- детали, где функциональны все края
# + TODO 0. Головоломки с Рамой-Плюнгером: ограничение поворотов (0,0)
# + TODO 0. Новые команды: задание области отображения для плюнгеров: Display: x1,y1,x2,y2
# + TODO 0. Новые команды: RemoveRings
# + TODO 0. упростил команду RotateAllParts: Angle
# + TODO 0. Задал возможность указывать диапазон в параметрах - 15..25
# + TODO 0. Вложенные скобки в параметрах
# + TODO 0. Новые хоткей: Ctrl+F6 - показать номера кругов, Shift+F6 - включить скрытые круги, Ctrl+F9 - сохранить только движения
# + TODO 0. Автомаркер: размер шрифта зависит от площади частей
# + TODO 0. Добавил тег Дата создания скрипта
# + TODO 0. Работаем при максимизированном на экран окне
# + TODO 0. Отображение этапов скрамбла и обновление процентов, каждые 5 сек
# + TODO 0. если нет папки с фото головоломок (экономия места в облегченном инсталляторе), то убираем кнопку Photo
# + TODO 0. увеличение скорости вращения при увеличении угла поворота, + зависимость от радиуса
# + TODO 0. Исправлено: в механизме undo-redo в симуляторе иногда пропадала часть стека действий

# + TODO 0. Два инсталятора - макси и мини+доп.папки
# --------------------------------------------------------------------------------------

# TODO *. Глобальные переменные: file_ext, fl_esc, fl_test, fl_test_photo, fl_test_scramble, dir_garden, dir_screenshots, shift_width,shift_height
# TODO *.                       puzzle_rings, puzzle_arch, puzzle_parts, puzzle_lines
# TODO *.                       puzzle_name, puzzle_author, puzzle_scale, puzzle_speed, puzzle_web_link, puzzle_width, puzzle_height, vek_mul
# TODO *. Вместо массивов с индексами - Именованный Словарь: part_arch, intersect

# TODO 1. Контурные отверстия в частях - несколько типов отверстий : 1. масштабирование контура, с коэффициентом. 2. отступ контура на сдвиг.
# TODO 1. Альфа канал при вращении

# TODO 1. Меню открытия с иконками и названиями. Поиск с фильтрами (автор, дата, класс)
# TODO 1. Латч головоломки: сохрание состояния, выделение круга мышкой - глобальный флаг Латч
# TODO 1. Оборвать по ЕСК долгую загрузку
# TODO 1. Умножение скорости по хоткей
# TODO 1. поддержка Свайпа на Тачскрине
# TODO 1. Более умный скрамбл: проверить после поворота кольца, а сможет ли чтото повернуться

# TODO 2. загрузка макросов - 1,2,3...
# TODO 2. поле для последовательности поворотов, возможность запустить свою
# TODO 2. сохранение последовательности поворотов и загрузка: 1R,2L
# TODO 2. Solved
# TODO 2. Вывод при генерации скриншотов инфы о количестве кругов и углах
# TODO 2. SplashScreen - анимация зеленых точек

# TODO 3. Бандаж заданных частей
# TODO 3. Поиск пересекающихся частей - вывод инфо об ошибках, красный контур
# TODO 4. Разделение частей линиями - для задания узоров
# TODO 4. Скругление уголков
# TODO 5. Слайдинги горизонтальные
# TODO *. сборка в Linux
# TODO *. не работает на Вин32 (((

#Param: radius, 28.93658623
#Ring: 1,  50, 50, 50, 60
#Ring: 2, 50+2*radius, 50, 50, 60
#Ring: 3,  50, 50, radius, 60
#Ring: 4, 50+2*radius, 50, radius, 60
#AutoCutParts: (1R,2R),18
# исчезают части
# Ecuber Ring 185 Geran.txt - нет выделения кругов и Ундо
# Capella4

def button_Button_click(button_str):
    var.BTN_CLICK,var.BTN_CLICK_STR = True,button_str

def button_init(SCREEN, font_button, no_photo):
    from pygame_widgets.button import Button
    from pygame_widgets.toggle import Toggle

    GREEN_COLOR, LIME_COLOR, BLUE_COLOR, LBLUE_COLOR, GRAY_COLOR = (0, 150, 0), (0, 250, 0), (0, 0, 250), (80, 200, 250), (100, 100, 100)

    button_y1 = int(var.WIN_HEIGHT) + 20
    button_Reset = Button(SCREEN, 10, button_y1, 45, 20, text='Reset', fontSize=20, font=font_button, margin=5,
                          radius=3,
                          inactiveColour=GREEN_COLOR, hoverColour=LIME_COLOR, pressedColour=LIME_COLOR,
                          onClick=lambda: button_Button_click("reset"))
    button_Scramble = Button(SCREEN, button_Reset.textRect.right + 10, button_y1, 70, 20, text='Scramble',
                             fontSize=20, font=font_button, margin=5, radius=3,
                             inactiveColour=GREEN_COLOR, hoverColour=LIME_COLOR, pressedColour=LIME_COLOR,
                             onClick=lambda: button_Button_click("scramble"))
    button_Undo = Button(SCREEN, button_Scramble.textRect.right + 10, button_y1, 40, 20, text='Undo',
                         fontSize=20, font=font_button, margin=5, radius=3,
                         inactiveColour=GREEN_COLOR, hoverColour=LIME_COLOR, pressedColour=LIME_COLOR,
                         onClick=lambda: button_Button_click("undo"))
    button_Redo = Button(SCREEN, button_Undo.textRect.right + 10, button_y1, 40, 20, text='Redo',
                         fontSize=20, font=font_button, margin=5, radius=3,
                         inactiveColour=GREEN_COLOR, hoverColour=LIME_COLOR, pressedColour=LIME_COLOR,
                         onClick=lambda: button_Button_click("redo"))

    if no_photo:
        button_Info = Button(SCREEN, button_Redo.textRect.right + 20, button_y1, 48, 20, text='Info ->',
                             fontSize=20, font=font_button, margin=5, radius=3,
                             inactiveColour=BLUE_COLOR, hoverColour=LBLUE_COLOR, pressedColour=LBLUE_COLOR,
                             onClick=lambda: button_Button_click("info"))
    else:
        button_Photo = Button(SCREEN, button_Redo.textRect.right + 20, button_y1, 60, 20, text='Photo ->',
                             fontSize=20, font=font_button, margin=5, radius=3,
                             inactiveColour=BLUE_COLOR, hoverColour=LBLUE_COLOR, pressedColour=LBLUE_COLOR,
                             onClick=lambda: button_Button_click("photo"))
        button_Info = Button(SCREEN, button_Photo.textRect.right + 10, button_y1, 48, 20, text='Info ->',
                             fontSize=20, font=font_button, margin=5, radius=3,
                             inactiveColour=BLUE_COLOR, hoverColour=LBLUE_COLOR, pressedColour=LBLUE_COLOR,
                             onClick=lambda: button_Button_click("info"))

    button_About = Button(SCREEN, button_Info.textRect.right + 10, button_y1, 60, 20, text='About ->',
                          fontSize=20, font=font_button, margin=5, radius=3,
                          inactiveColour=BLUE_COLOR, hoverColour=LBLUE_COLOR, pressedColour=LBLUE_COLOR,
                          onClick=lambda: button_Button_click("about"))

    button_y2 = button_y1 + 25
    button_Open = Button(SCREEN, 10, button_y2, 45, 20, text='Open',
                         fontSize=20, font=font_button, margin=5, radius=3,
                         inactiveColour=GREEN_COLOR, hoverColour=LIME_COLOR, pressedColour=LIME_COLOR,
                         onClick=lambda: button_Button_click("open"))
    button_Save = Button(SCREEN, button_Open.textRect.right + 10, button_y2, 45, 20, text='Save',
                         fontSize=20, font=font_button, margin=5, radius=3,
                         inactiveColour=GREEN_COLOR, hoverColour=LIME_COLOR, pressedColour=LIME_COLOR,
                         onClick=lambda: button_Button_click("save"))

    button_Help = Button(SCREEN, button_Undo.textRect.right + 10, button_y2, 80, 20, text='Solved State',
                         fontSize=20, font=font_button, margin=5, radius=3,
                         inactiveColour=GREEN_COLOR, hoverColour=LIME_COLOR, pressedColour=LIME_COLOR,
                         onClick=lambda: button_Button_click("help"))

    button_y3 = button_y2 + 30
    toggle_Marker = Toggle(SCREEN, 15, button_y3, 13,10, offColour=GRAY_COLOR, onColour=GREEN_COLOR, startOn=var.auto_marker)
    toggle_Circle = Toggle(SCREEN, 120, button_y3, 13,10, offColour=GRAY_COLOR, onColour=GREEN_COLOR, startOn=var.show_hidden_circles)

    button_y4 = button_y3 + 20
    button_set = [button_Reset, button_Scramble, button_Undo, button_Redo, button_Open, button_Save, button_Info, button_Help, button_About, toggle_Marker, toggle_Circle]
    if not no_photo:
        button_set.append(button_Photo)

    return button_y2, button_y3, button_y4, button_Save, button_Help, toggle_Marker, toggle_Circle, button_set

def main():
    var.fl_reset, var.show_hidden_circles, var.auto_marker, var.auto_marker_ring = False, False, 0, 0
    var.resized, var.fl_resize = 0, False # 0 - нет, 1 - да, 2 - макс

    file_ext, fl_esc, fl_load_save = False, False, False
    puzzle_name, puzzle_author, puzzle_scale, puzzle_speed, puzzle_kol, puzzle_web_link, puzzle_width, puzzle_height, vek_mul = "", "", 1, 2, 1, [], 0,0, -1
    puzzle_rings, puzzle_arch, puzzle_parts, puzzle_lines, remove_parts, copy_parts = [], [], [], [], [], []

    # обработка коммандной строки
    fl_reset_ini, fl_test, fl_test_photo, fl_test_scramble, dir_garden, dir_screenshots = arg_param_check()

    # инициализация режима Теста
    count_test_scramble, sub_folder = 0, ""
    if fl_test:
        file_num = 0
        mas_files, dir_garden, dir_screenshots = dir_test(dir_garden, dir_screenshots)
        purge_dir(dir_screenshots, "jpg,jpeg,png")

        start_time = time.time()
        print("Start testing...")
    else:
        _,_, dir_screenshots = dir_test()

    # основная инициализация
    pygame.init()  # Инициация PyGame
    font = pygame.font.SysFont('Verdana', 18)
    font2 = pygame.font.SysFont('Verdana', 12)
    font_button = pygame.font.SysFont("ArialB", 18)
    timer = pygame.time.Clock()
    Tk().withdraw()
    random.seed()

    infoObject = pygame.display.Info()
    screen_width, screen_height = infoObject.current_w, infoObject.current_h

    icon = os.path.join(os.path.abspath(os.curdir),"Geraniums Pot.png")
    if os.path.isfile(icon):
        pygame.display.set_icon(pygame.image.load(icon))

    no_photo = not os.path.isdir(os.path.join(os.path.abspath(os.curdir), "Photo"))

    ################################################################################
    ################################################################################
    # перезапуск программы при смене параметров
    while True:
        first_pass = True
        if fl_test:
            file_ext, count_test_scramble = True, 0
            if len(mas_files)==file_num: break
            sub_folder = mas_files[file_num][0].replace(dir_garden,"")
            fil,file_num = init_test(file_num, mas_files)
            close_spalsh_screen()
            if typeof(fil) != "str":
                puzzle_name, puzzle_author, puzzle_web_link, puzzle_scale, puzzle_speed, puzzle_rings, puzzle_arch, puzzle_parts, puzzle_lines, puzzle_kol, vek_mul, dirname, filename, puzzle_width, puzzle_height, remove_parts, copy_parts, fl_load_save = fil
            else: break

        elif not file_ext and not var.fl_resize:
            file_ext, fil = init_puzzle(VERSION, fl_reset_ini, fl_esc)
            close_spalsh_screen()
            if typeof(fil) != "str":
                puzzle_name, puzzle_author, puzzle_web_link, puzzle_scale, puzzle_speed, puzzle_rings, puzzle_arch, puzzle_parts, puzzle_lines, puzzle_kol, vek_mul, dirname, filename, puzzle_width, puzzle_height, remove_parts, copy_parts, fl_load_save = fil
            else: break

        if not var.fl_resize and not var.resized:
            var.WIN_WIDTH, var.WIN_HEIGHT = puzzle_width, puzzle_height

        help_mul = 2 if not fl_test else 1.5
        var.GAME = (puzzle_width, puzzle_height)
        if not var.fl_resize:
            var.HELP = (puzzle_width // help_mul, puzzle_height // help_mul)
        var.PHOTO = (puzzle_width // help_mul, puzzle_height // help_mul)
        DISPLAY = (var.WIN_WIDTH, var.WIN_HEIGHT + var.PANEL)
        shift_width,shift_height = (var.WIN_WIDTH-puzzle_width)//2,(var.WIN_HEIGHT-puzzle_height)//2

        # инициализация окна
        if not var.fl_reset and not var.fl_resize:
            pos_x = int(screen_width/2 - var.WIN_WIDTH/2)
            pos_y = int(screen_height - (var.WIN_HEIGHT + var.PANEL))
            os.environ['SDL_VIDEO_WINDOW_POS'] = '%i,%i' % (pos_x, pos_y)
            os.environ['SDL_VIDEO_CENTERED'] = '0'

            SCREEN = pygame.display.set_mode(DISPLAY, pygame.RESIZABLE)  # Создаем окошко
        game_scr = pygame.Surface(var.GAME) # , pygame.SRCALPHA, 32) #

        if not var.fl_resize:
            win_caption = puzzle_name if puzzle_name != "" else "Geraniums Pot Simulator"
            if puzzle_author != "": win_caption += " (" + puzzle_author.strip() + ")"
            pygame.display.set_caption(win_caption)  # Пишем в шапку

            if not fl_test:
                keyboard_press("alt")
                window_front(win_caption)

            if not fl_load_save:
                var.moves, var.moves_stack = 0, []
            var.redo_stack, var.solved = [], True

            mouse_xx, mouse_yy = 0, 0
            help,photo, help_gen = 0, 0, True
            animation_on, events = False, ""

        photo_screen = ""
        var.fl_resize = fl_esc = False
        fl_event = True

        rings_kol = 0
        for ring in puzzle_rings:
            if ring["type"]==0: rings_kol+=1

        # инициализация кнопок
        button_y2, button_y3, button_y4, button_Save, button_Help, toggle_Marker, toggle_Circle, button_set = button_init(SCREEN, font_button, no_photo)
        ctrl_pressed = shift_pressed = False

        ################################################################################
        ################################################################################
        # Основной цикл программы
        while True:
            timer.tick(50)

            if not animation_on:
                fl_break = var.undo = fl_screenshot = False
                mouse_x, mouse_y, mouse_left, mouse_right, ring_select = 0, 0, False, False, 0
                ring_num = direction = 0
                var.auto_marker, var.show_hidden_circles = toggle_Marker.value, toggle_Circle.value

                ################################################################################
                # обработка событий
                if not first_pass or fl_test: # при первом цикле, сначала надо полностью нарисовать, потом считывать кнопки
                    events = pygame.event.get()
                    var.auto_marker, var.show_hidden_circles = toggle_Marker.value, toggle_Circle.value
                    fl_event, fil, fil2 = events_check_read_puzzle(events, fl_break, fl_test, VERSION, var.BTN_CLICK, var.BTN_CLICK_STR, puzzle_width, puzzle_height, win_caption, file_ext, puzzle_name, puzzle_author, puzzle_web_link, puzzle_speed, puzzle_rings, puzzle_arch, puzzle_parts, puzzle_lines, help, photo, ring_num, direction, mouse_xx, mouse_yy, dirname, filename, ctrl_pressed, shift_pressed, SCREEN,game_scr,shift_width,shift_height)

                    if typeof(fil2) == "str":
                        if fil2 == "QUIT" and fl_test:
                            end_time = time.time() - start_time
                            minute, secunde = int(end_time//60), round(end_time%60,2)
                            print("End testing: "+str(minute)+" minutes, "+str(secunde)+" sec")
                        return fil
                    if typeof(fil) != "str":
                        puzzle_name, puzzle_author, puzzle_web_link, puzzle_scale, puzzle_speed, puzzle_rings, puzzle_arch, puzzle_parts, puzzle_lines, puzzle_kol, vek_mul, dirname, filename, puzzle_width, puzzle_height, remove_parts, copy_parts, fl_load_save = fil
                    elif fil=="break":
                        fl_esc = True
                    fl_break, file_ext, var.BTN_CLICK, var.BTN_CLICK_STR, ring_num, direction, mouse_xx, mouse_yy, mouse_x, mouse_y, mouse_left, mouse_right, help, photo, puzzle_width, puzzle_height, fl_screenshot, ctrl_pressed, shift_pressed = fil2

                    toggle_marker_check(toggle_Marker, toggle_Circle)
                    if fl_break or var.fl_resize:
                        break

                ################################################################################
                # обработка перемещения и нажатия в игровом поле
                # mouse_xx, mouse_yy - координаты мышки при перемещении. mouse_x, mouse_y - координаты точки клика
                # ring_select - координаты кольца над которым двигается курсор. ring_num - кольцо внутри которого был клик
                mouse_xx_, mouse_yy_, mouse_x_, mouse_y_ = mouse_xx-shift_width, mouse_yy-shift_height, mouse_x-shift_width, mouse_y-shift_height
                if (mouse_xx_ + mouse_yy_ > 0) and mouse_xx_ < puzzle_width and mouse_yy_ < puzzle_height and not var.undo:
                    ring_num, ring_select, direction = mouse_move_click(mouse_xx_, mouse_yy_, mouse_x_, mouse_y_, mouse_left, mouse_right, puzzle_rings, ring_num, ring_select, direction, puzzle_parts)

                ################################################################################
                # логика игры - выполнение перемещений
                while ring_num > 0:
                    ring = find_element(ring_num, puzzle_rings)
                    if len(ring["linked"])==0 or len(ring["linked"]["link_mas"])==0:
                        link_dict = dict(ring_num=ring_num, direction=1, gear_ratio=1, angle=0, sprite="")
                        link_mas = [ link_dict ]
                        # link_mas = [ [ring_num,1,1,0,""] ] - "ring_num", "direction", "gear_ratio", "angle", "sprite"
                    else:
                        link_mas = ring["linked"]["link_mas"]

                    angle_rotate = 0
                    for mm,link in enumerate(link_mas):
                        ring_num_, direction_, gears_ratio, game_sprite = link["ring_num"], link["direction"], link["gear_ratio"], link["sprite"]
                        direction_ = direction*direction_
                        #############################################################################
                        # 1. найдем все части внутри круга
                        ring = find_element(ring_num_, puzzle_rings)
                        if mm==0: # ring_num_==ring_num:
                            angle_rotate = find_angle_rotate(ring, direction_)
                            p_speed = calc_speed(puzzle_speed,angle_rotate,ring["radius"])
                            step, count = int(ring["radius"] * radians(angle_rotate) / (p_speed)), 0
                            angle_rotate0 = angle_rotate
                        else:
                            angle_rotate = angle_rotate0*gears_ratio

                        if angle_rotate == 0 or step==0:
                            link_mas[mm]["sprite"] = ""
                            continue
                        part_mas, part_mas_other = find_parts_in_circle(ring, puzzle_parts, puzzle_rings)
                        if len(part_mas) == 0:
                            link_mas[mm]["sprite"] = ""
                            continue
                        angle, angle_deg = radians(angle_rotate) / step, angle_rotate / step

                        if not check_latch(part_mas,direction_): continue

                        # 2. повернем все части внутри круга
                        if len(part_mas)>0:
                            # 2.1 анимация. сформируем круглый спрайт для дальнейшего вращения
                            animation_on = True

                            game_sprite = pygame.Surface((ring["radius"] * 2, ring["radius"] * 2), pygame.SRCALPHA, 32)
                            game_sprite = game_sprite.convert_alpha()

                            shift_x, shift_y = ring["center_x"] - ring["radius"], ring["center_y"] - ring["radius"]

                            game_sprite.fill((0, 0, 0, 0))
                            # pygame.draw.circle(game_sprite,(96, 96, 96, 100), (ring["radius"],ring["radius"]), ring["radius"])
                            for nn, part in enumerate(part_mas):
                                part_mas_rot = copy.deepcopy(part["spline"])  # нужно для пересчета координат. чтобы круг вписался в спрайт
                                for pos in part_mas_rot:
                                    pos[0], pos[1] = pos[0] - shift_x, pos[1] - shift_y
                                pygame.draw.polygon(game_sprite, mas_pos(var.PARTS_COLOR,part["color"]), part_mas_rot, 0)
                                draw_smoth_polygon(game_sprite, var.BLACK_COLOR, part_mas_rot, var.COUNTUR)

                                if len(part["marker"]):
                                    center_x, center_y = part["centroid"]["center_x"], part["centroid"]["center_y"]
                                    center_x, center_y = center_x-shift_x + part["marker"]["horizontal_shift"], center_y-shift_y - part["marker"]["vertical_shift"]

                                    marker_sprite = pygame.transform.rotate(part["marker"]["sprite"], part["marker"]["angle"])
                                    text_marker_place = marker_sprite.get_rect(center=(center_x, center_y))
                                    game_sprite.blit(marker_sprite, text_marker_place)  # Пишем маркер

                            # 2.2 поворот в массиве
                            rotate_parts(ring, part_mas, puzzle_arch, radians(angle_rotate), -direction_)
                            calc_parts_countur(part_mas, puzzle_arch)

                        link_mas[mm]["angle"], link_mas[mm]["sprite"] = angle_deg, game_sprite

                    if not var.undo and angle_rotate!=0:
                        var.moves += 1
                        var.moves_stack.append([ring_num, direction])
                        var.redo_stack = []

                    break

            #####################################################################################
            # отрисовка игрового поля
            if (fl_event or fl_test) and not animation_on:
                SCREEN.fill(var.BACKGROUND_COLOR)  # Заливаем поверхность сплошным цветом
                pf = pygame.Surface((var.WIN_WIDTH, 10))  # Рисуем разделительную черту
                pf.fill(pygame.Color("#B88800"))
                SCREEN.blit(pf, (0, var.WIN_HEIGHT))
                pf = pygame.Surface((var.WIN_WIDTH, var.WIN_HEIGHT))  # Рисуем серый блок
                pf.fill(pygame.Color(var.GRAY_COLOR))
                SCREEN.blit(pf, (0, 0))

                draw_game_screen(SCREEN,game_scr, puzzle_rings,puzzle_parts,ring_select, shift_width,shift_height)

            if animation_on:
                # цикл Анимации
                ring = find_element(ring_num, puzzle_rings)
                if len(ring["linked"]) == 0 or len(ring["linked"]["link_mas"]) == 0:
                    link_dict = dict(ring_num=ring_num, direction=1, gear_ratio=1, angle=angle_deg, sprite=game_sprite)
                    link_mas = [ link_dict ]
                    # link_mas = [[ring_num,1,1,angle_deg,game_sprite]] - "ring_num", "direction", "gear_ratio", "angle", "sprite"
                else:
                    link_mas = ring["linked"]["link_mas"]

                for link in link_mas:
                    ring_num_, direction_, angle_deg, game_sprite = link["ring_num"], link["direction"], link["angle"], link["sprite"]

                    if game_sprite=="": continue
                    direction_ = direction * direction_
                    # рисуем поворотную часть (плавный поворот только круглого спрайта)
                    ring = find_element(ring_num_, puzzle_rings)
                    game_sprite_rot = pygame.transform.rotate(game_sprite, angle_deg * count * -direction_) # по умолчанию вращение против часовой стрелки, поэтому минус
                    game_sprite_pos = game_sprite_rot.get_rect(center=(ring["center_x"], ring["center_y"]))
                    SCREEN.blit(game_sprite_rot, (game_sprite_pos.left+shift_width,game_sprite_pos.top+shift_height))

                step,count = step-1, count+1
                if step<0: animation_on = False

            if (fl_event or fl_test):
                pf = pygame.Surface((var.WIN_WIDTH, var.PANEL))  # Рисуем фон
                pf.fill(pygame.Color(var.BACKGROUND_COLOR))
                SCREEN.blit(pf, (0, var.WIN_HEIGHT+10))

                # отрисовка текстов
                parts_kol = len(puzzle_parts)
                draw_all_text(SCREEN, font, font2, puzzle_kol, rings_kol, parts_kol, button_Save, button_Help, toggle_Marker, toggle_Circle, button_y2, button_y3, button_y4)

            # окно помощи
            if help_gen:
                help_screen = pygame.transform.scale(game_scr, var.HELP)
                help_gen = False
            if help==1 and fl_event:
                SCREEN.blit(help_screen, (var.WIN_WIDTH-var.HELP[0]-var.BORDER//3, var.BORDER//3))
                pygame.draw.rect(SCREEN, pygame.Color("#B88800"), (var.WIN_WIDTH-var.HELP[0]-2*(var.BORDER//3), 0, var.HELP[0]+2*(var.BORDER//3), var.HELP[1]+2*(var.BORDER//3)), var.BORDER//3)

            # окно с фото головоломки
            if not no_photo and photo==1 and fl_event:
                if photo_screen=="":
                    photo_screen = find_photo(puzzle_name)
                if photo_screen!="":
                    SCREEN.blit(photo_screen, (var.WIN_WIDTH-var.PHOTO[0]-var.BORDER//3, var.BORDER//3))
                    pygame.draw.rect(SCREEN, pygame.Color("#B88800"), (var.WIN_WIDTH-var.PHOTO[0]-2*(var.BORDER//3), 0, var.PHOTO[0]+2*(var.BORDER//3), var.PHOTO[1]+2*(var.BORDER//3)), var.BORDER//3)

            if fl_screenshot:
                # мигнем экраном
                pygame.draw.rect(SCREEN, pygame.Color(var.BLUE_COLOR), (shift_width, shift_height, var.GAME[0], var.GAME[1]), var.BORDER//3)
                text_info, _ = ptext.draw("screenshot saving...", (var.BORDER//2+5, var.BORDER//2), color=var.BLUE_COLOR, fontsize=20, sysfontname='Verdana', align="left")

            pygame_widgets.update(events)
            pygame.display.update()  # обновление и вывод всех изменений на экран

            first_pass = fl_event = False
            #####################################################################################

            if fl_test or fl_screenshot:
                if not test_mode_screenshot(SCREEN,game_scr, puzzle_name,puzzle_rings,puzzle_arch,puzzle_parts, fl_test, fl_test_photo, fl_test_scramble, count_test_scramble, fl_screenshot, photo_screen, dir_screenshots, sub_folder, shift_width,shift_height):
                    break

        # удаляем кнопки
        for btn in button_set:
            btn.hide()

    if fl_test:
        end_time = time.time() - start_time
        minute, secunde = int(end_time // 60), round(end_time % 60, 2)
        print("End testing: " + str(minute) + " minutes, " + str(secunde) + " sec")

main()