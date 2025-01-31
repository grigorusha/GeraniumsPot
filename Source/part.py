import copy,random,time
import pygame
from math import pi, sqrt, cos, sin, tan, acos, asin, atan, exp, pow, radians, degrees, hypot

import glob as var
from draw import *
from calc import *
from syst import *

# puzzle_rings, puzzle_arch, puzzle_parts, puzzle_points, puzzle_lines, moves_stack - формат массивов. внутри словари именованные:

# puzzle_rings - [ring_num, center_x, center_y, radius, angle_deg, _pos , type, [inner], [linked], [mas_spline]]
#                        0         1         2       3          4  5         6       7         8             9
#              - [ring_num, center_x, center_y, radius, (angle_deg1,angle_deg2,...), jumble_angle_pos, type, [inner], [linked], [mas_spline]]
#                   - angle_deg1+angle_deg2+..=360 deg, jumble_angle_pos = 0,1,..
#       (круги создаются в процедуре: work.read_puzzle_script_and_init_puzzle: command == "Ring" и "CopyRing")
#              для головоломок с некратными углами, в параметре Angle массив углов, а также позиция текущего угла поворота всего круга.
#              type - 0 это стандартные кольца, 1 это вспомогательные кольца для нарезки, собственных частей не имеют, как контуры не отображаем
#                   - 2 зафиксированые вложенные кольца, части внутри них не поворачиваются
#              inner - [ring_num, inner_type] - массив вложенных крэйзи-колец, для связанного вращения или для разделения вращения колец
#                   inner_type - 0 не связанные кольца, 1 связаны
#              linked - [gears, [ [ring_num, direction, gear_ratio, angle_deg, sprite],... ]] - массив связанных колец, для связанного вращения или для разделения вращения колец
#                   gears - количество зубьев на шестеренке кольца, для вычисления передаточного числа
#                   link_mas - массив связанных с основным колец
#                       "ring_num", "direction", "gear_ratio", "angle", "sprite"
#                       gear_ratio - передаточное число
#              mas_spline - [ [x0,y0],[x1,y1],..,[xm,ym] ] - плавный сплайн для отрисовки контура круга
# puzzle_rings = dict(num, center_x, center_y, radius, angle, angle_pos , type, [inner], [linked], [spline])
#               "num", "center_x", "center_y", "radius", "angle", "angle_pos" , "type", "inner", "linked", "spline"

# puzzle_arch  - [arch_num, center_x, center_y, radius]
#       (арки создаются в процедурах: make_def_circles, rotate_parts,    work.read_puzzle_script_and_init_puzzle)
#              вторичные арки которые формируют части
# arch_dict = dict(num, center_x, center_y, radius) - "num", "center_x", "center_y", "radius"

# puzzle_parts - [part_num, color_index, visible, latch, [marker], [centroid], [mas_arch_lines], [mas_polygon], [mas_spline], fl_error]
#                        0            1        2                 3           4                 5              6             7   8
#       (части создаются в процедурах: make_def_circles, cut_parts_in_ring, copy_def_parts,mirror_def_parts,    work.read_puzzle_script_and_init_puzzle)
#       latch : 0 нет, -1 против часовой стрелки, 1 по часовой стрелке
#       marker - [text, angle, font_size, horizontal_shift, vertical_shift, sprite]
#       centroid - [center_x, center_y, area, max_radius]
#       mas_arch_lines - [ [part_arch1],[part_arch2],.. ]
# *         part_arch - [arch_num, type, direction, start_x, start_y, fl]
#                               0     1          2        3        4   5
# "arch_num", "type", "direction", "start_x", "start_y", "fl"
#               type - 0 окружность, 1 дуга, 2 линия
#               fl - начало попадает внутрь круга: -1 нет, 0 на границе, 1 внутри.  10 вся дуга совпадает с окружностью
#       mas_polygon - [ [x0,y0],..,[xn,yn] ] - сокращенный полигон (несколько точек из дуги) для быстрых проверок пересечений
#       mas_spline - [ [x0,y0],[x1,y1],..,[xm,ym] ] - плавный сплайн для отрисовки контура фигуры
#       fl_error - 0 нет ошибки, часть внутри другой части, часть пересекается с другой частью
# puzzle_parts - dict(num, color, visible, latch, [marker], [centroid], [arch_lines], [polygon], [spline], fl_error)
#                   "num", "color", "visible", "latch", "marker", "centroid", "arch_lines", "polygon", "spline", "fl_error"

# moves_stack - [ring_num, direction]
#       (движения сохраняются в процедуре: main.main)

## puzzle_lines - [line_num, x0,y0, x1,y1]
##              вторичные линии которые формируют части
## puzzle_areas - [area_num, [mas_lines]]

def rotate_parts(ring, part_mas, puzzle_arch, angle, direction):
    # поворот всех частей из массива относительно центра круга
    for part in part_mas:
        if len(part["marker"]): # маркеры
            part["marker"]["angle"] += degrees(angle)*direction
            part["marker"]["horizontal_shift"],part["marker"]["vertical_shift"] = rotate_point(part["marker"]["horizontal_shift"],part["marker"]["vertical_shift"], 0,0, angle*direction)

        if len(part["centroid"]): # центроид
            part["centroid"]["center_x"], part["centroid"]["center_y"] = rotate_point(part["centroid"]["center_x"],part["centroid"]["center_y"], ring["center_x"],ring["center_y"], angle*direction)

        for part_arch in part["arch_lines"]: # части. только координаты вершин (без полигона и сплайна)
            part_arch[3], part_arch[4] = rotate_point(part_arch[3],part_arch[4], ring["center_x"],ring["center_y"], angle*direction)

            arch_cur = find_element(part_arch[0], puzzle_arch)
            arch_x, arch_y = rotate_point(arch_cur["center_x"],arch_cur["center_y"], ring["center_x"],ring["center_y"], angle*direction)

            fl_arch = False
            for arch in puzzle_arch:
                if compare_xy(arch["center_x"], arch_x, 2) and compare_xy(arch["center_y"], arch_y, 2) and (arch_cur["radius"]==arch["radius"]):
                    part_arch[0] = arch["num"]
                    fl_arch = True
                    break

            if not fl_arch:
                arch_num = max(puzzle_arch, key=lambda i: i["num"])["num"] + 1
                arch_dict = dict(num=arch_num, center_x=arch_x, center_y=arch_y, radius=arch_cur["radius"])
                puzzle_arch.append(arch_dict)
                # puzzle_arch.append([arch_num, arch_x, arch_y, arch_cur[3]])
                part_arch[0] = arch_num

def mirror_parts(mirror_line, part_mas, puzzle_arch):
    # поворот всех частей из массива относительно центра круга
    for part in part_mas:
        if len(part["marker"]): # маркеры
            part["marker"]["angle"] += 360-part["marker"]["angle"]
            part["marker"]["horizontal_shift"],part["marker"]["vertical_shift"] = mirror_point(part["marker"]["horizontal_shift"],part["marker"]["vertical_shift"], mirror_line)

        if len(part["centroid"]): # центроид
            part["centroid"]["center_x"], part["centroid"]["center_y"] = mirror_point(part["centroid"]["center_x"],part["centroid"]["center_y"], mirror_line)

        for part_arch in part["arch_lines"]: # части. только координаты вершин (без полигона и сплайна)
            part_arch[2] = -part_arch[2]
            part_arch[3], part_arch[4] = mirror_point(part_arch[3],part_arch[4], mirror_line)

            arch_cur = find_element(part_arch[0], puzzle_arch)
            arch_x, arch_y = mirror_point(arch_cur["center_x"],arch_cur["center_y"], mirror_line)

            fl_arch = False
            for arch in puzzle_arch:
                if compare_xy(arch["center_x"], arch_x, 2) and compare_xy(arch["center_y"], arch_y, 2) and (arch_cur["radius"]==arch["radius"]):
                    part_arch[0] = arch["num"]
                    fl_arch = True
                    break

            if not fl_arch:
                arch_num = max(puzzle_arch, key=lambda i: i["num"])["num"] + 1
                arch_dict = dict(num=arch_num, center_x=arch_x, center_y=arch_y, radius=arch_cur["radius"])
                puzzle_arch.append(arch_dict)
                # puzzle_arch.append([arch_num, arch_x, arch_y, arch_cur[3]])
                part_arch[0] = arch_num

def len_puzzle_rings(puzzle_rings):
    len_puzzle_rings = 0
    for ring in puzzle_rings:
        if ring["type"] == 0: len_puzzle_rings += 1
    return len_puzzle_rings

def find_part_arch_next(part_arch_mas,nn):
    # возвращает следующую дугу у части по индексу
    if (len(part_arch_mas) == 1) or (nn == len(part_arch_mas) - 1):
        part_arch_next = part_arch_mas[0]
    else:
        part_arch_next = part_arch_mas[nn + 1]
    return part_arch_next

def calc_parts_countur(puzzle_parts,puzzle_arch,short_only=False):
    # расчет всех контуров-сплайнов для всех частей
    for part in puzzle_parts:
        mas_full_xy, mas_short_xy = [], []

        part_arch_mas = part["arch_lines"]
        for nn, part_arch in enumerate(part_arch_mas):
            arch = find_element(part_arch[0], puzzle_arch)
            arch_x, arch_y, arch_r = arch["center_x"], arch["center_y"], arch["radius"]

            direction = part_arch[2]

            part_arch_next = find_part_arch_next(part_arch_mas, nn)
            arch_mas = [ [part_arch[3], part_arch[4]] , [part_arch_next[3], part_arch_next[4]] ]

            if not short_only:
                mas_xy,fl_error = calc_arch_spline(arch_mas, arch_x, arch_y, arch_r, direction)
                if fl_error:
                    print("Error: "+str(part["num"])+", "+str(part_arch[0]))
                mas_full_xy += mas_xy
                mas_full_xy.pop()

            if len(part["arch_lines"])==1: # это окружность?
                mas_xy,fl_error = calc_arch_spline(arch_mas, arch_x, arch_y, arch_r, direction, 6)
            else:
                mas_xy,fl_error = calc_arch_spline(arch_mas, arch_x, arch_y, arch_r, direction, 4)
            mas_short_xy += mas_xy
            mas_short_xy.pop()

        part["polygon"], part["spline"] = mas_short_xy, mas_full_xy

def find_parts_intersecting_line(mas_lines, puzzle_parts):
    # найдем все части пересекающиеся с цепочкой из линий
    part_mas, part_mas_other = [], []
    for part in puzzle_parts:
        fl_part = 0  # 0 - часть не касается линий, >0 - количество пересечений
        for line in mas_lines:
            for nn,part_point in enumerate(part["polygon"]):
                part_point_next = mas_pos(part["polygon"],nn+1)
                pos = check_line_intersect(line[1],line[2], line[1],line[2], part_point[0],part_point[1], part_point_next[0],part_point_next[1])
                if pos:
                    fl_part += 1
        if fl_part>1:
            part_mas.append(part)
        else:
            part_mas_other.append(part)
    return part_mas, part_mas_other

def check_ring_intersecting_parts(ring, puzzle_parts):
    # ускоренная find_parts_in_circle - только на проверку пересечения
    # возвращаем False если есть пересечение частей
    inner_parts = 0
    for part in puzzle_parts:
        fl_part = -1  # 0 - часть за пределами круга, 1 - часть внутри круга, 2 часть пересекает круг, 3 часть совпадает с кругом (все точки касательные)

        # быстрая проверка по центроиду
        if len(part["centroid"]):
            center_x, center_y, max_radius = part["centroid"]["center_x"], part["centroid"]["center_y"], part["centroid"]["max_radius"],
            centroid_length = calc_length(center_x, center_y, ring["center_x"], ring["center_y"])
            if centroid_length>(max_radius+ring["radius"]):   # часть за пределами круга
                continue
            elif compare_xy(ring["radius"],(max_radius + centroid_length),6):  # часть совпадает с кругом
                inner_parts += 1
                continue
            elif ring["radius"]>(max_radius+centroid_length): # часть внутри круга
                inner_parts += 1
                continue

        if fl_part == -1:
            for part_point in part["polygon"]: # проверяем точки полигона
                pos = check_circle(ring["center_x"], ring["center_y"], part_point[0], part_point[1], ring["radius"])
                if pos["on_ring"]:
                    if fl_part == -1:
                        fl_part = 3
                elif pos["in_circle"]:
                    if fl_part == -1 or fl_part == 1 or fl_part == 3:
                        fl_part = 1
                    elif fl_part == 0:
                        fl_part = 2
                        return False
                else:
                    if fl_part == -1 or fl_part == 0 or fl_part == 3:
                        fl_part = 0
                    elif fl_part == 1:
                        fl_part = 2
                        return False
            if fl_part == 1 or fl_part == 3:
                inner_parts += 1
    if inner_parts==0: return False
    return True

def find_parts_in_circle(ring, puzzle_parts, puzzle_rings, mode=0):
    # найдем все части соотносящиеся с кругом, в зависимости от режима выборки
    # mode : 0 - все части в круге, нет пересечений с кругом, иначе выходим, 1 - только части внутри круга,
    # 2 - части совпадающие с кругом (все внутри и те что пересекают), 3 - только части пересекающие круг
    # во всех случаях исключаем части несвязанных вложенных кругов

    part_mas, part_mas_other = [], []
    for part in puzzle_parts:
        fl_part = -1  # 0 - часть за пределами круга, 1 - часть внутри круга, 2 часть пересекает круг, 3 часть совпадает с кругом (все точки касательные)

        # быстрая проверка по центроиду
        if len(part["centroid"]):
            center_x, center_y, max_radius = part["centroid"]["center_x"], part["centroid"]["center_y"], part["centroid"]["max_radius"],
            centroid_length = calc_length(center_x, center_y, ring["center_x"], ring["center_y"])
            if centroid_length>(max_radius+ring["radius"]):   # часть за пределами круга
                fl_part = 0
            elif ring["radius"]>(max_radius+centroid_length): # часть внутри круга
                fl_part = 1

        if fl_part == -1:
            for part_point in part["polygon"]: # проверяем точки полигона
                pos = check_circle(ring["center_x"], ring["center_y"], part_point[0], part_point[1], ring["radius"])
                if pos["on_ring"]:
                    if fl_part == -1:
                        fl_part = 3
                elif pos["in_circle"]:
                    if fl_part == -1 or fl_part == 1 or fl_part == 3:
                        fl_part = 1
                    elif fl_part == 0:
                        fl_part = 2
                        break
                else:
                    if fl_part == -1 or fl_part == 0 or fl_part == 3:
                        fl_part = 0
                    elif fl_part == 1:
                        fl_part = 2
                        break
        if (fl_part == 1 or fl_part == 3) and (mode != 3):
            part_mas.append(part)
        elif fl_part == 2 and (mode == 2 or mode == 3):
            part_mas.append(part)
        elif fl_part == 2 and mode == 0:
            part_mas = []
            break

    if len(puzzle_rings)>0 and len(ring["inner"])>0:
        for inner in ring["inner"]:
            if inner["type"]==1: continue
            ring2 = find_element(inner["num"],puzzle_rings)
            part_mas2, _ = find_parts_in_circle(ring2, puzzle_parts, puzzle_rings, 1)
            for part2 in part_mas2:
                for nn,part in enumerate(part_mas):
                    if part2 == part:
                        part_mas.pop(nn)
                        break

    for part in puzzle_parts:
        if part not in part_mas:
            part_mas_other.append(part)

    return part_mas, part_mas_other

def cut_parts_intersecting_line(mas_lines, puzzle_parts, puzzle_arch):
    # нарезка цепочкой из линий всех пересекающих ее частей
    part_mas, _ = find_parts_intersecting_line(mas_lines, puzzle_parts)

    for part in part_mas:
        if part["visible"]==0: continue

    return

def cut_parts_in_ring(ring, puzzle_arch, puzzle_parts):
    # нарезка контуром окружности всех пересекающих ее частей
    part_mas, _ = find_parts_in_circle(ring, puzzle_parts, [],3)
    arch_ring_num = find_arch(puzzle_arch, ring)

    part_new_mas = []
    part_num_new = max(puzzle_parts, key=lambda i: i["num"])["num"] + 1

    for part in part_mas:
        if part["visible"]==0: continue
        part_arch_mas = part["arch_lines"]

        # найдем точки пересечения - секущая Круг
        cut_point, nn = [], -1
        while nn<len(part_arch_mas)-1:
            nn += 1
            part_arch = part_arch_mas[nn]
            part_arch_next = find_part_arch_next(part_arch_mas, nn)

            if part_arch[1]<=1: # дуга
                arch = find_element(part_arch[0], puzzle_arch)
                intersect = two_circles_intersect(ring["center_x"], ring["center_y"], ring["radius"], arch["center_x"], arch["center_y"], arch["radius"])
            else: # линия
                intersect = circle_line_intersect(ring["center_x"], ring["center_y"], ring["radius"], part_arch[3],part_arch[4], part_arch_next[3],part_arch_next[4])
            if len(intersect) == 0: continue

            # проверим есть ли эти точки в массиве
            for point in cut_point:
                if len(intersect) == 0: break
                if len(intersect) == 2:
                    if (compare_xy(point[1],intersect[1][0],8) and compare_xy(point[2],intersect[1][1],8)):
                        intersect.pop(1)
                if (compare_xy(point[1],intersect[0][0],8) and compare_xy(point[2],intersect[0][1],8)):
                    intersect.pop(0)
            if len(intersect) == 0: continue

            # касание цельного круга...
            if len(part_arch_mas) == 1 and len(intersect) == 1: continue

            # установим флаги если точки пересечения лежат на дуге
            if len(part_arch_mas) == 1:  # цельная окружность
                fl1, fl2 = True, True
            else:
                if part_arch[1] <= 1:  # дуга
                    fl1, fl2 = check_point_in_arch(part_arch[3], part_arch[4], part_arch_next[3], part_arch_next[4], intersect[0][0], intersect[0][1], arch["center_x"], arch["center_y"], part_arch[2]), False
                    if len(intersect) == 2:
                        fl2 = check_point_in_arch(part_arch[3], part_arch[4], part_arch_next[3], part_arch_next[4], intersect[1][0], intersect[1][1], arch["center_x"], arch["center_y"], part_arch[2])
                else: # линия
                    fl1, fl2 = check_line(part_arch[3],part_arch[4], part_arch_next[3],part_arch_next[4], intersect[0][0],intersect[0][1]), False
                    if len(intersect) == 2:
                        fl2 = check_line(part_arch[3],part_arch[4], part_arch_next[3],part_arch_next[4], intersect[1][0],intersect[1][1])

            # дабавляем точки пересечений в массив, исключая те что в конце дуги (они попадут в начало следующей)
            if fl1:
                fl_corner = (compare_xy(part_arch[3],intersect[0][0],8) and compare_xy(part_arch[4],intersect[0][1],8))
                fl_corner_next = (compare_xy(part_arch_next[3],intersect[0][0],8) and compare_xy(part_arch_next[4],intersect[0][1],8))

                angle = calc_angle(ring["center_x"], ring["center_y"], intersect[0][0], intersect[0][1], ring["radius"])
                cut_point.append([nn, intersect[0][0], intersect[0][1], angle[0], fl_corner or fl_corner_next, (fl1 and fl2)])
                if fl_corner or fl_corner_next: fl1 = False
            if fl2:
                fl_corner = (compare_xy(part_arch[3],intersect[1][0],8) and compare_xy(part_arch[4],intersect[1][1],8))
                fl_corner_next = (compare_xy(part_arch_next[3],intersect[1][0],8) and compare_xy(part_arch_next[4],intersect[1][1],8))

                angle = calc_angle(ring["center_x"], ring["center_y"], intersect[1][0], intersect[1][1], ring["radius"])
                cut_point.append([nn, intersect[1][0], intersect[1][1], angle[0], fl_corner or fl_corner_next, (fl1 and fl2)])
                if fl_corner or fl_corner_next: fl2 = False

            # внесем новые точки в массив дуг
            if len(part_arch_mas) == 1 and fl1 and fl2:  # цельная окружность
                part_arch_mas = []
                x_ca, y_ca = calc_center_arch(intersect[0][0],intersect[0][1], intersect[1][0],intersect[1][1], arch["center_x"],arch["center_y"],arch["radius"], part_arch[2])
                pos = check_circle(ring["center_x"], ring["center_y"], x_ca, y_ca, ring["radius"])
                if pos["in_circle"]:
                    part_arch_mas.append([part_arch[0], 1, part_arch[2], intersect[0][0], intersect[0][1], 0,0])
                    part_arch_mas.append([part_arch[0], 1, part_arch[2], intersect[1][0], intersect[1][1], 0,0])
                else:
                    part_arch_mas.append([part_arch[0], 1, part_arch[2], intersect[1][0], intersect[1][1], 0,0])
                    part_arch_mas.append([part_arch[0], 1, part_arch[2], intersect[0][0], intersect[0][1], 0,0])
                nn += 1
            elif fl1 and not fl2:
                part_arch_mas.insert(nn+1,[part_arch[0], 1, part_arch[2], intersect[0][0], intersect[0][1], 0,0])
                nn += 1
            elif fl2 and not fl1:
                part_arch_mas.insert(nn+1, [part_arch[0], 1, part_arch[2], intersect[1][0], intersect[1][1], 0, 0])
                nn += 1
            elif fl1 and fl2:
                if part_arch[1] <= 1:  # дуга
                    x_ca, y_ca = calc_center_arch(intersect[0][0],intersect[0][1], intersect[1][0],intersect[1][1], arch["center_x"],arch["center_y"],arch["radius"], part_arch[2])
                    pos = check_circle(ring["center_x"], ring["center_y"], part_arch[3], part_arch[4], ring["radius"])
                    if pos["in_circle"]:
                        intersect[0], intersect[1] = intersect[1], intersect[0]
                    pos = check_circle(ring["center_x"], ring["center_y"], x_ca, y_ca, ring["radius"])
                    if pos["in_circle"]:
                        part_arch_mas.insert(nn+1, [part_arch[0], 1, part_arch[2], intersect[0][0], intersect[0][1], 0,0])
                        part_arch_mas.insert(nn+2, [part_arch[0], 1, part_arch[2], intersect[1][0], intersect[1][1], 0,0])
                    else:
                        part_arch_mas.insert(nn+1, [part_arch[0], 1, part_arch[2], intersect[1][0], intersect[1][1], 0,0])
                        part_arch_mas.insert(nn+2, [part_arch[0], 1, part_arch[2], intersect[0][0], intersect[0][1], 0,0])
                    nn += 2
                else: # линия
                    part_arch_mas.insert(nn+1, [part_arch[0], 1, part_arch[2], intersect[0][0], intersect[0][1], 0,0])
                    part_arch_mas.insert(nn+2, [part_arch[0], 1, part_arch[2], intersect[1][0], intersect[1][1], 0,0])

        # расставим флаги попадания углов и дуг внутрь круга
        if len(part_arch_mas) > 1:  # не цельная окружность
            for nn, part_arch in enumerate(part_arch_mas):
                pos = check_circle(ring["center_x"], ring["center_y"], part_arch[3], part_arch[4], ring["radius"], 5)
                part_arch[5] = part_arch[6] = 0 if pos["on_ring"] else (1 if pos["in_circle"] else -1)
                if part_arch[5] == 0:  # проверим, не совпадает ли дуга с окружностью
                    part_arch_next = find_part_arch_next(part_arch_mas, nn)
                    arch = find_element(part_arch[0], puzzle_arch)
                    x_ca, y_ca = calc_center_arch(part_arch[3], part_arch[4], part_arch_next[3], part_arch_next[4], arch["center_x"], arch["center_y"], arch["radius"], part_arch[2])
                    pos = check_circle(ring["center_x"], ring["center_y"], x_ca, y_ca, ring["radius"],5)
                    if pos["on_ring"]:  # середина дуги лежит на окружности
                        part_arch[6] = 0
                    elif pos["in_circle"] and not pos["on_ring"]:  # середина дуги лежит внутри окружности
                        part_arch[6] = 1
                    elif not pos["in_circle"]:  # середина дуги лежит вне окружности
                        part_arch[6] = -1

        cut_point.sort(key=lambda point: -point[3])

        # cut_point [part_arch_num, x,y, angle, fl_corner, fl_arc]
        #     fl_corner - точка на угле, fl_arc - на дуге две точки

        if len(cut_point) > 1:
            nn, part_new, fl_part, pos, fl_inout = -1, dict(), False, -1, 0
            while True:
                if len(part_new) > 0:
                    if len(part_new["arch_lines"])>(len(part_arch_mas)+len(cut_point)): break
                nn += 1
                if nn==len(part_arch_mas):
                    nn, fl = 0, False
                    if not fl_part:
                        for part_arch_ in part_arch_mas:
                            if abs(part_arch_[6])==1: # есть ли необработаные дуги
                                fl = True
                                break
                        if not fl:
                            if len(part_new) > 0: part_new_mas.append(part_new)
                            break

                part_arch = part_arch_mas[nn]

                if fl_part and pos==nn:
                    fl_part = False # новая часть закончена
                if not fl_part and abs(part_arch[6])>1: continue # дуга уже обработана / and part_arch[5]!=0

                if not fl_part and part_arch[5]==0 and part_arch[6]==0: continue # дуга совпадает с кругом

                part_arch_next = find_part_arch_next(part_arch_mas, nn)

                # создадим новую часть
                if not fl_part:
                    if len(part_new)>0: part_new_mas.append(part_new)
                    fl_part, pos, fl_inout = True, nn, part_arch[6]

                    if len(part_new)==0:
                        num = part["num"]
                    else:
                        num = part_num_new
                        part_num_new += 1
                    part_new = dict(num=num, color=part["color"], visible=part["visible"], latch=0, marker=dict(), centroid=dict(), arch_lines=[], polygon=[], spline=[], fl_error=0)
                    # part_new = [num, part["color"], part["visible"], [], [], [], [], [], 0]

                # проверим есть ли на дуге пересечения
                fl_cut, fl_cut_pos = False, -1
                for mm,point in enumerate(cut_point):
                    if compare_xy(point[1],part_arch[3],8) and compare_xy(point[2],part_arch[4],8):
                        fl_cut, fl_cut_pos = True, mm
                        break

                # если пересечений нет, добавим дугу
                if fl_inout == part_arch[6]:
                    part_new["arch_lines"].append( [part_arch[0], part_arch[1], part_arch[2], part_arch[3], part_arch[4], 0,0] )
                    part_arch[6] *= 2
                # есть пересечение, меняем направление - идем по кругу
                elif fl_cut:
                    point_next = mas_pos(cut_point,fl_cut_pos+fl_inout)
                    part_new["arch_lines"].append( [arch_ring_num, 1, fl_inout, part_arch[3], part_arch[4], 0,0] )
                    for mm,part_arch_ in enumerate(part_arch_mas):
                        if compare_xy(point_next[1],part_arch_[3],8) and compare_xy(point_next[2],part_arch_[4],8):
                            nn = mm-1
                            break

        pass

    for part_new in part_new_mas:
        fl_part = False
        for nn,part in enumerate(puzzle_parts):
            if part["num"] == part_new["num"]:
                puzzle_parts[nn] = part_new
                fl_part = True
                break
        if not fl_part:
            puzzle_parts.append(part_new)

    pass

def init_color_all_parts(puzzle_parts, puzzle_rings, auto_color_parts):
    # автоматическая раскраска всех частей со смешиванием цветов внутри пересечений
    for part in puzzle_parts:
        if part["visible"] == 0: continue
        part["color"]=0

    if len(auto_color_parts)>len_puzzle_rings(puzzle_rings):
        for ring in puzzle_rings:
            if ring["type"] != 0: continue
            part_mas, _ = find_parts_in_circle(ring, puzzle_parts, [], 2)
            for part in part_mas:
                if part["visible"]==0: continue
                if part["color"]==0:
                    part["color"] = ring["num"]
                elif part["color"]<len_puzzle_rings(puzzle_rings):
                    part["color"] += ring["num"] + len_puzzle_rings(puzzle_rings)-2
                else:
                    part["color"] += ring["num"]
        for part in puzzle_parts:
            if part["visible"]==0: continue
            part["color"] = int(auto_color_parts[ part["color"]-1 ])
    else:
        mm = 0
        for ring in puzzle_rings:
            if ring["type"] != 0: continue
            part_mas, _ = find_parts_in_circle(ring, puzzle_parts, [],2)
            for part in part_mas:
                if part["visible"]==0: continue
                if mm >= len(auto_color_parts): break
                add_color_ind = int(auto_color_parts[ mm ])
                if part["color"]==0:
                    part["color"] = add_color_ind
                else:
                    new_color = get_color(var.PARTS_COLOR[part["color"]], var.PARTS_COLOR[add_color_ind])
                    new_color_ind = -1
                    for nn,color in enumerate(var.PARTS_COLOR):
                        if color == new_color:
                            new_color_ind = nn
                            break
                    if new_color_ind == -1:
                        var.PARTS_COLOR.append(new_color)
                        new_color_ind = len(var.PARTS_COLOR)-1
                    part["color"] = new_color_ind
            mm += 1

def init_color_all_circles(puzzle_parts, puzzle_rings, auto_color_parts, first_coloring):
    # автоматическая раскраска всех частей внутри заданных кругов. без смешивания цветов
    if first_coloring:
        for part in puzzle_parts:
            if part["visible"] == 0: continue
            part["color"]=0

    while len(auto_color_parts)>1:
        part_mas = []
        pos_mas = auto_color_parts.pop(0)
        color = int(auto_color_parts.pop(0))
        if typeof(pos_mas)!="list":
            pos_mas = [pos_mas]
        for nn,pos in enumerate(pos_mas):
            ring = find_element(int(pos), puzzle_rings)
            if nn==0:
                part_mas, _ = find_parts_in_circle(ring, puzzle_parts, [], 2)
            else:
                part_mas2, _ = find_parts_in_circle(ring, part_mas, [], 2)
                part_mas = part_mas2.copy()
        for part in part_mas:
            if part["visible"]==0: continue
            part["color"] = color

def set_color_all_parts(puzzle_parts, set_color_parts):
    # раскраска всех заданных частей
    while len(set_color_parts)>1:
        pos_mas = set_color_parts.pop(0)
        color = int(set_color_parts.pop(0))
        if typeof(pos_mas)!="list":
            pos_mas = [pos_mas]
        for pos in pos_mas:
            part = find_element(int(pos),puzzle_parts)
            if part=="": continue
            if part["visible"]==0: continue
            part["color"] = color

def set_marker_all_parts(puzzle_parts, set_marker_parts, puzzle_scale):
    # установка маркеров на всех заданных частях
    for marker in set_marker_parts:
        if typeof(marker) != "list": continue
        if not 2<=len(marker)<=6: continue

        part = find_element(int(marker[0]), puzzle_parts)
        if part=="": continue
        marker_text = marker[1]
        if marker_text.find("\\n")>=0:
            marker_text = marker_text.replace("\\n","\n")

        marker_dict = dict(text=marker_text, angle=0, font_size=0, horizontal_shift=0, vertical_shift=0, sprite="")
        if len(marker)>=3:
            marker_dict["angle"] = float(marker[2])
        if len(marker)>=4:
            marker_dict["font_size"] = int(float(marker[3])*puzzle_scale)
        if len(marker)>=5:
            marker_dict["horizontal_shift"] = int(marker[4])
        if len(marker)>=6:
            marker_dict["vertical_shift"] = int(marker[5])

        part["marker"] = marker_dict

def calc_all_centroids(puzzle_parts):
    for part in puzzle_parts:
        center_x, center_y = calc_centroid(part["spline"])
        area = calc_area_polygon(part["spline"])
        max_radius = calc_max_radius(part["spline"], center_x, center_y)
        centroid_dict = dict(center_x=center_x, center_y=center_y, area=area, max_radius=max_radius)
        part["centroid"] = centroid_dict
        # part["centroid"] = [center_x, center_y, area, max_radius]

def find_angle_rotate(ring,direction,freeze=False):
    # найдем следующий угол поворота в некратных кругах
    angle_mas, angle_pos = ring["angle"], ring["angle_pos"]
    if typeof(angle_mas) == "list":
        angle_pos_pred = angle_pos
        if direction>0:
            angle_rotate = angle_mas[angle_pos]
            angle_pos += direction
            angle_pos = 0 if angle_pos == len(angle_mas) else angle_pos if angle_pos >= 0 else len(angle_mas) - 1
        else:
            angle_pos += direction
            angle_pos = 0 if angle_pos == len(angle_mas) else angle_pos if angle_pos >= 0 else len(angle_mas) - 1
            angle_rotate = angle_mas[angle_pos]

        if angle_mas[angle_pos_pred]==0 and angle_mas[angle_pos]==0:
            angle_pos = angle_pos_pred
        if not freeze:
            ring["angle_pos"] = angle_pos
    else:
        angle_rotate = angle_mas
    return angle_rotate

def turn_ring_and_cut(num_ring, direction, step, puzzle_rings, puzzle_arch, puzzle_parts, fl_only_turn = False):
    # повернуть все части внутри круга и запустить нарезку всех пресечений с остальными кругами
    ring1 = find_element(num_ring, puzzle_rings)
    part_mas, _ = find_parts_in_circle(ring1, puzzle_parts, puzzle_rings, 1)

    if direction==0:
        angle_deg = step
        angle = radians(angle_deg)
        direction = 1
    elif typeof(ring1["angle"])=="list" and step>1:
        angle = 0
        for _ in range(step):
            angle_deg = find_angle_rotate(ring1, direction)
            angle += radians(angle_deg)
    else:
        angle_deg = find_angle_rotate(ring1, direction)
        angle = radians(angle_deg)*step
    rotate_parts(ring1, part_mas, puzzle_arch, angle, direction)
    calc_parts_countur(puzzle_parts, puzzle_arch, True)

    if not fl_only_turn:
        for mm, ring2 in enumerate(puzzle_rings):
            if num_ring == ring2["num"]: continue
            if calc_length(ring1["center_x"], ring1["center_y"], ring2["center_x"], ring2["center_y"]) >= ring1["radius"] + ring2["radius"]: continue

            cut_parts_in_ring(ring2, puzzle_arch, puzzle_parts)
            calc_parts_countur(puzzle_parts, puzzle_arch, True)

def remove_def_parts(puzzle_parts, remove_parts):
    # удаление заданных частей
    for rem in remove_parts:
        pos = -1
        for nn,part in enumerate(puzzle_parts):
            if part["num"]==int(rem):
                puzzle_parts.pop(nn)
                break

def remove_micro_parts(puzzle_parts, area_param):
    # удаление заданных частей
    rem_parts = []
    for part in puzzle_parts:
        polygon = part["polygon"]
        area = calc_area_polygon(polygon)
        if area<=float(area_param[0]):
            rem_parts.append(part["num"])

    for rem in rem_parts:
        pos = -1
        for nn,part in enumerate(puzzle_parts):
            if part["num"]==rem:
                puzzle_parts.pop(nn)
                break

def hide_show_def_parts(puzzle_parts, hide_parts, flag, all=False):
    # скрываем заданные части
    if not all:
        for hide in hide_parts:
            if hide=="":continue
            part = find_element(int(hide),puzzle_parts)
            part["visible"] = 1 if flag > 0 else 0
    else:
        for part in puzzle_parts:
            if flag==0:
                part["visible"] = 1-part["visible"]
            else:
                part["visible"] = 1 if flag > 0 else 0

def copy_def_parts(copy_parts, puzzle_rings, puzzle_arch, puzzle_parts, move=False):
    # копирование заданных частей - по кругу заданным поворотом
    while len(copy_parts)>=1:
        parts_list = copy_parts[0]
        if parts_list=="": break
        parts_turn = copy_parts[1]

        part_mas = []
        if typeof(parts_list) != "list":
            parts_list = [parts_list]
        for part_num in parts_list:
            part = find_element(int(part_num), puzzle_parts)
            if move:
                part_mas.append(part)
            else:
                part_num_new = max(puzzle_parts, key=lambda i: i["num"])["num"] + 1
                part_new = copy.deepcopy(part)
                part_new["num"] = part_num_new
                part_mas.append(part_new)
                puzzle_parts.append(part_new)

        if typeof(parts_turn) != "list":
            parts_turn = [parts_turn]

        #############################################
        pos = 0
        while pos<len(parts_turn):
            turn = parts_turn[pos]
            if is_number(turn):
                num_ring = int(turn)
                ring = find_element(num_ring, puzzle_rings)
                angle_deg = float(parts_turn[pos+1])
                direction = 1
                angle = radians(angle_deg)
                rotate_parts(ring, part_mas, puzzle_arch, angle, direction)
                pos+=1
            else:
                num_ring, direction, step = get_command(turn)
                if num_ring == 0: continue

                ring = find_element(num_ring, puzzle_rings)
                if typeof(ring["angle"]) == "list" and step > 1:
                    for _ in range(step):
                        angle_deg = find_angle_rotate(ring, direction,True)
                        angle = radians(angle_deg)
                        rotate_parts(ring, part_mas, puzzle_arch, angle, direction)
                else:
                    angle_deg = find_angle_rotate(ring, direction,True)
                    angle = radians(angle_deg)
                    rotate_parts(ring, part_mas, puzzle_arch, angle*step, direction)
            pos += 1
            calc_parts_countur(puzzle_parts, puzzle_arch, True)

        copy_parts.pop(0)
        copy_parts.pop(0)

def mirror_def_parts(mir_parts, puzzle_arch, puzzle_parts):
    # копирование заданных частей - зеркально относительно линии
    while len(mir_parts)>=1:
        parts_list = mir_parts[0]
        if parts_list=="": break
        mirror_line = mir_parts[1]
        if typeof(mirror_line) != "list" and len(mirror_line)!=4: break

        part_mas = []
        if typeof(parts_list) != "list":
            parts_list = [parts_list]
        for part_num in parts_list:
            part = find_element(int(part_num), puzzle_parts)
            part_num_new = max(puzzle_parts, key=lambda i: i["num"])["num"] + 1
            part_new = copy.deepcopy(part)
            part_new["num"] = part_num_new
            part_mas.append(part_new)
            puzzle_parts.append(part_new)

        #############################################
        mirror_parts(mirror_line, part_mas, puzzle_arch)
        calc_parts_countur(puzzle_parts, puzzle_arch, True)

        mir_parts.pop(0)
        mir_parts.pop(0)

def sort_and_renum_all_parts(puzzle_parts):
    # сортировка и перенумеровка частей
    part_mas = []
    for nn, part in enumerate(puzzle_parts):
        center_x, center_y = calc_centroid(part["polygon"])
        part_mas.append( [round(center_x,1), round(center_y,1), part] )
    part_mas.sort(key=lambda par: (-par[1], par[0]))
    for nn, part_cent in enumerate(part_mas):
        part_cent[2]["num"] = nn+1
    puzzle_parts.sort(key=lambda part: (part["num"]))

def remove_dublikate_parts(puzzle_parts):
    # найти и удалить дублирующиеся части
    part_dub = []
    for nn,part1 in enumerate(puzzle_parts):
        for mm, part2 in enumerate(puzzle_parts[nn+1:]):
            if len(part1["arch_lines"])!=len(part2["arch_lines"]): continue # разная длина

            # нужно сверить все дуги частей независимо от старта и направления
            pos1, pos2, direction = 0, -1, 1
            part_arc1 = part1["arch_lines"][pos1]
            for pp,part_arc2 in enumerate(part2["arch_lines"]):
                if part_arc1[0]==part_arc2[0] and part_arc1[1]==part_arc2[1] and part_arc1[2]==part_arc2[2] and compare_xy(part_arc1[3],part_arc2[3],3) and compare_xy(part_arc1[4],part_arc2[4],3) :
                    pos2 = pp
                    break
                if compare_xy(part_arc1[3],part_arc2[3],3) and compare_xy(part_arc1[4],part_arc2[4],3):
                    part_arc2next = mas_pos(part2["arch_lines"], pp-1)
                    if part_arc1[0]==part_arc2next[0] and part_arc1[1]==part_arc2next[1] and part_arc1[2]==(-part_arc2next[2]):
                        pos2 = pp
                        direction = -1
                        break
            if pos2 < 0: continue # нет стартовой вершины

            equal = True
            for pp, part_arc1 in enumerate(part1["arch_lines"]):
                part_arc2 = mas_pos(part2["arch_lines"], pos2+direction*pp)
                if direction>0:
                    if part_arc1[0]==part_arc2[0] and part_arc1[1]==part_arc2[1] and part_arc1[2]==part_arc2[2] and compare_xy(part_arc1[3],part_arc2[3],3) and compare_xy(part_arc1[4],part_arc2[4],3):
                        continue
                else:
                    if compare_xy(part_arc1[3],part_arc2[3],3) and compare_xy(part_arc1[4],part_arc2[4],3):
                        part_arc2next = mas_pos(part2["arch_lines"], pos2+direction*pp-1)
                        if part_arc1[0] == part_arc2next[0] and part_arc1[1] == part_arc2next[1] and part_arc1[2] == (-part_arc2next[2]):
                            continue
                equal = False
                break
            if equal:
                part_dub.append(part2)

    for part_rem in part_dub:
        for nn,part in enumerate(puzzle_parts):
            if part == part_rem:
                puzzle_parts.pop(nn)
                break

def copy_ring(ring_num, turn_command, puzzle_rings):
    ring_source = find_element(ring_num, puzzle_rings)
    center_x, center_y = ring_source["center_x"],ring_source["center_y"]

    if typeof(turn_command) == "list":
        if len(turn_command)==2:
            num_ring_center = int(turn_command[0])
            ring_center = find_element(num_ring_center, puzzle_rings)
            direction = 1
            angle_deg = float(turn_command[1])
            angle = radians(angle_deg)
            center_x, center_y = rotate_point(center_x,center_y, ring_center["center_x"],ring_center["center_y"], angle*direction)
    else:
        num_ring_center, direction, step = get_command(turn_command)
        if num_ring_center != 0:
            ring_center = find_element(num_ring_center, puzzle_rings)
            angle_deg = find_angle_rotate(ring_center, direction)
            angle = radians(angle_deg)
            center_x, center_y = rotate_point(center_x,center_y, ring_center["center_x"],ring_center["center_y"], angle*step*direction)

    return center_x, center_y

def remove_ring(puzzle_rings, remove_ring_mas):
    for ring_num in remove_ring_mas:
        for nn,ring in enumerate(puzzle_rings):
            if ring["num"] == int(ring_num):
                puzzle_rings.pop(nn)
                break

def find_arch(puzzle_arch, ring):
    for arch in puzzle_arch:
        if compare_xy(arch["center_x"],ring["center_x"],8) and compare_xy(arch["center_y"],ring["center_y"],8) and compare_xy(arch["radius"],ring["radius"],8):
            return arch["num"]
    return -1

def cut_def_lines(puzzle_lines, puzzle_parts, puzzle_arch, cut_lines, auto_renumbering):
    mas_lines = []
    for nn,num_line in enumerate(cut_lines):
        num_line = int(num_line)
        line = find_element(num_line, puzzle_lines)
        mas_lines.append(line)
    cut_parts_intersecting_line(mas_lines, puzzle_parts, puzzle_arch)

    calc_parts_countur(puzzle_parts, puzzle_arch, True)
    remove_dublikate_parts(puzzle_parts)
    if auto_renumbering==1:
        sort_and_renum_all_parts(puzzle_parts)

def cut_def_circles(puzzle_rings, puzzle_arch, puzzle_parts, cut_circles, auto_renumbering):
    for nn,num_ring in enumerate(cut_circles):
        num_ring = int(num_ring)
        ring1 = find_element(num_ring, puzzle_rings)
        cut_parts_in_ring(ring1, puzzle_arch, puzzle_parts)
        calc_parts_countur(puzzle_parts, puzzle_arch, True)
    remove_dublikate_parts(puzzle_parts)
    if auto_renumbering==1:
        sort_and_renum_all_parts(puzzle_parts)

def make_def_circles(puzzle_rings, puzzle_arch, puzzle_parts, make_circles, fl_all=False):
    for ring_num in make_circles:
        ring = find_element(int(ring_num),puzzle_rings)

        arch_num = find_arch(puzzle_arch, ring)
        if arch_num < 0:
            arch_num = len(puzzle_arch)
            arch_dict = dict(arch_num=arch_num, center_x=ring["center_x"], center_y=ring["center_y"], radius=ring["radius"])
            puzzle_arch.append(arch_dict)
            # arch = [arch_num, ring["center_x"], ring["center_y"], ring[3]]
            # puzzle_arch.append(arch)

        if ring["type"]!=0 and not fl_all: continue

        color = ring["num"] + 2
        part_arch = [arch_num, 0, 1, ring["center_x"], ring["center_y"] + ring["radius"], 0, 0]
        if len(puzzle_parts)==0:
            part_num_new = len(puzzle_parts)+1
        else:
            part_num_new = max(puzzle_parts, key=lambda i: i["num"])["num"] + 1
        part_dict = dict(num=part_num_new, color=color, visible=1, latch=0, marker=dict(), centroid=dict(), arch_lines=[part_arch], polygon=[], spline=[], fl_error=0)
        puzzle_parts.append(part_dict)
        # part = [part_num_new, color, 1, [], [], [part_arch], [], [], 0]
        # puzzle_parts.append(part)

    calc_parts_countur(puzzle_parts, puzzle_arch, True)

def rotate_all_parts(puzzle_rings, puzzle_arch, puzzle_parts, rotate_parts_param):
    center_x,center_y,angle_deg = float(rotate_parts_param[0]),float(rotate_parts_param[1]),float(rotate_parts_param[2])
    angle = radians(angle_deg)

    for ring in puzzle_rings:
        ring["center_x"],ring["center_y"] = rotate_point(ring["center_x"],ring["center_y"], center_x,center_y, angle)
    for arch in puzzle_arch:
        arch["center_x"],arch["center_y"] = rotate_point(arch["center_x"],arch["center_y"], center_x,center_y, angle)
    for part in puzzle_parts:
        for part_arch in part["arch_lines"]:
            part_arch[3], part_arch[4] = rotate_point(part_arch[3],part_arch[4], center_x,center_y, angle)
        if len(part["marker"]):
            # part["marker"]["angle"] += -angle_deg
            part["marker"]["horizontal_shift"], part["marker"]["vertical_shift"] = rotate_point(part["marker"]["horizontal_shift"],part["marker"]["vertical_shift"], center_x,center_y, angle)
        if len(part["centroid"]):
            part["centroid"]["center_x"], part["centroid"]["center_y"] = rotate_point(part["centroid"]["center_x"],part["centroid"]["center_y"], center_x,center_y, angle)

    calc_parts_countur(puzzle_parts, puzzle_arch, True)

def scramble_puzzle(puzzle_rings, puzzle_arch, puzzle_parts, type, draw_state, SCREEN,game_scr,shift_width,shift_height):
    # обработка рандома для Скрамбла
    random.seed()
    start_time = time.time()
    pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_WAITARROW)
    win_caption = pygame.display.get_caption()
    pygame.display.set_caption("Please wait! Scrambling ...")

    scramble_mul = 1 if type=="scramble" else 10
    for ring in puzzle_rings:
        if typeof(ring["angle"]) == "list":
            scramble_mul *= 2
            break
    scramble_move = len_puzzle_rings(puzzle_rings) * len(puzzle_parts) * scramble_mul * 3

    ring_num_min,ring_num_max = min(puzzle_rings, key=lambda i: i["num"])["num"],max(puzzle_rings, key=lambda i: i["num"])["num"],

    step = ring_num_pred = percent_pred = 0
    time_pred = start_time
    while step<=scramble_move:
        fl_break = False
        cur_time = time.time()
        time_sec = int(cur_time-time_pred)

        percent = int(100 * step / scramble_move)
        if time_sec>=5: # if (percent%5)==0 and (percent_pred!=percent):
            try:
                events = pygame.event.get()
                for ev in events:  # Обрабатываем события
                    if (ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE):
                        fl_break = True

                if draw_state: # (percent%10)==0
                    calc_parts_countur(puzzle_parts, puzzle_arch)
                    draw_game_screen(SCREEN,game_scr, puzzle_rings, puzzle_parts, 0, shift_width, shift_height)

                pygame.display.set_caption("Please wait! Scrambling ... " + str(percent) + "% (ESC)")
                pygame.display.update()
            except:
                pass
            time_pred = cur_time  # percent_pred = percent
        if fl_break: break

        # выберем круг для поворота
        direction = random.choice([-1, 1])
        while True:
            ring_num = random.randint(ring_num_min,ring_num_max)
            ring = find_element(ring_num, puzzle_rings)
            if ring=="": continue
            if ring["type"]!=0 : continue
            break
            # if ring_num_pred != ring_num: break
        ring_num_pred = ring_num

        if len(ring["linked"]) == 0 or len(ring["linked"]["link_mas"]) == 0:
            link_dict = dict(ring_num=ring_num, direction=1, gear_ratio=1, angle=0, sprite="")
            link_mas = [ link_dict ]
            # link_mas = [[ring_num, 1, 1, 0, ""]]
        else:
            link_mas = ring["linked"]["link_mas"]

        # проверим - можем ли мы повернуть заданный круг
        fl_turn = True
        for mm, link in enumerate(link_mas):
            ring_num_ = link["ring_num"]
            linked_ring = find_element(ring_num_, puzzle_rings)
            if not check_ring_intersecting_parts(linked_ring, puzzle_parts):
                fl_turn = False
                break
        if not fl_turn: continue

        # выполним поворот круга
        for mm, link in enumerate(link_mas):
            ring_num_, direction_, gears_ratio = link["ring_num"], link["direction"], link["gear_ratio"]
            direction_ = direction * direction_

            ring = find_element(ring_num_, puzzle_rings)
            if mm == 0:  # ring_num_==ring_num:
                angle_rotate = find_angle_rotate(ring, direction_)
                angle_rotate0 = angle_rotate
            else:
                angle_rotate = angle_rotate0 * gears_ratio

            #############################################################################
            # 1. найдем все части внутри круга
            part_mas, part_mas_other = find_parts_in_circle(ring, puzzle_parts, puzzle_rings)
            if len(part_mas) == 0 or angle_rotate == 0:
                continue

            if not check_latch(part_mas, direction): continue

            # 2. повернем все части внутри круга
            if len(part_mas) > 0:
                rotate_parts(ring, part_mas, puzzle_arch, radians(angle_rotate), -direction)
                calc_parts_countur(part_mas, puzzle_arch, True)
        step += 1

    calc_parts_countur(puzzle_parts, puzzle_arch)

    pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
    if typeof(win_caption)=="str":
        pygame.display.set_caption(win_caption)
    elif typeof(win_caption)=="list":
        pygame.display.set_caption(win_caption[0])

def check_all_rings(puzzle_rings):
    for nn,ring in enumerate(puzzle_rings):
        for mm,ring2 in enumerate(puzzle_rings):
            if nn==mm: continue

            # находим концентрические, но не равные круги
            if compare_xy(ring["center_x"],ring2["center_x"],8) and compare_xy(ring["center_y"],ring2["center_y"],8) and not compare_xy(ring["radius"],ring2["radius"],8):
                if ring["radius"]>ring2["radius"]:
                    inner_type = 0
                    if ring["angle"]==ring2["angle"] and typeof(ring["angle"])!="list" and ring["type"]==ring2["type"]:
                        inner_type = 1
                    elif ring2["type"]==1:
                        inner_type = 1
                    fl_inner = False
                    for inner in ring["inner"]:
                        if inner["num"]==ring2["num"] and inner["type"]==inner_type:
                            fl_inner = True
                    if not fl_inner:
                        inner_dict = dict(num=ring2["num"],type=inner_type)
                        ring["inner"].append(inner_dict)
                        # ring["inner"].append( [ring2["num"],inner_type] )

def rotate_def_circles(puzzle_rings, puzzle_arch, puzzle_parts, rotate_circles, auto_renumbering):
    # авторотация частей
    for nn,cut_command in enumerate(rotate_circles):
        if cut_command=="": continue
        if typeof(cut_command)=="list":
            # обработка команд в скобках
            count = 1
            if nn+1<len(rotate_circles):
                if is_number(rotate_circles[nn+1]):
                    count = int(rotate_circles[nn+1])

            if is_number(cut_command[0])==1 and len(cut_command)==2:
                # обработка числовой записи RotateCircles: (1,36), (2,-72) - круг и угол поворота
                num_ring, angle_deg = int(cut_command[0]), float(cut_command[1])
                direction = 0
                turn_ring_and_cut(num_ring, direction, angle_deg, puzzle_rings, puzzle_arch, puzzle_parts, True)
            else:
                # запуск вида (1L, 3R2, 1R),2 - повтор последовательности команд
                for _ in range(count):
                    for mm, turn_command in enumerate(cut_command):
                        num_ring, direction, step = get_command(turn_command)
                        if num_ring == 0: continue
                        turn_ring_and_cut(num_ring, direction, step, puzzle_rings, puzzle_arch, puzzle_parts, True)
        else:
            # запуск одиночной команды: 1R2
            num_ring, direction, step = get_command(cut_command)
            if num_ring==0: continue
            turn_ring_and_cut(num_ring, direction, step, puzzle_rings, puzzle_arch, puzzle_parts, True)

    # найти и удалить дублирующиеся части
    remove_dublikate_parts(puzzle_parts)
    if auto_renumbering==1:
        sort_and_renum_all_parts(puzzle_parts)

    calc_parts_countur(puzzle_parts, puzzle_arch)

def init_cut_all_ring_to_parts(puzzle_rings, puzzle_arch, puzzle_parts, auto_cut_parts, auto_renumbering, init=True):
    if init:
        # инициализируем круги и запускаем нарезку частей с помощью заданной или случайной последовательности

        # сформируем цельные круги
        make_circles = []
        for ring in puzzle_rings:
            make_circles.append(ring["num"])
        make_def_circles(puzzle_rings, puzzle_arch, puzzle_parts, make_circles)

        # первичное разбиение кругов на части.
        fl_cutting_circles = True

        # нужно пропустить при таком синтаксисе, тк запускаем не все круги: AutoCutParts: (1L, 3L2, 1R), (1L, 3R2, 1R, 2), (1L, 2R2, 1R, 1,3)
        if len(auto_cut_parts)>0:
            if typeof(auto_cut_parts[0])=="list":
                fl_cutting_circles = False
                if (auto_cut_parts[0][0]=="Random" or is_number(auto_cut_parts[0][0])):
                    fl_cutting_circles = True
                elif len(auto_cut_parts)>1:
                    if not is_number(auto_cut_parts[0][0]) and is_number(auto_cut_parts[1]):
                        fl_cutting_circles = True

        if fl_cutting_circles:
            for mm, ring in enumerate(puzzle_rings):
                cut_parts_in_ring(ring, puzzle_arch, puzzle_parts)
                calc_parts_countur(puzzle_parts, puzzle_arch, True)

                # найти и удалить дублирующиеся части
                remove_dublikate_parts(puzzle_parts)

    # авторотация и разбиение на части
    for nn,cut_command in enumerate(auto_cut_parts):
        if cut_command=="": continue
        if (typeof(cut_command)=="list" and cut_command[0]=="Random") or cut_command=="Random":
            # запуск команды Random,50
            num_ring_pred = 0
            if typeof(cut_command)=="list" and len(cut_command)>2:
                random.seed(int(cut_command[2]))
            else:
                random.seed(1)
            if typeof(cut_command) == "list":
                count = int(cut_command[1])
            else:
                count = int(auto_cut_parts[nn+1])

            for nn in range(count):
                direction = random.choice([-1, 1])
                while True:
                    num_ring = random.randint(1, len_puzzle_rings(puzzle_rings))
                    if num_ring_pred == num_ring: continue
                    num_ring_pred = num_ring
                    break
                turn_ring_and_cut(num_ring, direction, 1, puzzle_rings, puzzle_arch, puzzle_parts)
        elif typeof(cut_command)=="list":
            # обработка команд в скобках
            count = 1
            if nn+1<len(auto_cut_parts):
                if is_number(auto_cut_parts[nn+1]):
                    count = int(auto_cut_parts[nn+1])

            if count==1:
                # запуск вида (1L, 3R2, 1R, 2) - секущий круг внутри скобок
                fl_one_ring = False
                for mm, turn_command in enumerate(cut_command):
                    if mm==0 and is_number(turn_command):
                        # обработка числовой записи AutoCutParts: (1,36), (2,-72) - круг и угол поворота
                        num_ring, angle_deg = int(cut_command[0]), float(cut_command[1])
                        direction = 0
                        turn_ring_and_cut(num_ring, direction, angle_deg, puzzle_rings, puzzle_arch, puzzle_parts, True)
                        break

                    elif not is_number(turn_command):
                        # повернуть все части внутри круга
                        num_ring, direction, step = get_command(turn_command)
                        if num_ring == 0: continue
                        turn_ring_and_cut(num_ring, direction, step, puzzle_rings, puzzle_arch, puzzle_parts, True)
                    else:
                        # запустить нарезку с заданным кругом
                        num_ring = int(turn_command)
                        if num_ring!=0:
                            ring1 = find_element(num_ring, puzzle_rings)
                            cut_parts_in_ring(ring1, puzzle_arch, puzzle_parts)
                            calc_parts_countur(puzzle_parts, puzzle_arch, True)
                        fl_one_ring = True
                if not fl_one_ring:
                    # обработка (1L, 3L2, 1R)
                    for mm, ring2 in enumerate(puzzle_rings):
                        cut_parts_in_ring(ring2, puzzle_arch, puzzle_parts)
                        calc_parts_countur(puzzle_parts, puzzle_arch, True)
            else:
                # запуск вида (1L, 3R2, 1R),2 - повтор последовательности команд
                for _ in range(count):
                    for mm, turn_command in enumerate(cut_command):
                        num_ring, direction, step = get_command(turn_command)
                        if num_ring == 0: continue
                        turn_ring_and_cut(num_ring, direction, step, puzzle_rings, puzzle_arch, puzzle_parts)

        else:
            # запуск одиночной команды: 1R2
            num_ring, direction, step = get_command(cut_command)
            if num_ring==0: continue
            turn_ring_and_cut(num_ring, direction, step, puzzle_rings, puzzle_arch, puzzle_parts)

    # найти и удалить дублирующиеся части
    remove_dublikate_parts(puzzle_parts)
    if auto_renumbering==1:
        sort_and_renum_all_parts(puzzle_parts)

    calc_parts_countur(puzzle_parts, puzzle_arch)

def get_command(cut_command):
    command = cut_command.upper()
    pos = command.find("R")
    pos = pos if pos >= 0 else command.find("L")
    if pos < 0 or len(command) < 2: return 0, 0, 0

    num_ring = int(command[0:pos])
    direction = 1 if command[pos].upper() == "R" else -1 if command[pos].upper() == "L" else 0
    if direction == 0: return 0, 0, 0
    step = 1 if len(command) == pos + 1 else int(command[pos + 1:])
    return num_ring, direction, step

def link_rings(puzzle_rings, linked_mas):
    if len(linked_mas)==0: return

    def link_def_rings(puzzle_rings, link_mas):
        for nn,link_num in enumerate(link_mas):
            link_mas[nn] = int(link_num)

        for link_num1 in link_mas:
            ring1 = find_element(abs(link_num1), puzzle_rings)
            gears1, linked1 = ring1["linked"]["gears"], ring1["linked"]["link_mas"]
            for link_num2 in link_mas:
                if link_num1 == link_num2:
                    link_dict = dict(ring_num=abs(link_num1), direction=1, gear_ratio=1, angle=0, sprite="")
                    linked1.insert(0, link_dict)
                    # linked1.insert( 0,[abs(link_num1),1,1,0,""] )
                else:
                    ring2 = find_element(abs(link_num2), puzzle_rings)
                    gears2 = ring2["linked"]["gears"]
                    direction = 1 if link_num1*link_num2>0 else -1
                    link_dict = dict(ring_num=abs(link_num2), direction=direction, gear_ratio=gears1/gears2, angle=0, sprite="")
                    linked1.append(link_dict)
                    # linked1.append( [abs(link_num2),direction,gears1/gears2,0,""] )

    if typeof(linked_mas[0])!="list":
        link_def_rings(puzzle_rings, linked_mas)
    else:
        for link in linked_mas:
            link_def_rings(puzzle_rings, link)

def latch_parts(puzzle_parts, latch_mas):
    while len(latch_mas)>=1:
        parts_list = latch_mas[0]
        parts_direct = latch_mas[1]

        if is_number(parts_direct):
            parts_direct = int(parts_direct)
            direction = 1 if parts_direct==1 else -1 if parts_direct==-1 else 0
        else:
            direction = 1 if parts_direct=='+' else -1 if parts_direct=='-' else 0

        if typeof(parts_list) != "list":
            parts_list = [parts_list]
        for part_num in parts_list:
            part = find_element(int(part_num), puzzle_parts)
            part["latch"] = direction

        latch_mas.pop(0)
        latch_mas.pop(0)

def check_latch(part_mas, direction=0):
    if direction==0: # проверяем есть ли в круге противоположный набор защелок
        fl_dir = 0
        for part in part_mas:
            if part["latch"]==0: continue
            if fl_dir == 0:
                fl_dir = part["latch"]
            elif fl_dir != part["latch"]:
                return False
    else: # проверяем есть ли обратные защелки от заданного направления
        for part in part_mas:
            if part["latch"]==0: continue
            if part["latch"]!=direction:
                return False
    return True

# def find_incorrect_parts(puzzle_parts):
#     # поиск накладывающихся друг на друга кусочков
#     len_puz = len(puzzle_parts)
#     for nn,part1 in enumerate(puzzle_parts[:len_puz-1]):
#         if part1[8]==2: continue
#
#         count_in = count_out = 0
#         center_x1, center_y1, _, max_radius1 = part1["centroid"]
#
#         for mm, part2 in enumerate(puzzle_parts[nn+1:]):
#             if part2["fl_error"]==2: continue
#             # быстрая проверка по центроиду
#             center_x2, center_y2, _, max_radius2 = part2["centroid"]
#             centroid_length = calc_length(center_x1, center_y1, center_x2, center_y2)
#             if centroid_length > (max_radius1 + max_radius2):  # части далеко друг от друга
#                 continue
#
#             # проверка всех точек
#             for x,y in part1[6"polygon"]:
#                 fl_pol, _ = check_polygon(part2["polygon"], part2["centroid"], x, y)
#                 if fl_pol:
#                     count_in += 1
#                 else:
#                     count_out += 1
#                 if count_in>0 and count_out>0:
#                     break
#
#             if count_in > 0 and count_out == 0: # наложение
#                 part1["fl_error"] = 1 if part1["fl_error"]<1 else part1["fl_error"]
#                 part2["fl_error"] = 1 if part2["fl_error"]<1 else part2["fl_error"]
#                 print(1,count_in,count_out)
#             elif count_in > 2 and count_out > 0:  # пересечение
#                 part1["fl_error"] = 2 if part1["fl_error"]<2 else part1["fl_error"]
#                 part2["fl_error"] = 2 if part2["fl_error"]<2 else part2["fl_error"]
#                 print(2,count_in,count_out)

def draw_game_screen(SCREEN,game_scr, puzzle_rings,puzzle_parts,ring_select, shift_width,shift_height):
    # global SCREEN,game_scr

    game_scr.fill(pygame.Color(var.GRAY_COLOR))

    # отрисовка контуров
    for nn, ring in enumerate(puzzle_rings):
        if ring["type"] == 0:
            draw_smoth_polygon(game_scr, var.GRAY_COLOR2, ring["spline"], 2)
        # elif not (len(ring["linked"]) == 0 or len(ring["linked"]["link_mas"]) == 0):
        #     draw_smooth_gear(game_scr, GRAY_COLOR2, ring["center_x"], ring["center_y"], ring["radius"]+5, 10)

    # отрисовка частей
    for nn, part in enumerate(puzzle_parts):
        if part["visible"] > 0:
            pygame.draw.polygon(game_scr, mas_pos(var.PARTS_COLOR, part["color"]), part["spline"], 0) # Заливка
        if part["fl_error"] == 0:
            draw_smoth_polygon(game_scr, var.BLACK_COLOR, part["spline"], var.COUNTUR)
    for nn, part in enumerate(puzzle_parts):
        if part["fl_error"] != 0:
            draw_smoth_polygon(game_scr, var.RED_COLOR, part["spline"], var.COUNTUR)

    # # отрисовка отверстий у частей
    # for nn,part in enumerate(puzzle_parts):
    #     if part["visible"]>0:
    #         part["polygon"]
    #         pygame.draw.polygon(game_scr,mas_pos(PARTS_COLOR,part["color"]),part["spline"],0)

    # отрисовка выделения
    if ring_select > 0:
        ring = find_element(ring_select, puzzle_rings)
        draw_smoth_polygon(game_scr, var.WHITE_COLOR, ring["spline"], 2)
        if not (len(ring["linked"]) == 0 or len(ring["linked"]["link_mas"]) == 0):
            for nn, link in enumerate(ring["linked"]["link_mas"]):
                if nn == 0: continue
                linked_ring = find_element(link["ring_num"], puzzle_rings)
                if check_ring_intersecting_parts(linked_ring, puzzle_parts):
                    draw_smoth_polygon(game_scr, var.WHITE_COLOR, linked_ring["spline"], 2)

    # рисуем маркеры
    draw_all_markers(game_scr, puzzle_parts, puzzle_rings)

    SCREEN.blit(game_scr, (shift_width, shift_height))

def test_mode_screenshot(SCREEN,game_scr, puzzle_name,puzzle_rings,puzzle_arch,puzzle_parts, fl_test, fl_test_photo, fl_test_scramble, count_test_scramble, fl_screenshot, photo_screen, dir_screenshots, sub_folder, shift_width,shift_height):
    # global game_scr

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
                game_scr.blit(photo_screen, (var.GAME[0] - var.PHOTO[0] - var.BORDER // 3, var.BORDER // 3))
                pygame.draw.rect(game_scr, pygame.Color("#B88800"), (var.GAME[0] - var.PHOTO[0] - 2 * (var.BORDER // 3), 0, var.PHOTO[0] + 2 * (var.BORDER // 3), var.PHOTO[1] + 2 * (var.BORDER // 3)), var.BORDER // 3)
                screenshot2 = os.path.join(dir_screenshots + sub_folder, puzzle_name + " (photo).jpg")
                pygame.image.save(game_scr, screenshot2)

        if fl_test_scramble > 0:
            # сохраним скрин запутанной головоломки
            if count_test_scramble > 0:
                screenshot = os.path.join(dir_screenshots + sub_folder, puzzle_name + " (scramble " + str(count_test_scramble) + ").jpg")
                pygame.image.save(game_scr, screenshot)
            if count_test_scramble < fl_test_scramble:
                scramble_puzzle(puzzle_rings, puzzle_arch, puzzle_parts, "scramble", False, SCREEN,game_scr,shift_width,shift_height)
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
