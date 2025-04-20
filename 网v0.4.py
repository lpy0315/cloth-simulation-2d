import sys
from math import pi, hypot

import numba
import pygame
from pygame.locals import *

if True:
    # os.environ['SDL_VIDEO_WINDOW_POS'] = "%d, %d" % (10, 40)

    # 生成窗口
    pygame.init()
    pygame.display.set_caption("title")  # 标题
    oldsize = WindowWidth, WindowHight = 1000, 700  # 1122, 602  # 1900,992
    screen = pygame.display.set_mode(oldsize, RESIZABLE)
    # screen.fill((255, 255, 255))  # 背景颜色白色
    screen.fill((180, 180, 255))  # 淡蓝色
    timer = pygame.time.Clock()
    isfullscreen = False
    # 加载字体
    font1 = pygame.font.SysFont("MicrosoftYaHei", 100)

    # 鼠标的信息
    mouse_x = mouse_y = 0
    move_x = move_y = 0
    ldt = rdt = 0
    mouse_lisdown = mouse_risdown = mouse_llongdown = mouse_rlongdown = False
    mouse_down = mouse_up = lgup = rgup = False
    mouse_down_x = mouse_down_y = mouse_up_x = mouse_up_y = False
    wheel = False
    wheell = 0
    keydown = []

    moves = [[0, 0]] * 12
    movesi = 0
    wheelmoves = [0] * 20
    wheelmovesi = 0
    fpss = [60.0] * 60
    fpssi = 0
    fpss2 = [60.0] * 60
    fpssi2 = 0


    def print_text(where: pygame.Surface, afont, x, y, text, color=(0, 0, 0), sizem=1.0):
        """打印字体函数"""
        img_text = afont.render(text, True, color)
        textwidth, textheight = img_text.get_rect().size
        textwidth *= sizem
        textheight *= sizem
        where.blit(pygame.transform.smoothscale(img_text, (textwidth, textheight)), (x, y))


    def resize():
        global isfullscreen, screen, WindowWidth, WindowHight, oldsize
        # 这个函数中必须先判断窗口大小是否变化，在判断是否全屏
        # 否则，在全屏之后，pygame会判定为全屏操作也是改变窗体大小的一个操作，所以会显示一个比较大的窗口但不是全屏模式
        for event in pygame.event.get(VIDEORESIZE):
            oldsize = WindowWidth, WindowHight = event.size[0], event.size[1]
            screen = pygame.display.set_mode(oldsize, RESIZABLE)
        for event in pygame.event.get(KEYDOWN):
            if event.key == K_F11:
                if not isfullscreen:
                    isfullscreen = True
                    maxsize = WindowWidth, WindowHight = pygame.display.list_modes()[0]
                    screen = pygame.display.set_mode(maxsize, FULLSCREEN)
                else:
                    isfullscreen = False
                    # oldsize = WindowWidth, WindowHight = 960, 660
                    screen = pygame.display.set_mode(oldsize, flags=0)
                    screen = pygame.display.set_mode(oldsize, flags=RESIZABLE)
            pygame.event.post(event)

xp, yp = -4, 4

rk = 0.4

points = []
pointsmove = []

for i in range(10):
    points.append([])
    pointsmove.append([True] * 10)
    for j in range(10):
        bl = 1.3
        points[i].append([xp + rk * j + rk * (i % 2) / 2, yp - bl * rk * i * 0.75 ** 0.5,
                          xp + rk * j + rk * (i % 2) / 2, yp - bl * rk * i * 0.75 ** 0.5])

# 标记固定点
for i in range(len(pointsmove)):
    pointsmove[0][i] = False


def calculate_polygon_area(vertices):
    area = (vertices[-1][0] - vertices[0][0]) * (vertices[-1][1] + vertices[0][1])
    for i in range(len(vertices) - 1):
        area += (vertices[i][0] - vertices[i + 1][0]) * (vertices[i][1] + vertices[i + 1][1])
    return abs(area / 2)


pointson = 0
mouseon = 1
mouser = 1
# 物理参数配置
grid_spacing = 70
gravity_x = 0.0
gravity_y = -0.5
spring_rest_length = 0.4
time_step = 1 / 60
constraint_iterations = 20
spring_stiffness = 0.1
velocity_decay = 0.99


# 弹簧约束处理
# @numba.njit
def apply_spring_constraint(p1x, p1y, _0, _1, pi_move, p2x, p2y, _2, _3, p2_move, rest_length, stiffness):
    dx = p2x - p1x
    dy = p2y - p1y
    distance = hypot(dx, dy)
    if distance == 0:
        return

    displacement = (distance - rest_length) * stiffness
    delta_x = dx * displacement
    delta_y = dy * displacement

    if pi_move and p2_move:
        p1x += delta_x / 2
        p1y += delta_y / 2
        p2x -= delta_x / 2
        p2y -= delta_y / 2
    elif pi_move:
        p1x += delta_x
        p1y += delta_y
    elif p2_move:
        p2x -= delta_x
        p2y -= delta_y
    return p1x, p1y, _0, _1, p2x, p2y, _2, _3


# 主循环
while True:
    if True:
        # 事件侦测与信息获取
        resize()
        wheel = False
        wheell = 0
        move_x = move_y = 0
        moves[movesi][0] = moves[movesi][1] = 0
        wheelmoves[wheelmovesi] = 0
        events = pygame.event.get()
        for event in events:
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                elif event.key == K_LCTRL or event.key == K_RCTRL:
                    keydown.append("ctrl")
                else:
                    try:
                        keydown.append(chr(event.key))
                    except:
                        pass
            elif event.type == KEYUP:
                if event.key == K_LCTRL or event.key == K_RCTRL:
                    word = "ctrl"
                    keydown.pop(keydown.index(word))
                else:
                    try:
                        word = chr(event.key)
                        keydown.pop(keydown.index(word))
                    except:
                        pass
            elif event.type == MOUSEMOTION:
                mouse_x, mouse_y = event.pos
                move_x, move_y = event.rel
                if mouse_llongdown:
                    moves[movesi][0] = move_x
                    moves[movesi][1] = move_y
            elif event.type == MOUSEBUTTONDOWN:
                mouse_down = event.button
                mouse_down_x, mouse_down_y = event.pos
                if event.button == 1:
                    mouse_lisdown = True
                    if ldt == 0:
                        ldt = 1
                elif event.button == 3:
                    mouse_risdown = True
                    if rdt == 0:
                        rdt = 1
            elif event.type == MOUSEBUTTONUP:
                mouse_up = event.button
                mouse_up_x, mouse_up_y = event.pos
                if event.button == 1:
                    mouse_lisdown = False
                    lgup = True
                elif event.button == 3:
                    mouse_risdown = False
                    rgup = True
            elif event.type == MOUSEWHEEL:
                wheel = True
                wheell = event.y
                wheelmoves[wheelmovesi] = event.y
    # 处理鼠标滚轮缩放
    mouse_wheel_zoom = sum(wheelmoves) / len(wheelmoves) / 12
    grid_spacing = max(6.0, grid_spacing * (mouse_wheel_zoom + 1))

    # 绘制背景网格
    grid_color = (0, 0, 255)
    gird_range = 15
    for i in range(-gird_range, gird_range + 1):
        for j in range(-gird_range, gird_range + 1):
            position = [i * grid_spacing + WindowWidth / 2, -j * grid_spacing + WindowHight / 2]
            radius = max(0.05 * grid_spacing, 1)
            pygame.draw.circle(screen, grid_color, position, radius)

    # 绘制所有连接线
    for j in range(len(points)):
        pygame.draw.aalines(screen, (0, 0, 0), False,
                            [[i[0] * grid_spacing + WindowWidth / 2, -i[1] * grid_spacing + WindowHight / 2] for i in
                             points[j]], round(max(0.03 * grid_spacing, 1)))

    for j in range(len(points[0])):
        pygame.draw.aalines(screen, (0, 0, 0), False, [[points[i][j][0] * grid_spacing + WindowWidth / 2,
                                                        -points[i][j][1] * grid_spacing + WindowHight / 2] for i in
                                                       range(len(points))],
                            round(max(0.03 * grid_spacing, 1)))

    for j in range(1, len(points[0])):
        pt = (-1) ** (j + 1)
        pygame.draw.aalines(screen, (0, 0, 0), False, [[points[i][j - i % 2][0] * grid_spacing + WindowWidth / 2,
                                                        -points[i][j - i % 2][1] * grid_spacing + WindowHight / 2] for i
                                                       in range(len(points))],
                            round(max(0.03 * grid_spacing, 1)))

    if pointson:
        for i in range(len(points)):
            for j in range(len(points[i])):
                pygame.draw.circle(screen, (255, 0, 0),
                                   [points[i][j][0] * grid_spacing + WindowWidth / 2 + 1,
                                    -points[i][j][1] * grid_spacing + WindowHight / 2 + 1], 0.04 * grid_spacing)

    # 转换鼠标坐标为模拟空间坐标
    mouse_x_scaled = (mouse_x - WindowWidth / 2) / grid_spacing
    mouse_y_scaled = -(mouse_y - WindowHight / 2) / grid_spacing

    # 更新质点位置
    for i in range(len(points)):
        for j in range(len(points[i])):
            point = points[i][j]
            if not pointsmove[i][j]:  # 跳过固定点
                continue

            x, y, last_x, last_y = point
            is_movable = pointsmove[i][j]

            vel_x = (x - last_x) * velocity_decay
            vel_y = (y - last_y) * velocity_decay

            # 应用重力和速度
            new_x = x + vel_x + gravity_x * time_step
            new_y = y + vel_y + gravity_y * time_step

            # 鼠标交互影响
            if mouseon:
                for _ in range(2):
                    distance = hypot(x - mouse_x_scaled, y - mouse_y_scaled)
                    if distance < mouser:
                        influence = 0.5 * (mouser - distance) / distance
                        new_x += (x - mouse_x_scaled) * influence
                        new_y += (y - mouse_y_scaled) * influence

            points[i][j] = [new_x, new_y, x, y]

    # 应用所有弹簧约束
    for _ in range(constraint_iterations):
        # 垂直方向约束
        for layer_idx in range(len(points) - 1):
            for point_idx in range(len(points[layer_idx])):
                newp = apply_spring_constraint(
                    *points[layer_idx][point_idx], pointsmove[layer_idx][point_idx],
                    *points[layer_idx + 1][point_idx], pointsmove[layer_idx + 1][point_idx],
                    spring_rest_length, spring_stiffness
                )
                points[layer_idx][point_idx] = newp[0:4]
                points[layer_idx + 1][point_idx] = newp[4:8]

        # 对角线方向约束
        for layer_idx in range(len(points) - 1):
            direction = (-1) ** (layer_idx + 1)
            for point_idx in range((layer_idx + 1) % 2, len(points[layer_idx]) - layer_idx % 2):
                paired_idx = point_idx + direction
                newp = apply_spring_constraint(
                    *points[layer_idx][point_idx], pointsmove[layer_idx][point_idx],
                    *points[layer_idx + 1][paired_idx], pointsmove[layer_idx + 1][paired_idx],
                    spring_rest_length, spring_stiffness
                )
                points[layer_idx][point_idx] = newp[0:4]
                points[layer_idx + 1][paired_idx] = newp[4:8]

        # 水平方向约束
        for layer_idx in range(len(points)):
            for point_idx in range(len(points[layer_idx]) - 1):
                newp = apply_spring_constraint(
                    *points[layer_idx][point_idx], pointsmove[layer_idx][point_idx],
                    *points[layer_idx][point_idx + 1], pointsmove[layer_idx][point_idx + 1],
                    spring_rest_length, spring_stiffness
                )
                points[layer_idx][point_idx] = newp[0:4]
                points[layer_idx][point_idx + 1] = newp[4:8]

    # 绘制鼠标作用范围指示器
    if mouseon:
        r = mouser * grid_spacing * 1.95
        pygame.draw.arc(screen, (255, 127, 127), [
            mouse_x - r / 2, mouse_y - r / 2, r, r], 0, 2 * pi)
        pygame.draw.arc(screen, (255, 127, 127), [
            mouse_x - r / 2 + 1, mouse_y - r / 2 + 1, r - 2, r - 2], 0, 2 * pi)

    if True:
        pygame.display.update()
        # screen.fill((255, 255, 255))  # 背景颜色白色
        screen.fill((180, 180, 255))  # 淡蓝色

        dt = timer.tick(60)
        mouse_llongdown = False
        mouse_rlongdown = False

        # sdt2 = (dt / 1000)

        if not mouse_lisdown:
            ldt = 0
        if ldt != 0:
            ldt += dt
            if ldt > 80:
                mouse_llongdown = True

        if not mouse_risdown:
            rdt = 0
        if rdt != 0:
            rdt += dt
            if rdt > 80:
                mouse_rlongdown = True

        lgup = rgup = False

        movesi = (movesi + 1) % len(moves)
        wheelmovesi = (wheelmovesi + 1) % len(wheelmoves)
        fpssi = (fpssi + 1) % len(fpss)
        fpssi2 = (fpssi2 + 1) % len(fpss2)

        fpss[fpssi] = 1000 / dt
        fpss2[fpssi2] = timer.get_fps()

        pygame.draw.rect(screen, (180, 180, 255), (5, 5, 100, 100), 0)

        print_text(screen, font1, 10, 10, "dtfps:" + str(round(1000 / dt, 1)), (0, 0, 0), 0.12)
        print_text(screen, font1, 10, 30, "fps:" + str(round(timer.get_fps(), 1)), (0, 0, 0), 0.12)

        print_text(screen, font1, 10, 50, "平均dtfps:" + str(round(sum(fpss) / len(fpss), 1)), (0, 0, 0), 0.12)
        print_text(screen, font1, 10, 70, "平均fps:" + str(round(sum(fpss2) / len(fpss2), 1)), (0, 0, 0), 0.12)

        # print_text(screen, font1, 10, 90, "体积:" + str(round(vnow, 3)), (0, 0, 0), 0.12)
        # print_text(screen, font1, 10, 110, "体积:" + str(round(v1, 3)), (0, 0, 0), 0.12)
# 2,0.1,0.99 短程作用
# 2,0.9 大弹力、短程作用
# 15,0.05 流畅
# 15,0.05 不可超限

# stapoints = list(product([-2, -1, 0, 1, 2], [-2, -1, 0, 1, 2]))

# F11全屏来源：版权声明：本文为CSDN博主「Lucas-hao」的原创文章，遵循CC 4.0 BY-SA版权协议，转载请附上原文出处链接及本声明。
# 原文链接：https://blog.csdn.net/weixin_45951701/article/details/107272385
