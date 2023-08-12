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
    # поиск элемента массива по номеру
    for elem in mas:
        if elem[0] == pos:
            return elem
    return ""

def mas_pos(mas_xy, pos):
    ll = len(mas_xy)
    if pos >= ll:
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
    t = 0
    for count in range(len(polygon) - 1):
        y = polygon[count + 1][1] + polygon[count][1]
        x = polygon[count + 1][0] - polygon[count][0]
        z = y * x
        t += z
    return abs(t / 2.0)

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

def check_circle(center_x, center_y, x, y, rad):
    # проверка попадает ли точка внутрь окружности
    length = calc_length(center_x, center_y, x, y)
    return (length<=rad, length/rad)

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
        return inter

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
        return inter
