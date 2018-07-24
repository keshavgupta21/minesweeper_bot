import pygame
from pygame.locals import *
from sdlBased import SDLBoard
from time import sleep

class MineSweeper:
    def __init__(self, board):
        self.board = board
        self.safeSquares = set()
        self.bombSquares = set()
        self.uncovered = set()
        self.allSquares = {(x, y) for x in range(self.board.width) for y in range(self.board.height)}
        self.boundary = set()

    def getBombNeighbors(self, (x, y)):
        s = set()
        for (dx, dy) in [(0, 1), (-1, 1), (-1, 0), (-1, -1), (0, -1), (1, 0), (1, -1), (1, 1)]:
            x_ = x + dx
            y_ = y + dy
            if 0 <= x_ < self.board.width and 0 <= y_ < self.board.height and self.board.board2D[y_][x_] is None and (x_, y_) in self.bombSquares:
                s.add((x_, y_))
        return s

    def getNonBombNeighbors(self, (x, y)):
        s = set()
        for (dx, dy) in [(0, 1), (-1, 1), (-1, 0), (-1, -1), (0, -1), (1, 0), (1, -1), (1, 1)]:
            x_ = x + dx
            y_ = y + dy
            if 0 <= x_ < self.board.width and 0 <= y_ < self.board.height and self.board.board2D[y_][x_] is None and (x_, y_) not in self.bombSquares:
                s.add((x_, y_))
        return s

    def get9Block(self, (x, y)):
        s = set()
        for (dx, dy) in [(0, 1), (-1, 1), (0, 0), (-1, 0), (-1, -1), (0, -1), (1, 0), (1, -1), (1, 1)]:
            x_ = x + dx
            y_ = y + dy
            if 0 <= x_ < self.board.width and 0 <= y_ < self.board.height:
                s.add((x_, y_))
        return s

    def get8Block(self, (x, y)):
        s = set()
        for (dx, dy) in [(0, 1), (-1, 1), (-1, 0), (-1, -1), (0, -1), (1, 0), (1, -1), (1, 1)]:
            x_ = x + dx
            y_ = y + dy
            if 0 <= x_ < self.board.width and 0 <= y_ < self.board.height:
                s.add((x_, y_))
        return s

    def step(self, maxBorderSize = 15):
        self.board.update2DBoard()
        for (x, y) in self.uncovered:
            val = self.board.board2D[y][x]
            if val != 0:
                bombNeighbors = self.getBombNeighbors((x, y))
                nonBombNeighbors = self.getNonBombNeighbors((x, y))
                if val == len(bombNeighbors) + len(nonBombNeighbors):
                    for (x_, y_) in nonBombNeighbors:
                        self.bombSquares.add((x_, y_))
                elif val == len(bombNeighbors):
                    for (x_, y_) in nonBombNeighbors:
                        self.safeSquares.add((x_, y_))
        if self.safeSquares:
            for (bestX, bestY) in self.safeSquares:
                uncovered = self.board.dig(bestX, bestY)
                if uncovered is not None:
                    self.uncovered |= uncovered
            self.safeSquares = set()
            self.boundary = set()
        else:
            self.boundary = set()
            covered = self.allSquares - self.uncovered - self.bombSquares
            for pos in self.uncovered:
                self.boundary |= self.get9Block(pos) & covered


if __name__ == "__main__":
    width = 20
    height = 20
    bombs = 40
    mineSize = 20
    sdlBoard = SDLBoard(width, height, bombs, mineSize)
    minesweeper = MineSweeper(sdlBoard)
    i = 0
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                exit()
            elif event.type == MOUSEBUTTONDOWN and event.button == 1:
                pos = pygame.mouse.get_pos()
                minesweeper.uncovered |= sdlBoard.dig((pos[0]-5)/mineSize, (pos[1]-5)/mineSize)
        minesweeper.step()
        sdlBoard.check()
        i += 1
        if i % 1 == 0:
            sdlBoard.refreshScreen(minesweeper.bombSquares, minesweeper.safeSquares, minesweeper.boundary)
        if sdlBoard.state != "ongoing":
            sdlBoard.updateState()
            sleep(1)
            exit()
