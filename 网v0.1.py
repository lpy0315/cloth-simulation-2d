import math
import sys
from math import *
import pygame
# import pygame._sdl2
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


    def Resize():
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
for i in range(20):
    points.append([])
    for j in range(20):
        points[i].append([xp + rk * j + rk * (i % 2) / 2, yp - rk * i * 0.75 ** 0.5, xp + rk * j + rk * (i % 2) / 2,
                          yp - rk * i * 0.75 ** 0.5, True])


def jf(a):
    area = (a[-1][0] - a[0][0]) * (a[-1][1] + a[0][1])
    for i in range(len(a) - 1):
        area += (a[i][0] - a[i + 1][0]) * (a[i][1] + a[i + 1][1])
    return abs(area / 2)


whk = 50

for i in range(len(points[0])):
    points[0][i][4] = False

# print(*points,sep="\n")

pointson = True
mouseon = True
mouser = 1
xg = 0  # .15
yg = -0.5
dissta = 0.4
sdt2 = 1 / 60
ren = 20
rek = 0.1
vk = 0.99

v0 = 15
vrek = 0.1

# 2,0.1,0.99 短程作用
# 2,0.9 大弹力、短程作用
# 15,0.05 流畅
# 15,0.05 不可超限

# stapoints = list(product([-2, -1, 0, 1, 2], [-2, -1, 0, 1, 2]))
# 主循环
while True:
    if True:
        # 事件侦测与信息获取
        Resize()
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

    mouse_wheel_length = sum(wheelmoves) / len(wheelmoves) / 12
    whk = max(6.0, whk * (mouse_wheel_length + 1))

    for i in range(-6, 7):
        for j in range(-6, 7):
            pygame.draw.circle(screen, (0, 0, 255), [i * whk + WindowWidth / 2, -j * whk + WindowHight / 2],
                               max(0.05 * whk, 1))
    for j in range(len(points)):
        pygame.draw.lines(screen, (0, 0, 0), False,
                          [[i[0] * whk + WindowWidth / 2, -i[1] * whk + WindowHight / 2] for i in points[j]],
                          round(max(0.03 * whk, 1)))

    for j in range(len(points[0])):
        pygame.draw.lines(screen, (0, 0, 0), False,
                          [[points[i][j][0] * whk + WindowWidth / 2,
                            -points[i][j][1] * whk + WindowHight / 2] for i in range(len(points))],
                          round(max(0.03 * whk, 1)))

    for j in range(1, len(points[0])):
        pt = (-1) ** (j + 1)
        pygame.draw.lines(screen, (0, 0, 0), False,
                          [[points[i][j - i % 2][0] * whk + WindowWidth / 2,
                            -points[i][j - i % 2][1] * whk + WindowHight / 2] for i in range(len(points))],
                          round(max(0.03 * whk, 1)))
    '''
    for i in range(len(points)):
        for j in range(len(points[i])):
            pygame.draw.circle(screen, (255, 0, 0),
                               [points[i][j][0] * whk + WindowWidth / 2, -points[i][j][1] * whk + WindowHight / 2],
                               0.04 * whk)
    '''
    mx = (mouse_x - WindowWidth / 2) / whk
    my = -(mouse_y - WindowHight / 2) / whk

    for i in range(len(points)):
        for j in range(len(points[i])):
            if not points[i][j][4]:
                continue
            x, y, lx, ly, mov = points[i][j]
            vtotal = math.hypot(x - lx, y - ly)
            mv = 10
            # realvm = max(realvm, vtotal)
            if abs(vtotal) < mv:
                nx = x + (x - lx) * vk + xg * sdt2
                ny = y + (y - ly) * vk + yg * sdt2
            else:
                nx = x + (x - lx) / vtotal * mv * 0.8 + (xg) * sdt2
                ny = y + (y - ly) / vtotal * mv * 0.8 + (yg) * sdt2
            # print(ny,y)
            # nx = x + math.copysign((abs((x - lx) * vk / mv) ** 0.33) * mv, x - lx)
            # ny = y + math.copysign((abs((y - ly) * vk / mv) ** 0.33) * mv, y - ly) - g * sdt2
            if mouseon:
                dis = math.hypot(x - mx, y - my)
                if dis < mouser:
                    dis2 = 0.5 / min(0.8, (dis / mouser) ** 4) / 2
                    nx += 0.1 * (x - mx) * dis2
                    ny += 0.1 * (y - my) * dis2
            points[i][j] = [nx, ny, x, y, mov]

    if mouseon:
        r = mouser * whk * 1.95
        pygame.draw.arc(screen, (255, 127, 127), [
            mouse_x - r / 2, mouse_y - r / 2, r, r], 0, 2 * pi)
        pygame.draw.arc(screen, (255, 127, 127), [
            mouse_x - r / 2 + 1, mouse_y - r / 2 + 1, r - 2, r - 2], 0, 2 * pi)

    for _ in range(ren):
        for j in range(len(points) - 1):
            for i in range(len(points[0])):
                if (not points[j][i][4]) and (not points[j + 1][i][4]):
                    continue
                if points[j][i][4] and mouseon:
                    x, y = points[j][i][0], points[j][i][1]
                    dis = math.hypot(x - mx, y - my)
                    if dis < mouser:  # + i / 300
                        points[j][i][0] += 0.5 * (x - mx) / dis * (mouser - dis + 0.02)  # + i / 300
                        points[j][i][1] += 0.5 * (y - my) / dis * (mouser - dis + 0.02)
                x1, y1 = points[j][i][0], points[j][i][1]
                x2, y2 = points[j + 1][i][0], points[j + 1][i][1]
                disx, disy = x2 - x1, y2 - y1
                disr = math.hypot(disx, disy)
                diserr = disr - dissta
                disx /= disr
                disy /= disr
                dx, dy = disx * diserr * rek, disy * diserr * rek
                if points[j][i][4] and points[j + 1][i][4]:
                    points[j][i][0] += dx / 2
                    points[j][i][1] += dy / 2
                    points[j + 1][i][0] -= dx / 2
                    points[j + 1][i][1] -= dy / 2
                elif points[j][i][4] and (not points[j + 1][i][4]):
                    points[j][i][0] += dx
                    points[j][i][1] += dy
                elif (not points[j][i][4]) and points[j + 1][i][4]:
                    points[j + 1][i][0] -= dx
                    points[j + 1][i][1] -= dy
            if points[-1][i][4] and mouseon:
                x, y = points[-1][i][0], points[-1][i][1]
                dis = math.hypot(x - mx, y - my)
                if dis < mouser:
                    points[-1][i][0] += 0.3 * (x - mx) / dis * (mouser - dis) / mouser
                    points[-1][i][1] += 0.3 * (y - my) / dis * (mouser - dis) / mouser

        #  for i_ in range(ren):
        for j in range(len(points) - 1):
            pt = (-1) ** (j + 1)
            for i in range((j + 1) % 2, len(points[0]) - j % 2):
                if (not points[j][i][4]) and (not points[j + 1][i + pt][4]):
                    continue
                if points[j][i][4] and mouseon:
                    x, y = points[j][i][0], points[j][i][1]
                    dis = math.hypot(x - mx, y - my)
                    if dis < mouser:  # + i / 300
                        points[j][i][0] += 0.5 * (x - mx) / dis * (mouser - dis + 0.02)  # + i / 300
                        points[j][i][1] += 0.5 * (y - my) / dis * (mouser - dis + 0.02)
                x1, y1 = points[j][i][0], points[j][i][1]
                x2, y2 = points[j + 1][i + pt][0], points[j + 1][i + pt][1]
                disx, disy = x2 - x1, y2 - y1
                disr = math.hypot(disx, disy)
                diserr = disr - dissta
                disx /= disr
                disy /= disr
                dx, dy = disx * diserr * rek, disy * diserr * rek
                if points[j][i][4] and points[j + 1][i + pt][4]:
                    points[j][i][0] += dx / 2
                    points[j][i][1] += dy / 2
                    points[j + 1][i + pt][0] -= dx / 2
                    points[j + 1][i + pt][1] -= dy / 2
                elif points[j][i][4] and (not points[j + 1][i + pt][4]):
                    points[j][i][0] += dx
                    points[j][i][1] += dy
                elif (not points[j][i][4]) and points[j + 1][i][4]:
                    points[j + 1][i + pt][0] -= dx
                    points[j + 1][i + pt][1] -= dy
            if points[-1][i + pt][4] and mouseon:
                x, y = points[-1][i + pt][0], points[-1][i + pt][1]
                dis = math.hypot(x - mx, y - my)
                if dis < mouser:
                    points[-1][i + pt][0] += 0.3 * \
                                             (x - mx) / dis * (mouser - dis) / mouser
                    points[-1][i][1 + pt] += 0.3 * \
                                             (y - my) / dis * (mouser - dis) / mouser

        # for i_ in range(ren):
        for j in range(len(points)):
            for i in range(len(points[j]) - 1):
                if (not points[j][i][4]) and (not points[j][i + 1][4]):
                    continue
                if points[j][i][4] and mouseon:
                    x, y = points[j][i][0], points[j][i][1]
                    dis = math.hypot(x - mx, y - my)
                    if dis < mouser:  # + i / 300
                        points[j][i][0] += 0.5 * (x - mx) / dis * (mouser - dis + 0.02)  # + i / 300
                        points[j][i][1] += 0.5 * (y - my) / dis * (mouser - dis + 0.02)
                x1, y1 = points[j][i][0], points[j][i][1]
                x2, y2 = points[j][i + 1][0], points[j][i + 1][1]
                disx, disy = x2 - x1, y2 - y1
                disr = math.hypot(disx, disy)
                diserr = disr - dissta
                disx /= disr
                disy /= disr
                dx, dy = disx * diserr * rek, disy * diserr * rek
                if points[j][i][4] and points[j][i + 1][4]:
                    points[j][i][0] += dx / 2
                    points[j][i][1] += dy / 2
                    points[j][i + 1][0] -= dx / 2
                    points[j][i + 1][1] -= dy / 2
                elif points[j][i][4] and (not points[j][i + 1][4]):
                    points[j][i][0] += dx
                    points[j][i][1] += dy
                elif (not points[j][i][4]) and points[j][i + 1][4]:
                    points[j][i + 1][0] -= dx
                    points[j][i + 1][1] -= dy
            if points[j][-1][4] and mouseon:
                x, y = points[j][-1][0], points[j][-1][1]
                dis = math.hypot(x - mx, y - my)
                if dis < mouser:
                    points[j][-1][0] += 0.3 * (x - mx) / dis * (mouser - dis) / mouser
                    points[j][-1][1] += 0.3 * (y - my) / dis * (mouser - dis) / mouser

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

# F11全屏来源：版权声明：本文为CSDN博主「Lucas-hao」的原创文章，遵循CC 4.0 BY-SA版权协议，转载请附上原文出处链接及本声明。
# 原文链接：https://blog.csdn.net/weixin_45951701/article/details/107272385
