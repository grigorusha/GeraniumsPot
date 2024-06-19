from work import *
from syst import *

import pygame, pygame_widgets

from math import pi, sqrt, cos, sin, tan, acos, asin, atan, exp, pow, radians, degrees, hypot

from tkinter import Tk
import os,copy,time, ptext
# import Pillow - for pyinstaller splash-screen

VERSION = "1.9.1"

# + TODO 0. Горячие кнопки: F6-Маркеры, F7-Скриншот, F9-Сохранить, crtl+O-Открыть
# + TODO 0. Сделать Скриншот. скопировать в буфер. мигнуть при скриншоте
# + TODO 0. Сохранить/восстановить состояние головоломки. восстановить историю ходов
# + TODO 0. Шестеренки/Линкед: добавил параметр Gears к команде Ring, добавил команду Linked, новая папка Geared Puzzles, Save
# + TODO 0. Шестеренки/Линкед: Круги с разным передаточным числом, Команда Scramble учитывает связки, выделение связанных колец
# + TODO 0. Новая команда: RenumberingAuto: 0
# + TODO 0. ошибка: изменить Scale, потом Reset - не меняет размер окна
# + TODO 0. Проверить работу в WINE

# --------------------------------------------------------------------------------------

# TODO 1. SplashScreen - анимация зеленых точек
# TODO 1. PygameMenu
# TODO 1. Новые команды: RingUpdate, RingDelete
# TODO 1. если нет движений мышкой и событий - ничего не перерисовывать
# TODO 1. сборка в DEBIAN,FEDORA

# TODO 2. Бандаж заданных частей
# TODO 2. Оборвать по ЕСК долгую загрузку
# TODO 2. проценты : Повтор в последовательностях

# TODO 3. Контурные отверстия в частях
# TODO 3. Поиск пересекающихся частей - вывод инфо об ошибках, красный контур

# TODO 4. Разделение частей линиями - для задания узоров
# TODO 4. Скругление уголков

# TODO 5. Меню открытия с иконками и названиями. Поиск с фильтрами (автор, дата, класс)
# TODO 5. копиРинг - не должен менять индекс угла при повороте джамб колец
# TODO 5. Слайдинги горизонтальные
# TODO *. Поиск дубликатов - игнор микро-отрезков
# TODO *. Авто-поиск новых кругов
# TODO *. Рисунки
# TODO *. Solved

BACKGROUND_COLOR = "#000000"
GRAY_COLOR, GRAY_COLOR2, BLACK_COLOR = "#606060", "#C0C0C0", "#000000"
WHITE_COLOR, RED_COLOR, GREEN_COLOR, BLUE_COLOR = "#FFFFFF", "#FF0000", "#008000", "#0000FF"
PARTS_COLOR =    [(255, 255, 255, 255), (30, 30, 30, 255), (150, 150, 150, 255),  # 0 белый 1 черный 2 серый
                  (255, 0, 0, 255), (0, 150, 0, 255), (0, 0, 255, 255),           # 3 красный 4 зеленый 5 синий
                  (255, 255, 0, 255), (128, 0, 128, 255), (0, 128, 128, 255),     # 6 желтый (крас+зел) 7 фиолетовый (кра+син) 8 бирюзовый (зел+син)
                  (250, 150, 0, 255), (100, 200, 250, 255), (250, 120, 190, 255), # 9 оранжевый 10 голубой 11 розовый
                  (120, 60, 30, 255), (200, 130, 250, 255), (70, 250, 70, 255)]   # 12 коричневый 13 сиреневый 14 лайм

WIN_WIDTH, WIN_HEIGHT = 470, 300
PANEL = 29 * 4
BORDER = 20
COUNTUR = 1.5
GAME = (WIN_WIDTH, WIN_HEIGHT)

dirname = filename = ""

BTN_CLICK = False
BTN_CLICK_STR = ""

def button_Button_click(button_str):
    global BTN_CLICK, BTN_CLICK_STR
    BTN_CLICK_STR = button_str
    BTN_CLICK = True

def button_init(screen, font_button, WIN_HEIGHT, auto_marker, show_hidden_circles):
    from pygame_widgets.button import Button
    from pygame_widgets.toggle import Toggle
    GREEN_COLOR, LIME_COLOR = (0, 150, 0), (0, 250, 0)
    BLUE_COLOR, LBLUE_COLOR = (0, 0, 250), (80, 200, 250)
    GRAY_COLOR = (100, 100, 100)

    button_y1 = int(WIN_HEIGHT) + 20
    button_Reset = Button(screen, 10, button_y1, 45, 20, text='Reset', fontSize=20, font=font_button, margin=5,
                          radius=3,
                          inactiveColour=GREEN_COLOR, hoverColour=LIME_COLOR, pressedColour=LIME_COLOR,
                          onClick=lambda: button_Button_click("reset"))
    button_Scramble = Button(screen, button_Reset.textRect.right + 10, button_y1, 70, 20, text='Scramble',
                             fontSize=20, font=font_button, margin=5, radius=3,
                             inactiveColour=GREEN_COLOR, hoverColour=LIME_COLOR, pressedColour=LIME_COLOR,
                             onClick=lambda: button_Button_click("scramble"))
    button_Undo = Button(screen, button_Scramble.textRect.right + 10, button_y1, 40, 20, text='Undo',
                         fontSize=20, font=font_button, margin=5, radius=3,
                         inactiveColour=GREEN_COLOR, hoverColour=LIME_COLOR, pressedColour=LIME_COLOR,
                         onClick=lambda: button_Button_click("undo"))
    button_Redo = Button(screen, button_Undo.textRect.right + 10, button_y1, 40, 20, text='Redo',
                         fontSize=20, font=font_button, margin=5, radius=3,
                         inactiveColour=GREEN_COLOR, hoverColour=LIME_COLOR, pressedColour=LIME_COLOR,
                         onClick=lambda: button_Button_click("redo"))

    button_Photo = Button(screen, button_Redo.textRect.right + 20, button_y1, 60, 20, text='Photo ->',
                         fontSize=20, font=font_button, margin=5, radius=3,
                         inactiveColour=BLUE_COLOR, hoverColour=LBLUE_COLOR, pressedColour=LBLUE_COLOR,
                         onClick=lambda: button_Button_click("photo"))
    button_Info = Button(screen, button_Photo.textRect.right + 10, button_y1, 48, 20, text='Info ->',
                         fontSize=20, font=font_button, margin=5, radius=3,
                         inactiveColour=BLUE_COLOR, hoverColour=LBLUE_COLOR, pressedColour=LBLUE_COLOR,
                         onClick=lambda: button_Button_click("info"))
    button_About = Button(screen, button_Info.textRect.right + 10, button_y1, 60, 20, text='About ->',
                          fontSize=20, font=font_button, margin=5, radius=3,
                          inactiveColour=BLUE_COLOR, hoverColour=LBLUE_COLOR, pressedColour=LBLUE_COLOR,
                          onClick=lambda: button_Button_click("about"))

    button_y2 = button_y1 + 25
    button_Open = Button(screen, 10, button_y2, 45, 20, text='Open',
                         fontSize=20, font=font_button, margin=5, radius=3,
                         inactiveColour=GREEN_COLOR, hoverColour=LIME_COLOR, pressedColour=LIME_COLOR,
                         onClick=lambda: button_Button_click("open"))
    button_Save = Button(screen, button_Open.textRect.right + 10, button_y2, 45, 20, text='Save',
                         fontSize=20, font=font_button, margin=5, radius=3,
                         inactiveColour=GREEN_COLOR, hoverColour=LIME_COLOR, pressedColour=LIME_COLOR,
                         onClick=lambda: button_Button_click("save"))

    button_Help = Button(screen, button_Undo.textRect.right + 10, button_y2, 80, 20, text='Solved State',
                         fontSize=20, font=font_button, margin=5, radius=3,
                         inactiveColour=GREEN_COLOR, hoverColour=LIME_COLOR, pressedColour=LIME_COLOR,
                         onClick=lambda: button_Button_click("help"))

    button_y3 = button_y2 + 30
    toggle_Marker = Toggle(screen, 15, button_y3, 13,10, offColour=GRAY_COLOR, onColour=GREEN_COLOR, startOn=auto_marker)
    toggle_Circle = Toggle(screen, 120, button_y3, 13,10, offColour=GRAY_COLOR, onColour=GREEN_COLOR, startOn=show_hidden_circles)

    button_y4 = button_y3 + 20
    return button_y2, button_y3, button_y4, button_Save, button_Help, toggle_Marker, toggle_Circle, [button_Reset, button_Scramble, button_Undo, button_Redo, button_Open, button_Save, button_Info, button_Help, button_Photo, button_About, toggle_Marker, toggle_Circle]

def main():
    global VERSION, BTN_CLICK, BTN_CLICK_STR, WIN_WIDTH, WIN_HEIGHT, BORDER, GAME, filename

    file_ext, fl_reset, fl_esc, fl_load_save, show_hidden_circles = False, False, False, False, False
    puzzle_name, puzzle_author, puzzle_scale, puzzle_speed, puzzle_kol, auto_marker, auto_marker_ring, puzzle_web_link, puzzle_width, puzzle_height, vek_mul = "", "", 1, 2, 1, 0, 0, [], 0,0, -1
    puzzle_rings, puzzle_arch, puzzle_parts, puzzle_lines, puzzle_points, remove_parts, copy_parts = [], [], [], [], [], [], []
    resized, fl_resize = 0, False # 0 - нет, 1 - да, 2 - макс

    # инициализация режима Теста
    fl_reset_ini, fl_test, fl_test_photo, fl_test_scramble, dir_garden, dir_screenshots = arg_param_check()
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

    ################################################################################
    ################################################################################
    # перезапуск программы при смене параметров
    while True:
        if fl_test:
            file_ext, help_gen, count_test_scramble = True, False, 0
            if len(mas_files)==file_num: break
            sub_folder = mas_files[file_num][0].replace(dir_garden,"")
            fil,file_num = init_test(file_num, mas_files, BORDER, PARTS_COLOR)
            close_spalsh_screen()
            if typeof(fil) != "str":
                puzzle_name, puzzle_author, puzzle_web_link, puzzle_scale, puzzle_speed, puzzle_rings, puzzle_arch, puzzle_parts, puzzle_lines, puzzle_points, puzzle_kol, vek_mul, dirname, filename, puzzle_width, puzzle_height, auto_marker, auto_marker_ring, remove_parts, copy_parts, show_hidden_circles, moves, moves_stack, fl_load_save = fil
            else: break

        elif not file_ext and not fl_resize:
            file_ext, fil = init_puzzle(BORDER, PARTS_COLOR, VERSION, fl_reset_ini, fl_esc)
            close_spalsh_screen()
            if typeof(fil) != "str":
                puzzle_name, puzzle_author, puzzle_web_link, puzzle_scale, puzzle_speed, puzzle_rings, puzzle_arch, puzzle_parts, puzzle_lines, puzzle_points, puzzle_kol, vek_mul, dirname, filename, puzzle_width, puzzle_height, auto_marker, auto_marker_ring, remove_parts, copy_parts, show_hidden_circles, moves, moves_stack, fl_load_save = fil
            else: break

        if not fl_resize and not resized:
            WIN_WIDTH, WIN_HEIGHT = puzzle_width, puzzle_height

        help_mul = 2 if not fl_test else 1.5
        DISPLAY = (WIN_WIDTH, WIN_HEIGHT + PANEL)
        GAME = (puzzle_width, puzzle_height)
        HELP = (WIN_WIDTH // help_mul, WIN_HEIGHT // help_mul)
        PHOTO = (WIN_WIDTH // help_mul, WIN_HEIGHT // help_mul)
        shift_width,shift_height = (WIN_WIDTH-puzzle_width)//2,(WIN_HEIGHT-puzzle_height)//2

        # инициализация окна
        if not fl_reset and not fl_resize:
            pos_x = int(screen_width/2 - WIN_WIDTH/2)
            pos_y = int(screen_height - (WIN_HEIGHT + PANEL))
            os.environ['SDL_VIDEO_WINDOW_POS'] = '%i,%i' % (pos_x, pos_y)
            os.environ['SDL_VIDEO_CENTERED'] = '0'

            screen = pygame.display.set_mode(DISPLAY, RESIZABLE)  # Создаем окошко
        game_scr = Surface(GAME) # , pygame.SRCALPHA, 32) #

        if not fl_resize:
            win_caption = puzzle_name if puzzle_name != "" else "Geraniums Pot Simulator"
            if puzzle_author != "": win_caption += " (" + puzzle_author.strip() + ")"
            pygame.display.set_caption(win_caption)  # Пишем в шапку

            if not fl_test:
                keyboard_press("alt")
                window_front(win_caption)

            if not fl_load_save:
                moves, moves_stack = 0, []
            redo_stack, solved = [], True

            mouse_xx, mouse_yy = 0, 0
            help,help_gen,photo,photo_gen = 0, True, 0, True
            animation_on, events = False, ""
            if fl_test: help_gen = False

        fl_resize = fl_esc = False

        rings_kol = 0
        for ring in puzzle_rings:
            if ring[6]==0: rings_kol+=1

        # инициализация кнопок
        button_y2, button_y3, button_y4, button_Save, button_Help, toggle_Marker, toggle_Circle, button_set = button_init(screen, font_button, WIN_HEIGHT, auto_marker, show_hidden_circles)
        ctrl_pressed = shift_pressed = False

        ################################################################################
        ################################################################################
        # Основной цикл программы
        while True:
            timer.tick(50)

            if not animation_on:
                fl_break = undo = fl_screenshot = False
                mouse_x, mouse_y, mouse_left, mouse_right, ring_select = 0, 0, False, False, 0
                ring_num = direction = 0
                auto_marker, show_hidden_circles = toggle_Marker.value, toggle_Circle.value

                ################################################################################
                # обработка событий
                if not help_gen: # при первом цикле, сначала надо полностью нарисовать, потом считывать кнопки
                    events = pygame.event.get()
                    auto_marker, show_hidden_circles = toggle_Marker.value, toggle_Circle.value
                    fil, fil2 = events_check_read_puzzle(events, fl_break, fl_reset, fl_test, VERSION, BTN_CLICK, BTN_CLICK_STR, BORDER, WIN_WIDTH, WIN_HEIGHT, puzzle_width, puzzle_height, PANEL, win_caption, file_ext, puzzle_name, puzzle_author, puzzle_web_link, puzzle_speed, puzzle_rings, puzzle_arch, puzzle_parts, puzzle_lines, puzzle_points, help, photo, undo, moves, moves_stack, redo_stack, ring_num, direction, mouse_xx, mouse_yy, dirname, filename, PARTS_COLOR, auto_marker, auto_marker_ring, ctrl_pressed, shift_pressed, resized)

                    if typeof(fil2) == "str":
                        if fil2 == "QUIT" and fl_test:
                            end_time = time.time() - start_time
                            minute, secunde = int(end_time//60), round(end_time%60,2)
                            print("End testing: "+str(minute)+" minutes, "+str(secunde)+" sec")
                        return fil
                    if typeof(fil) != "str":
                        puzzle_name, puzzle_author, puzzle_web_link, puzzle_scale, puzzle_speed, puzzle_rings, puzzle_arch, puzzle_parts, puzzle_lines, puzzle_points, puzzle_kol, vek_mul, dirname, filename, puzzle_width, puzzle_height, auto_marker, auto_marker_ring, remove_parts, copy_parts, show_hidden_circles, moves, moves_stack, fl_load_save = fil
                    elif fil=="break":
                        fl_esc = True
                    fl_break, fl_reset, file_ext, fl_resize, resized, BTN_CLICK, BTN_CLICK_STR, undo, moves, moves_stack, redo_stack, ring_num, direction, mouse_xx, mouse_yy, mouse_x, mouse_y, mouse_left, mouse_right, help, photo, WIN_WIDTH, WIN_HEIGHT, puzzle_width, puzzle_height, auto_marker, fl_screenshot, ctrl_pressed, shift_pressed = fil2

                    if auto_marker!=toggle_Marker.value:
                        toggle_Marker.value=auto_marker
                        if auto_marker:
                            toggle_Marker.colour, toggle_Marker.handleColour = toggle_Marker.onColour, toggle_Marker.handleOnColour
                        else:
                            toggle_Marker.colour, toggle_Marker.handleColour = toggle_Marker.offColour, toggle_Marker.handleOffColour

                    if fl_break or fl_resize: break

                ################################################################################
                # обработка перемещения и нажатия в игровом поле
                # mouse_xx, mouse_yy - координаты мышки при перемещении. mouse_x, mouse_y - координаты точки клика
                # ring_select - координаты кольца над которым двигается курсор. ring_num - кольцо внутри которого был клик
                mouse_xx_, mouse_yy_, mouse_x_, mouse_y_ = mouse_xx-shift_width, mouse_yy-shift_height, mouse_x-shift_width, mouse_y-shift_height
                if (mouse_xx_ + mouse_yy_ > 0) and mouse_xx_ < puzzle_width and mouse_yy_ < puzzle_height and not undo:
                    ring_num, ring_select, direction = mouse_move_click(mouse_xx_, mouse_yy_, mouse_x_, mouse_y_, mouse_left, mouse_right, puzzle_rings, ring_num, ring_select, direction, puzzle_parts, show_hidden_circles)

                ################################################################################
                # логика игры - выполнение перемещений
                while ring_num > 0:
                    ring = find_element(ring_num, puzzle_rings)
                    if len(ring[8])==0 or len(ring[8][1])==0:
                        link_mas = [ [ring_num,1,1,0,""] ]
                    else:
                        link_mas = ring[8][1]

                    for mm,link in enumerate(link_mas):
                        ring_num_, direction_, gears_ratio, _, game_sprite = link
                        direction_ = direction*direction_
                        #############################################################################
                        # 1. найдем все части внутри круга
                        ring = find_element(ring_num_, puzzle_rings)
                        if mm==0: # ring_num_==ring_num:
                            angle_rotate = find_angle_rotate(ring, direction_)
                            p_speed = puzzle_speed*4 if angle_rotate>=120 else puzzle_speed*2
                            step, count = int(ring[3] * radians(angle_rotate) / (p_speed)), 0
                            angle_rotate0 = angle_rotate
                        else:
                            angle_rotate = angle_rotate0*gears_ratio

                        part_mas, part_mas_other = find_parts_in_circle(ring, puzzle_parts, puzzle_rings)
                        if len(part_mas) == 0 or angle_rotate == 0 or step==0:
                            link_mas[mm][4] = ""
                            continue
                        angle, angle_deg = radians(angle_rotate) / step, angle_rotate / step

                        # 2. повернем все части внутри круга
                        if len(part_mas)>0:
                            # 2.1 анимация. сформируем круглый спрайт для дальнейшего вращения
                            animation_on = True

                            game_sprite = Surface((ring[3] * 2, ring[3] * 2), pygame.SRCALPHA, 32)
                            game_sprite = game_sprite.convert_alpha()

                            shift_x, shift_y = ring[1] - ring[3], ring[2] - ring[3]

                            game_sprite.fill((0, 0, 0, 0))
                            # pygame.draw.circle(game_sprite,(96, 96, 96, 100), (ring[3],ring[3]), ring[3])
                            for nn, part in enumerate(part_mas):
                                part_mas_rot = copy.deepcopy(part[7])  # нужно для пересчета координат. чтобы круг вписался в спрайт
                                for pos in part_mas_rot:
                                    pos[0], pos[1] = pos[0] - shift_x, pos[1] - shift_y
                                pygame.draw.polygon(game_sprite, PARTS_COLOR[part[1]], part_mas_rot, 0)
                                draw_smoth_polygon(game_sprite, BLACK_COLOR, part_mas_rot, COUNTUR)

                                if len(part[3])==0: continue
                                marker_text, marker_angle, marker_size, marker_horizontal_shift, marker_vertical_shift, marker_sprite = part[3]
                                center_x, center_y, area, max_radius = part[4]
                                center_x, center_y = center_x-shift_x + marker_horizontal_shift, center_y-shift_y - marker_vertical_shift

                                marker_sprite = pygame.transform.rotate(marker_sprite, marker_angle)
                                text_marker_place = marker_sprite.get_rect(center=(center_x, center_y))
                                game_sprite.blit(marker_sprite, text_marker_place)  # Пишем маркер

                            # 2.2 поворот в массиве
                            rotate_parts(ring, part_mas, puzzle_arch, puzzle_points, radians(angle_rotate), -direction_)
                            calc_parts_countur(part_mas, puzzle_arch)

                        link_mas[mm][3], link_mas[mm][4] = angle_deg, game_sprite

                    if not undo:
                        moves += 1
                        moves_stack.append([ring_num, direction])
                        redo_stack = []

                    break

            #####################################################################################
            # отрисовка игрового поля
            if not animation_on:
                screen.fill(BACKGROUND_COLOR)  # Заливаем поверхность сплошным цветом
                pf = Surface((WIN_WIDTH, 10))  # Рисуем разделительную черту
                pf.fill(Color("#B88800"))
                screen.blit(pf, (0, WIN_HEIGHT))
                pf = Surface((WIN_WIDTH, WIN_HEIGHT))  # Рисуем серый блок
                pf.fill(Color(GRAY_COLOR))
                screen.blit(pf, (0, 0))

                # отрисовка текстов
                parts_kol = len(puzzle_parts)
                draw_all_text(screen, font, font2, puzzle_kol, rings_kol, parts_kol, moves, solved, button_Save, button_Help, toggle_Marker, toggle_Circle, button_y2, button_y3, button_y4)

                ############################################
                game_scr.fill(Color(GRAY_COLOR))

                # отрисовка контуров
                for nn,ring in enumerate(puzzle_rings):
                    if ring[6]==0:
                        draw_smoth_polygon(game_scr, GRAY_COLOR2, ring[9], 2)
                    # elif not (len(ring[8]) == 0 or len(ring[8][1]) == 0):
                    #     draw_smooth_gear(game_scr, GRAY_COLOR2, ring[1], ring[2], ring[3]+5, 10)

                # отрисовка частей
                for nn,part in enumerate(puzzle_parts):
                    if part[2]>0:
                        pygame.draw.polygon(game_scr,PARTS_COLOR[part[1]],part[7],0)
                    if part[8]==0:
                        draw_smoth_polygon(game_scr,BLACK_COLOR,part[7],COUNTUR)
                for nn, part in enumerate(puzzle_parts):
                    if part[8] != 0:
                        draw_smoth_polygon(game_scr,RED_COLOR,part[7],COUNTUR)

                # # отрисовка отверстий у частей
                # for nn,part in enumerate(puzzle_parts):
                #     if part[2]>0:
                #         part[6]
                #         pygame.draw.polygon(game_scr,PARTS_COLOR[part[1]],part[7],0)

                # отрисовка выделения
                if ring_select>0:
                    ring = find_element(ring_select, puzzle_rings)
                    draw_smoth_polygon(game_scr, WHITE_COLOR, ring[9], 2)
                    if not (len(ring[8]) == 0 or len(ring[8][1]) == 0):
                        for nn,linked in enumerate(ring[8][1]):
                            if nn==0: continue
                            linked_ring = find_element(linked[0], puzzle_rings)
                            if check_ring_intersecting_parts(linked_ring, puzzle_parts):
                                draw_smoth_polygon(game_scr, WHITE_COLOR, linked_ring[9], 2)

                # рисуем маркеры
                draw_all_markers(game_scr, puzzle_parts,puzzle_rings, auto_marker,auto_marker_ring, BLACK_COLOR,WHITE_COLOR,RED_COLOR)

                screen.blit(game_scr, (shift_width,shift_height))

            else:
                # цикл Анимации
                ring = find_element(ring_num, puzzle_rings)
                if len(ring[8]) == 0 or len(ring[8][1]) == 0:
                    link_mas = [[ring_num,1,1,angle_deg,game_sprite]]
                else:
                    link_mas = ring[8][1]

                for ring_num_, direction_, gears_ratio, angle_deg, game_sprite in link_mas:
                    if game_sprite=="": continue
                    direction_ = direction * direction_
                    # рисуем поворотную часть (плавный поворот только круглого спрайта)
                    ring = find_element(ring_num_, puzzle_rings)
                    game_sprite_rot = pygame.transform.rotate(game_sprite, angle_deg * count * -direction_) # по умолчанию вращение против часовой стрелки, поэтому минус
                    game_sprite_new = game_sprite_rot.get_rect(center=(ring[1], ring[2]))
                    screen.blit(game_sprite_rot, (game_sprite_new.left+shift_width,game_sprite_new.top+shift_height))

                step,count = step-1, count+1
                if step<0: animation_on = False

            # окно помощи
            if help_gen:
                help_gen = False
                help_screen = pygame.transform.scale(game_scr, HELP)
            if help==1:
                screen.blit(help_screen, (GAME[0]-HELP[0]-BORDER//3, BORDER//3))
                draw.rect(screen, Color("#B88800"), (GAME[0]-HELP[0]-2*(BORDER//3), 0, HELP[0]+2*(BORDER//3), HELP[1]+2*(BORDER//3)), BORDER//3)

            # окно с фото головоломки
            if photo_gen:
                photo_gen, photo = False, 0
                photo_screen, PHOTO = find_photo(puzzle_name, PHOTO)
            if photo==1 and photo_screen!="":
                screen.blit(photo_screen, (GAME[0]-PHOTO[0]-BORDER//3, BORDER//3))
                draw.rect(screen, Color("#B88800"), (GAME[0]-PHOTO[0]-2*(BORDER//3), 0, PHOTO[0]+2*(BORDER//3), PHOTO[1]+2*(BORDER//3)), BORDER//3)

            if fl_screenshot:
                # мигнем экраном
                draw.rect(screen, Color(BLUE_COLOR), (0, 0, GAME[0], GAME[1]), BORDER//3)
                text_info, _ = ptext.draw("screenshot saving...", (BORDER//2+5, BORDER//2), color=BLUE_COLOR, fontsize=20, sysfontname='Verdana', align="left")

            pygame_widgets.update(events)
            pygame.display.update()  # обновление и вывод всех изменений на экран

            #####################################################################################

            if fl_test or fl_screenshot:
                if not test_mode_screenshot(game_scr, puzzle_name,puzzle_rings,puzzle_arch,puzzle_parts,puzzle_points, fl_test, fl_test_photo, fl_test_scramble, fl_screenshot, count_test_scramble, photo_screen, dir_screenshots, sub_folder, GAME, PHOTO, BORDER):
                    break

        # удаляем кнопки
        for btn in button_set:
            btn.hide()

    if fl_test:
        end_time = time.time() - start_time
        minute, secunde = int(end_time // 60), round(end_time % 60, 2)
        print("End testing: " + str(minute) + " minutes, " + str(secunde) + " sec")

main()