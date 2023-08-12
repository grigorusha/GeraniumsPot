from work import *
from syst import *

import pygame
import pygame_widgets

from math import pi, sqrt, cos, sin, tan, acos, asin, atan, exp, pow, radians

from tkinter import Tk
import os
import copy
import keyboard
# import Pillow - for pyinstaller spalsh screen

# TODO 1.  Механизм маркеров : задать, вращение, масштабирование
# TODO 2.  Разделение частей линиями - для задания узоров
# TODO 3.  Бандаж заданных частей
# TODO 4.  Вложенные круги - Крейзи
# TODO 5.  Вспомогательные круги
# TODO 6.  Последовательное исполнение скриптов
# TODO 7.  Hide/Show parts
# TODO 8.  Поиск пересекающихся частей - вывод инфо об ошибках
# TODO 9.  Выводить инфо о головоломке: количество частей, кругов
# TODO 10. Авто-поиск новых кругов
# TODO 11. Вычисление площади частей
# TODO 12. Авто удаление микро частей
# TODO 13. Solved
# TODO 14. Save
# TODO 15. Scramble - отдельная функция. проценты


# TODO *. Скругление уголков
# TODO *. Слайдинги горизонтальные
# TODO *. Шестеренки, Линкед
# TODO *. Рисунки

BACKGROUND_COLOR = "#000000"
GRAY_COLOR, GRAY_COLOR2, BLACK_COLOR = "#808080", "#C0C0C0", "#000000"
WHITE_COLOR, RED_COLOR, GREEN_COLOR, BLUE_COLOR = "#FFFFFF", "#FF0000", "#008000", "#0000FF"
PARTS_COLOR =    [(255, 255, 255, 255), (30, 30, 30, 255), (200, 200, 200, 255),  # 0 белый 1 черный 2 серый
                  (255, 0, 0, 255), (0, 150, 0, 255), (0, 0, 255, 255),           # 3 красный 4 зеленый 5 синий
                  (255, 255, 0, 255), (128, 0, 128, 255), (0, 128, 128, 255),     # 6 желтый (крас+зел) 7 фиолетовый (кра+син) 8 бирюзовый (зел+син)
                  (250, 150, 0, 255), (100, 200, 250, 255), (250, 120, 190, 255),  # 9 оранжевый 10 голубой 11 розовый
                  (120, 60, 30, 255), (200, 130, 250, 255), (70, 250, 70, 255)]   # 12 коричневый 13 сиреневый 14 лайм

WIN_WIDTH, WIN_HEIGHT = 470, 300
PANEL = 33 * 3
BORDER = 20
COUNTUR = 4
GAME = (WIN_WIDTH, WIN_HEIGHT)

dirname = filename = ""

BTN_CLICK = False
BTN_CLICK_STR = ""

def button_Button_click(button_str):
    global BTN_CLICK, BTN_CLICK_STR
    BTN_CLICK_STR = button_str
    BTN_CLICK = True

def button_init(screen, font_button, WIN_HEIGHT):
    from pygame_widgets.button import Button
    GREEN_COLOR, BLUE_COLOR = "#008000", "#0000FF"

    button_y1 = WIN_HEIGHT + 20
    button_Reset = Button(screen, 10, button_y1, 45, 20, text='Reset', fontSize=20, font=font_button, margin=5,
                          radius=3,
                          inactiveColour=GREEN_COLOR, hoverColour=GREEN_COLOR, pressedColour=(0, 200, 20),
                          onClick=lambda: button_Button_click("reset"))
    button_Scramble = Button(screen, button_Reset.textRect.right + 10, button_y1, 70, 20, text='Scramble',
                             fontSize=20, font=font_button, margin=5, radius=3,
                             inactiveColour=GREEN_COLOR, hoverColour=GREEN_COLOR, pressedColour=(0, 200, 20),
                             onClick=lambda: button_Button_click("scramble"))
    button_Undo = Button(screen, button_Scramble.textRect.right + 10, button_y1, 40, 20, text='Undo',
                         fontSize=20, font=font_button, margin=5, radius=3,
                         inactiveColour=GREEN_COLOR, hoverColour=GREEN_COLOR, pressedColour=(0, 200, 20),
                         onClick=lambda: button_Button_click("undo"))

    button_Photo = Button(screen, button_Undo.textRect.right + 20, button_y1, 60, 20, text='Photo ->',
                         fontSize=20, font=font_button, margin=5, radius=3,
                         inactiveColour=BLUE_COLOR, hoverColour=BLUE_COLOR, pressedColour=(0, 200, 20),
                         onClick=lambda: button_Button_click("photo"))
    button_Info = Button(screen, button_Photo.textRect.right + 10, button_y1, 48, 20, text='Info ->',
                         fontSize=20, font=font_button, margin=5, radius=3,
                         inactiveColour=BLUE_COLOR, hoverColour=BLUE_COLOR, pressedColour=(0, 200, 20),
                         onClick=lambda: button_Button_click("info"))
    button_About = Button(screen, button_Info.textRect.right + 10, button_y1, 60, 20, text='About ->',
                          fontSize=20, font=font_button, margin=5, radius=3,
                          inactiveColour=BLUE_COLOR, hoverColour=BLUE_COLOR, pressedColour=(0, 200, 20),
                          onClick=lambda: button_Button_click("about"))

    button_y2 = button_y1 + 25
    button_Open = Button(screen, 10, button_y2, 45, 20, text='Open', fontSize=20, font=font_button, margin=5,
                         radius=3,
                         inactiveColour=GREEN_COLOR, hoverColour=GREEN_COLOR, pressedColour=(0, 200, 20),
                         onClick=lambda: button_Button_click("open"))

    button_Help = Button(screen, button_Scramble.textRect.right + 10, button_y2, 80, 20, text='Solved State',
                         fontSize=20, font=font_button, margin=5, radius=3,
                         inactiveColour=GREEN_COLOR, hoverColour=GREEN_COLOR, pressedColour=(0, 200, 20),
                         onClick=lambda: button_Button_click("help"))

    button_y3 = button_y2 + 30
    return button_y2, button_y3, button_Open, button_Help, [button_Reset, button_Scramble, button_Undo, button_Open, button_Info, button_Help, button_Photo, button_About]

def main():
    global BTN_CLICK, BTN_CLICK_STR, WIN_WIDTH, WIN_HEIGHT, BORDER, GAME, filename

    try:  # pyinstaller spalsh screen
        import pyi_splash
        pyi_splash.close()
    except:
        pass

    file_ext, fl_reset = False, False
    puzzle_name, puzzle_author, puzzle_scale, puzzle_speed, puzzle_kol, auto_marker, puzzle_link = "", "", 1, 2, 1, 1, []
    puzzle_rings, puzzle_arch, puzzle_parts, remove_parts, copy_parts = [], [], [], [], []
    vek_mul = -1

    # основная инициализация
    pygame.init()  # Инициация PyGame
    font = pygame.font.SysFont('Verdana', 18)
    font2 = pygame.font.SysFont('Verdana', 12)
    font_marker = pygame.font.SysFont('Verdana', 10)
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
        if not file_ext:
            fil = init_puzzle(BORDER, PARTS_COLOR)
            puzzle_name, puzzle_author, puzzle_link, puzzle_scale, puzzle_speed, puzzle_rings, puzzle_arch, puzzle_parts, puzzle_kol, vek_mul, dirname, filename, WIN_WIDTH, WIN_HEIGHT, auto_marker, remove_parts, copy_parts = fil

        help_mul = 2
        DISPLAY = (WIN_WIDTH, WIN_HEIGHT + PANEL)  # Группируем ширину и высоту в одну переменную
        GAME = (WIN_WIDTH, WIN_HEIGHT)
        HELP = (WIN_WIDTH // help_mul, WIN_HEIGHT // help_mul)
        PHOTO = (WIN_WIDTH // help_mul, WIN_HEIGHT // help_mul)

        # инициализация окна
        if not fl_reset:
            pos_x = int(screen_width/2 - WIN_WIDTH/2)
            pos_y = int(screen_height - (WIN_HEIGHT + PANEL))
            os.environ['SDL_VIDEO_WINDOW_POS'] = '%i,%i' % (pos_x, pos_y)
            os.environ['SDL_VIDEO_CENTERED'] = '0'

            screen = pygame.display.set_mode(DISPLAY)  # Создаем окошко
            game_scr = Surface(GAME) # pygame.SRCALPHA

        win_caption = puzzle_name if puzzle_name != "" else "Geraniums Pot Simulator"
        if puzzle_author != "": win_caption += " (" + puzzle_author.strip() + ")"
        pygame.display.set_caption(win_caption)  # Пишем в шапку

        keyboard.press_and_release("alt") # странный трюк, чтобы вернуть фокус после сплаш скрина
        window_front(win_caption)

        scramble_move, moves, moves_stack = 0, 0, []
        solved = True

        mouse_xx, mouse_yy = 0, 0
        help,help_gen,photo,photo_gen = 0, True, 0, True
        animation_on, events = False, ""

        # инициализация кнопок
        button_y2, button_y3, button_Open, button_Help, button_set = button_init(screen, font_button, WIN_HEIGHT)

        ################################################################################
        ################################################################################
        # Основной цикл программы
        while True:
            timer.tick(150)

            if not animation_on:
                fl_break = undo = False
                mouse_x, mouse_y, mouse_left, mouse_right, ring_select = 0, 0, False, False, 0
                ring_num = direction = 0

                ################################################################################
                # обработка событий
                if not help_gen: # при первом цикле, сначала надо полностью нарисовать, потом считывать кнопки
                    events = pygame.event.get()
                    fil, fil2 = events_check_read_puzzle(events, fl_break, fl_reset, BTN_CLICK, BTN_CLICK_STR, BORDER, WIN_WIDTH, WIN_HEIGHT, win_caption, file_ext, puzzle_link, puzzle_rings, puzzle_parts, help, photo, scramble_move, undo, moves, moves_stack, ring_num, direction, mouse_xx, mouse_yy, dirname, filename, PARTS_COLOR, auto_marker)

                    if typeof(fil2) == "str":
                        return fil
                    if typeof(fil) != "str":
                        puzzle_name, puzzle_author, puzzle_link, puzzle_scale, puzzle_speed, puzzle_rings, puzzle_arch, puzzle_parts, puzzle_kol, vek_mul, dirname, filename, WIN_WIDTH, WIN_HEIGHT, auto_marker, remove_parts, copy_parts = fil
                    fl_break, fl_reset, file_ext, BTN_CLICK, BTN_CLICK_STR, scramble_move, undo, moves, moves_stack, ring_num, direction, mouse_xx, mouse_yy, mouse_x, mouse_y, mouse_left, mouse_right, help, photo, mouse_xx, mouse_yy = fil2
                    if fl_break: break

                ################################################################################
                # обработка перемещения и нажатия в игровом поле
                # mouse_xx, mouse_yy - координаты мышки при перемещении. mouse_x, mouse_y - координаты точки клика
                # ring_select - координаты кольца над которым двигается курсор. ring_num - кольцо внутри которого был клик
                if (mouse_xx + mouse_yy > 0) and mouse_xx < WIN_WIDTH and mouse_yy < WIN_HEIGHT and not undo:
                    ring_num, ring_select, direction = mouse_move_click(mouse_xx, mouse_yy, mouse_x, mouse_y, mouse_left, mouse_right, puzzle_rings, ring_num, ring_select, direction)

                ################################################################################
                # логика игры - выполнение перемещений
                while ring_num > 0 or scramble_move > 0:
                    #############################################################################
                    # обработка рандома для Скрамбла
                    if scramble_move > 0:
                        mouse.set_cursor(SYSTEM_CURSOR_WAITARROW)
                        display.set_caption("Please wait! Scrambling ...")

                        direction = random.choice([-1, 1])
                        ring_num = random.randint(1, len(puzzle_rings))
                        ring_select = 0

                    # поворот круга
                    ring = find_element(ring_num, puzzle_rings)

                    # 1. найдем все части внутри круга
                    part_mas, part_mas_other = find_parts_in_circle(ring, puzzle_parts)

                    if scramble_move > 0 and len(part_mas) == 0: continue

                    # 2. повернем все части внутри круга
                    if len(part_mas)>0:
                        angle_rotate = find_angle_rotate(ring,direction)

                        # 2.1 анимация. сформируем круглый спрайт для дальнейшего вращения
                        if scramble_move == 0:
                            animation_on = True

                            game_sprite = Surface((ring[3] * 2, ring[3] * 2), pygame.SRCALPHA)

                            step, count = int(ring[3] * radians(angle_rotate) / puzzle_speed), 0
                            angle, angle_deg = radians(angle_rotate) / step, angle_rotate / step
                            shift_x, shift_y = ring[1] - ring[3], ring[2] - ring[3]

                            part_mas_rot = copy.deepcopy(part_mas) # нужно для пересчета координат. чтобы круг вписался в спрайт

                            pygame.draw.circle(game_sprite,GRAY_COLOR, (ring[3],ring[3]), ring[3])
                            for nn, part in enumerate(part_mas_rot):
                                for pos in part[3]:
                                    pos[0], pos[1] = pos[0] - shift_x, pos[1] - shift_y
                                pygame.draw.polygon(game_sprite, PARTS_COLOR[part[1]], part[3], 0)
                                pygame.draw.polygon(game_sprite, BLACK_COLOR, part[3], COUNTUR)

                        # 2.2 поворот в массиве
                        rotate_part(ring, part_mas, puzzle_arch, radians(angle_rotate), direction)
                        calc_parts_countur(part_mas, puzzle_arch)

                        if not undo:
                            moves += 1
                            moves_stack.append([ring_num, direction])

                    # 3. скрамбл
                    if scramble_move > 0:
                        scramble_move -= 1
                        if scramble_move > 0: continue
                        moves, moves_stack = 0, []
                        mouse.set_cursor(SYSTEM_CURSOR_ARROW)
                        display.set_caption(win_caption)

                    break

            #####################################################################################
            # отрисовка игрового поля
            if not animation_on:
                screen.fill(BACKGROUND_COLOR)  # Заливаем поверхность сплошным цветом
                pf = Surface((WIN_WIDTH, 10))  # Рисуем разделительную черту
                pf.fill(Color("#B88800"))
                screen.blit(pf, (0, WIN_HEIGHT))

                # отрисовка текстов
                draw_all_text(screen, font, font2, puzzle_kol, moves, solved, button_Open, button_Help, button_y2, button_y3)

                ############################################
                game_scr.fill(Color(GRAY_COLOR))

                # отрисовка контуров
                for nn,ring in enumerate(puzzle_rings):
                    if ring[0]!=ring_select:
                        pygame.draw.circle(game_scr,GRAY_COLOR2, (ring[1],ring[2]),ring[3]+5,3)

                # отрисовка частей
                for nn,part in enumerate(puzzle_parts):
                    pygame.draw.polygon(game_scr,PARTS_COLOR[part[1]],part[3],0)
                    pygame.draw.polygon(game_scr,BLACK_COLOR,part[3],COUNTUR)

                # отрисовка выделения
                if ring_select>0:
                    ring = find_element(ring_select, puzzle_rings)
                    pygame.draw.circle(game_scr,WHITE_COLOR, (ring[1],ring[2]),ring[3]+5,3)

                # рисуем авто-маркеры
                if auto_marker:
                    for nn, part in enumerate(puzzle_parts):
                        center_x, center_y = calc_centroid(part[4])
                        text_marker = font_marker.render(str(part[0]), True, BLACK_COLOR if part[1]!=1 else WHITE_COLOR)
                        text_marker_place = text_marker.get_rect(center=(center_x, center_y))
                        game_scr.blit(text_marker, text_marker_place)  # Пишем маркет

                screen.blit(game_scr, (0, 0))

            else:
                # рисуем поворотную часть (плавный поворот только круглого спрайта)
                ring = find_element(ring_num, puzzle_rings)
                game_sprite_rot = pygame.transform.rotate(game_sprite, angle_deg * count * -direction) # по умолчанию вращение против часовой стрелки, поэтому минус
                game_sprite_new = game_sprite_rot.get_rect(center=(ring[1], ring[2]))
                screen.blit(game_sprite_rot, game_sprite_new)

                step,count = step-1, count+1
                if step==0: animation_on = False

            # окно помощи
            if help_gen:
                help_gen = False
                help_screen = pygame.transform.scale(game_scr, HELP)
            if help==1:
                screen.blit(help_screen, (GAME[0]-HELP[0]-BORDER//3, BORDER//3))
                draw.rect(screen, Color("#B88800"), (GAME[0]-HELP[0]-2*(BORDER//3), 0, HELP[0]+2*(BORDER//3), HELP[1]+2*(BORDER//3)), BORDER//3)

            # окно с фото головоломки
            if photo_gen:
                photo_gen = False
                photo_path1 = os.path.abspath(os.curdir) + "\\Photo\\"+puzzle_name+".jpg"
                photo_path2 = os.path.abspath(os.curdir) + "\\Photo\\"+puzzle_name+".png"
                if os.path.isfile(photo_path1):
                    photo_screen = pygame.image.load(photo_path1)
                    photo_screen = pygame.transform.scale(photo_screen, PHOTO)
                elif os.path.isfile(photo_path2):
                    photo_screen = pygame.image.load(photo_path2)
                    photo_screen = pygame.transform.scale(photo_screen, PHOTO)
                else:
                    photo,photo_screen = 0,""
            if photo==1 and photo_screen!="":
                screen.blit(photo_screen, (GAME[0]-PHOTO[0]-BORDER//3, BORDER//3))
                draw.rect(screen, Color("#B88800"), (GAME[0]-PHOTO[0]-2*(BORDER//3), 0, PHOTO[0]+2*(BORDER//3), PHOTO[1]+2*(BORDER//3)), BORDER//3)

            #####################################################################################
            pygame_widgets.update(events)
            pygame.display.update()  # обновление и вывод всех изменений на экран

        # удаляем кнопки
        for btn in button_set:
            btn.hide()

main()