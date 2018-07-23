import pygame
from pygame.locals import *
from sdlBased import SDLBoard
from random import choice
from time import sleep

class MineSweeper:
    def __init__(self, board):
        self.board = board
        self.width = board.width
        self.height = board.height
        self.bombs = board.bombs
        self.board.showScores = False
        self.board.bombFlags = set()
        self.board.bombScores = self.getBaseScores()
        self.invisibleBlocks = set(self.board.bombScores.keys())

    def getBaseScores(self):
        return {(x, y): 1.0 - float(self.bombs - len(self.board.bombFlags))/(self.width*self.height) for x in range(self.width) for y in range(self.height)}

    def getNumFlags(self, x, y):
        count = 0
        board = self.board.get2DBoard()
        for dx in range(-1, 2):
            for dy in range(-1, 2):
                if not (dx == 0 and dy == 0):
                    x_ = x + dx
                    y_ = y + dy
                    if 0 <= x_ < self.width and 0 <= y_ < self.height and board[y_][x_] is None and (x_, y_) in self.board.bombFlags:
                        count += 1
        return count

    def getInvisibleNeighborXYs(self, x, y):
        ret = []
        board = self.board.get2DBoard()
        for dx in range(-1, 2):
            for dy in range(-1, 2):
                if not (dx == 0 and dy == 0):
                    x_ = x + dx
                    y_ = y + dy
                    if 0 <= x_ < self.width and 0 <= y_ < self.height and board[y_][x_] is None and (x_, y_) not in self.board.bombFlags:
                        ret.append((x_, y_))
        return ret

    def getVisibleNeighborXYs(self, x, y):
        ret = []
        board = self.board.get2DBoard()
        for dx in range(-1, 2):
            for dy in range(-1, 2):
                if not (dx == 0 and dy == 0):
                    x_ = x + dx
                    y_ = y + dy
                    if 0 <= x_ < self.width and 0 <= y_ < self.height and board[y_][x_] is not None:
                        ret.append((x_, y_))
        return ret

    def printScores(self):
        _str = ""
        for y in range(self.height):
            for x in range(self.width):
                p = self.bombScores[(x, y)]
                if (x, y) in self.board.bombFlags:
                    _str += " *** "
                elif p:
                    _str += "{0:0.2f} ".format(p)
                else:
                    _str += "     "
            _str += "\n"
        print(_str)

    def step(self):
        board = self.board.get2DBoard()
        self.board.bombScores = self.getBaseScores()
        for x in range(self.width):
            for y in range(self.height):
                val = board[y][x]
                if val is not None and val != 0:
                    nonFlagInvNeighbor = self.getInvisibleNeighborXYs(x, y)
                    flagNumber = self.getNumFlags(x, y)
                    if flagNumber == val:
                        for (x_, y_) in nonFlagInvNeighbor:
                            self.board.safeSquares.add((x_, y_))
                    elif nonFlagInvNeighbor:
                        pNotBomb = 1 - float(val - flagNumber)/len(nonFlagInvNeighbor)
                        for (x_, y_) in nonFlagInvNeighbor:
                            if pNotBomb == 0:
                                self.board.bombFlags.add((x_, y_))
                            self.board.bombScores[(x_, y_)] *= pNotBomb
        for x in range(self.width):
            for y in range(self.height):
                donors = max(1, len(self.getVisibleNeighborXYs(x, y)))
                self.board.bombScores[(x, y)] /= donors
        if self.board.safeSquares:
            for (x, y) in self.board.safeSquares:
                break
            self.board.dig(x, y)
            self.board.safeSquares.remove((x, y))
        else:
            playable = self.invisibleBlocks - self.board.bombFlags
            bestX, bestY = (None, None)
            highestScore = 0
            for (x, y) in playable:
                if (bestX, bestY) == (None, None):
                    (bestX, bestY) = (x, y)
                if board[y][x] is None and highestScore < self.board.bombScores[(x, y)] and (x, y) not in self.board.bombFlags:
                    highestScore = self.board.bombScores[(x, y)]
                    (bestX, bestY) = (x, y)
            self.board.dig(bestX, bestY)

if __name__ == "__main__":
    width = 20
    height = 20
    bombs = 60
    mineSize = 20
    sdlBoard = SDLBoard(width, height, bombs, mineSize)
    minesweeper = MineSweeper(sdlBoard)
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                exit()
        minesweeper.step()
        sdlBoard.check()
        sdlBoard.refreshScreen()
        if sdlBoard.state != "ongoing":
            sdlBoard.updateState()
            sleep(1)
            exit()
