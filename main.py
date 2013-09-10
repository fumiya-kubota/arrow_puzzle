#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pygame
from pygame.locals import *
import sys
from puzzle import puzzle

SCREEN_SIZE = (700, 500)  # 画面サイズ

def main():
    # Pygameを初期化
    pygame.init()
    # SCREEN_SIZEの画面を作成
    screen = pygame.display.set_mode(SCREEN_SIZE)
    pygame.display.set_caption('Arrow Lead')
    sysfont = pygame.font.SysFont(None, 35)
    clock = pygame.time.Clock()
    puzzleboard = puzzle.PuzzleBoard(screen, sysfont)
    while True:
        screen.fill((0, 0, 0))   # Background is white
        puzzleboard.view_puzzle_board()

        for event in pygame.event.get():
            # 終了イベント
            if event.type == QUIT:
                sys.exit()
            if event.type == KEYDOWN:
            # キーを押したとき
             # ESCキーならスクリプトを終了
                if event.key == K_ESCAPE:
                    sys.exit()
                elif event.key == K_a:
                    puzzleboard.rotate()
                elif event.key == K_s:
                    puzzleboard.rotate(True)
                elif event.key == K_UP:
                    puzzleboard.move_cursor_y('up')
                elif event.key == K_DOWN:
                    puzzleboard.move_cursor_y('down')
                elif event.key == K_RIGHT:
                    puzzleboard.move_cursor_x('right')
                elif event.key == K_LEFT:
                    puzzleboard.move_cursor_x('left')
                elif event.key == K_f:
                    puzzleboard.board_update()

        pygame.display.update()  # update display
        clock.tick(60)


if __name__ == '__main__':
    main()
