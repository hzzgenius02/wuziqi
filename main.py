"""
Python全套免费视频教程&大量实例，请关注我的公众号：跟哥一起学python，id：tiger-python
pygame 实现简单的五子棋游戏
"""
import pygame
import ai
from tkinter import *
import tkinter
from tkinter import messagebox
from pygame.locals import *
from PIL import Image, ImageTk

# 颜色常量
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (178, 34, 34)
GREEN = (46, 139, 87)
BLUE = (30, 30, 200)
YELLOW = (238, 238, 0)
c_line = (28, 28, 28)
c_background = (0xE3, 0x92, 0x65)

# 错误码
G_POS_PLACED = -4
G_RANGE_ERR = -3
G_STAT_ERR = -2
G_ERR = -1
G_OK = 0
G_FINISH = 1
G_WIN = 2

winner = 0
mode = 0  # 0:未选择，1:双人，2：人机
mixer = 1  # 背景音乐
music = 1  # 落子声音

class GoBang:
    def __init__(self, map_size=15):
        self.screen = None
        self.times = 0
        self.map_size = map_size
        # map_size * map_size的二维列表，用于表示棋盘
        # 0 ~ 无棋子， 1 ~ 黑棋，-1 ~ 白棋
        self.map = [[0 for y in range(0, map_size)] for x in range(0, map_size)]
        # 走棋的历史记录，用于悔棋。它是一个list，它的成员是一个元组(棋子类型，map.x，map.y)
        self.move_stack = []
        self.status = 0
        self.win_mode = 0  # 记录五连珠的形式，1：竖直; 2：水平; 3：左上-右下; 4.右上-左下
        self.win_x = 0
        self.win_y = 0  # 定位五连珠的点坐标，如竖直线中的（0，4）
        if mode != 0:
            self.status = 1

    def start_move(self):
        self.status = 1

    def get_last_move(self):
        return self.move_stack[-1]

    def get_steps(self):
        return len(self.move_stack)

    # 判断输赢的算法: 只需要判断当前落子相关的四条直线（横、竖、左斜、右斜），是否形成5个连子。
    # 将直线上的落子(黑~ 1，白~ -1)，依次相加，连续的子绝对值之和达到5，即可判定为胜利
    def __check_winner_(self):
        tmp = 0
        last_step = self.move_stack[-1]
        # 竖向直线, x 固定
        for y in range(0, self.map_size):
            # 必须是连续的
            if y > 0 \
                    and self.map[last_step[1]][y] != self.map[last_step[1]][y - 1]:
                tmp = 0
            tmp += self.map[last_step[1]][y]
            if abs(tmp) >= 5:
                self.win_mode = 1
                self.win_x = last_step[1]
                self.win_y = y
                print('success mode 1:', last_step[1], y)  # 竖向直线最下面的
                return last_step[0]

        # 横向直线, y 固定
        tmp = 0
        for x in range(0, self.map_size):
            # 必须是连续的
            if x > 0 \
                    and self.map[x][last_step[2]] != self.map[x - 1][last_step[2]]:
                tmp = 0
            tmp += self.map[x][last_step[2]]
            if abs(tmp) >= 5:
                self.win_mode = 2
                self.win_x = x
                self.win_y = last_step[2]
                print('success mode 2:', x, last_step[2])  # 竖向直线最下面的
                return last_step[0]

        # 右斜直线，计算出左上角顶点的坐标。然后x,y都递增，到达最右下角顶点。
        tmp = 0
        min_dist = min(last_step[1], last_step[2])
        top_point = [last_step[1] - min_dist, last_step[2] - min_dist]
        for incr in range(0, self.map_size):
            # 不能超出棋盘边界
            if top_point[0] + incr > self.map_size - 1 \
                    or top_point[1] + incr > self.map_size - 1:
                break
            # 必须是连续的
            if incr > 0 \
                    and self.map[top_point[0] + incr][top_point[1] + incr] \
                    != self.map[top_point[0] + incr - 1][top_point[1] + incr - 1]:
                tmp = 0
            tmp += self.map[top_point[0] + incr][top_point[1] + incr]
            if abs(tmp) >= 5:
                self.win_mode = 3
                self.win_x = top_point[0] + incr
                self.win_y = top_point[1] + incr
                print('success mode 3:', top_point[0] + incr, top_point[1] + incr)
                return last_step[0]

        # 左斜直线，计算出右上角顶点的坐标。然后x递减、y递增，到达最左下角顶点。
        tmp = 0
        min_dist = min(self.map_size - 1 - last_step[1], last_step[2])
        top_point = [last_step[1] + min_dist, last_step[2] - min_dist]
        for incr in range(0, self.map_size):
            # 不能超出棋盘边界
            if top_point[0] - incr < 0 \
                    or top_point[1] + incr > self.map_size - 1:
                break
            # 必须是连续的
            if incr > 0 \
                    and self.map[top_point[0] - incr][top_point[1] + incr] \
                    != self.map[top_point[0] - incr + 1][top_point[1] + incr - 1]:
                tmp = 0
            tmp += self.map[top_point[0] - incr][top_point[1] + incr]
            if abs(tmp) >= 5:
                self.win_mode = 4
                self.win_x = top_point[0] - incr
                self.win_y = top_point[1] + incr
                print('success mode 4:', top_point[0] - incr, top_point[1] + incr)
                return last_step[0]
        return 0

    # 判断本局是否结束
    def __check_(self):
        # 所有步数已经走完
        if len(self.move_stack) >= self.map_size ** 2:
            return G_FINISH
        # 赢了
        temp = self.__check_winner_()
        if temp != 0:
            print('落子：',temp)
            global winner
            winner = temp
            return G_WIN
        # 未结束
        return G_OK

    # 落子，走一步棋
    def move(self, x, y):
        if self.status != 1 and self.status != 2:
            return G_STAT_ERR
        if self.map_size <= x or x < 0 \
                or self.map_size <= y or y < 0:
            return G_RANGE_ERR
        if self.map[x][y] != 0:
            return G_POS_PLACED

        t = 1 if self.status == 1 else -1
        self.map[x][y] = t
        self.move_stack.append((t, x, y))

        # 判断是否结束
        ret = self.__check_()
        if self.is_finish(ret):
            if ret == G_WIN:
                self.__set_status(3)
            else:
                self.__set_status(4)
            return ret

        # 切换状态
        last_step = self.move_stack[-1]
        stat = 2 if last_step[0] == 1 else 1
        self.__set_status(stat)
        return G_OK

    def __set_status(self, stat):
        self.status = stat

    def is_finish(self, err_code):
        if err_code == G_FINISH \
                or err_code == G_WIN:
            return True
        return False

    # 悔一步棋
    def rollback(self):
        if len(self.move_stack) == 0:
            return G_ERR
        step = self.move_stack.pop()
        self.map[step[1]][step[2]] = 0
        # 刷新当前状态
        if step[0] == 1:  # 如果当前悔的是黑棋，那么状态切换为等待黑棋落子
            self.status = 1
        elif step[0] == -1:
            self.status = 2
        else:
            return G_ERR
        return G_OK

    # 获取当前状态
    # 0 ~ 未开局
    # 1 ~ 等待黑棋落子
    # 2 ~ 等待白棋落子
    # 3 ~ 结束（一方获胜）
    # 4 ~ 结束（棋盘走满）
    def get_status(self):
        return self.status

    def get_move_stack(self):
        return self.move_stack

class TigerGoBang(GoBang):
    # 定义游戏相关参数
    def __init__(self, map_size=15, map_unit=45):
        global winner
        winner = 0
        # self.mixer = 1  # 背景音乐
        # self.music = 1  # 落子声音
        self.SIZE = map_size
        self.UNIT = map_unit
        self.TITLE = '五子棋游戏'
        self.PANEL_WIDTH = 220  # 右侧面板宽度
        self.BORDER_WIDTH = 35  # 预留宽度
        self.LINE_WIDTH = 4  # 边缘宽度
        self.INSIDE_WIDTH = 4  # 边框跟实际的棋盘之间的间隔
        self.BODER_LENTH = self.UNIT * (self.SIZE - 1) + self.INSIDE_WIDTH * 2 + self.LINE_WIDTH * 2  # 边框线的长度
        self.OUTER_SIDE = self.BORDER_WIDTH - self.INSIDE_WIDTH - self.LINE_WIDTH

        # 计算棋盘的有效范围
        self.RANGE_X = [self.BORDER_WIDTH, self.BORDER_WIDTH + (self.SIZE - 1) * self.UNIT]
        self.RANGE_Y = [self.BORDER_WIDTH, self.BORDER_WIDTH + (self.SIZE - 1) * self.UNIT]
        # 计算状态面板的有效范围
        self.PANEL_X = [self.BORDER_WIDTH + (self.SIZE - 1) * self.UNIT,
                        self.BORDER_WIDTH + (self.SIZE - 1) * self.UNIT + self.PANEL_WIDTH]
        self.PANEL_Y = [self.BORDER_WIDTH, self.BORDER_WIDTH + (self.SIZE - 1) * self.UNIT]

        # 计算窗口大小
        self.WINDOW_WIDTH = self.BORDER_WIDTH * 2 \
                            + self.PANEL_WIDTH \
                            + (self.SIZE - 1) * self.UNIT
        self.WINDOW_HEIGHT = self.BORDER_WIDTH * 2 \
                             + (self.SIZE - 1) * self.UNIT

        # 父类初始化
        super(TigerGoBang, self).__init__(map_size=map_size)
        # 初始化游戏
        self.__game_init_()

    # 绘制棋盘
    def __draw_map(self):
        # 绘制棋盘
        POS_START = [self.BORDER_WIDTH, self.BORDER_WIDTH]

        s_font = pygame.font.SysFont('arial', 15, True)

        # 绘制行
        for item in range(0, self.SIZE):
            pygame.draw.line(self.screen, c_line,
                             [POS_START[0], POS_START[1] + item * self.UNIT],
                             [POS_START[0] + (self.SIZE - 1) * self.UNIT, POS_START[1] + item * self.UNIT],
                             2)
            s_surface = s_font.render(f'{item + 1}', True, c_line)
            self.screen.blit(s_surface, [POS_START[0] - 27, POS_START[1] + item * self.UNIT - 9])

        # 绘制列
        for item in range(0, self.SIZE):
            pygame.draw.line(self.screen, c_line,
                             [POS_START[0] + item * self.UNIT, POS_START[1]],
                             [POS_START[0] + item * self.UNIT, POS_START[1] + (self.SIZE - 1) * self.UNIT],
                             2)
            s_surface = s_font.render(chr(ord('A') + item), True, c_line)
            self.screen.blit(s_surface, [POS_START[0] + item * self.UNIT - 5, POS_START[1] - 25])

        # 画棋盘网格线外的边框
        pygame.draw.rect(self.screen, c_line, (self.OUTER_SIDE, self.OUTER_SIDE, self.BODER_LENTH, self.BODER_LENTH),
                         self.LINE_WIDTH)
        # 画天元及其他四个星
        pygame.draw.circle(self.screen, c_line, (POS_START[0] + self.UNIT * 7, POS_START[0] + self.UNIT * 7), 6, 0)
        pygame.draw.circle(self.screen, c_line, (POS_START[0] + self.UNIT * 3, POS_START[0] + self.UNIT * 3), 6, 0)
        pygame.draw.circle(self.screen, c_line, (POS_START[0] + self.UNIT * 11, POS_START[0] + self.UNIT * 3), 6, 0)
        pygame.draw.circle(self.screen, c_line, (POS_START[0] + self.UNIT * 3, POS_START[0] + self.UNIT * 11), 6, 0)
        pygame.draw.circle(self.screen, c_line, (POS_START[0] + self.UNIT * 11, POS_START[0] + self.UNIT * 11), 6, 0)

    # 绘制棋子
    def __draw_chess(self):
        mst = self.get_move_stack()
        for item in mst:
            x = self.BORDER_WIDTH + item[1] * self.UNIT
            y = self.BORDER_WIDTH + item[2] * self.UNIT
            t_color = BLACK if item[0] == 1 else WHITE
            pygame.draw.circle(self.screen, t_color, [x, y], int(self.UNIT / 2.5))

    def __draw_win_line(self):
        if winner != 0:
            if self.win_mode == 1:
                # t[0] * self.UNIT + self.BORDER_WIDTH, t[1] * self.UNIT + self.BORDER_WIDTH
                for i in range(5):
                    x = 35 + 45 * self.win_x
                    y = 35 + 45 * (self.win_y - i)
                    pygame.draw.circle(self.screen, GREEN, [x, y], int(45 / 6.5))
            elif self.win_mode == 2:
                for i in range(5):
                    x = 35 + 45 * (self.win_x - i)
                    y = 35 + 45 * self.win_y
                    pygame.draw.circle(self.screen, GREEN, [x, y], int(45 / 6.5))
            elif self.win_mode == 3:
                for i in range(5):
                    x = 35 + 45 * (self.win_x - i)
                    y = 35 + 45 * (self.win_y - i)
                    pygame.draw.circle(self.screen, GREEN, [x, y], int(45 / 6.5))
            elif self.win_mode == 4:
                for i in range(5):
                    x = 35 + 45 * (self.win_x + i)
                    y = 35 + 45 * (self.win_y - i)
                    pygame.draw.circle(self.screen, GREEN, [x, y], int(45 / 6.5))

    # 全部重绘
    def __redraw_all(self):
        # 重刷背景图
        # self.screen.blit(pygame.image.load(r"bg.jpg"), (0, 0))
        self.screen.fill(c_background)
        # 绘制棋盘
        self.__draw_map()
        # 绘制棋子
        self.__draw_chess()
        # 绘制面板
        self.__draw_panel_()
        # 绘制胜利点位
        self.__draw_win_line()

    # 初始化pygame
    def __game_init_(self):
        pygame.init()
        # 设置窗口的大小，单位为像素
        self.screen = pygame.display.set_mode((self.WINDOW_WIDTH, self.WINDOW_HEIGHT))
        # 设置窗口标题
        pygame.display.set_caption(self.TITLE)
        # 设置背景颜色
        self.screen.fill(c_background)
        # background = pygame.image.load(r"bg.jpg")
        # self.screen.blit(background, (0, 0))

        # 加载音效文件
        self.sound_black = pygame.mixer.Sound('1.wav')
        self.sound_white = pygame.mixer.Sound('2.wav')
        self.sound_win = pygame.mixer.Sound('WIN.wav')
        self.sound_error = pygame.mixer.Sound('4.wav')
        self.sound_button = pygame.mixer.Sound('btn.mp3')

        # 绘制棋盘
        self.__draw_map()
        # 绘制右侧的状态面板
        self.__draw_panel_()

    # panel区域重绘，用黄色矩形覆盖
    def __draw_panel_(self):
        pygame.draw.rect(self.screen, c_background,
                         [self.PANEL_X[0] + 30, 0,
                          1000, 1000])
        # 放置棋盒图片
        pt = pygame.image.load(r"he.png")
        self.screen.blit(pt, [self.PANEL_X[0] + 30, self.PANEL_Y[0] + 70])

        self.panel_font = pygame.font.SysFont('dengxian', 23, True)

        # 走棋状态
        stat = self.get_status()
        if stat == 0:
            stat_str = '请选择游戏模式'
        elif stat == 1:
            if mode == 1:
                stat_str = '等待黑棋落子..'
            elif mode == 2:
                stat_str = '等待玩家落子..'
        elif stat == 2:
            stat_str = '等待白棋落子..'
        elif stat == 4:
            stat_str = '游戏结束！'
        elif stat == 3:
            if winner == 1:
                stat_str = '黑棋获胜！'
            else:
                stat_str = '白棋获胜！'
        else:
            stat_str = ''
        self.surface_stat = self.panel_font.render(stat_str, False, BLUE)
        self.screen.blit(self.surface_stat, [self.PANEL_X[0] + 24, self.PANEL_Y[0]+26])

        # 步数
        steps = self.get_steps()
        self.surface_steps = self.panel_font.render(f'步数: {steps}', False, RED)
        self.screen.blit(self.surface_steps, [self.PANEL_X[0] + 40, self.PANEL_Y[0] -16])

        # 设置按钮位置信息
        offset_x = self.PANEL_X[0] + 50
        offset_y = self.PANEL_Y[0] + 380
        btn_h = 50
        btn_w = 150
        btn_gap = 20
        btn_text_x = 30
        btn_text_y = 13
        #
        # # 双人对战
        # self.BTN_RANGE_DOUBLE_X = [offset_x, offset_x + btn_w]
        # self.BTN_RANGE_DOUBLE_Y = [offset_y - (btn_h + btn_gap) * 3,
        #                                 offset_y - (btn_h + btn_gap) * 3 + btn_h]
        # if mode == 1:
        #     pygame.draw.rect(self.screen, WHITE,
        #                      [offset_x, offset_y - (btn_h + btn_gap) * 3,
        #                       btn_w, btn_h], 4)
        #     self.surface_btn = self.panel_font.render(f'双人对战', False, WHITE)
        #     self.screen.blit(self.surface_btn,
        #                      [offset_x + btn_text_x, offset_y - (btn_h + btn_gap) * 3 + btn_text_y])
        # else:
        #     pygame.draw.rect(self.screen, BLACK,
        #                      [offset_x, offset_y - (btn_h + btn_gap) * 3,
        #                       btn_w, btn_h], 4)
        #     self.surface_btn = self.panel_font.render(f'双人对战', False, BLACK)
        #     self.screen.blit(self.surface_btn,
        #                      [offset_x + btn_text_x, offset_y - (btn_h + btn_gap) * 3 + btn_text_y])

        # 人机对战
        self.BTN_RANGE_MAC_X = [offset_x, offset_x + btn_w / 2 - 5]
        self.BTN_RANGE_MAC_Y = [offset_y - btn_h - btn_gap,
                                        offset_y - btn_h - btn_gap + btn_h]
        if mode == 2:
            pygame.draw.rect(self.screen, WHITE,
                             [offset_x, offset_y - btn_h - btn_gap,
                              btn_w / 2 - 5, btn_h], 4)
            self.surface_btn = self.panel_font.render(f'人机', False, WHITE)
            self.screen.blit(self.surface_btn,
                             [offset_x + btn_text_x - 15, offset_y - btn_h - btn_gap + btn_text_y])
        else:
            pygame.draw.rect(self.screen, GREEN,
                             [offset_x, offset_y - btn_h - btn_gap,
                              btn_w / 2 - 5, btn_h], 4)
            self.surface_btn = self.panel_font.render(f'人机', False, RED)
            self.screen.blit(self.surface_btn,
                             [offset_x + btn_text_x - 15, offset_y - btn_h - btn_gap + btn_text_y])

        # 双人对战
        self.BTN_RANGE_DOUBLE_X = [offset_x + btn_w / 2 + 5, offset_x + btn_w]
        self.BTN_RANGE_DOUBLE_Y = [offset_y - btn_h - btn_gap,
                                        offset_y - btn_h - btn_gap + btn_h]
        if mode == 2 or mode == 0:
            pygame.draw.rect(self.screen, GREEN,
                             [offset_x + btn_w / 2 + 5, offset_y - btn_h - btn_gap,
                              btn_w / 2 - 5, btn_h], 4)
            self.surface_btn = self.panel_font.render(f'双人', False, RED)
            self.screen.blit(self.surface_btn,
                             [offset_x + btn_text_x + 65, offset_y - btn_h - btn_gap + btn_text_y])
        else:
            pygame.draw.rect(self.screen, WHITE,
                             [offset_x + btn_w / 2 + 5, offset_y - btn_h - btn_gap,
                              btn_w / 2 - 5, btn_h], 4)
            self.surface_btn = self.panel_font.render(f'双人', False, WHITE)
            self.screen.blit(self.surface_btn,
                             [offset_x + btn_text_x + 65, offset_y - btn_h - btn_gap + btn_text_y])

        # 认输
        self.BTN_RANGE_GIVE_UP_X = [offset_x, offset_x + btn_w]
        self.BTN_RANGE_GIVE_UP_Y = [offset_y, offset_y + btn_h]
        pygame.draw.rect(self.screen, GREEN,
                         [offset_x, offset_y,
                          btn_w, btn_h], 4)
        self.surface_btn = self.panel_font.render(f'认       输', False, RED)
        self.screen.blit(self.surface_btn, [offset_x + btn_text_x, offset_y + btn_text_y])


        # 悔棋
        self.BTN_RANGE_RB_X = [offset_x, offset_x + btn_w]
        self.BTN_RANGE_RB_Y = [offset_y + btn_h + btn_gap,
                                        offset_y + btn_h + btn_gap + btn_h]
        pygame.draw.rect(self.screen, GREEN,
                         [offset_x, offset_y + btn_h + btn_gap,
                          btn_w, btn_h], 4)
        self.surface_btn = self.panel_font.render(f'悔       棋', False, RED)
        self.screen.blit(self.surface_btn,
                         [offset_x + btn_text_x, offset_y + btn_h + btn_gap + btn_text_y])

        # 重新开始
        self.BTN_RANGE_NEW_START_X = [offset_x, offset_x + btn_w]
        self.BTN_RANGE_NEW_START_Y = [offset_y + (btn_h + btn_gap) * 2,
                                        offset_y + (btn_h + btn_gap) * 2 + btn_h]
        pygame.draw.rect(self.screen, GREEN,
                         [offset_x, offset_y + (btn_h + btn_gap) * 2,
                          btn_w, btn_h], 4)
        self.surface_btn = self.panel_font.render(f'重新开始', False, RED)
        self.screen.blit(self.surface_btn,
                         [offset_x + btn_text_x, offset_y + (btn_h + btn_gap) * 2 + btn_text_y])

        # 游戏说明
        # self.BTN_RANGE_Inform_GAME_X = [811, 832]
        # self.BTN_RANGE_Inform_GAME_Y = [16, 38]
        # pt = pygame.image.load(r"mixer.png")
        # self.screen.blit(pt, [self.PANEL_X[0] + 152, self.PANEL_Y[0] - 18])
        # pygame.draw.rect(self.screen, GREEN,
        #                  [offset_x, offset_y + (btn_h + btn_gap) * 2,
        #                   btn_w, btn_h], 4)
        # self.surface_btn = self.panel_font.render(f'游戏说明', False, RED)
        # self.screen.blit(self.surface_btn,
        #                  [offset_x + btn_text_x, offset_y + (btn_h + btn_gap) * 2 + btn_text_y])

        # 退出游戏
        self.BTN_RANGE_EXIT_GAME_X = [offset_x, offset_x + btn_w]
        self.BTN_RANGE_EXIT_GAME_Y = [offset_y + (btn_h + btn_gap) * 3,
                                      offset_y + (btn_h + btn_gap) * 3 + btn_h]
        pygame.draw.rect(self.screen, GREEN,
                         [offset_x, offset_y + (btn_h + btn_gap) * 3,
                          btn_w, btn_h], 4)
        self.surface_btn = self.panel_font.render(f'退出游戏', False, RED)
        self.screen.blit(self.surface_btn,
                         [offset_x + btn_text_x, offset_y + (btn_h + btn_gap) * 3 + btn_text_y])

        # 位置坐标
        m_w = 25
        m_h = 25
        m_gap = 10
        offset_xm = self.PANEL_X[0] + 180
        offset_ym = self.PANEL_Y[0] - 20

        # 提示框
        self.BTN_RANGE_Inform_GAME_X = [811, 832]
        self.BTN_RANGE_Inform_GAME_Y = [16, 38]
        pygame.draw.rect(self.screen, YELLOW,
                         [offset_xm - m_w - m_gap, offset_ym,
                          m_w, m_h], 3)
        pt = pygame.image.load(r"2.png")
        self.screen.blit(pt, [self.PANEL_X[0] + 148, self.PANEL_Y[0] - 17])

        # 音效框
        self.BTN_RANGE_STOP_MIXER_X = [offset_xm, offset_xm + m_w]
        self.BTN_RANGE_STOP_MIXER_Y = [offset_ym, offset_ym + m_h]
        pygame.draw.rect(self.screen, YELLOW,
                         [offset_xm, offset_ym,
                          m_w, m_h], 3)
        # 放置背景音乐图片
        pt = pygame.image.load(r"music.png")
        self.screen.blit(pt, [self.PANEL_X[0] + 183, self.PANEL_Y[0] - 18])
        if mixer == 0:
            pygame.draw.line(self.screen, YELLOW,
                             (self.PANEL_X[0] + 180, self.PANEL_Y[0] - 18),
                             (self.PANEL_X[0] + 205, self.PANEL_Y[0] + 2), 4)

        # 音乐框
        self.BTN_RANGE_STOP_MUSIC_X = [offset_xm + m_w + m_gap, offset_xm + m_w * 2 + m_gap]
        self.BTN_RANGE_STOP_MUSIC_Y = [offset_ym, offset_ym + m_h]
        pygame.draw.rect(self.screen, YELLOW,
                         [offset_xm + m_w + m_gap, offset_ym,
                          m_w, m_h], 3)
        # 放置落子音效图片
        pt = pygame.image.load(r"mixer.png")
        self.screen.blit(pt, [self.PANEL_X[0] + 222, self.PANEL_Y[0] - 18])
        if music == 0:
            pygame.draw.line(self.screen, YELLOW,
                             (self.PANEL_X[0] + 215, self.PANEL_Y[0] - 18),
                             (self.PANEL_X[0] + 240, self.PANEL_Y[0] + 2), 4)

    def __do_move_(self, pos):
        # 落子在棋盘之外无效
        if pos[0] < self.RANGE_X[0] - 20 or pos[0] > self.RANGE_X[1] + 20 \
                or pos[1] < self.RANGE_Y[0] - 20 or pos[1] > self.RANGE_Y[1] + 20:
            self.sound_error.play()
            return G_ERR

        # 播放落子音效
        if music == 1:
            if self.get_status() == 1:  # 黑棋
                self.sound_black.set_volume(0.4)
                self.sound_black.play()
            else:  # 白棋
                self.sound_white.set_volume(4.0)
                self.sound_white.play()
        # 判断当前落子的位置,需要吸附在最近的落棋点
        s_x = round((pos[0] - self.BORDER_WIDTH) / self.UNIT)
        s_y = round((pos[1] - self.BORDER_WIDTH) / self.UNIT)
        print(self.status, s_x, s_y)
        x = self.BORDER_WIDTH + self.UNIT * s_x
        y = self.BORDER_WIDTH + self.UNIT * s_y
        # 先move，再draw
        ret = self.move(s_x, s_y)
        if ret < 0:
            self.sound_error.play()
            return G_ERR
        # draw
        last_move = self.get_last_move()
        t_color = BLACK if last_move[0] == 1 else WHITE
        pygame.draw.circle(self.screen, t_color, [x, y], int(self.UNIT / 2.5))
        # pygame.draw.circle(self.screen, BLACK, [x, y], int(self.UNIT / 2.5), 1)

        self.__redraw_all()

        if self.get_status() >= 3:
            self.sound_win.set_volume(0.2)
            self.sound_win.play()

        if mode == 2 and self.status == 2:
            m = self.get_last_move()[1]
            n = self.get_last_move()[2]
            t = ai.BetaGo(self.map, m, n, -1, self.times)
            self.times += 1
            print('机器落子:', t)
            # 逻辑坐标转为棋盘物理坐标
            p = (t[0] * self.UNIT + self.BORDER_WIDTH, t[1] * self.UNIT + self.BORDER_WIDTH)
            print(p)
            self.__do_move_(p)
        return G_OK

    # 执行悔棋功能
    def __do_rollback_(self):
        print('悔棋：', winner)
        self.sound_button.play()
        if winner == 0:
            if self.rollback() == G_OK:
                self.__redraw_all()
            if mode == 2 and self.status == 2:
                if self.rollback() == G_OK:
                    self.__redraw_all()

    # 执行新开一局
    def __do_new_start(self):
        print('1:', self.status)
        self.__init__()
        print('2:', self.status)
        if music == 1:
            self.sound_button.play()
        self.start()

    def __do_inform_(self):
        root = Tk()
        root.wm_withdraw()
        text = '五子棋是世界智力运动会竞技项目之一，是一种两人对弈的纯策略型棋类游戏，是世界智力运动会竞技项目之一，' \
               '通常双方分别使用黑白两色的棋子，下在棋盘直线与横线的交叉点上，先形成5子连线者获胜。\n\n' \
               '棋具与围棋通用，起源于中国上古时代的传统黑白棋种之一。主要流行于华人和汉字文化圈的国家以及欧美一些地区，是世界上最古老的棋。\n\n' \
               '容易上手，老少皆宜，而且趣味横生，引人入胜；不仅能增强思维能力，提高智力，而且富含哲理，有助于修身养性。已在各个游戏平台有应用。\n\n'
        messagebox.showinfo('游戏说明', text)
        root.destroy()

    def __do_mousemove_(self, pos):
        # 在panel区域内才显示，并且已经有棋子的地方不显示
        # 判断当前鼠标的位置,需要吸附在最近的落棋点
        s_x = round((pos[0] - self.BORDER_WIDTH) / self.UNIT)
        s_y = round((pos[1] - self.BORDER_WIDTH) / self.UNIT)
        x = self.BORDER_WIDTH + self.UNIT * s_x
        y = self.BORDER_WIDTH + self.UNIT * s_y
        self.__redraw_all()
        if 30 <= x <= 665 and 30 <= y <= 665 and self.map[s_x][s_y] == 0:
            pygame.draw.circle(self.screen, RED, [x, y], int(self.UNIT / 6.5))

    # 认输
    def __do_give_up_(self):
        self.sound_button.play()
        if self.move_stack:  # 未下棋时不能认输
            self.status = 3
            global winner
            winner = self.get_last_move()[0]
            self.__redraw_all()
            self.sound_win.set_volume(0.2)
            self.sound_win.play()

    # 是否点击了按钮
    def __do_btn_(self, pos):
        global mode
        if self.BTN_RANGE_NEW_START_X[0] < pos[0] < self.BTN_RANGE_NEW_START_X[1] \
                and self.BTN_RANGE_NEW_START_Y[0] < pos[1] < self.BTN_RANGE_NEW_START_Y[1]:
            # 鼠标点击的位置坐标，落在“重新开始”方框内
            mode = 0
            self.__do_new_start()
            return G_OK
        elif self.BTN_RANGE_DOUBLE_X[0] < pos[0] < self.BTN_RANGE_DOUBLE_X[1] \
                and self.BTN_RANGE_DOUBLE_Y[0] < pos[1] < self.BTN_RANGE_DOUBLE_Y[1]:
            # 双人
            self.start_move()
            mode = 1
            self.status = 1
            self.__do_new_start()
            return G_OK
        elif self.BTN_RANGE_MAC_X[0] < pos[0] < self.BTN_RANGE_MAC_X[1] \
                and self.BTN_RANGE_MAC_Y[0] < pos[1] < self.BTN_RANGE_MAC_Y[1]:
            # 落在“人机模式”方框内，切换模式
            self.start_move()
            mode = 2
            self.status = 1
            self.__do_new_start()
            return G_OK
        elif self.BTN_RANGE_GIVE_UP_X[0] < pos[0] < self.BTN_RANGE_GIVE_UP_X[1] \
                and self.BTN_RANGE_GIVE_UP_Y[0] < pos[1] < self.BTN_RANGE_GIVE_UP_Y[1]:
            # 落在“认输”方框内
            self.__do_give_up_()
            return G_OK
        elif self.BTN_RANGE_Inform_GAME_X[0] < pos[0] < self.BTN_RANGE_Inform_GAME_X[1] \
                and self.BTN_RANGE_Inform_GAME_Y[0] < pos[1] < self.BTN_RANGE_Inform_GAME_Y[1]:
            # 落在“游戏说明”方框内
            self.__do_inform_()
            return G_OK
        elif self.BTN_RANGE_EXIT_GAME_X[0] < pos[0] < self.BTN_RANGE_EXIT_GAME_X[1] \
                and self.BTN_RANGE_EXIT_GAME_Y[0] < pos[1] < self.BTN_RANGE_EXIT_GAME_Y[1]:
            sys.exit()
        elif self.BTN_RANGE_RB_X[0] < pos[0] < self.BTN_RANGE_RB_X[1] \
                and self.BTN_RANGE_RB_Y[0] < pos[1] < self.BTN_RANGE_RB_Y[1]:
            self.__do_rollback_()
            return G_OK
        elif self.BTN_RANGE_STOP_MIXER_X[0] < pos[0] < self.BTN_RANGE_STOP_MIXER_X[1] \
                and self.BTN_RANGE_STOP_MIXER_Y[0] < pos[1] < self.BTN_RANGE_STOP_MIXER_Y[1]:
            # 停止背景音乐
            global mixer
            if mixer == 1:
                pygame.draw.line(self.screen, YELLOW,
                                 (self.PANEL_X[0] + 180, self.PANEL_Y[0] - 18),
                                 (self.PANEL_X[0] + 205, self.PANEL_Y[0] + 2), 4)
                pygame.mixer.music.pause()
                mixer = 0
            else:
                mixer = 1
                self.__redraw_all()
                pygame.mixer.music.play(-1, 0)
            return G_OK
        elif self.BTN_RANGE_STOP_MUSIC_X[0] < pos[0] < self.BTN_RANGE_STOP_MUSIC_X[1] \
                and self.BTN_RANGE_STOP_MUSIC_Y[0] < pos[1] < self.BTN_RANGE_STOP_MUSIC_Y[1]:
            global music
            if music == 1:
                pygame.draw.line(self.screen, YELLOW,
                                 (self.PANEL_X[0] + 215, self.PANEL_Y[0] - 18),
                                 (self.PANEL_X[0] + 240, self.PANEL_Y[0] + 2), 4)
                music = 0
            else:
                music = 1
                self.__redraw_all()
            return G_OK
        # [self.PANEL_X[0] + 130, self.PANEL_Y[0]]
        elif self.PANEL_X[0] + 30 < pos[0] < self.PANEL_X[0] + 250 \
                and self.PANEL_Y[0] + 40 < pos[1] < self.PANEL_Y[0] + 200:
            # 点击围棋图标
            root = tkinter.Tk()
            img = Image.open("bqb.jpg")  # 打开图片
            photo = ImageTk.PhotoImage(img)  # 使用ImageTk的PhotoImage方法
            tkinter.Label(master=root, image=photo).grid(row=0, column=0)
            root.mainloop()
            # root.destroy()
            return G_OK
        else:
            return G_ERR

    def start(self):
        # self.start_move()
        pygame.mixer.music.load("BGM.wav")  # 载入背景音乐
        pygame.mixer.music.set_volume(0.4)
        if mixer == 1:
            pygame.mixer.music.play(-1, 0)  # 开始播放bgm

        # 程序主循环
        while True:
            # 获取事件
            for event in pygame.event.get():
                # 判断事件是否为退出事件
                if event.type == QUIT:
                    # 退出pygame
                    pygame.quit()
                    # 退出系统
                    sys.exit()
                # 鼠标移动事件
                if event.type == MOUSEMOTION:
                    self.__do_mousemove_(event.pos)
                # 鼠标点击事件
                if event.type == MOUSEBUTTONUP:
                    # print(event.pos)
                    if self.__do_btn_(event.pos) < 0:
                        # 非按钮事件，则处理走棋
                        if event.button == 1:
                            if mode == 1 or (mode == 2 and self.status == 1):
                                self.__do_move_(event.pos)
                        # elif event.button == 3 and self.status == 2 and mode == 2:
                        #     # ai走棋
                        #     m = self.get_last_move()[1]
                        #     n = self.get_last_move()[2]
                        #     t = ai.BetaGo(self.map, m, n, -1, self.times)
                        #     self.times += 1
                        #     print('机器落子:', t)
                        #     # 逻辑坐标转为棋盘物理坐标
                        #     p = (t[0] * self.UNIT + self.BORDER_WIDTH, t[1] * self.UNIT + self.BORDER_WIDTH)
                        #     self.__do_move_(p)
            # 绘制屏幕内容
            pygame.display.update()


# class TestDialog(gui.Dialog):
#     def __init__(this):
#         title = gui.Label("Some Dialog Box")
#         label = gui.Label("Close this window to resume.")
#         gui.Dialog.__init__(this, title, label)


if __name__ == '__main__':
    mode = 0
    inst1 = TigerGoBang(map_unit=45)
    inst1.start()
