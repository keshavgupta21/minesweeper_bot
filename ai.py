import pygame
from pygame.locals import *
from sdlBased import SDLBoard
from time import sleep

class MineSweeper:
    def __init__(self, board):
        self.board = board
        self.bombSquares = set()
        self.safeSquares = set()
        self.lastUncovered = set()
        self.boundary = set()
        self.newBoundary = set()
        self.coveredSquares = {(x, y) for x in range(self.board.width) for y in range(self.board.height)}

    def getFlagNeighbors(self, x, y):
        flagNeighbors = set()
        for (dx, dy) in [(0, 1), (-1, 1), (-1, 0), (-1, -1), (0, -1), (1, 0), (1, -1), (1, 1)]:
            (x_, y_) = (x + dx, y + dy)
            if 0 <= x_ < self.board.width and 0 <= y_ < self.board.height and (x_, y_) in self.bombSquares and self.board.board2D[y_][x_] is None:
                flagNeighbors.add((x_, y_))
        return flagNeighbors

    def getNonFlagNeighbors(self, x, y):
        nonFlagNeighbors = set()
        for (dx, dy) in [(0, 1), (-1, 1), (-1, 0), (-1, -1), (0, -1), (1, 0), (1, -1), (1, 1)]:
            (x_, y_) = (x + dx, y + dy)
            if 0 <= x_ < self.board.width and 0 <= y_ < self.board.height and (x_, y_) not in self.bombSquares and self.board.board2D[y_][x_] is None:
                nonFlagNeighbors.add((x_, y_))
        return nonFlagNeighbors

    def get9Squares(self, x, y):
        allNeighbors = set()
        for (dx, dy) in [(0, 1), (-1, 1), (-1, 0), (0, 0), (-1, -1), (0, -1), (1, 0), (1, -1), (1, 1)]:
            (x_, y_) = (x + dx, y + dy)
            if 0 <= x_ < self.board.width and 0 <= y_ < self.board.height:
                allNeighbors.add((x_, y_))
        return allNeighbors

    def step(self, iterations = 1):
        self.board.update2DBoard()
        boundary = set()
        for (x, y) in self.lastUncovered:
            boundary |= self.get9Squares(x, y)
        boundary -= self.lastUncovered
        self.newBoundary = set()
        for (x, y) in boundary:
            self.newBoundary |= self.get9Squares(x, y)
        self.newBoundary &= self.lastUncovered
        self.boundary |= self.newBoundary
        for _ in range(iterations):
            for (x, y) in self.boundary:
                val = self.board.board2D[y][x]
                flagNeighbors = self.getFlagNeighbors(x, y)
                nonFlagNeighbors = self.getNonFlagNeighbors(x, y)
                if val == len(nonFlagNeighbors) + len(flagNeighbors):
                    for (x_, y_) in nonFlagNeighbors:
                        self.bombSquares.add((x_, y_))
                if val == len(flagNeighbors):
                    for (x_, y_) in nonFlagNeighbors:
                        self.safeSquares.add((x_, y_))
        if self.safeSquares:
            self.lastUncovered = set()
            for (bestX, bestY) in self.safeSquares:
                self.lastUncovered |= self.board.dig(bestX, bestY)
            self.safeSquares = set()
        else:
            for (bestX, bestY) in self.coveredSquares:
                break
            self.lastUncovered = self.board.dig(bestX, bestY)
        if self.lastUncovered is not None:
            self.coveredSquares -= self.lastUncovered

if __name__ == "__main__":
    width = 100
    height = 100
    bombs = 1000
    mineSize = 5
    sdlBoard = SDLBoard(width, height, bombs, mineSize)
    minesweeper = MineSweeper(sdlBoard)
    i = 0
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                exit()
        try:
            print(eval(y))
        except:
            pass
        minesweeper.step()
        sdlBoard.check()
        i += 1
        if i % 1 == 0:
            sdlBoard.refreshScreen(minesweeper.bombSquares, minesweeper.safeSquares, minesweeper.newBoundary)
        if sdlBoard.state != "ongoing":
            sdlBoard.updateState()
            sleep(1)
            exit()
