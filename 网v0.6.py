import sys
from math import pi, hypot

import pygame
from pygame.locals import *
import numpy as np

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

# 参数设置
xp, yp = -4, 4
rk = 0.4
velocity_decay = 0.98
gravity = (0, 0.1)
constraint_iterations = 5
spring_rest_length = rk * 0.5
spring_stiffness = 0.1


# 初始化网格点（使用NumPy数组）
def initialize_points():
    i, j = np.mgrid[0:20, 0:20]
    offset = (i % 2) * rk / 2
    x = xp + rk * j + offset
    y = yp - rk * i * np.sqrt(0.75)
    return np.dstack([x, y, x.copy(), y.copy()])
    # ValueError: operands could not be broadcast together with shapes (20,) (0,) (20,)


# 初始化可移动标记（顶层固定）
def initialize_movable():
    movable = np.ones((20, 20), dtype=bool)
    movable[0, :] = False  # 固定顶层
    return movable


points = initialize_points()
pointsmove = initialize_movable()



def apply_constraints(points, movable):
    # 创建副本用于安全修改
    new_points = points.copy()

    # 预计算所有可能需要的点对索引
    for _ in range(constraint_iterations):
        # 垂直约束（层间约束）
        for layer in range(19):
            mask = movable[layer] | movable[layer + 1]
            p1 = new_points[layer]
            p2 = new_points[layer + 1]

            dx = p2[:, 0] - p1[:, 0]
            dy = p2[:, 1] - p1[:, 1]
            dist = np.hypot(dx, dy)
            valid = (dist != 0) & mask

            displacement = (dist[valid] - spring_rest_length) * spring_stiffness
            delta_x = dx[valid] * displacement
            delta_y = dy[valid] * displacement

            # 同时更新两个点
            m1 = movable[layer, valid]
            m2 = movable[layer + 1, valid]

            # 双方都可移动
            both_movable = m1 & m2
            valid_indices = np.where(both_movable)[0]
            new_points[layer, valid, valid_indices] += delta_x[both_movable] * 0.5
            new_points[layer, valid, valid_indices] += delta_y[both_movable] * 0.5
            new_points[layer + 1, valid, valid_indices] -= delta_x[both_movable] * 0.5
            new_points[layer + 1, valid, valid_indices] -= delta_y[both_movable] * 0.5

            # 仅p1可移动
            only_p1 = m1 & ~m2
            new_points[layer, valid, 0] += delta_x[only_p1]
            new_points[layer, valid, 1] += delta_y[only_p1]

            # 仅p2可移动
            only_p2 = ~m1 & m2
            new_points[layer + 1, valid, 0] -= delta_x[only_p2]
            new_points[layer + 1, valid, 1] -= delta_y[only_p2]

        # 其他约束（水平、对角线）的类似向量化处理...
        # 此处需要根据具体约束模式补充实现

    return new_points


def update_points(points, movable, mouse_pos=None, mouser=0):
    # 分离当前位置和最后位置
    current = points[:, :, :2].copy()
    last = points[:, :, 2:].copy()

    # 计算速度并应用重力
    velocity = (current - last) * velocity_decay
    new_pos = current + velocity + np.array(gravity) * 0.1

    # 鼠标交互处理
    if mouse_pos is not None:
        mx, my = mouse_pos
        dx = new_pos[:, :, 0] - mx
        dy = new_pos[:, :, 1] - my
        dist = np.hypot(dx, dy)
        influence = np.clip((mouser - dist) / mouser, 0, 1)
        new_pos[:, :, 0] -= dx * influence * 0.5
        new_pos[:, :, 1] -= dy * influence * 0.5

    # 更新位置并保留最后位置
    updated = np.dstack([new_pos, current])

    # 应用约束
    updated = apply_constraints(updated, movable)

    # 固定点保持原位
    updated[~movable] = points[~movable]
    return updated
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
time_step = 1 / 60

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
    gird_range = 10
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

    points = update_points(points, pointsmove, (mouse_x_scaled, mouse_y_scaled))

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
