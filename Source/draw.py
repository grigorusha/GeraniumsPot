import os,ptext
import pygame
from math import pi, sqrt, cos, sin, tan, acos, asin, atan, atan2, exp, pow, radians, degrees, hypot

import glob as var
# from part import check_ring_intersecting_parts,scramble_puzzle
from syst import send_to_clipboard
from calc import mas_pos,find_element

def draw_all_text(SCREEN, font, font2, puzzle_kol, rings_kol, parts_kol, button_Save, button_Help, toggle_Marker, toggle_Circle, button_y2, button_y3, button_y4):
    # 2
    # Пишем количество уровней
    text_puzzles = font2.render(str(puzzle_kol) + ' puzzles', True, var.WHITE_COLOR)
    text_puzzles_place = text_puzzles.get_rect(topleft=(button_Save.textRect.right + 10, button_y2 + 1))
    SCREEN.blit(text_puzzles, text_puzzles_place)
    # Пишем количество перемещений
    text_moves = font.render('Moves: ' + str(var.moves), True, var.RED_COLOR)
    text_moves_place = text_moves.get_rect(topleft=(button_Help.textRect.right + 18, button_y2 - 3))
    SCREEN.blit(text_moves, text_moves_place)
    # Пишем статус
    # text_solved = font.render('Solved', True, WHITE_COLOR) if solved else font.render('not solved', True, RED_COLOR)
    # text_solved_place = text_solved.get_rect(topleft=(text_moves_place.right + 10, button_y2 - 3))
    # SCREEN.blit(text_solved, text_solved_place)

    # 3
    # Пишем текст переключателей + инфо о головоломке
    marker_text = "On" if toggle_Marker.value else "Off"
    text_marker = font2.render('Marker ' + marker_text, True, var.WHITE_COLOR)
    text_marker_place = text_moves.get_rect(topleft=(40, button_y3-4))
    SCREEN.blit(text_marker, text_marker_place)

    circle_text = "On" if toggle_Circle.value else "Off"
    text_circle = font2.render('Hidden circles ' + circle_text, True, var.WHITE_COLOR)
    text_circle_place = text_moves.get_rect(topleft=(145, button_y3-4))
    SCREEN.blit(text_circle, text_circle_place)

    text_info = font2.render('Total parts: ' + str(parts_kol) + ", circles: "+str(rings_kol), True, var.YELLOW_COLOR)
    text_info_place = text_moves.get_rect(topleft=(text_circle_place.right + 30, button_y3-4))
    SCREEN.blit(text_info, text_info_place)

    # 4
    # Пишем подсказку
    text_info = font2.render('Use: mouse wheel - ring rotate, space button - undo, F11/F12 - prev/next file', True, var.GREEN_COLOR)
    text_info_place = text_moves.get_rect(topleft=(10, button_y4 - 3))
    SCREEN.blit(text_info, text_info_place)

def draw_all_markers(game_scr, puzzle_parts,puzzle_rings):
    for nn, part in enumerate(puzzle_parts):
        marker_sprite = ""
        marker_color = var.BLACK_COLOR if part["color"] != 1 else var.WHITE_COLOR
        center_x, center_y, area = part["centroid"]["center_x"], part["centroid"]["center_y"], part["centroid"]["area"],
        if var.auto_marker:
            marker_size = int(area / 80) # 10
            marker_size = 20 if marker_size>20 else 7 if marker_size<7 else marker_size
            marker_sprite, _ = ptext.draw(str(part["num"]), (0, 0), color=marker_color, fontsize=marker_size, sysfontname='Verdana', align="center")
        elif len(part["marker"]):
            marker_size, marker_sprite = part["marker"]["font_size"], part["marker"]["sprite"]
            center_x += part["marker"]["horizontal_shift"]
            center_y -= part["marker"]["vertical_shift"]
            if marker_sprite == "":
                if marker_size == 0:
                    marker_size = int(area / 200)
                fontname = 'Verdana'
                if "↑↓→←".find(part["marker"]["text"]) >= 0:
                    fontname = 'fonts/arialn.ttf'
                    marker_sprite, _ = ptext.draw(part["marker"]["text"], (0, 0), color=marker_color, fontsize=marker_size, fontname=fontname, align="center")
                else:
                    marker_sprite, _ = ptext.draw(part["marker"]["text"], (0, 0), color=marker_color, fontsize=marker_size, sysfontname=fontname, align="center")
                part["marker"]["sprite"] = marker_sprite
            marker_sprite = pygame.transform.rotate(marker_sprite, part["marker"]["angle"])
        if marker_sprite != "":
            text_marker_place = marker_sprite.get_rect(center=(center_x, center_y))
            game_scr.blit(marker_sprite, text_marker_place)  # Пишем маркер
    if var.auto_marker_ring:
        for nn, ring in enumerate(puzzle_rings):
            if ring["type"] != 0: continue
            center_x, center_y = ring["center_x"], ring["center_y"]
            text_marker, _ = ptext.draw(str(ring["num"]), (0, 0), color=var.RED_COLOR, fontsize=20, sysfontname='Verdana', align="center", owidth=1, ocolor="blue")
            text_marker_place = text_marker.get_rect(center=(center_x, center_y))
            game_scr.blit(text_marker, text_marker_place)  # Пишем маркер

def draw_smooth_gear(SCREEN, color, cir_x, cir_y, radius, teeth):
    def draw_arc(SCREEN, color, center, start, end, radius):
        angle_start = degrees(atan2(start[1] - center[1], start[0] - center[0]))
        angle_end = degrees(atan2(end[1] - center[1], end[0] - center[0]))
        if angle_end < angle_start:
            angle_end += 360
        pygame.draw.arc(SCREEN, color, (center[0] - radius, center[1] - radius, radius * 2, radius * 2), radians(angle_start), radians(angle_end), 2)

    for i in range(teeth):
        angle0 = (i-1) * 2*pi / teeth
        angle1 = i * 2*pi / teeth
        angle2 = (i+1) * 2*pi / teeth
        x0 = int(cir_x + radius * cos(angle0))
        y0 = int(cir_y + radius * sin(angle0))
        x1 = int(cir_x + radius * cos(angle1))
        y1 = int(cir_y + radius * sin(angle1))
        x2 = int(cir_x + radius * cos(angle2))
        y2 = int(cir_y + radius * sin(angle2))
        draw_arc(SCREEN, color, (x1,y1), (x0,y0), (x2,y2), radius)
        # draw.circle(SCREEN, color, (x_i, y_i), 3, 2)

def draw_smoth_polygon(surface, color, polygon, width):
    # рисуем плавную кривую с пиксельным сглаживанием
    # заменяем pygame.draw.polygon - тк там грубая пиксельная ступенька
    for nn, p1 in enumerate(polygon):
        p2 = mas_pos(polygon, nn + 1)

        # delta vector
        d = (p2[0] - p1[0], p2[1] - p1[1])
        # distance between the points
        dis = hypot(*d)
        # scaled perpendicular vector (vector from p1 & p2 to the polygon's points)
        if dis != 0:
            sp = (-d[1] * width / (2 * dis), d[0] * width / (2 * dis))
        else:
            sp = (0,0)

        # points
        p1_1 = (p1[0] - sp[0], p1[1] - sp[1])
        p1_2 = (p1[0] + sp[0], p1[1] + sp[1])
        p2_1 = (p2[0] - sp[0], p2[1] - sp[1])
        p2_2 = (p2[0] + sp[0], p2[1] + sp[1])

        # draw two line
        pygame.draw.aaline(surface, color, p1_1, p1_2, 1)
        pygame.draw.aaline(surface, color, p2_1, p2_2, 1)

def find_photo(puzzle_name):
    photo_screen, photo_path = "", ""
    dir = os.path.join(os.path.abspath(os.curdir),"Photo")
    if os.path.isdir(dir):
        for root, dirs, files in os.walk(dir):
            for fil in files:
                if (fil.lower() == puzzle_name.lower() + ".jpg") or (fil.lower() == puzzle_name.lower() + ".jpeg") or (fil.lower() == puzzle_name.lower() + ".png"):
                    photo_path = os.path.join(root,fil)
                    break
            if photo_path != "": break
        if os.path.isfile(photo_path):
            photo_screen = pygame.image.load(photo_path)
            photo_rect = (photo_screen.get_rect().width, photo_screen.get_rect().height)
            if photo_rect[0] / photo_rect[1] <= var.PHOTO[0] / var.PHOTO[1]:
                scale_ko = var.PHOTO[1] / photo_rect[1]
                new_width = int(scale_ko * photo_rect[0])
                var.PHOTO = (new_width, var.PHOTO[1])
            else:
                scale_ko = var.PHOTO[0] / photo_rect[0]
                new_height = int(scale_ko * photo_rect[1])
                var.PHOTO = (var.PHOTO[0], new_height)

            photo_screen = pygame.transform.scale(photo_screen, var.PHOTO)
    return photo_screen
