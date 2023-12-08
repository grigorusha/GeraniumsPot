from calc import *
from syst import *

from pygame import *

import copy
import random
from math import pi, sqrt, cos, sin, tan, acos, asin, atan, exp, pow, radians, degrees

# puzzle_rings, puzzle_arch, puzzle_parts - формат массивов:

# puzzle_rings - [ring_num, center_x, center_y, radius, angle_deg, _ , type]
#              - [ring_num, center_x, center_y, radius, (angle_deg1,angle_deg2,...), jumble_angle_pos, type] - angle_deg1+angle_deg2+..=360 deg, jumble_angle_pos = 0,1,..
#       (круги создаются в процедуре: work.read_puzzle_script_and_init_puzzle)
#              для головоломок с некратными углами, в параметре Angle массив углов, а также позиция текущего угла поворота всего круга.
#              type - 0 это стандартный кольца, 1 это вспомогательные кольца для нарезки, собственных частей не имеют, как контуры не отображаем

# puzzle_arch  - [arch_num, center_x, center_y, radius]
#       (арки создаются в процедурах: make_def_circles, rotate_part,    work.read_puzzle_script_and_init_puzzle)
#              вторичные арки которые формируют части

# puzzle_parts - [part_num, color_index, visible, [marker], [centroid], [mas_arch_lines], [mas_polygon], [mas_spline]]
#                        0            1        2        3           4                 5              6             7
#       (части создаются в процедурах: make_def_circles, cut_parts_in_ring, copy_def_parts,    work.read_puzzle_script_and_init_puzzle)
#       marker - [text, angle, font_size, sprite]
#       centroid - [center_x, center_y, area]
#       mas_arch_lines - [ [part_arch1],[part_arch2],.. ]
#           part_arch - [arch_num, type, direction, start_x, start_y, fl]
#                               0     1          2        3        4   5
#               type - 0 окружность, 1 дуга, 2 линия
#               fl - начало попадает внутрь круга: -1 нет, 0 на границе, 1 внутри.  10 вся дуга совпадает с окружностью
#       mas_polygon - [ [x0,y0],..,[xn,yn] ] - сокращенный полигон (несколько точек из дуги) для быстрых проверок пересечений
#       mas_spline - [ [x0,y0],[x1,y1],..,[xm,ym] ] - плавный сплайн для отрисовки контура фигуры

# puzzle_lines - [line_num, x0, y0, angle]
#              вторичные линии которые формируют части

# puzzle_areas - [area_num, [mas_lines]]

def rotate_part(ring, part_mas, puzzle_arch, angle, direction):
    # поворот всех частей из массива относительно центра круга
    for part in part_mas:
        if len(part[3])>0:
            part[3][1] += degrees(angle)*-direction
        if len(part[4])>0:
            part[4][0], part[4][1] = rotate_point(ring[1], ring[2], part[4][0], part[4][1], angle*-direction)

        for part_arch in part[5]:
            part_arch[3], part_arch[4] = rotate_point(ring[1], ring[2], part_arch[3], part_arch[4], angle*-direction) # разворачиваем direction, тк центр координат вверху

            arch_cur = find_element(part_arch[0], puzzle_arch)
            arch_x, arch_y = rotate_point(ring[1], ring[2], arch_cur[1], arch_cur[2], angle*-direction)

            fl_arch = False
            for arch in puzzle_arch:
                if compare_xy(arch[1], arch_x, 2) and compare_xy(arch[2], arch_y, 2) and (arch_cur[3]==arch[3]):
                    part_arch[0] = arch[0]
                    fl_arch = True
                    break

            if not fl_arch:
                arch_num = max(puzzle_arch, key=lambda i: i[0])[0] + 1
                puzzle_arch.append([arch_num, arch_x, arch_y, arch_cur[3]])
                part_arch[0] = arch_num

def len_puzzle_rings(puzzle_rings):
    len_puzzle_rings = 0
    for ring in puzzle_rings:
        if ring[6] == 0: len_puzzle_rings += 1
    return len_puzzle_rings

def calc_arch_spline(arch_mas, arch_x, arch_y, arch_r, direction, max_iter = 0):
    # расчет всех точек сплайна для полигона. max_iter - дает возможность поcчитать только грубое приближение
    fl_error = False
    step = 1
    input_xy = arch_mas.copy()
    fl_iter, iter = True, 0
    while fl_iter:
        fl_iter, iter = False, iter + 1
        mas_xy, len_mas = [], len(input_xy) - 1
        for nn in range(len_mas):
            mas_xy.append([input_xy[nn][0], input_xy[nn][1]])

            x1, y1 = mas_pos(input_xy, nn)
            x3, y3 = mas_pos(input_xy, nn + 1)

            len_vek = calc_length(x1, y1, x3, y3)
            if iter==1 and x1==x3 and y1==y3:
                # чистая окружность с одной исходной точкой
                x2, y2 = (arch_x-x1)+arch_x, (arch_y-y1)+arch_y
                mas_xy.append([x2, y2])
                fl_iter = True

            elif len_vek > step:
                x2, y2 = calc_center_arch(x1, y1, x3, y3, arch_x, arch_y, arch_r, direction)

                mas_xy.append([x2, y2])
                fl_iter = True
        mas_xy.append([input_xy[len_mas][0], input_xy[len_mas][1]])
        input_xy = mas_xy.copy()

        if max_iter>0 and iter>=max_iter:
            break

        if iter > 100:
            print("BAD !!!! - "+str(iter))
            fl_error = True
            break # иногда уходит в бесконечный цикл... ;(

    return mas_xy, fl_error

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

        part_arch_mas = part[5]
        for nn, part_arch in enumerate(part_arch_mas):
            arch = find_element(part_arch[0], puzzle_arch)
            arch_x, arch_y, arch_r = arch[1], arch[2], arch[3]

            direction = part_arch[2]

            part_arch_next = find_part_arch_next(part_arch_mas, nn)
            arch_mas = [ [part_arch[3], part_arch[4]] , [part_arch_next[3], part_arch_next[4]] ]

            if not short_only:
                mas_xy,fl_error = calc_arch_spline(arch_mas, arch_x, arch_y, arch_r, direction)
                if fl_error:
                    print("Error: "+str(part[0])+", "+str(part_arch[0]))
                mas_full_xy += mas_xy
                mas_full_xy.pop()

            if len(part[5])==1: # это окружность?
                mas_xy,fl_error = calc_arch_spline(arch_mas, arch_x, arch_y, arch_r, direction, 6)
            else:
                mas_xy,fl_error = calc_arch_spline(arch_mas, arch_x, arch_y, arch_r, direction, 4)
            mas_short_xy += mas_xy
            mas_short_xy.pop()

        if len(part)>=7:
            part[6], part[7] = mas_short_xy, mas_full_xy
        else:
            part.append(mas_short_xy)
            part.append(mas_full_xy)

def find_parts_in_circle(ring, puzzle_parts, mode=0):
    # найдем все части соотносящиеся с кругом, в зависимости от режима выборки
    # mode : 0 - все части в круге, нет пересечений с кругом, 1 - только части внутри круга,
    # 2 - части совпадающие с кругом (все внутри и те что пересекают), 3 - только части пересекающие круг

    part_mas, part_mas_other = [], []
    for part in puzzle_parts:
        fl_part = -1  # 0 - часть за пределами круга, 1 - часть внутри, 2 часть пересекает круг, 3 часть совпадает с кругом (все точки касательные)
        for part_point in part[6]:
            pos = check_circle(ring[1], ring[2], part_point[0], part_point[1], ring[3])
            if pos[1]:
                if fl_part == -1:
                    fl_part = 3
            elif pos[0]:
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
    for part in puzzle_parts:
        if part not in part_mas:
            part_mas_other.append(part)

    return part_mas, part_mas_other

def cut_parts_in_ring(ring, puzzle_arch, puzzle_parts):
    # нарезка контуром окружности всех пересекающих ее частей
    part_mas, _ = find_parts_in_circle(ring, puzzle_parts, 3)
    arch_ring_num = find_arch(puzzle_arch, ring)

    part_new_mas = []
    part_num_new = max(puzzle_parts, key=lambda i: i[0])[0] + 1

    for part in part_mas:
        if part[2]==0: continue
        part_arch_mas = part[5]

        # найдем точки пересечения
        cut_point, nn = [], -1
        while nn<len(part_arch_mas)-1:
            nn += 1
            part_arch = part_arch_mas[nn]

            part_arch_next = find_part_arch_next(part_arch_mas, nn)
            arch = find_element(part_arch[0], puzzle_arch)
            intersect = circles_intersect(ring[1], ring[2], ring[3], arch[1], arch[2], arch[3])
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
                fl1, fl2 = check_point_in_arch(part_arch[3], part_arch[4], part_arch_next[3], part_arch_next[4], intersect[0][0], intersect[0][1], arch[1], arch[2], part_arch[2]), False
                if len(intersect) == 2:
                    fl2 = check_point_in_arch(part_arch[3], part_arch[4], part_arch_next[3], part_arch_next[4], intersect[1][0], intersect[1][1], arch[1], arch[2], part_arch[2])

            # дабавляем точки пересечений в массив, исключая те что в конце дуги (они попадут в начало следующей)
            if fl1:
                fl_corner = (compare_xy(part_arch[3],intersect[0][0],8) and compare_xy(part_arch[4],intersect[0][1],8))
                fl_corner_next = (compare_xy(part_arch_next[3],intersect[0][0],8) and compare_xy(part_arch_next[4],intersect[0][1],8))

                angle = calc_angle(ring[1], ring[2], intersect[0][0], intersect[0][1], ring[3])
                cut_point.append([nn, intersect[0][0], intersect[0][1], angle[0], fl_corner or fl_corner_next, (fl1 and fl2)])
                if fl_corner or fl_corner_next: fl1 = False
            if fl2:
                fl_corner = (compare_xy(part_arch[3],intersect[1][0],8) and compare_xy(part_arch[4],intersect[1][1],8))
                fl_corner_next = (compare_xy(part_arch_next[3],intersect[1][0],8) and compare_xy(part_arch_next[4],intersect[1][1],8))

                angle = calc_angle(ring[1], ring[2], intersect[1][0], intersect[1][1], ring[3])
                cut_point.append([nn, intersect[1][0], intersect[1][1], angle[0], fl_corner or fl_corner_next, (fl1 and fl2)])
                if fl_corner or fl_corner_next: fl2 = False

            # внесем новые точки в массив дуг
            if len(part_arch_mas) == 1 and fl1 and fl2:  # цельная окружность
                part_arch_mas = []
                x_ca, y_ca = calc_center_arch(intersect[0][0],intersect[0][1], intersect[1][0],intersect[1][1], arch[1],arch[2],arch[3], part_arch[2])
                pos = check_circle(ring[1], ring[2], x_ca, y_ca, ring[3])
                if pos[0]:
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
                x_ca, y_ca = calc_center_arch(intersect[0][0],intersect[0][1], intersect[1][0],intersect[1][1], arch[1],arch[2],arch[3], part_arch[2])
                pos = check_circle(ring[1], ring[2], part_arch[3], part_arch[4], ring[3])
                if pos[0]:
                    intersect[0], intersect[1] = intersect[1], intersect[0]
                pos = check_circle(ring[1], ring[2], x_ca, y_ca, ring[3])
                if pos[0]:
                    part_arch_mas.insert(nn+1, [part_arch[0], 1, part_arch[2], intersect[0][0], intersect[0][1], 0,0])
                    part_arch_mas.insert(nn+2, [part_arch[0], 1, part_arch[2], intersect[1][0], intersect[1][1], 0,0])
                else:
                    part_arch_mas.insert(nn+1, [part_arch[0], 1, part_arch[2], intersect[1][0], intersect[1][1], 0,0])
                    part_arch_mas.insert(nn+2, [part_arch[0], 1, part_arch[2], intersect[0][0], intersect[0][1], 0,0])
                nn += 2

        # расставим флаги попадания углов и дуг внутрь круга
        if len(part_arch_mas) > 1:  # не цельная окружность
            for nn, part_arch in enumerate(part_arch_mas):
                pos = check_circle(ring[1], ring[2], part_arch[3], part_arch[4], ring[3], 5)
                part_arch[5] = part_arch[6] = 0 if pos[1] else (1 if pos[0] else -1)
                if part_arch[5] == 0:  # проверим, не совпадает ли дуга с окружностью
                    part_arch_next = find_part_arch_next(part_arch_mas, nn)
                    arch = find_element(part_arch[0], puzzle_arch)
                    x_ca, y_ca = calc_center_arch(part_arch[3], part_arch[4], part_arch_next[3], part_arch_next[4], arch[1], arch[2], arch[3], part_arch[2])
                    pos = check_circle(ring[1], ring[2], x_ca, y_ca, ring[3],5)
                    if pos[1]:  # середина дуги лежит на окружности
                        part_arch[6] = 0
                    elif pos[0] and not pos[1]:  # середина дуги лежит внутри окружности
                        part_arch[6] = 1
                    elif not pos[0]:  # середина дуги лежит вне окружности
                        part_arch[6] = -1

        cut_point.sort(key=lambda point: -point[3])

        # cut_point [part_arch_num, x,y, angle, fl_corner, fl_arc]
        #     fl_corner - точка на угле, fl_arc - на дуге две точки

        if len(cut_point) > 1:
            nn, part_new, fl_part, pos, fl_inout = -1, [], False, -1, 0
            while True:
                if len(part_new) > 0:
                    if len(part_new[5])>(len(part_arch_mas)+len(cut_point)): break
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
                        num = part[0]
                    else:
                        num = part_num_new
                        part_num_new += 1
                    part_new = [num, part[1], part[2], [], [], [], [], []]

                # проверим есть ли на дуге пересечения
                fl_cut, fl_cut_pos = False, -1
                for mm,point in enumerate(cut_point):
                    if compare_xy(point[1],part_arch[3],8) and compare_xy(point[2],part_arch[4],8):
                        fl_cut, fl_cut_pos = True, mm
                        break

                # если пересечений нет, добавим дугу
                if fl_inout == part_arch[6]:
                    part_new[5].append( [part_arch[0], part_arch[1], part_arch[2], part_arch[3], part_arch[4], 0,0] )
                    part_arch[6] *= 2
                # есть пересечение, меняем направление - идем по кругу
                elif fl_cut:
                    point_next = mas_pos(cut_point,fl_cut_pos+fl_inout)
                    part_new[5].append( [arch_ring_num, 1, fl_inout, part_arch[3], part_arch[4], 0,0] )
                    for mm,part_arch_ in enumerate(part_arch_mas):
                        if compare_xy(point_next[1],part_arch_[3],8) and compare_xy(point_next[2],part_arch_[4],8):
                            nn = mm-1
                            break

        pass

    for part_new in part_new_mas:
        fl_part = False
        for nn,part in enumerate(puzzle_parts):
            if part[0] == part_new[0]:
                puzzle_parts[nn] = part_new
                fl_part = True
                break
        if not fl_part:
            puzzle_parts.append(part_new)

    pass

def init_color_all_parts(puzzle_parts, puzzle_rings, auto_color_parts, PARTS_COLOR):
    # автоматическая раскраска всех частей со смешиванием цветов внутри пересечений
    for part in puzzle_parts:
        if part[2] == 0: continue
        part[1]=0

    if len(auto_color_parts)>len_puzzle_rings(puzzle_rings):
        for ring in puzzle_rings:
            if ring[6] != 0: continue
            part_mas, _ = find_parts_in_circle(ring, puzzle_parts, 2)
            for part in part_mas:
                if part[2]==0: continue
                if part[1]==0:
                    part[1] = ring[0]
                elif part[1]<len_puzzle_rings(puzzle_rings):
                    part[1] += ring[0] + len_puzzle_rings(puzzle_rings)-2
                else:
                    part[1] += ring[0]
        for part in puzzle_parts:
            if part[2]==0: continue
            part[1] = int(auto_color_parts[ part[1]-1 ])
    else:
        mm = 0
        for ring in puzzle_rings:
            if ring[6] != 0: continue
            part_mas, _ = find_parts_in_circle(ring, puzzle_parts, 2)
            for part in part_mas:
                if part[2]==0: continue
                if mm >= len(auto_color_parts): break
                add_color_ind = int(auto_color_parts[ mm ])
                if part[1]==0:
                    part[1] = add_color_ind
                else:
                    new_color = get_color(PARTS_COLOR[part[1]], PARTS_COLOR[add_color_ind])
                    new_color_ind = -1
                    for nn,color in enumerate(PARTS_COLOR):
                        if color == new_color:
                            new_color_ind = nn
                            break
                    if new_color_ind == -1:
                        PARTS_COLOR.append(new_color)
                        new_color_ind = len(PARTS_COLOR)-1
                    part[1] = new_color_ind
            mm += 1

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
            if part[2]==0: continue
            part[1] = color

def set_marker_all_parts(puzzle_parts, set_marker_parts, puzzle_scale):
    # установка маркеров на всех заданных частях
    for marker in set_marker_parts:
        if typeof(marker) != "list": continue
        if not 2<=len(marker)<=6: continue

        part = find_element(int(marker[0]), puzzle_parts)
        marker_text = marker[1]
        if marker_text.find("\\n")>=0:
            marker_text = marker_text.replace("\\n","\n")

        marker_part = [ marker_text,0,0,0,0,"" ]
        if len(marker)>=3:
            marker_part[1] = float(marker[2])
        if len(marker)>=4:
            marker_part[2] = int(float(marker[3])*puzzle_scale)
        if len(marker)>=5:
            marker_part[3] = int(marker[4])
        if len(marker)>=6:
            marker_part[4] = int(marker[5])

        part[3] = marker_part

def calc_all_centroids(puzzle_parts):
    for part in puzzle_parts:
        center_x, center_y = calc_centroid(part[7])
        area = calc_area_polygon(part[7])
        part[4] = [center_x, center_y, area]

def find_angle_rotate(ring,direction,freeze=False):
    # найдем следующий угол поворота в некратных кругах
    angle_mas, angle_pos = ring[4], ring[5]
    if typeof(angle_mas) == "list":
        if direction>0:
            angle_rotate = angle_mas[angle_pos]
            angle_pos += direction
            angle_pos = 0 if angle_pos == len(angle_mas) else angle_pos if angle_pos >= 0 else len(angle_mas) - 1
        else:
            angle_pos += direction
            angle_pos = 0 if angle_pos == len(angle_mas) else angle_pos if angle_pos >= 0 else len(angle_mas) - 1
            angle_rotate = angle_mas[angle_pos]
        if not freeze:
            ring[5] = angle_pos
    else:
        angle_rotate = angle_mas
    return angle_rotate

def turn_ring_and_cut(num_ring, direction, step, puzzle_rings, puzzle_arch, puzzle_parts):
    # повернуть все части внутри круга и запустить нарезку всех пресечений с остальными кругами
    ring1 = find_element(num_ring, puzzle_rings)
    part_mas, _ = find_parts_in_circle(ring1, puzzle_parts, 1)

    if typeof(ring1[4])=="list" and step>1:
        for _ in range(step):
            angle_deg = find_angle_rotate(ring1, direction)
            angle = radians(angle_deg)
            rotate_part(ring1, part_mas, puzzle_arch, angle, -direction)
    else:
        angle_deg = find_angle_rotate(ring1, direction)
        angle = radians(angle_deg)
        rotate_part(ring1, part_mas, puzzle_arch, angle*step, -direction)  # разворачиваем direction, тк центр координат вверху
    calc_parts_countur(puzzle_parts, puzzle_arch, True)

    for mm, ring2 in enumerate(puzzle_rings):
        if num_ring == ring2[0]: continue
        if calc_length(ring1[1], ring1[2], ring2[1], ring2[2]) >= ring1[3] + ring2[3]: continue

        cut_parts_in_ring(ring2, puzzle_arch, puzzle_parts)
        calc_parts_countur(puzzle_parts, puzzle_arch, True)

def remove_def_parts(puzzle_parts, remove_parts):
    # удаление заданных частей
    for rem in remove_parts:
        pos = -1
        for nn,part in enumerate(puzzle_parts):
            if part[0]==int(rem):
                puzzle_parts.pop(nn)
                break

def remove_micro_parts(puzzle_parts, area_param):
    # удаление заданных частей
    rem_parts = []
    for part in puzzle_parts:
        polygon = part[6]
        area = calc_area_polygon(polygon)
        if area<=float(area_param[0]):
            rem_parts.append(part[0])

    for rem in rem_parts:
        pos = -1
        for nn,part in enumerate(puzzle_parts):
            if part[0]==rem:
                puzzle_parts.pop(nn)
                break

def hide_show_def_parts(puzzle_parts, hide_parts, flag, all=False):
    # скрываем заданные части
    if not all:
        for hide in hide_parts:
            if hide=="":continue
            part = find_element(int(hide),puzzle_parts)
            part[2] = 1 if flag > 0 else 0
    else:
        for part in puzzle_parts:
            if flag==0:
                part[2] = 1-part[2]
            else:
                part[2] = 1 if flag > 0 else 0

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
                part_num_new = max(puzzle_parts, key=lambda i: i[0])[0] + 1
                part_new = copy.deepcopy(part)
                part_new[0] = part_num_new
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
                rotate_part(ring, part_mas, puzzle_arch, angle, -direction)  # разворачиваем direction, тк центр координат вверху
                pos+=1
            else:
                num_ring, direction, step = get_command(turn)
                if num_ring == 0: continue

                ring = find_element(num_ring, puzzle_rings)
                if typeof(ring[4]) == "list" and step > 1:
                    for _ in range(step):
                        angle_deg = find_angle_rotate(ring, direction,True)
                        angle = radians(angle_deg)
                        rotate_part(ring, part_mas, puzzle_arch, angle, -direction)
                else:
                    angle_deg = find_angle_rotate(ring, direction,True)
                    angle = radians(angle_deg)
                    rotate_part(ring, part_mas, puzzle_arch, angle * step, -direction)  # разворачиваем direction, тк центр координат вверху
            pos += 1
            calc_parts_countur(puzzle_parts, puzzle_arch, True)

        copy_parts.pop(0)
        copy_parts.pop(0)

def sort_and_renum_all_parts(puzzle_parts):
    # сортировка и перенумеровка частей
    part_mas = []
    for nn, part in enumerate(puzzle_parts):
        center_x, center_y = calc_centroid(part[6])
        part_mas.append( [round(center_x,1), round(center_y,1), part] )
    part_mas.sort(key=lambda part: (-part[1], part[0]))
    for nn, part_cent in enumerate(part_mas):
        part_cent[2][0] = nn+1
    puzzle_parts.sort(key=lambda part: (part[0]))

def remove_dublikate_parts(puzzle_parts):
    # найти и удалить дублирующиеся части
    part_dub = []
    for nn,part1 in enumerate(puzzle_parts):
        for mm, part2 in enumerate(puzzle_parts[nn+1:]):
            if len(part1[5])!=len(part2[5]): continue # разная длина

            # нужно сверить все дуги частей независимо от старта и направления
            pos1, pos2, direction = 0, -1, 1
            part_arc1 = part1[5][pos1]
            for pp,part_arc2 in enumerate(part2[5]):
                if part_arc1[0]==part_arc2[0] and part_arc1[1]==part_arc2[1] and part_arc1[2]==part_arc2[2] and compare_xy(part_arc1[3],part_arc2[3],3) and compare_xy(part_arc1[4],part_arc2[4],3) :
                    pos2 = pp
                    break
                if compare_xy(part_arc1[3],part_arc2[3],3) and compare_xy(part_arc1[4],part_arc2[4],3):
                    part_arc2next = mas_pos(part2[5], pp-1)
                    if part_arc1[0]==part_arc2next[0] and part_arc1[1]==part_arc2next[1] and part_arc1[2]==(-part_arc2next[2]):
                        pos2 = pp
                        direction = -1
                        break
            if pos2 < 0: continue # нет стартовой вершины

            equal = True
            for pp, part_arc1 in enumerate(part1[5]):
                part_arc2 = mas_pos(part2[5], pos2+direction*pp)
                if direction>0:
                    if part_arc1[0]==part_arc2[0] and part_arc1[1]==part_arc2[1] and part_arc1[2]==part_arc2[2] and compare_xy(part_arc1[3],part_arc2[3],3) and compare_xy(part_arc1[4],part_arc2[4],3):
                        continue
                else:
                    if compare_xy(part_arc1[3],part_arc2[3],3) and compare_xy(part_arc1[4],part_arc2[4],3):
                        part_arc2next = mas_pos(part2[5], pos2+direction*pp-1)
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

def copy_ring(ring_num,turn_command,puzzle_rings):
    ring_source = find_element(ring_num, puzzle_rings)
    center_x, center_y = ring_source[1],ring_source[2]

    if typeof(turn_command) == "list":
        if len(turn_command)==2:
            num_ring_center = int(turn_command[0])
            ring_center = find_element(num_ring_center, puzzle_rings)
            direction = 1
            angle_deg = float(turn_command[1])
            angle = radians(angle_deg)
            center_x, center_y = rotate_point(ring_center[1], ring_center[2], center_x, center_y, angle *direction)  # разворачиваем direction, тк центр координат вверху
    else:
        num_ring_center, direction, step = get_command(turn_command)
        if num_ring_center != 0:
            ring_center = find_element(num_ring_center, puzzle_rings)
            angle_deg = find_angle_rotate(ring_center, direction)
            angle = radians(angle_deg)
            center_x, center_y = rotate_point(ring_center[1], ring_center[2], center_x, center_y, angle*step *direction)

    return center_x, center_y

def find_arch(puzzle_arch, ring):
    for arch in puzzle_arch:
        if compare_xy(arch[1],ring[1],8) and compare_xy(arch[2],ring[2],8) and compare_xy(arch[3],ring[3],8):
            return arch[0]
    return -1

def cut_def_circles(puzzle_rings, puzzle_arch, puzzle_parts, cut_circles):
    for nn,num_ring in enumerate(cut_circles):
        num_ring = int(num_ring)
        ring1 = find_element(num_ring, puzzle_rings)
        cut_parts_in_ring(ring1, puzzle_arch, puzzle_parts)
        calc_parts_countur(puzzle_parts, puzzle_arch, True)
    remove_dublikate_parts(puzzle_parts)
    sort_and_renum_all_parts(puzzle_parts)

def make_def_circles(puzzle_rings, puzzle_arch, puzzle_parts, make_circles):
    for ring_num in make_circles:
        ring = find_element(int(ring_num),puzzle_rings)

        arch_num = find_arch(puzzle_arch, ring)
        if arch_num < 0:
            arch_num = len(puzzle_arch)
            arch = [arch_num, ring[1], ring[2], ring[3]]
            puzzle_arch.append(arch)

        if ring[6] != 0: continue

        color = ring[0] + 2
        part_arch = [arch_num, 0, 1, ring[1], ring[2] + ring[3], 0, 0]
        part = [len(puzzle_parts)+1, color, 1, [], [], [part_arch], [], []]
        puzzle_parts.append(part)

    calc_parts_countur(puzzle_parts, puzzle_arch, True)

def rotate_all_parts(puzzle_rings, puzzle_arch, puzzle_parts, rotate_parts_param):
    center_x,center_y,angle_deg = float(rotate_parts_param[0]),float(rotate_parts_param[1]),float(rotate_parts_param[2])
    angle = -radians(angle_deg)

    for ring in puzzle_rings:
        ring[1],ring[2] = rotate_point(center_x,center_y, ring[1],ring[2], -angle) # разворачиваем direction, тк центр координат вверху
    for arch in puzzle_arch:
        arch[1],arch[2] = rotate_point(center_x,center_y, arch[1],arch[2], -angle)
    for part in puzzle_parts:
        for part_arch in part[5]:
            part_arch[3], part_arch[4] = rotate_point(center_x,center_y, part_arch[3], part_arch[4], -angle)
        # if len(part[3])>0:
        #     part[3][1] += -angle_deg
        if len(part[4]) > 0:
            part[4][0], part[4][1] = rotate_point(center_x, center_y, part[4][0], part[4][1], -angle)

    calc_parts_countur(puzzle_parts, puzzle_arch, True)

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

def init_cut_all_ring_to_parts(puzzle_rings, puzzle_arch, puzzle_parts, auto_cut_parts, init=True):
    if init:
        # инициализируем круги и запускаем нарезку частей с помощью заданной или случайной последовательности

        # сформируем цельные круги
        make_circles = []
        for ring in puzzle_rings:
            make_circles.append(ring[0])
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
            count = 1
            if nn+1<len(auto_cut_parts):
                if is_number(auto_cut_parts[nn+1]):
                    count = int(auto_cut_parts[nn+1])

            if count==1:
                fl_one_ring = False
                for mm, turn_command in enumerate(cut_command):
                    if mm==0 and is_number(turn_command):
                        num_ring = int(turn_command)
                        ring = find_element(num_ring, puzzle_rings)
                        part_mas, _ = find_parts_in_circle(ring, puzzle_parts, 1)
                        angle_deg = float(cut_command[mm + 1])
                        direction = 1
                        angle = radians(angle_deg)
                        rotate_part(ring, part_mas, puzzle_arch, angle, -direction)  # разворачиваем direction, тк центр координат вверху
                        calc_parts_countur(puzzle_parts, puzzle_arch, True)
                        break

                    elif not is_number(turn_command):
                        num_ring, direction, step = get_command(turn_command)
                        if num_ring == 0: continue

                        # повернуть все части внутри круга
                        ring1 = find_element(num_ring, puzzle_rings)
                        part_mas, _ = find_parts_in_circle(ring1, puzzle_parts, 1)
                        if typeof(ring1[4]) == "list" and step > 1:
                            for _ in range(step):
                                angle_deg = find_angle_rotate(ring1, direction)
                                angle = radians(angle_deg)
                                rotate_part(ring1, part_mas, puzzle_arch, angle, -direction)  # разворачиваем direction, тк центр координат вверху
                        else:
                            angle_deg = find_angle_rotate(ring1, direction)
                            angle = radians(angle_deg)
                            rotate_part(ring1, part_mas, puzzle_arch, angle * step, -direction)  # разворачиваем direction, тк центр координат вверху
                        calc_parts_countur(puzzle_parts, puzzle_arch, True)
                    else:
                        # запустить нарезку с заданным кругом
                        num_ring = int(turn_command)
                        if num_ring!=0:
                            ring1 = find_element(num_ring, puzzle_rings)
                            cut_parts_in_ring(ring1, puzzle_arch, puzzle_parts)
                            calc_parts_countur(puzzle_parts, puzzle_arch, True)
                        fl_one_ring = True
                if not fl_one_ring:
                    for mm, ring2 in enumerate(puzzle_rings):
                        cut_parts_in_ring(ring2, puzzle_arch, puzzle_parts)
                        calc_parts_countur(puzzle_parts, puzzle_arch, True)
            else:
                for _ in range(count):
                    for mm, turn_command in enumerate(cut_command):
                        num_ring, direction, step = get_command(turn_command)
                        if num_ring == 0: continue
                        turn_ring_and_cut(num_ring, direction, step, puzzle_rings, puzzle_arch, puzzle_parts)

        else:
            num_ring, direction, step = get_command(cut_command)
            if num_ring==0: continue
            turn_ring_and_cut(num_ring, direction, step, puzzle_rings, puzzle_arch, puzzle_parts)

    # найти и удалить дублирующиеся части
    # sort_and_renum_all_parts(puzzle_parts)
    remove_dublikate_parts(puzzle_parts)
    sort_and_renum_all_parts(puzzle_parts)

    calc_parts_countur(puzzle_parts, puzzle_arch)

def find_incorrect_parts(puzzle_parts, puzzle_arch):
    calc_parts_countur(puzzle_parts, puzzle_arch)

    # поиск накладывающихся друг на друга кусочков
    for nn,part1 in enumerate(puzzle_parts):
        count_in = count_out = 0
        for mm, part2 in enumerate(puzzle_parts[nn+1:]):
            for x,y in part1[6]:
                fl_pol, _ = check_polygon(part2[7], x, y)
                if count_in:
                    count_in += 1
                else:
                    count_out += 1
                if count_in>0 and count_out>0:
                    break



