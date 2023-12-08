from math import pi, sqrt, cos, sin, tan, acos, asin, atan, exp, pow, radians

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
        if elem[0] == pos:
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

def check_polygon(polygon, x, y):
    # проверка попадает ли точка внутрь полигона
    center_x, center_y = calc_centroid(polygon)
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
    return (length<=rad, compare_xy(in_ring, 1, nn), in_ring)

def rotate_point(center_x, center_y, x, y, angle):
    # поворот точки относительно центра координат по часовой стрелке
    adjusted_x,adjusted_y = x - center_x, y - center_y
    cos_rad,sin_rad = cos(angle),sin(angle)
    qx = cos_rad * adjusted_x + sin_rad * adjusted_y
    qy = cos_rad * adjusted_y - sin_rad * adjusted_x
    qx, qy = center_x + qx, center_y + qy
    return round(qx,10), round(qy,10)

def circles_intersect(x1,y1,r1,x2,y2,r2):
    # возвращаем точки пересечения или точку касания двух окружностей
    if compare_xy(x1,x2,8) and compare_xy(y1,y2,8):
        return []

    inter = []
    x2,y2 = round(x2-x1,10),round(y2-y1,10)

    if y2 != 0:
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

    else:
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

    if len(inter)==2:
        length = calc_length(inter[0][0],inter[0][1],inter[1][0],inter[1][1])
        if compare_xy(length,0,4):
            inter.pop(1)

    return inter

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
