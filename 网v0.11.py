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

rk = 0.3
velocity_decay = 0.99
gravity = (0, 0.1)
constraint_iterations = 3
spring_rest_length = rk
spring_stiffness = 0.08


def calculate_polygon_area(vertices):
    area = (vertices[-1][0] - vertices[0][0]) * (vertices[-1][1] + vertices[0][1])
    for i in range(len(vertices) - 1):
        area += (vertices[i][0] - vertices[i + 1][0]) * (vertices[i][1] + vertices[i + 1][1])
    return abs(area / 2)


grid_width = 40
grid_height = 30
offsetx = 0
offsety = 1


# 初始化网格点（使用NumPy数组）
def initialize_points():
    # 计算网格中心的偏移量
    xp = -grid_width * rk / 2 + offsetx
    yp = grid_height * rk * np.sqrt(0.75) / 2 + offsety
    # 使用np.mgrid生成网格索引
    i, j = np.mgrid[0:grid_height, 0:grid_width]
    # 计算x和y的坐标，并加入新的offsetx和offsety
    offset = (i % 2) * rk / 2
    x = xp + rk * j + offset
    y = yp - rk * i * np.sqrt(0.75)
    # 返回结果，x和y的副本是为了保持原始代码的结构
    return np.dstack([x, y, x.copy(), y.copy()])


# 初始化可移动标记（顶层固定）
def initialize_movable():
    movable = np.ones((grid_height, grid_width), dtype=bool)
    movable[0, 0:12] = False
    movable[0, -12:] = False
    return movable


points = initialize_points()
pointsmove = initialize_movable()

'''
def apply_mouse(mouse_pos, mouser):
    dx = new_points[:, :, 0] - mx
    dy = new_points[:, :, 1] - my
    dist = np.hypot(dx, dy)
    influence = np.clip((mouser - dist) / mouser, 0, 1) * msk
    new_points[:, :, 0] += dx * influence
    new_points[:, :, 1] += dy * influence
'''

def apply_direction_constraint(points, p1_indices, p2_indices):
    """应用特定方向的约束

    参数:
    points - 点坐标数组
    movable - 可移动标记数组
    p1_indices - 第一组点的索引 (i1, j1)
    p2_indices - 第二组点的索引 (i2, j2)
    """
    # 创建副本用于安全修改
    new_points = points.copy()

    # 提取相应索引的点
    i1, j1 = p1_indices
    i2, j2 = p2_indices
    p1_all = new_points[i1, j1]
    p2_all = new_points[i2, j2]

    # 计算坐标差
    dx = p2_all[..., 0] - p1_all[..., 0]
    dy = p2_all[..., 1] - p1_all[..., 1]

    # 计算弹簧力误差及方向调整量
    distance = np.hypot(dx, dy)
    # 避免除以零
    valid_dist = distance > 0
    err = np.zeros_like(distance)
    err[valid_dist] = (distance[valid_dist] - spring_rest_length) * spring_stiffness / distance[valid_dist]
    delta_x = dx * err
    delta_y = dy * err

    # 计算各情况对坐标的调整量
    # 双方可移动的调整量
    delta_p1_x_both = 0.5 * delta_x
    delta_p1_y_both = 0.5 * delta_y
    delta_p2_x_both = -0.5 * delta_x
    delta_p2_y_both = -0.5 * delta_y

    # 应用调整量到坐标
    new_points[i1, j1, 0] += delta_p1_x_both
    new_points[i1, j1, 1] += delta_p1_y_both
    new_points[i2, j2, 0] += delta_p2_x_both
    new_points[i2, j2, 1] += delta_p2_y_both

    return new_points

#如果有numba
import importlib.util
if importlib.util.find_spec("numba") and False:
    from numba import jit
    apply_direction_constraint = jit(apply_direction_constraint)

def apply_constraints(points, movable, mouse_pos=None, mouser=1e-5):
    #global new_points, mx, my, msk
    # 创建副本用于安全修改
    new_points = points.copy()
    mx, my = mouse_pos
    msk = 0.08

    for _ in range(constraint_iterations):
        # 1. 垂直方向约束（层间约束）
        i1 = np.arange(points.shape[0] - 1)[:, None]  # 形状为 (19, 1)
        j1 = np.arange(points.shape[1])[None, :]  # 形状为 (1, 20)
        i2 = i1 + 1
        j2 = j1
        new_points = apply_direction_constraint(new_points, (i1, j1), (i2, j2))

        dx = new_points[:, :, 0] - mx
        dy = new_points[:, :, 1] - my
        dist = np.hypot(dx, dy)
        influence = np.clip((mouser - dist) / mouser, 0, 1) * msk
        new_points[:, :, 0] += dx * influence
        new_points[:, :, 1] += dy * influence
        # 2. 对角线方向约束
        for layer_idx in range(points.shape[0] - 1):
            direction = (-1) ** (layer_idx + 1)
            # 创建有效的点对索引
            if direction > 0:  # 向右对角线
                valid_j1 = np.arange((layer_idx + 1) % 2, points.shape[1] - layer_idx % 2)
                valid_j2 = valid_j1 + 1
            else:  # 向左对角线
                valid_j1 = np.arange((layer_idx + 1) % 2, points.shape[1] - layer_idx % 2)
                valid_j2 = valid_j1 - 1

            # 过滤掉超出范围的索引
            valid_mask = (valid_j2 >= 0) & (valid_j2 < points.shape[1])
            valid_j1 = valid_j1[valid_mask]
            valid_j2 = valid_j2[valid_mask]

            if len(valid_j1) > 0:
                i1 = np.full_like(valid_j1, layer_idx)
                i2 = np.full_like(valid_j2, layer_idx + 1)
                new_points = apply_direction_constraint(new_points, (i1, valid_j1), (i2, valid_j2))

        dx = new_points[:, :, 0] - mx
        dy = new_points[:, :, 1] - my
        dist = np.hypot(dx, dy)
        influence = np.clip((mouser - dist) / mouser, 0, 1) * msk
        new_points[:, :, 0] += dx * influence
        new_points[:, :, 1] += dy * influence

        # 3. 水平方向约束
        i1 = np.arange(points.shape[0])[:, None]  # 形状为 (20, 1)
        j1 = np.arange(points.shape[1] - 1)[None, :]  # 形状为 (1, 19)
        i2 = i1
        j2 = j1 + 1
        new_points = apply_direction_constraint(new_points, (i1, j1), (i2, j2))

        dx = new_points[:, :, 0] - mx
        dy = new_points[:, :, 1] - my
        dist = np.hypot(dx, dy)
        influence = np.clip((mouser - dist) / mouser, 0, 1) * msk
        new_points[:, :, 0] += dx * influence
        new_points[:, :, 1] += dy * influence
    return new_points


pointson = 0
mouseon = 1
mouser = 1.5
# 物理参数配置
grid_spacing = 70
gravity_x = 0.0
gravity_y = -0.5
time_step = 1 / 60
maxfps = 180

force = np.zeros_like(points[:, :, :2])
force[-2:, :, 1] -= 0.02
force[-2:, :2, 0] -= 0.005
force[-2:, -2:, 0] += 0.005
force[:, 0, 0] -= 0.001
force[:, -1, 0] += 0.001
force*=1.8


def update_points(points, movable, mouse_pos, mouser):
    # 分离当前位置和最后位置
    current = points[:, :, :2].copy()
    last = points[:, :, 2:].copy()

    new_pos = current + (current - last) * velocity_decay - np.array(gravity) * 0.013*constraint_iterations*spring_stiffness
    new_pos += force*constraint_iterations*spring_stiffness

    # 鼠标交互处理
    if mouseon:
        for _ in range(0):
            mx, my = mouse_pos
            dx = new_pos[:, :, 0] - mx
            dy = new_pos[:, :, 1] - my
            dist = np.hypot(dx, dy)
            influence = np.clip((mouser - dist) / mouser, 0, 1)
            new_pos[:, :, 0] += dx * influence * 0.07
            new_pos[:, :, 1] += dy * influence * 0.07

    # 更新位置并保留最后位置
    updated = np.dstack([new_pos, current])
    updated = apply_constraints(updated, movable, mouse_pos, mouser)
    # 固定点保持原位
    updated[~movable] = points[~movable]
    return updated


grid_color = (0, 0, 255)
gird_range = 10
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

    points = update_points(points, pointsmove, (mouse_x_scaled, mouse_y_scaled), mouser)

    # 绘制鼠标作用范围指示器
    if mouseon:
        r = mouser * grid_spacing * 1.99
        pygame.draw.arc(screen, (255, 127, 127), [
            mouse_x - r / 2, mouse_y - r / 2, r, r], 0, 2 * pi)
        pygame.draw.arc(screen, (255, 127, 127), [
            mouse_x - r / 2 + 1, mouse_y - r / 2 + 1, r - 2, r - 2], 0, 2 * pi)

    if True:
        pygame.display.update()
        # screen.fill((255, 255, 255))  # 背景颜色白色
        screen.fill((180, 180, 255))  # 淡蓝色

        dt = timer.tick(maxfps)
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

    '''# 补帧
    frame = points[:, :, :2] / 2 + points[:, :, 2:] / 2
    # 绘制背景网格
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

    if mouseon:
        # 转换鼠标坐标为模拟空间坐标
        mouse_x_scaled = (mouse_x - WindowWidth / 2) / grid_spacing
        mouse_y_scaled = -(mouse_y - WindowHight / 2) / grid_spacing
        r = mouser * grid_spacing * 1.99
        pygame.draw.arc(screen, (255, 127, 127), [
            mouse_x - r / 2, mouse_y - r / 2, r, r], 0, 2 * pi)
        pygame.draw.arc(screen, (255, 127, 127), [
            mouse_x - r / 2 + 1, mouse_y - r / 2 + 1, r - 2, r - 2], 0, 2 * pi)

    if True:
        pygame.display.update()
        # screen.fill((255, 255, 255))  # 背景颜色白色
        screen.fill((180, 180, 255))  # 淡蓝色

        dt = timer.tick(maxfps)
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
        # print_text(screen, font1, 10, 110, "体积:" + str(round(v1, 3)), (0, 0, 0), 0.12)'''
# 2,0.1,0.99 短程作用
# 2,0.9 大弹力、短程作用
# 15,0.05 流畅
# 15,0.05 不可超限

# stapoints = list(product([-2, -1, 0, 1, 2], [-2, -1, 0, 1, 2]))

# F11全屏来源：版权声明：本文为CSDN博主「Lucas-hao」的原创文章，遵循CC 4.0 BY-SA版权协议，转载请附上原文出处链接及本声明。
# 原文链接：https://blog.csdn.net/weixin_45951701/article/details/107272385
