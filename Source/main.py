from work import *
from syst import *

import pygame
import pygame.gfxdraw
import pygame_widgets

from math import pi, sqrt, cos, sin, tan, acos, asin, atan, exp, pow, radians, degrees, hypot

from tkinter import Tk
import os,copy,keyboard,time

import ptext
# import Pillow - for pyinstaller spalsh screen

VERSION = "1.9"

# TODO 1. Повтор в последовательностях + проценты
# TODO 1. Поиск пересекающихся частей - вывод инфо об ошибках, красный контур
# TODO 1. Оборвать по ЕСК долгую загрузку

# TODO 2. Бандаж заданных частей
# TODO 3. копиРинг - не должен менять индекс угла при повороте джамб колец

# TODO 4. Разделение частей линиями - для задания узоров
# TODO 4. Контурные отверстия в частях
# TODO 4. Скругление уголков
# TODO 4. Поиск дубликатов - игнор микро-отрезков

# TODO *. Авто-поиск новых кругов
# TODO *. Solved
# TODO *. Save
# TODO *. Слайдинги горизонтальные
# TODO *. Шестеренки, Линкед
# TODO *. Рисунки

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
    button_Open = Button(screen, 10, button_y2, 45, 20, text='Open', fontSize=20, font=font_button, margin=5,
                         radius=3,
                         inactiveColour=GREEN_COLOR, hoverColour=LIME_COLOR, pressedColour=LIME_COLOR,
                         onClick=lambda: button_Button_click("open"))

    button_Help = Button(screen, button_Scramble.textRect.right + 10, button_y2, 80, 20, text='Solved State',
                         fontSize=20, font=font_button, margin=5, radius=3,
                         inactiveColour=GREEN_COLOR, hoverColour=LIME_COLOR, pressedColour=LIME_COLOR,
                         onClick=lambda: button_Button_click("help"))

    button_y3 = button_y2 + 30
    toggle_Marker = Toggle(screen, 15, button_y3, 13,10, offColour=GRAY_COLOR, onColour=GREEN_COLOR, startOn=auto_marker)
    toggle_Circle = Toggle(screen, 120, button_y3, 13,10, offColour=GRAY_COLOR, onColour=GREEN_COLOR, startOn=show_hidden_circles)

    button_y4 = button_y3 + 20
    return button_y2, button_y3, button_y4, button_Open, button_Help, toggle_Marker, toggle_Circle, [button_Reset, button_Scramble, button_Undo, button_Redo, button_Open, button_Info, button_Help, button_Photo, button_About, toggle_Marker, toggle_Circle]

def main():
    global VERSION, BTN_CLICK, BTN_CLICK_STR, WIN_WIDTH, WIN_HEIGHT, BORDER, GAME, filename

    file_ext, fl_reset, fl_resize, fl_esc, show_hidden_circles = False, False, False, False, False
    puzzle_name, puzzle_author, puzzle_scale, puzzle_speed, puzzle_kol, auto_marker, auto_marker_ring, puzzle_link, puzzle_width, puzzle_height = "", "", 1, 2, 1, 0, 0, [], 0,0
    puzzle_rings, puzzle_arch, puzzle_parts, puzzle_lines, puzzle_points, remove_parts, copy_parts = [], [], [], [], [], [], []
    vek_mul = -1

    # инициализация режима Теста
    fl_reset_ini, fl_test, fl_test_photo, fl_test_scramble, dir_garden, dir_screenshots = arg_param_check()
    if fl_test:
        file_num, count_test_scramble, sub_folder = 0, 0, ""
        mas_files, dir_garden, dir_screenshots = dir_test(dir_garden, dir_screenshots)
        purge_dir(dir_screenshots, "jpg,jpeg,png")

        start_time = time.time()
        print("Start testing...")

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

    icon = os.path.abspath(os.curdir) + "\\Geraniums Pot.png"
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
                puzzle_name, puzzle_author, puzzle_link, puzzle_scale, puzzle_speed, puzzle_rings, puzzle_arch, puzzle_parts, puzzle_lines, puzzle_points, puzzle_kol, vek_mul, dirname, filename, puzzle_width, puzzle_height, auto_marker, auto_marker_ring, remove_parts, copy_parts, show_hidden_circles = fil
            else: break

        elif not file_ext and not fl_resize:
            file_ext, fil = init_puzzle(BORDER, PARTS_COLOR, VERSION, fl_reset_ini, fl_esc)
            close_spalsh_screen()
            if typeof(fil) != "str":
                puzzle_name, puzzle_author, puzzle_link, puzzle_scale, puzzle_speed, puzzle_rings, puzzle_arch, puzzle_parts, puzzle_lines, puzzle_points, puzzle_kol, vek_mul, dirname, filename, puzzle_width, puzzle_height, auto_marker, auto_marker_ring, remove_parts, copy_parts, show_hidden_circles = fil
            else: break

        if not fl_resize:
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
                keyboard.press_and_release("alt") # странный трюк, чтобы вернуть фокус после сплаш скрина
                window_front(win_caption)

            moves, moves_stack, redo_stack = 0, [], []
            solved = True

            mouse_xx, mouse_yy = 0, 0
            help,help_gen,photo,photo_gen = 0, True, 0, True
            animation_on, events = False, ""
            if fl_test: help_gen = False

        fl_resize = fl_esc = False

        rings_kol = 0
        for ring in puzzle_rings:
            if ring[6]==0: rings_kol+=1

        # инициализация кнопок
        button_y2, button_y3, button_y4, button_Open, button_Help, toggle_Marker, toggle_Circle, button_set = button_init(screen, font_button, WIN_HEIGHT, auto_marker, show_hidden_circles)

        ################################################################################
        ################################################################################
        # Основной цикл программы
        while True:
            timer.tick(150)

            if not animation_on:
                fl_break = undo = False
                mouse_x, mouse_y, mouse_left, mouse_right, ring_select = 0, 0, False, False, 0
                ring_num = direction = 0
                auto_marker, show_hidden_circles = toggle_Marker.value, toggle_Circle.value

                ################################################################################
                # обработка событий
                if not help_gen: # при первом цикле, сначала надо полностью нарисовать, потом считывать кнопки
                    events = pygame.event.get()
                    fil, fil2 = events_check_read_puzzle(events, fl_break, fl_reset, fl_test, VERSION, BTN_CLICK, BTN_CLICK_STR, BORDER, WIN_WIDTH, WIN_HEIGHT, puzzle_width, puzzle_height, PANEL, win_caption, file_ext, puzzle_link, puzzle_rings, puzzle_arch, puzzle_parts, puzzle_lines, puzzle_points, help, photo, undo, moves, moves_stack, redo_stack, ring_num, direction, mouse_xx, mouse_yy, dirname, filename, PARTS_COLOR, auto_marker, auto_marker_ring)

                    if typeof(fil2) == "str":
                        if fil2 == "QUIT" and fl_test:
                            end_time = time.time() - start_time
                            minute, secunde = int(end_time//60), round(end_time%60,2)
                            print("End testing: "+str(minute)+" minutes, "+str(secunde)+" sec")
                        return fil
                    if typeof(fil) != "str":
                        puzzle_name, puzzle_author, puzzle_link, puzzle_scale, puzzle_speed, puzzle_rings, puzzle_arch, puzzle_parts, puzzle_lines, puzzle_points, puzzle_kol, vek_mul, dirname, filename, puzzle_width, puzzle_height, auto_marker, auto_marker_ring, remove_parts, copy_parts, show_hidden_circles = fil
                    elif fil=="break":
                        fl_esc = True
                    fl_break, fl_reset, file_ext, fl_resize, BTN_CLICK, BTN_CLICK_STR, undo, moves, moves_stack, redo_stack, ring_num, direction, mouse_xx, mouse_yy, mouse_x, mouse_y, mouse_left, mouse_right, help, photo, WIN_WIDTH, WIN_HEIGHT, puzzle_width, puzzle_height = fil2

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
                    #############################################################################
                    # 1. найдем все части внутри круга
                    ring = find_element(ring_num, puzzle_rings)
                    part_mas, part_mas_other = find_parts_in_circle(ring, puzzle_parts, puzzle_rings)

                    if len(part_mas) == 0: break

                    # 2. повернем все части внутри круга
                    if len(part_mas)>0:
                        angle_rotate = find_angle_rotate(ring,direction)

                        # 2.1 анимация. сформируем круглый спрайт для дальнейшего вращения
                        animation_on = True

                        game_sprite = Surface((ring[3] * 2, ring[3] * 2), pygame.SRCALPHA, 32)
                        game_sprite = game_sprite.convert_alpha()

                        step, count = int(ring[3] * radians(angle_rotate) / puzzle_speed), 0
                        angle, angle_deg = radians(angle_rotate) / step, angle_rotate / step
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
                        rotate_parts(ring, part_mas, puzzle_arch, puzzle_points, radians(angle_rotate), -direction)
                        calc_parts_countur(part_mas, puzzle_arch)

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
                draw_all_text(screen, font, font2, puzzle_kol, rings_kol, parts_kol, moves, solved, button_Open, button_Help, toggle_Marker, toggle_Circle, button_y2, button_y3, button_y4)

                ############################################
                game_scr.fill(Color(GRAY_COLOR))

                # отрисовка контуров
                for nn,ring in enumerate(puzzle_rings):
                    if ring[6]==0:
                        draw_smoth_polygon(game_scr, GRAY_COLOR2, ring[8], 2)

                # отрисовка частей
                for nn,part in enumerate(puzzle_parts):
                    if part[2]>0:
                        pygame.draw.polygon(game_scr,PARTS_COLOR[part[1]],part[7],0)
                    if part[8]==0:
                        draw_smoth_polygon(game_scr,BLACK_COLOR,part[7],COUNTUR)
                for nn, part in enumerate(puzzle_parts):
                    if part[8] != 0:
                        draw_smoth_polygon(game_scr,RED_COLOR,part[7],COUNTUR)

                # отрисовка выделения
                if ring_select>0:
                    ring = find_element(ring_select, puzzle_rings)
                    # if check_ring_intersecting_parts(ring, puzzle_parts):
                    draw_smoth_polygon(game_scr, WHITE_COLOR, ring[8], 2)

                # рисуем маркеры
                for nn, part in enumerate(puzzle_parts):
                    marker_sprite = ""
                    marker_color = BLACK_COLOR if part[1] != 1 else WHITE_COLOR
                    center_x, center_y, area, max_radius = part[4]
                    if auto_marker:
                        marker_sprite, _ = ptext.draw(str(part[0]), (0, 0), color=marker_color, fontsize=10, sysfontname='Verdana', align="center")
                    elif len(part[3])!=0:
                        marker_text, marker_angle, marker_size, marker_horizontal_shift, marker_vertical_shift, marker_sprite = part[3]
                        center_x += marker_horizontal_shift
                        center_y -= marker_vertical_shift
                        if marker_sprite=="":
                            if marker_size==0:
                                marker_size = int(area/200)
                            fontname = 'Verdana'
                            if "↑↓→←".find(marker_text)>=0:
                                fontname = 'Arial'
                            marker_sprite, _ = ptext.draw(marker_text, (0, 0), color=marker_color, fontsize=marker_size, sysfontname=fontname, align="center")
                            part[3][5] = marker_sprite
                        marker_sprite = pygame.transform.rotate(marker_sprite, marker_angle)
                    if marker_sprite!="":
                        text_marker_place = marker_sprite.get_rect(center=(center_x, center_y))
                        game_scr.blit(marker_sprite, text_marker_place)  # Пишем маркер
                if auto_marker_ring:
                    for nn, ring in enumerate(puzzle_rings):
                        if ring[6]!=0: continue
                        center_x, center_y = ring[1],ring[2]
                        text_marker, _ = ptext.draw(str(ring[0]), (0, 0), color=RED_COLOR, fontsize=20, sysfontname='Verdana', align="center", owidth=1, ocolor="blue")
                        text_marker_place = text_marker.get_rect(center=(center_x, center_y))
                        game_scr.blit(text_marker, text_marker_place)  # Пишем маркер

                screen.blit(game_scr, (shift_width,shift_height))

            else:
                # рисуем поворотную часть (плавный поворот только круглого спрайта)
                ring = find_element(ring_num, puzzle_rings)
                game_sprite_rot = pygame.transform.rotate(game_sprite, angle_deg * count * -direction) # по умолчанию вращение против часовой стрелки, поэтому минус
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

            #####################################################################################
            pygame_widgets.update(events)
            pygame.display.update()  # обновление и вывод всех изменений на экран

            if fl_test:
                if count_test_scramble==0:
                    # сохраним скрин решенной головоломки
                    if sub_folder != "":
                        if not os.path.isdir(dir_screenshots+sub_folder):
                            os.mkdir(dir_screenshots+sub_folder)

                    screenshot = os.path.join(dir_screenshots+sub_folder, puzzle_name + ".jpg")
                    pygame.image.save(game_scr, screenshot)

                    # сохраним скрин с открытым фото реальной головоломки
                    if fl_test_photo and photo_screen != "":
                        game_scr.blit(photo_screen, (GAME[0]-PHOTO[0]-BORDER//3, BORDER//3))
                        draw.rect(game_scr, Color("#B88800"), (GAME[0]-PHOTO[0]-2*(BORDER//3), 0, PHOTO[0]+2*(BORDER//3), PHOTO[1]+2*(BORDER//3)), BORDER//3)
                        screenshot2 = os.path.join(dir_screenshots+sub_folder, puzzle_name + " (photo).jpg")
                        pygame.image.save(game_scr, screenshot2)

                if fl_test_scramble>0:
                    # сохраним скрин запутанной головоломки
                    if count_test_scramble>0:
                        screenshot = os.path.join(dir_screenshots+sub_folder, puzzle_name + " (scramble "+str(count_test_scramble)+").jpg")
                        pygame.image.save(game_scr, screenshot)
                    if count_test_scramble<fl_test_scramble:
                        scramble_puzzle(puzzle_rings, puzzle_arch, puzzle_parts, puzzle_points, "scramble")
                        count_test_scramble += 1
                        continue

                break

        # удаляем кнопки
        for btn in button_set:
            btn.hide()

    if fl_test:
        end_time = time.time() - start_time
        minute, secunde = int(end_time // 60), round(end_time % 60, 2)
        print("End testing: " + str(minute) + " minutes, " + str(secunde) + " sec")

main()