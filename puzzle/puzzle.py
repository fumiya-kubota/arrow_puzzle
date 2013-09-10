#!/usr/bin/env python
# -*- coding: utf-8 -*-
from random import random
from .resources import resource, blocksize
import pygame
from .tail_recursion import tail_recursion

LIMIT_MOVE = 100
ONE_SIDE_LENGTH = 7
EAST_BLOCK = 0
WEST_BLOCK = 1
SOUTH_BLOCK = 2
NORTH_BLOCK = 3

EAST_FRAME = 4
WEST_FRAME = 5
SOUTH_FRAME = 6
NORTH_FRAME = 7

BOARD_X = 75
BOARD_Y = 75

BLOCK_IMAGE = {
    EAST_BLOCK: resource.east_image,
    WEST_BLOCK: resource.west_image,
    SOUTH_BLOCK: resource.south_image,
    NORTH_BLOCK: resource.north_image
}
distance_pos = (450, 100)
distance_value_pos = (475, 130)

time_pos = (450, 200)
time_value_pos = (475, 230)


class PuzzleBoard(object):
    animate_time = 100
    iterate_idx = range(ONE_SIDE_LENGTH)

    def __init__(self, screen, sysfont):
        super(PuzzleBoard, self).__init__()
        self.FRAMES = frozenset([EAST_FRAME, WEST_FRAME, SOUTH_FRAME, NORTH_FRAME])
        self.COLLISION = {
            EAST_BLOCK: WEST_BLOCK,
            WEST_BLOCK: EAST_BLOCK,
            SOUTH_BLOCK: NORTH_BLOCK,
            NORTH_BLOCK: SOUTH_BLOCK
        }
        self.CONNECTION_FRAME2BLOCK = {
            WEST_FRAME: EAST_BLOCK,
            EAST_FRAME: WEST_BLOCK,
            NORTH_FRAME: SOUTH_BLOCK,
            SOUTH_FRAME: NORTH_BLOCK
        }
        self.ADVANCE_BOARD = {
            EAST_BLOCK: (1, 0),
            WEST_BLOCK: (-1, 0),
            SOUTH_BLOCK: (0, 1),
            NORTH_BLOCK: (0, -1)
        }
        self.ARROW_SHAPE = {
            (-1, 0): ((15, 9), (15, -9)),
            (1, 0): ((-15, 9), (-15, -9)),
            (0, -1): ((9, 15), (-9, 15)),
            (0, 1): ((9, -15), (-9, -15))
        }
        self.NUMBER_RENDERER = {}
        for num in '0123456789':
            self.NUMBER_RENDERER[num] = sysfont.render(num, True, (255, 255, 255))
        self.DISTANCE_LABEL = sysfont.render('Distance', True, (255, 255, 255))
        self.TIME_LABEL = sysfont.render('MOVEMENT', True, (255, 255, 255))

        self.board = self.init_puzzle_board()
        self.screen = screen
        self.moving = []
        self.flash = []
        self.select_x = 0
        self.select_y = 0
        self.flash_count = 1
        self.limit = LIMIT_MOVE
        self.distance = 0
        self.board_update()

    def view_puzzle_board(self):

        self.screen.blit(self.DISTANCE_LABEL, distance_pos)
        for idx, num in enumerate(str(self.distance)):
            self.screen.blit(self.NUMBER_RENDERER[num], (distance_value_pos[0] + idx * 20, distance_value_pos[1]))
        self.screen.blit(self.TIME_LABEL, time_pos)
        for idx, num in enumerate(str(self.limit)):
            self.screen.blit(self.NUMBER_RENDERER[num], (time_value_pos[0] + idx * 20, time_value_pos[1]))

        idx = 0
        while idx < len(self.moving):
            left, top, time, anti, ended = self.moving[idx]
            pasttime = pygame.time.get_ticks() - time
            prograss = float(pasttime) / self.animate_time
            if prograss > 1:
                self.real_rotate(left, top, anti)
                prograss = 1
                del self.moving[idx]
                idx -= 1
            lt = BLOCK_IMAGE[self.board[top][left][0]]
            lb = BLOCK_IMAGE[self.board[top + 1][left][0]]
            rb = BLOCK_IMAGE[self.board[top + 1][left + 1][0]]
            rt = BLOCK_IMAGE[self.board[top][left + 1][0]]
            x, y = BOARD_X + blocksize * left, BOARD_Y + blocksize * top
            if anti:
                self.screen.blit(lt, (x, y + prograss * blocksize))
                self.screen.blit(rt, (x + blocksize - prograss * blocksize, y))
                self.screen.blit(rb, (x + blocksize, y + blocksize - prograss * blocksize))
                self.screen.blit(lb, (x + prograss * blocksize, y + blocksize))
            else:
                self.screen.blit(lt, (x + prograss * blocksize, y))
                self.screen.blit(rt, (x + blocksize, y + prograss * blocksize))
                self.screen.blit(rb, (x + blocksize - prograss * blocksize, y + blocksize))
                self.screen.blit(lb, (x, y + blocksize - prograss * blocksize))
            idx += 1

        y = 0
        while y < ONE_SIDE_LENGTH:
            x = 0
            while x < ONE_SIDE_LENGTH:
                block, active = self.board[y][x]
                """
                if self.need_flush:
                    self.board[y][x][2] = self._flush_block(x, y)
                """
                if not active:
                    pos = (BOARD_X + blocksize * x, BOARD_Y + blocksize * y)
                    self.screen.blit(BLOCK_IMAGE[block], pos)
                x += 1
            y += 1

        if self.flash:
            self.flash_count += 1
        for succeed, course in self.flash:
            color = self._get_flush_color(course[0])
            if succeed:
                width = 6
            else:
                width = 3
            lines = [(BOARD_X + blocksize * x + blocksize / 2, BOARD_Y + blocksize * y + blocksize / 2) for x, y in course[:self.flash_count]]
            pygame.draw.lines(self.screen, color, False, lines, width)
            if self.flash_count >= len(course):
                x1, y1 = course[-2]
                x2, y2 = course[-1]
                umb1, umb2 = self.ARROW_SHAPE[(x2 - x1, y2 - y1)]
                if succeed:
                    pos = (BOARD_X + blocksize * x2 + blocksize / 2, BOARD_Y + blocksize * y2 + blocksize / 2)
                else:
                    pos = (BOARD_X + blocksize * x2 + blocksize / 2, BOARD_Y + blocksize * y2 + blocksize / 2)

                pygame.draw.line(
                    self.screen, color, pos,
                    (pos[0] + umb1[0], pos[1] + umb1[1]),
                    width
                )
                pygame.draw.line(
                    self.screen, color, pos,
                    (pos[0] + umb2[0], pos[1] + umb2[1]),
                    width
                )

        if self.flash_count > 30:
            self.flash_count = 1
            courses = [course for suc, course in self.flash if suc]
            self.flash = []
            self.distance += self.delete_block(courses)

        pygame.draw.rect(
            self.screen,
            (0, 0, 0),
            pygame.Rect(
                (BOARD_X + self.select_x * blocksize, BOARD_Y + self.select_y * blocksize),
                (blocksize * 2, blocksize * 2)
            ),
            3
        )

    def init_puzzle_board(self):
        board = [[[self._rand_block(), False] for i in xrange(ONE_SIDE_LENGTH)] for j in xrange(ONE_SIDE_LENGTH)]
        for x in board:
            x.extend(((EAST_FRAME,), (WEST_FRAME,)))
        board.append([(SOUTH_FRAME,) for i in xrange(ONE_SIDE_LENGTH)])
        board.append([(NORTH_FRAME,) for i in xrange(ONE_SIDE_LENGTH)])
        return board

    def turn_animate(self, left, top, anti):
        self.moving.append((left, top, pygame.time.get_ticks(), anti, False))

    def rotate(self, anti=False):
        if self.limit <= 0:
            return
        if not 0 <= self.select_x < ONE_SIDE_LENGTH - 1 or not 0 <= self.select_y < ONE_SIDE_LENGTH - 1:
            return
        self.board[self.select_y][self.select_x][1] =\
            self.board[self.select_y + 1][self.select_x][1] =\
            self.board[self.select_y + 1][self.select_x + 1][1] =\
            self.board[self.select_y][self.select_x + 1][1] = True
        self.turn_animate(self.select_x, self.select_y, anti)

    def real_rotate(self, left, top, anti):
        self.board[top][left][1] =\
            self.board[top + 1][left][1] =\
            self.board[top + 1][left + 1][1] =\
            self.board[top][left + 1][1] = False
        if anti:
            (
                self.board[top + 1][left],
                self.board[top + 1][left + 1],
                self.board[top][left + 1],
                self.board[top][left]) = (self.board[top][left],
                                          self.board[top + 1][left],
                                          self.board[top + 1][left + 1],
                                          self.board[top][left + 1])
        else:
            (
                self.board[top][left + 1],
                self.board[top + 1][left + 1],
                self.board[top + 1][left],
                self.board[top][left]) = (self.board[top][left],
                                          self.board[top][left + 1],
                                          self.board[top + 1][left + 1],
                                          self.board[top + 1][left])
        self.board_update()
        self.limit -= 1

    def delete_block(self, courses):
        distance = 0
        for course in courses:
            distance += len(course[1:-1])
            for x, y in course[1:-1]:

                self.board[y][x][0] = self._rand_block()
        if courses:
            self.board_update()
        return distance

    def move_cursor_x(self, direction):
        if direction is 'left':
            if self.select_x > 0:
                self.select_x -= 1
        elif direction is 'right':
            if self.select_x < ONE_SIDE_LENGTH - 2:
                self.select_x += 1
        else:
            raise NotImplementedError

    def move_cursor_y(self, direction):
        if direction is 'up':
            if self.select_y > 0:
                self.select_y -= 1
        elif direction is 'down':
            if self.select_y < ONE_SIDE_LENGTH - 2:
                self.select_y += 1
        else:
            raise NotImplementedError

    def board_update(self):
        flash = []
        for idx in self.iterate_idx:
            if self.board[0][idx][0] == SOUTH_BLOCK:
                flash.append(self._run_circuit(idx, 0, SOUTH_FRAME, [(idx, -1)]))
            if self.board[ONE_SIDE_LENGTH - 1][idx][0] == NORTH_BLOCK:
                flash.append(self._run_circuit(idx, ONE_SIDE_LENGTH - 1, NORTH_FRAME, [(idx, 7)]))
            if self.board[idx][0][0] == EAST_BLOCK:
                flash.append(self._run_circuit(0, idx, EAST_FRAME, [(-1, idx)]))
            if self.board[idx][ONE_SIDE_LENGTH - 1][0] == WEST_BLOCK:
                flash.append(self._run_circuit(ONE_SIDE_LENGTH - 1, idx, WEST_FRAME, [(7, idx)]))
        self.flash_count = 1
        self.flash = flash

    def _get_flush_color(self, point):
        x, y = point
        if x < 0:
            return (0, 255, 0)
        elif x >= ONE_SIDE_LENGTH:
            return (255, 175, 0)
        elif y < 0:
            return (50, 0, 255)
        else:
            return (255, 0, 0)

    @tail_recursion
    def _run_circuit(self, cur_x, cur_y, goal, course):
        course.append((cur_x, cur_y))
        current_block = self.board[cur_y][cur_x][0]
        if current_block == goal:
            return True, course
        elif current_block in self.FRAMES or current_block == self.COLLISION[current_block] or (cur_x, cur_y) in course[:-1]:
            return False, course[:-2]
        else:
            x, y = self.ADVANCE_BOARD[current_block]
            return self._run_circuit(cur_x + x, cur_y + y, goal, course)

    def _rand_block(self):
        val = random()
        if val < .25:
            return EAST_BLOCK
        if val > .75:
            return WEST_BLOCK
        if val < .5:
            return SOUTH_BLOCK
        return NORTH_BLOCK
