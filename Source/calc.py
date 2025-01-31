from math import pi, sqrt, cos, sin, tan, acos, asin, atan, exp, pow, radians, degrees, hypot

from syst import typeof

def compare_xy(x, y, rr):
    # сравнение двух величин, с учетом погрешности
    return round(abs(x - y), rr) <= 10**(-rr)

def sign(x):
    # знак числа. но близкое к нулю число, интерпретируется как ноль
    if x > 0:
        return 1
    elif compare_xy(x,0,8):
        return 0
    else:
        return -1

def find_element(pos, mas):
    # поиск элемента массива по номеру (индекс в первой ячейке)
    for elem in mas:
        if typeof(elem)=="list":
            if elem[0] == pos:
                return elem
        elif typeof(elem)=="dict":
            if elem["num"] == pos:
                return elem

    return ""

def mas_pos(mas_xy, pos):
    # получить элемент массива независимо от выхода индекса за границы
    ll = len(mas_xy)
    while pos >= ll:
        pos -= ll
    return mas_xy[pos]

def get_color(colorRGBA1, colorRGBA2):
    # смешиваем два цвета RGB
    alpha = 255 - ((255 - colorRGBA1[3]) * (255 - colorRGBA2[3]) / 255)
    # red   = (colorRGBA1[0] * (255 - colorRGBA2[3]) + colorRGBA2[0] * colorRGBA2[3]) / 255
    # green = (colorRGBA1[1] * (255 - colorRGBA2[3]) + colorRGBA2[1] * colorRGBA2[3]) / 255
    # blue  = (colorRGBA1[2] * (255 - colorRGBA2[3]) + colorRGBA2[2] * colorRGBA2[3]) / 255
    red   = round((1 - (1 - colorRGBA1[0] / 255) * (1 - colorRGBA2[0] / 255)) * 255);
    green = round((1 - (1 - colorRGBA1[1] / 255) * (1 - colorRGBA2[1] / 255)) * 255);
    blue  = round((1 - (1 - colorRGBA1[2] / 255) * (1 - colorRGBA2[2] / 255)) * 255);
    return (int(red), int(green), int(blue), int(alpha))

def calc_length(x1, y1, x2, y2):
    # длина отрезка
    x, y = x2 - x1, y2 - y1
    return sqrt(x*x + y*y)

def calc_angle(center_x, center_y, x, y, rad=0):
    # угол поворота вектора относительно центра окружности
    x, y = x - center_x, y - center_y
    if rad == 0: rad = calc_length(0, 0, x, y)
    if rad == 0: return 0,0

    cos = round(x / rad, 8)
    if -1 <= cos <= 1:
        angle = acos(round(cos, 10))
        grad = angle * 180 / pi
        if y < 0:
            grad = 360 - grad
            angle = 2 * pi - angle
    else:
        angle = grad = 0
    return angle, round(grad, 8)

def calc_len_polygon(polygon):
    # длина периметра полигона
    len_line = 0
    for nn in range(len(polygon) - 1):
        len_line += calc_length(polygon[nn][0], polygon[nn][1], polygon[nn + 1][0], polygon[nn + 1][1])
    return len_line

def calc_area_polygon(polygon):
    # вычисление площади полигона
    area = 0
    for count in range(-1, len(polygon) - 1):
        y = polygon[count + 1][1] + polygon[count][1]
        x = polygon[count + 1][0] - polygon[count][0]
        area += y * x / 2
    return abs(area)

def calc_max_radius(polygon, center_x, center_y):
    # найдем расстояние до максимально удаленной точки от центроида полигона
    max_radius = 0
    for x,y in polygon:
        length = calc_length(x,y, center_x, center_y)
        max_radius = max(max_radius,length)
    return max_radius

def calc_centroid(polygon):
    # поиск координат центроида полигона
    x, y = 0, 0
    n = len(polygon)
    signed_area = 0
    for i in range(n):
        x0, y0 = polygon[i][0], polygon[i][1]
        x1, y1 = polygon[(i + 1) % n][0], polygon[(i + 1) % n][1]

        area = (x0 * y1) - (x1 * y0)
        signed_area += area
        x += (x0 + x1) * area
        y += (y0 + y1) * area
    signed_area *= 0.5
    if signed_area!=0:
        x /= 6 * signed_area
        y /= 6 * signed_area
    return x, y

def check_polygon(polygon, centroid, x, y):
    # проверка попадает ли точка внутрь полигона
    if len(centroid):
        center_x, center_y = calc_centroid(polygon)
    else:
        center_x, center_y = centroid["center_x"], centroid["center_y"]
    length = calc_length(center_x, center_y, x, y)

    odd = False
    i,j = 0,len(polygon)-1
    while i < len(polygon)-1:
        i += 1
        if (((polygon[i][1]>y) != (polygon[j][1]>y)) and (x<( (polygon[j][0] - polygon[i][0]) * (y-polygon[i][1]) / (polygon[j][1] - polygon[i][1])) + polygon[i][0])):
            odd = not odd
        j = i
    return odd, length

def check_line(x1, y1, x2, y2, center_x, center_y):
    return compare_xy( (center_y-y1)*(x2-x1), (center_x-x1)*(y2-y1), 4)

def check_circle(center_x, center_y, x, y, rad, nn=2):
    # проверка попадает ли точка внутрь окружности, лежит ли она на окружности с небольшой погрешностью
    length = calc_length(center_x, center_y, x, y)
    in_ring = length/rad if rad != 0 else 0

    result = dict(in_circle=length<=rad, on_ring=compare_xy(in_ring, 1, nn), proporce_cent=in_ring, distance_ring=abs(rad-length))
    return result
    # return (length<=rad, compare_xy(in_ring, 1, nn), in_ring, abs(rad-length))

def rotate_point(x, y, center_x, center_y, angle):
    # поворот точки относительно центра координат по часовой стрелке
    adjusted_x, adjusted_y = x - center_x, y - center_y
    cos_rad, sin_rad = cos(angle), sin(angle)
    qx = cos_rad * adjusted_x + sin_rad * adjusted_y
    qy = cos_rad * adjusted_y - sin_rad * adjusted_x
    qx, qy = center_x + qx, center_y + qy
    qx, qy = round(qx, 10), round(qy, 10)
    return qx, qy

    ## puzzle_points - [x, y, [mas_new_coordinate]]
    ##      mas_new_coordinate - [center_x, center_y, angle, rotated_x, rotated_y]
    ##      кэш новых координат точек после поворота. у одной точки могут быть несколько новых позиций
    ##      (как выяснил кэширование работает медленнее, чем просто расчет тригонометрии - отключил)

    # # сначала поищем точку в кэше - как выяснил кэширование работает медленнее, чем просто расчет тригонометрии
    # # puzzle_points - [x, y, [center_x, center_y, angle, rotated_x, rotated_y]]
    #
    # def binary_search(mas_points, x, y):
    #     low, mid, high = 0, 0, len(mas_points) - 1
    #
    #     while low <= high:
    #         mid = (high + low) // 2
    #         point = mas_points[mid]
    #
    #         if compare_xy(x, point[0], 8):
    #             if compare_xy(y, point[1], 8):
    #                 return mid, mid
    #             elif point[1] < y:
    #                 low = mid + 1
    #             elif point[1] > y:
    #                 high = mid - 1
    #         else:
    #             if point[0] < x:
    #                 low = mid + 1
    #             elif point[0] > x:
    #                 high = mid - 1
    #     return -1, mid
    #
    # def find_rotated_point(x, y, center_x, center_y, angle, puzzle_points):
    #     nn, pp = binary_search(puzzle_points, x, y)
    #     if nn >= 0:
    #         mm = 0
    #         mas_new_pos = puzzle_points[nn][2]
    #         for center_x2, center_y2, angle2, _, _ in mas_new_pos:
    #             if compare_xy(center_x, center_x2, 8) and compare_xy(center_y, center_y2, 8) and compare_xy(angle, angle2, 8):
    #                 return nn, mm, pp
    #             mm += 1
    #         return nn, -1, pp
    #     return -1, -1, pp
    #
    # if fl_find_point:
    #     pos,pos2,pos3 = find_rotated_point(x, y, center_x, center_y, angle, puzzle_points)
    # else:
    #     pos = pos2 = pos3 = -1
    #
    # if pos2 < 0:
    #     adjusted_x,adjusted_y = x - center_x, y - center_y
    #     cos_rad,sin_rad = cos(angle),sin(angle)
    #     qx = cos_rad * adjusted_x + sin_rad * adjusted_y
    #     qy = cos_rad * adjusted_y - sin_rad * adjusted_x
    #     qx, qy = center_x + qx, center_y + qy
    #     qx, qy = round(qx, 10), round(qy, 10)
    #
    #     if compare_xy(x,qx,8) and compare_xy(y,qy,8):
    #         pass
    #     elif fl_find_point:
    #         if pos < 0:
    #             if len(puzzle_points)==0:
    #                 puzzle_points.append([round(x, 10), round(y, 10), [[center_x, center_y, angle, qx, qy]]])
    #             else:
    #                 puzzle_points.insert(pos3,[round(x, 10), round(y, 10), [[center_x, center_y, angle, qx, qy]]])
    #             # puzzle_points.sort(key=lambda points: (points[0], points[1]))
    #         else:
    #             mas_new_pos = puzzle_points[pos][2]
    #             mas_new_pos.append([center_x, center_y, angle, qx, qy])
    # else:
    #     mas_new_pos = puzzle_points[pos][2]
    #     qx, qy = mas_new_pos[pos2][3],mas_new_pos[pos2][4]
    # return qx, qy

def mirror_point(x,y, mirror_line):
    # отзеркалим точку относительно линии
    line_start_x,line_start_y, line_end_x,line_end_y = mirror_line
    if compare_xy(line_start_x,line_end_x,8) and compare_xy(line_start_y,line_end_y,8):
        # вырожденный случай, вместо линии точка.
        mirror_point_x,mirror_point_y = line_start_x,line_start_y
    else:
        dx = line_end_x - line_start_x
        dy = line_end_y - line_start_y

        length_squared = dx*dx + dy*dy
        u = ((x - line_start_x) * dx + (y - line_start_y) * dy) / length_squared

        mirror_point_x = line_start_x + u * dx
        mirror_point_y = line_start_y + u * dy

    opposite_x = 2 * mirror_point_x - x
    opposite_y = 2 * mirror_point_y - y
    return opposite_x, opposite_y

def circle_line_intersect(x,y,r, px1,py1, px2,py2):
    # возвращаем точки пересечения или точку касания окружности и линии

    inter = []
    px1,py1 = round(px1-x,10),round(py1-y,10)
    px2,py2 = round(px2-x,10),round(py2-y,10)

    if compare_xy(px1, px2, 8): # вертикальная линия
        px = px1
        d = r*r - px*px

        if compare_xy(d,0,8): # касательная
            inter.append( (round(x+px,10),round(y,10)) )
            return inter
        if d < 0:
            return inter
        dd = sqrt(d)

        py = dd
        inter.append( (round(x+px,10),round(y+py,10)) )
        py = -dd
        inter.append( (round(x+px,10),round(y+py,10)) )

    else:
        m = (py2-py1)/(px2-px1)
        n = - (m*px1+py1)
        a,b,c = m*m+1, 2*m*n, n*n-r*r
        d = b*b-4*a*c

        if compare_xy(d,0,8):
            px = -b / (2*a)
            py = m*px+n
            inter.append( (round(x+px,10),round(y+py,10)) )
            return inter
        if d<0 :
            return inter
        dd = sqrt(d)

        px = (-b+dd) / (2*a)
        py = m*px+n
        inter.append( (round(x+px,10),round(y+py,10)) )
        px = (-b-dd) / (2*a)
        py = m*px+n
        inter.append( (round(x+px,10),round(y+py,10)) )

    return inter

def two_circles_intersect(x1,y1,r1,x2,y2,r2):
    # возвращаем точки пересечения или точку касания двух окружностей
    if compare_xy(x1,x2,8) and compare_xy(y1,y2,8):
        return []

    dist = calc_length(x1,y1,x2,y2)
    if not compare_xy(dist,r1+r2,8):
        if dist>(r1+r2): return []

    inter = []
    x2,y2 = round(x2-x1,10),round(y2-y1,10)

    if compare_xy(y2,0,8):
        x = (x2*x2-r2*r2+r1*r1)/(2*x2)
        d = r1*r1-x*x

        if compare_xy(d,0,8):
            y = 0
            inter.append( (round(x+x1,10),round(y+y1,10)) )
            return inter
        if d < 0:
            return inter
        dd = sqrt(d)

        y = dd
        inter.append( (round(x+x1,10),round(y+y1,10)) )
        y = -dd
        inter.append( (round(x+x1,10),round(y+y1,10)) )
    else:
        p = (x2*x2+y2*y2-r2*r2+r1*r1)/(2*y2)
        q = x2/y2
        k,m,n = q*q+1, -2*p*q, p*p-r1*r1
        d = m*m-4*k*n

        if compare_xy(d,0,8):
            x = -m / (2*k)
            y = p - q*x
            inter.append( (round(x+x1,10),round(y+y1,10)) )
            return inter
        if d<0 :
            return inter
        dd = sqrt(d)

        x = (-m+dd) / (2*k)
        y = p - q*x
        inter.append( (round(x+x1,10),round(y+y1,10)) )
        x = (-m-dd) / (2*k)
        y = p - q*x
        inter.append( (round(x+x1,10),round(y+y1,10)) )

    if len(inter)==2:
        length = calc_length(inter[0][0],inter[0][1],inter[1][0],inter[1][1])
        if compare_xy(length,0,4):
            inter.pop(1)

    return inter

def calc_arch_spline(arch_mas, arch_x, arch_y, arch_r, direction, max_iter = 0):
    # расчет всех точек сплайна для полигона. max_iter - дает возможность поcчитать только грубое приближение
    fl_error = False
    step = 0.7
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

def calc_center_arch(x1, y1, x3, y3, arch_x, arch_y, arch_r, direction=1):
    # найдем точку в центре дуги
    angle1, grad1 = calc_angle(arch_x, arch_y, x1, y1, arch_r)
    angle3, grad3 = calc_angle(arch_x, arch_y, x3, y3, arch_r)

    if (angle1 < angle3 and direction == 1) or (angle1 > angle3 and direction == -1):
        angle2, grad2 = (angle1 + angle3 - 2 * pi) / 2, (grad1 + grad3 - 360) / 2
    else:
        angle2, grad2 = (angle1 + angle3) / 2, (grad1 + grad3) / 2

    angle_cos, angle_sin = cos(angle2), sin(angle2)
    x2, y2 = angle_cos * arch_r + arch_x, angle_sin * arch_r + arch_y
    return x2, y2

def find_angle_direction(p2x, p2y, p1x, p1y, cx, cy):
    # возвращает направление движения дуги. по часовой или против часовой стрелки. для углов <= 180гр
    x1, y1 = p1x - cx, p1y - cy
    x2, y2 = p2x - cx, p2y - cy
    s12 = sign(x1 * y2 - y1 * x2)
    return 1 if s12>=0 else -1

def check_line_intersect(px1,py1, qx1,qy1, px2,py2, qx2,qy2):
    # https://www.geeksforgeeks.org/check-if-two-given-line-segments-intersect/
    # Основная функция, которая возвращает true, если отрезки «p1q1» и «p2q2» пересекаются.

    def on_segment(px,py, qx,qy, rx,ry):
        # функция проверяет, лежит ли точка q на отрезке 'pr'.
        if ((qx <= max(px, rx)) and (qx >= min(px, rx)) and (qy <= max(py, ry)) and (qy >= min(py, ry))):
            return True
        return False

    def orientation(px,py, qx,qy, rx,ry):
        # найти ориентацию упорядоченного триплета из точек (p,q,r). функция возвращает следующие значения:
        # 0 : Collinear points, 1 : Clockwise points, 2 : Counterclockwise
        val1 = float(qy-py)*(rx-qx)
        val2 = float(qx-px)*(ry-qy)
        if compare_xy(val1,val2, 8): # Collinear orientation
            return 0
        elif (val1 > val2): # Clockwise orientation
            return 1
        elif (val1 < val2): # Counterclockwise orientation
            return 2

    # Найти 4 ориентации, необходимые для общих и особых случаев.
    o1 = orientation(px1,py1, qx1,qy1, px2,py2)
    o2 = orientation(px1,py1, qx1,qy1, qx2,qy2)
    o3 = orientation(px2,py2, qx2,qy2, px1,py1)
    o4 = orientation(px2,py2, qx2,qy2, qx1,qy1)

    # общий случай - чистое пересечение
    if ((o1 != o2) and (o3 != o4)):
        return True

    # особые случаи - один конец отрезка лежит на другом отрезке

    # p1,q1 и p2 лежат на одной прямой, а p2 лежит на отрезке p1q1.
    if ((o1 == 0) and on_segment(px1,py1, px2,py2, qx1,qy1)): return True

    # q2 лежит на отрезке p1q1
    if ((o2 == 0) and on_segment(px1,py1, qx2,qy2, qx1,qy1)): return True

    # p1 лежит на отрезке p2q2
    if ((o3 == 0) and on_segment(px2,py2, px1,py1, qx2,qy2)): return True

    # q1 лежит на отрезке p2q2
    if ((o4 == 0) and on_segment(px2,py2, qx1,qy1, qx2,qy2)): return True

    return False

def calc_spline(input_mas, closed=True):
    def check_in_line(x1,y1,x2,y2,x,y):
        return compare_xy( (x-x1)*(y2-y1), (x2-x1)*(y-y1), -1 )

    def check_in_circle(x0,y0,x2,y2,x4,y4,x6,y6):
        # применим терему косинусов
        aa = calc_length(x2,y2, x4,y4)
        bb = calc_length(x2,y2, x0,y0)
        cc = calc_length(x4,y4, x0,y0)
        cosA1 = (bb*bb + cc*cc - aa*aa) / 2*bb*cc

        bb = calc_length(x2,y2, x6,y6)
        cc = calc_length(x4,y4, x6,y6)
        cosA2 = (bb*bb + cc*cc - aa*aa) / 2*bb*cc

        return compare_xy( cosA1, cosA2, -1 )

    def find_center_circle(x1, y1, x2, y2, x3, y3):
        if check_in_line(x1, y1, x2, y2, x3, y3):
            px, py, pr = (x1 + x3) / 2, (y1 + y3) / 2, 0
        else:
            c = (x1 - x2) ** 2 + (y1 - y2) ** 2
            a = (x2 - x3) ** 2 + (y2 - y3) ** 2
            b = (x3 - x1) ** 2 + (y3 - y1) ** 2
            s = 2 * (a * b + b * c + c * a) - (a * a + b * b + c * c)
            px = (a * (b + c - a) * x1 + b * (c + a - b) * x2 + c * (a + b - c) * x3) / s
            py = (a * (b + c - a) * y1 + b * (c + a - b) * y2 + c * (a + b - c) * y3) / s
            ar,br,cr = sqrt(a),sqrt(b),sqrt(c)
            pr = ar * br * cr / ((ar + br + cr) * (-ar + br + cr) * (ar - br + cr) * (ar + br - cr)) ** 0.5
        return px,py,pr

    step = 1
    input_xy = input_mas.copy()
    if closed:
        if input_xy[0][0]==input_xy[-1][0] and input_xy[0][1]==input_xy[-1][1]:
            input_xy.pop()

    fl_iter, iter = True, 0
    while fl_iter:
        fl_iter, iter = False, iter+1
        mas_xy, len_mas = [], len(input_xy)
        for nn in range(len_mas):
            mas_xy.append( [input_xy[nn][0],input_xy[nn][1]] )

            if not closed and (nn==0 or nn==len_mas-2):
                # построение начала и конца разомкнутой кривой
                if nn==0:
                    x0, y0 = mas_pos(input_xy,nn)
                    x2, y2 = mas_pos(input_xy,nn+1)
                    x4, y4 = mas_pos(input_xy,nn+2)
                else:
                    x0, y0 = mas_pos(input_xy, nn+1)
                    x2, y2 = mas_pos(input_xy, nn)
                    x4, y4 = mas_pos(input_xy, nn-1)

                len_vek = calc_length(x0,y0,x2,y2)
                if len_vek>step:
                    if check_in_line(x2,y2,x4,y4,x0,y0):
                        # если 4 точки на одной прямой линии, то найдем середину отрезка
                        x1,y1 = (x2 + x0)/2, (y2 + y0)/2
                    else:
                        x1,y1 = (x0*3 + x2*6 - x4)/8, (y0*3 + y2*6 - y4)/8
                    mas_xy.append( [x1,y1] )
                    fl_iter = True
            elif not closed and nn==len_mas-1:
                pass

            else: # построение центральной части замкнутой кривой
                x0,y0 = mas_pos(input_xy,nn-1)
                x2,y2 = mas_pos(input_xy,nn)
                x4,y4 = mas_pos(input_xy,nn+1)
                x6,y6 = mas_pos(input_xy,nn+2)

                len_vek = calc_length(x2,y2,x4,y4)
                if len_vek>step:
                    if check_in_line(x2,y2,x4,y4,x0,y0) and check_in_line(x2,y2,x4,y4,x6,y6):
                        # если 4 точки на одной прямой линии, то найдем середину отрезка
                        x3,y3 = (x2 + x4)/2, (y2 + y4)/2
                    elif ( check_in_line(x2, y2, x4, y4, x0, y0) or check_in_line(x2, y2, x4, y4, x6, y6) ) and iter<3:
                        # если 3 точки на одной прямой линии, и первые шаги итераций , то найдем середину отрезка
                        x3, y3 = (x2 + x4) / 2, (y2 + y4) / 2
                    elif check_in_circle(x0,y0,x2,y2,x4,y4,x6,y6):
                        xx1, yy1 = -(x0 - x2), -(y0 - y2)
                        xx2, yy2 = x4 - x2, y4 - y2
                        multiVec = xx1 * yy2 - xx2 * yy1
                        direction = 1 if multiVec < 0 else -1

                        # если 4 точки на одной окружности, то найдем середину дуги
                        px,py, pr = find_center_circle(x0,y0,x2,y2,x4,y4)

                        angle2, grad2 = calc_angle(px,py, x2,y2, pr)
                        angle4, grad4 = calc_angle(px,py, x4,y4, pr)

                        angle3, grad3 = (angle2 + angle4) / 2, (grad2 + grad4) / 2
                        if (angle2<angle4 and direction==1) or (angle2>angle4 and direction==-1):
                            angle3, grad3 = (angle2 + angle4 - 2*pi) / 2, (grad2 + grad4 - 360) / 2

                        angle_cos, angle_sin = cos(angle3), sin(angle3)
                        x3, y3 = angle_cos * pr + px, angle_sin * pr + py

                    else:
                        x3,y3 = (-x0 + x2*9 + x4*9 - x6)/16, (-y0 + y2*9 + y4*9 - y6)/16
                    mas_xy.append( [x3,y3] )
                    fl_iter = True

        input_xy = mas_xy.copy()
    return mas_xy

def calc_speed(puzzle_speed,angle_rotate,radius):
    if angle_rotate >= 270:
        p_speed = puzzle_speed * 8
    elif angle_rotate >= 180:
        p_speed = puzzle_speed * 6
    elif angle_rotate >= 130:
        p_speed = puzzle_speed * 5
    elif angle_rotate >= 90:
        p_speed = puzzle_speed * 4
    else:
        p_speed = puzzle_speed * 2

    if radius >= 1000:
        p_speed *= 7
    elif radius >= 800:
        p_speed *= 5
    elif radius >= 600:
        p_speed *= 4
    elif radius >= 500:
        p_speed *= 3.5
    elif radius >= 400:
        p_speed *= 3
    elif radius >= 300:
        p_speed *= 2.5
    elif radius >= 200:
        p_speed *= 2
    elif radius >= 100:
        p_speed *= 1.5

    return p_speed

# def calc_countur(input_xy, shift):
#     shift_xy1, shift_xy2, shift_x1, shift_y1, shift_x2, shift_y2, spline_sh1, spline_sh2 = [], [], [], [], [], [], [], []
#     shift_out, shift_in = shift + 5, shift + 2
#     for nn, pos_xy in enumerate(input_xy):
#         xx0, yy0 = pos_xy
#         if nn + 1 == len(input_xy):
#             xx_next, yy_next = input_xy[0]
#         else:
#             xx_next, yy_next = input_xy[nn + 1]
#         xx_pred, yy_pred = input_xy[nn - 1]
#
#         ang_next, grd_next = calc_angle(xx0, yy0, xx_next, yy_next)
#         ang_pred, grd_pred = calc_angle(xx0, yy0, xx_pred, yy_pred)
#
#         ang11, ang22, grd11, grd22 = (ang_next + ang_pred) / 2, pi + (ang_next + ang_pred) / 2, (grd_next + grd_pred) / 2, 180 + (grd_next + grd_pred) / 2
#
#         if ang_next > ang_pred:
#             ang22 -= 2 * pi
#             grd22 -= 360
#             ang11, ang22 = ang22, ang11
#             grd11, grd22 = grd22, grd11
#
#         sh_x1, sh_y1 = shift_in * cos(ang11) + xx0, shift_in * sin(ang11) + yy0
#         sh_x2, sh_y2 = shift_out * cos(ang22) + xx0, shift_in * sin(ang22) + yy0
#
#         shift_xy1.append((sh_x1, sh_y1))
#         shift_xy2.append((sh_x2, sh_y2))
#
#     spline_sh1, spline_sh2 = calc_spline(shift_xy1), calc_spline(shift_xy2)
#
#     center_x, center_y = centroid(input_xy)
#     spline_len1 = calc_len_polygon(shift_xy1)
#     spline_len2 = calc_len_polygon(shift_xy2)
#
#     if spline_len1 < spline_len2:
#         orbit_mas.append([nom, orbit_len, input_xy, spline_xy, spline_mas, shift_xy1, spline_sh1, shift_xy2, spline_sh2, (center_x, center_y)])
#     else:
#         orbit_mas.append([nom, orbit_len, input_xy, spline_xy, spline_mas, shift_xy2, spline_sh2, shift_xy1, spline_sh1, (center_x, center_y)])
