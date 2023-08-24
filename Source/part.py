import copy
from pygame import display

from calc import *
from syst import *
import random

# puzzle_rings, puzzle_arch, puzzle_parts - формат массивов:

# puzzle_rings - [ring_num, center_x, center_y, radius, angle_deg, _ , type]
#              - [ring_num, center_x, center_y, radius, (angle_deg1,angle_deg2,...), jumble_angle_pos, type] - angle_deg1+angle_deg2+..=360 deg, jumble_angle_pos = 0,1,..
#              для головоломок с некратными углами, в параметре Angle массив углов, а также позиция текущего угла поворота всего круга.
#              type - 0 это стандартный кольца, 1 это вспомогательные кольца для нарезки, собственных частей не имеют, как контуры не отображаем

# puzzle_arch  - [arch_num, center_x, center_y, radius]
#              первые арки полностью совпадают с кольцами. дальше идут вторичные арки которые формируют части

# puzzle_parts - [part_num, color_index, [mas_arch], [mas_spline], [mas_polygon]]
#       mas_arch - [ [part_arch1],[part_arch2],.. ]
#            part_arch - [arch_num, direction, start_x, start_y, [arch_spline] ]
#                 arch_spline - [ [x0,y0],[x1,y1],..,[xm,ym] ] - сплайн для отрисовки одной линии
#       mas_spline - [ [x0,y0],[x1,y1],..,[xm,ym] ] - плавный сплайн для отрисовки контура фигуры
#       mas_polygon - [ [x0,y0],..,[xn,yn] ] - сокращенный полигон (несколько точек из дуги) для быстрых проверок пересечений

def rotate_part(ring, part_mas, puzzle_arch, angle, direction):
    # поворот всех частей из массива относительно центра круга
    for part in part_mas:
        for part_arch in part[2]:
            part_arch[2], part_arch[3] = rotate_point(ring[1], ring[2], part_arch[2], part_arch[3], angle*-direction) # разворачиваем direction, тк центр координат вверху

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
                angle1, grad1 = calc_angle(arch_x, arch_y, x1, y1, arch_r)
                angle3, grad3 = calc_angle(arch_x, arch_y, x3, y3, arch_r)

                if (angle1 < angle3 and direction == 1) or (angle1 > angle3 and direction == -1):
                    angle2, grad2 = (angle1 + angle3 - 2 * pi) / 2, (grad1 + grad3 - 360) / 2
                else:
                    angle2, grad2 = (angle1 + angle3) / 2, (grad1 + grad3) / 2

                angle_cos, angle_sin = cos(angle2), sin(angle2)
                x2, y2 = angle_cos * arch_r + arch_x, angle_sin * arch_r + arch_y

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

def find_incorrect_parts(puzzle_parts, puzzle_arch):
    # поиск накладывающихся друг на друга кусочков
    pass
    # for nn,part1 in enumerate(puzzle_parts):
    #     for mm, part2 in enumerate(puzzle_parts[nn+1:]):
    #
    #         for na, part_arch1 in enumerate(part1[2]):
    #             part_arch_next1 = find_part_arch_next(part1, nn)
    #
    #             for ma, part_arch2 in enumerate(part2[2]):
    #                 arch1,arch2 = find_element(part_arch1,puzzle_arch), find_element(part_arch2,puzzle_arch)
    #                 intersect = circles_intersect(arch1[1], arch1[2], arch1[3], arch2[1], arch2[2], arch2[3])
    #                 if len(intersect)==2:
    #                     if (part_arch1[2]!=intersect[0][0] and part_arch1[3]!=intersect[0][1]) and (part_arch_next1[2]!=intersect[0][0] and part_arch_next1[3]!=intersect[0][1])
    #                         check_point_in_arch(p2x, p2y, p1x, p1y, ax, ay, cx, cy, anti)
    #         pass

def find_part_arch_next(part,nn):
    # возвращает следующую дугу у части по индексу
    if len(part[2]) == 1:
        part_arch_next = part[2][nn]
    elif nn == len(part[2]) - 1:
        part_arch_next = part[2][0]
    else:
        part_arch_next = part[2][nn + 1]
    return part_arch_next

def calc_parts_countur(puzzle_parts,puzzle_arch,short_only=False):
    # расчет всех контуров-сплайнов для всех частей
    for part in puzzle_parts:
        mas_full_xy, mas_short_xy = [], []

        for nn, part_arch in enumerate(part[2]):
            arch = find_element(part_arch[0], puzzle_arch)
            arch_x, arch_y, arch_r = arch[1], arch[2], arch[3]

            direction = part_arch[1]

            part_arch_next = find_part_arch_next(part, nn)
            arch_mas = [[part_arch[2], part_arch[3]], [part_arch_next[2], part_arch_next[3]]]

            if not short_only:
                mas_xy,fl_error = calc_arch_spline(arch_mas, arch_x, arch_y, arch_r, direction)
                if fl_error:
                    print("Error: "+str(part[0])+", "+str(part_arch[0]))
                if len(part_arch)>=5:
                    part_arch[4] = mas_xy
                else:
                    part_arch.append(mas_xy)
                mas_full_xy += mas_xy
                mas_full_xy.pop()

            if len(part[2])==1: # это окружность?
                mas_xy,fl_error = calc_arch_spline(arch_mas, arch_x, arch_y, arch_r, direction, 4)
            else:
                mas_xy,fl_error = calc_arch_spline(arch_mas, arch_x, arch_y, arch_r, direction, 2)
            mas_short_xy += mas_xy
            mas_short_xy.pop()

        if len(part)>=4:
            part[3], part[4] = mas_full_xy, mas_short_xy
        else:
            part.append(mas_full_xy)
            part.append(mas_short_xy)

def check_point_in_arch(p1x, p1y, p2x, p2y, ax, ay, cx, cy, anti):
    # проверяет попадает ли точка внутрь дуги
    x1, y1 = p1x - cx, p1y - cy
    x2, y2 = p2x - cx, p2y - cy
    xa, ya = ax - cx, ay - cy
    if anti==-1:
        x1, y1, x2, y2 = x2, y2, x1, y1

    rad = calc_length(0, 0, xa, ya)
    ang1, ang1deg = calc_angle(0,0, x1,y1, rad)
    ang2, ang2deg = calc_angle(0,0, x2,y2, rad)
    anga, angadeg = calc_angle(0,0, xa,ya, rad)

    delta, deltadeg = ang2, ang2deg
    ang1, ang1deg = ang1-delta, ang1deg-deltadeg
    ang2, ang2deg = ang2-delta, ang2deg-deltadeg
    anga, angadeg = anga-delta, angadeg-deltadeg

    if ang1<0: ang1, ang1deg = ang1+2*pi, ang1deg+360
    if anga<0: anga, angadeg = anga+2*pi, angadeg+360

    if anga>=ang2 and anga<=ang1: return True

    return False

def find_angle_direction(p2x, p2y, p1x, p1y, cx, cy):
    # возвращает направление движения дуги. по часовой или против часовой стрелки. для углов <= 180гр
    x1, y1 = p1x - cx, p1y - cy
    x2, y2 = p2x - cx, p2y - cy
    s12 = sign(x1 * y2 - y1 * x2)
    return 1 if s12>=0 else -1

def find_parts_in_circle(ring, puzzle_parts, mode=0):
    # найдем все части соотносящиеся с кругом, в зависимости от режима выборки
    # mode : 0 - все части в круге, нет пересечений с кругом, 1 - только части внутри круга,
    # 2 - части совпадающие с кругом (все внутри и те что пересекают), 3 - только части пересекающие круг

    part_mas, part_mas_other = [], []
    for part in puzzle_parts:
        fl_part = -1  # 0 - часть за пределами круга, 1 - часть внутри, 2 часть пересекает круг, 3 часть совпадает с кругом (все точки касательные)
        for part_point in part[4]:
            pos = check_circle(ring[1], ring[2], part_point[0], part_point[1], ring[3])
            if compare_xy(pos[1], 1, 2):
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
    part_mas_other, _ = find_parts_in_circle(ring, puzzle_parts, 1)

    for part in part_mas:
        if part[1]<0: continue
        cut_point = []
        for nn, part_arch in enumerate(part[2]):
            part_arch_next = find_part_arch_next(part, nn)
            arch = find_element(part_arch[0], puzzle_arch)
            intersect = circles_intersect(ring[1], ring[2], ring[3], arch[1], arch[2], arch[3])

            if len(part[2])==1: # цельная окружность
                fl1, fl2 = True, True
            elif len(intersect) == 0:
                continue
            elif len(intersect) == 2:
                if (part_arch[2] == intersect[0][0] and part_arch[3] == intersect[0][1]) or (part_arch[2] == intersect[1][0] and part_arch[3] == intersect[1][1]):
                    if (part_arch_next[2] == intersect[0][0] and part_arch_next[3] == intersect[0][1]):
                        cut_point.append([ring[0], nn, intersect[0][0], intersect[0][1], len(intersect) == 2, True])
                    elif (part_arch_next[2] == intersect[1][0] and part_arch_next[3] == intersect[1][1]):
                        cut_point.append([ring[0], nn, intersect[1][0], intersect[1][1], len(intersect) == 2, True])
                    continue
                fl1 = check_point_in_arch(part_arch[2], part_arch[3], part_arch_next[2], part_arch_next[3], intersect[0][0], intersect[0][1], arch[1], arch[2], part_arch[1])
                fl2 = check_point_in_arch(part_arch[2], part_arch[3], part_arch_next[2], part_arch_next[3], intersect[1][0], intersect[1][1], arch[1], arch[2], part_arch[1])
            elif len(intersect) == 1:
                if (part_arch[2] == intersect[0][0] and part_arch[3] == intersect[0][1]):
                    continue
                fl1 = check_point_in_arch(part_arch[2], part_arch[3], part_arch_next[2], part_arch_next[3], intersect[0][0], intersect[0][1], arch[1], arch[2], part_arch[1])
                fl2 = False

            if fl1:
                fl_corner = True if (part_arch_next[2] == intersect[0][0] and part_arch_next[3] == intersect[0][1]) else False
                cut_point.append([ring[0], nn, intersect[0][0], intersect[0][1], len(intersect) == 2, fl_corner])
            if fl2:
                fl_corner = True if (part_arch_next[2] == intersect[1][0] and part_arch_next[3] == intersect[1][1]) else False
                cut_point.append([ring[0], nn, intersect[1][0], intersect[1][1], len(intersect) == 2, fl_corner])
            if fl1 and fl2:
                if check_point_in_arch(part_arch[2], part_arch[3], cut_point[0][2], cut_point[0][3], cut_point[1][2], cut_point[1][3], arch[1], arch[2], part_arch[1]):
                    cut_point.append(cut_point[0])
                    cut_point.pop(0)

        if len(cut_point) == 2:
            part_num_new = max(puzzle_parts, key=lambda i: i[0])[0] + 1
            part1, part2 = [part[0], part[1], [], [], []], [part_num_new, part[1], [], [], []]
            # fl_part2 = True

            if len(part[2]) != 1:
                for nn, part_arch in enumerate(part[2]):
                    if nn <= cut_point[0][1]:
                        part1[2].append([part_arch[0], part_arch[1], part_arch[2], part_arch[3]])

                    if nn == cut_point[0][1]:
                        arch = find_element(cut_point[0][0], puzzle_arch)
                        direction = find_angle_direction(cut_point[0][2], cut_point[0][3], cut_point[1][2], cut_point[1][3], arch[1], arch[2])
                        part1[2].append([ring[0], direction, cut_point[0][2], cut_point[0][3]])
                        if not cut_point[0][5]:
                            part2[2].append([part_arch[0], part_arch[1], cut_point[0][2], cut_point[0][3]])

                    if nn > cut_point[0][1] and nn <= cut_point[1][1]:
                        part2[2].append([part_arch[0], part_arch[1], part_arch[2], part_arch[3]])
                    if nn == cut_point[1][1]:
                        arch = find_element(cut_point[1][0], puzzle_arch)
                        direction = find_angle_direction(cut_point[0][2], cut_point[0][3], cut_point[1][2], cut_point[1][3], arch[1], arch[2])
                        part2[2].append([ring[0], -direction, cut_point[1][2], cut_point[1][3]])
                        if not cut_point[1][5]:
                            part1[2].append([part_arch[0], part_arch[1], cut_point[1][2], cut_point[1][3]])
                    if nn > cut_point[1][1]:
                        part1[2].append([part_arch[0], part_arch[1], part_arch[2], part_arch[3]])
            else:
                # цельная окружность
                part_arch = part[2][0]
                arch = find_element(part_arch[0],puzzle_arch)

                direction = find_angle_direction(cut_point[0][2], cut_point[0][3], cut_point[1][2], cut_point[1][3], arch[1], arch[2])

                part1[2].append([part_arch[0], direction, cut_point[1][2], cut_point[1][3]])
                part1[2].append([ring[0], -direction, cut_point[0][2], cut_point[0][3]])

                if direction>0:
                    part2[2].append([ring[0], 1, cut_point[1][2], cut_point[1][3]])
                    part2[2].append([part_arch[0], 1, cut_point[0][2], cut_point[0][3]])
                else:
                    part2[2].append([ring[0], 1, cut_point[0][2], cut_point[0][3]])
                    part2[2].append([part_arch[0], 1, cut_point[1][2], cut_point[1][3]])
                # if len(part_mas_other) == 1:
                #     if len(part_mas_other[0][2]) == 1: # там цельная окружность
                #         fl_part2 = False

            for nn, part in enumerate(puzzle_parts):
                if part[0] == part1[0]:
                    puzzle_parts[nn] = part1
                    break
            puzzle_parts.append(part2)

def init_color_all_parts(puzzle_parts, puzzle_rings, auto_color_parts, PARTS_COLOR):
    # автоматическая раскраска всех частей со смешиванием цветов внутри пересечений
    for part in puzzle_parts:
        part[1]=0

    if len(auto_color_parts)>len_puzzle_rings(puzzle_rings):
        for ring in puzzle_rings:
            if ring[6] != 0: continue
            part_mas, _ = find_parts_in_circle(ring, puzzle_parts, 2)
            for part in part_mas:
                if part[1]==0:
                    part[1] = ring[0]
                elif part[1]<len_puzzle_rings(puzzle_rings):
                    part[1] += ring[0] + len_puzzle_rings(puzzle_rings)-2
                else:
                    part[1] += ring[0]
        for part in puzzle_parts:
            part[1] = int(auto_color_parts[ part[1]-1 ])
    else:
        for ring in puzzle_rings:
            if ring[6] != 0: continue
            part_mas, _ = find_parts_in_circle(ring, puzzle_parts, 2)
            for part in part_mas:
                if ring[0]-1 >= len(auto_color_parts): break
                add_color_ind = int(auto_color_parts[ ring[0]-1 ])
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
            part[1] = color

def find_angle_rotate(ring,direction,freeze=False):
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
        polygon = part[4]
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
            part[1] = abs(part[1])*flag
    else:
        for part in puzzle_parts:
            if flag==0:
                part[1] = -part[1]
            else:
                part[1] = abs(part[1])*flag

def copy_def_parts(copy_parts, puzzle_rings, puzzle_arch, puzzle_parts, move=False):
    # копирование заданных частей - по кругу заданным поворотом
    while len(copy_parts)>=1:
        parts_list = copy_parts[0]
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
                num_ring = int(turn[0])
                ring = find_element(num_ring, puzzle_rings)
                angle_deg = float(parts_turn[pos+1])
                direction = 1
                angle = radians(angle_deg)
                rotate_part(ring, part_mas, puzzle_arch, angle, -direction)  # разворачиваем direction, тк центр координат вверху
                pos+=1
            else:
                num_ring = int(turn[0])
                ring = find_element(num_ring, puzzle_rings)
                direction = 1 if turn[1].upper() == "R" else -1 if turn[1].upper() == "L" else 0
                if direction == 0: continue
                step = 1 if len(turn) < 3 else int(turn[2:])
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
        center_x, center_y = calc_centroid(part[4])
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
            if len(part1[2])!=len(part2[2]): continue # разная длина

            # нужно сверить все дуги частей независимо от старта и направления
            pos1, pos2, direction = 0, -1, 1
            part_arc1 = part1[2][pos1]
            for pp,part_arc2 in enumerate(part2[2]):
                if part_arc1[0]==part_arc2[0] and part_arc1[1]==part_arc2[1] and compare_xy(part_arc1[2],part_arc2[2],3) and compare_xy(part_arc1[3],part_arc2[3],3) :
                    pos2 = pp
                    break
                if compare_xy(part_arc1[2],part_arc2[2],3) and compare_xy(part_arc1[3],part_arc2[3],3):
                    part_arc2next = mas_pos(part2[2], pp-1)
                    if part_arc1[0]==part_arc2next[0] and part_arc1[1]==(-part_arc2next[1]):
                        pos2 = pp
                        direction = -1
                        break
            if pos2 < 0: continue # нет стартовой вершины

            equal = True
            for pp, part_arc1 in enumerate(part1[2]):
                part_arc2 = mas_pos(part2[2], pos2+direction*pp)
                if direction>0:
                    if part_arc1[0]==part_arc2[0] and part_arc1[1]==part_arc2[1] and compare_xy(part_arc1[2],part_arc2[2],3) and compare_xy(part_arc1[3],part_arc2[3],3):
                        continue
                else:
                    if compare_xy(part_arc1[2],part_arc2[2],3) and compare_xy(part_arc1[3],part_arc2[3],3):
                        part_arc2next = mas_pos(part2[2], pos2+direction*pp-1)
                        if part_arc1[0] == part_arc2next[0] and part_arc1[1] == (-part_arc2next[1]):
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

def init_cut_all_ring_to_parts(puzzle_rings, puzzle_arch, puzzle_parts, auto_cut_parts, init=True):
    if init:
        # инициализируем круги и запускаем нарезку частей с помощью заданной или случайной последовательности

        # сформируем цельные круги
        for ring in puzzle_rings:
            arch = [ring[0], ring[1], ring[2], ring[3]]
            puzzle_arch.append(arch)
            if ring[6] != 0: continue

            color = ring[0] + 2
            part_arch = [ring[0], 1, ring[1], ring[2] + ring[3]]
            part = [ring[0], color, [part_arch], [], []]
            puzzle_parts.append(part)

        calc_parts_countur(puzzle_parts, puzzle_arch, True)

        # первичное разбиение кругов на части.
        fl_cutting_circles = True
        if len(auto_cut_parts)>0:
            if typeof(auto_cut_parts[0])=="list":
                if auto_cut_parts[0][0]!="Random":
                    fl_cutting_circles = False

        if fl_cutting_circles:
            for mm, ring in enumerate(puzzle_rings):
                cut_parts_in_ring(ring, puzzle_arch, puzzle_parts)
                calc_parts_countur(puzzle_parts, puzzle_arch, True)

        # найти и удалить дублирующиеся части
        remove_dublikate_parts(puzzle_parts)

    # авторотация и разбиение на части
    for nn,cut_command in enumerate(auto_cut_parts):
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
                percent = int(100*nn/count)
                if percent%5==0:
                    try:
                        display.set_caption("Please wait! Loading ... "+str(percent+5)+"%")
                        display.update()
                    except: pass

                direction = random.choice([-1, 1])
                while True:
                    num_ring = random.randint(1, len_puzzle_rings(puzzle_rings))
                    if num_ring_pred == num_ring: continue
                    num_ring_pred = num_ring
                    break
                turn_ring_and_cut(num_ring, direction, 1, puzzle_rings, puzzle_arch, puzzle_parts)
        elif typeof(cut_command)=="list":
            fl_one_ring = False
            for mm, turn_command in enumerate(cut_command):
                if not is_number(turn_command):
                    if len(turn_command) < 2: continue
                    num_ring = int(turn_command[0])
                    direction = 1 if turn_command[1].upper() == "R" else -1 if turn_command[1].upper() == "L" else 0
                    if direction == 0: continue
                    step = 1 if len(turn_command) < 3 else int(turn_command[2:])

                    # повернуть все части внутри круга
                    ring1 = find_element(num_ring, puzzle_rings)
                    part_mas, _ = find_parts_in_circle(ring1, puzzle_parts, 1)
                    if typeof(ring1[4]) == "list" and step > 1:
                        for _ in range(step):
                            angle_deg = find_angle_rotate(ring1, direction)
                            angle = radians(angle_deg)
                            rotate_part(ring1, part_mas, puzzle_arch, angle, -direction)
                    else:
                        angle_deg = find_angle_rotate(ring1, direction)
                        angle = radians(angle_deg)
                        rotate_part(ring1, part_mas, puzzle_arch, angle * step, -direction)  # разворачиваем direction, тк центр координат вверху
                    calc_parts_countur(puzzle_parts, puzzle_arch, True)
                else:
                    # запустить нарезку с заданным кругом
                    num_ring = int(turn_command)
                    ring1 = find_element(num_ring, puzzle_rings)
                    cut_parts_in_ring(ring1, puzzle_arch, puzzle_parts)
                    calc_parts_countur(puzzle_parts, puzzle_arch, True)
                    fl_one_ring = True
            if not fl_one_ring:
                for mm, ring2 in enumerate(puzzle_rings):
                    cut_parts_in_ring(ring2, puzzle_arch, puzzle_parts)
                    calc_parts_countur(puzzle_parts, puzzle_arch, True)

        else:
            if len(cut_command)<2: continue
            num_ring = int(cut_command[0])
            direction = 1 if cut_command[1].upper()=="R" else -1 if cut_command[1].upper()=="L" else 0
            if direction==0: continue
            step = 1 if len(cut_command)<3 else int(cut_command[2:])

            turn_ring_and_cut(num_ring, direction, step, puzzle_rings, puzzle_arch, puzzle_parts)

    # найти и удалить дублирующиеся части
    remove_dublikate_parts(puzzle_parts)
    sort_and_renum_all_parts(puzzle_parts)

    calc_parts_countur(puzzle_parts, puzzle_arch)
