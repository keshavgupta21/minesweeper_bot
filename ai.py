import pygame
from pygame.locals import *
from sdlBased import SDLBoard
from time import sleep
from random import sample

class MineSweeper:
    def __init__(self, board):
        self.board = board
        self.safeSquares = set()
        self.probablySafeSquares = []
        self.bombSquares = set()
        self.uncovered = set()
        self.allSquares = {(x, y) for x in range(self.board.width) for y in range(self.board.height)}
        self.clickedSquare = (-1, -1)

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

    def step(self, maxBorderSize = 20, clearAllSafe = False):
        if self.safeSquares:
            if clearAllSafe:
                for (bestX, bestY) in self.safeSquares:
                    uncovered = self.board.dig(bestX, bestY)
                    if uncovered is not None:
                        self.uncovered |= uncovered
                self.safeSquares = set()
            else:
                for (bestX, bestY) in self.safeSquares:
                    uncovered = self.board.dig(bestX, bestY)
                    if uncovered is not None:
                        self.uncovered |= uncovered
                    break
                self.safeSquares.remove((bestX, bestY))
                self.clickedSquare = (bestX, bestY)
        else:
            self.board.update2DBoard()
            covered = self.allSquares - self.uncovered - self.bombSquares - self.safeSquares
            if len(self.uncovered) > len(covered):
                uncoveredEdge = set()
                for pos in covered:
                    uncoveredEdge |= self.get8Block(pos) & self.uncovered
            else:
                uncoveredEdge = self.uncovered
            for (x, y) in uncoveredEdge:
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
                return
            else:
                boundary = set()
                covered = self.allSquares - self.uncovered - self.bombSquares - self.safeSquares
                for pos in self.uncovered:
                    boundary |= self.get9Block(pos)
                boundary &= covered

                boundaryMapping = {cell: {cell} for cell in boundary}
                changes = True
                while changes:
                    changes = False
                    for cell in self.uncovered:
                        neighbors = self.get9Block(cell) & boundary
                        if neighbors:
                            piece = set()
                            for ncell in neighbors:
                                piece |= boundaryMapping[ncell]
                            for ncell in neighbors:
                                if boundaryMapping[ncell] != piece:
                                    changes = True
                                boundaryMapping[ncell] = piece

                boundaryPieces = []
                alreadyAdded = set()
                for pieceSeed in boundaryMapping:
                    if pieceSeed not in alreadyAdded:
                        piece = boundaryMapping[pieceSeed]
                        boundaryPieces.append(piece)
                        alreadyAdded |= piece

                self.backupBombSquares = self.bombSquares.copy()
                self.probablySafeSquares = []
                boundaryPieces.sort(key = lambda t: len(t))
                for piece in boundaryPieces:
                    n = len(piece)
                    if n < maxBorderSize:
                        pieceL = list(piece)
                        countD = {x : [0, 0] for x in piece}
                        relevantUncovered = set()
                        for cell in pieceL:
                            relevantUncovered |= self.get9Block(cell) & self.uncovered
                        totalCount = 0
                        for i in range(2**n):
                            idx = 0
                            while i:
                                if i%2:
                                    self.bombSquares.add(pieceL[idx])
                                i = int(i/2)
                                idx += 1
                            for (x, y) in relevantUncovered:
                                if len(self.getBombNeighbors((x, y))) != self.board.board2D[y][x]:
                                    break
                            else:
                                for cell in countD:
                                    if cell in self.bombSquares:
                                        countD[cell][0] += 1
                                    countD[cell][1] += 1
                            self.bombSquares = self.backupBombSquares.copy()
                        for cell in piece:
                            if countD[cell][0] == 0:
                                self.safeSquares.add(cell)
                            else:
                                countD[cell][0] /= countD[cell][1]
                                if countD[cell][0] >= 0.99:
                                    self.bombSquares.add(cell)
                                else:
                                    self.probablySafeSquares.append((cell, countD[cell][0]))
                    if self.safeSquares:
                        self.probablySafeSquares.sort(key = lambda t: t[1], reverse = True)
                        return
                self.probablySafeSquares.sort(key = lambda t: t[1], reverse = True)

                if self.safeSquares:
                    return
                elif self.probablySafeSquares:
                    self.safeSquares.add(self.probablySafeSquares.pop()[0])
                else:
                    self.safeSquares.add(sample(self.allSquares - self.uncovered - self.bombSquares, 1)[0])
                    return

if __name__ == "__main__":
    width = 30
    height = 16
    bombs = 99
    mineSize = 30
    while True:
        sdlBoard = SDLBoard(width, height, bombs, mineSize)
        minesweeper = MineSweeper(sdlBoard)
        sdlBoard.refreshScreen(minesweeper.bombSquares, minesweeper.safeSquares)
        i = 0
        while True:
            for event in pygame.event.get():
                if event.type == QUIT:
                    exit()
            minesweeper.step(clearAllSafe = False)
            sdlBoard.check()
            i += 1
            if i % 1 == 0:
                sdlBoard.refreshScreen(minesweeper.bombSquares, {minesweeper.clickedSquare})
            if sdlBoard.state != "ongoing":
                sdlBoard.updateState()
                sleep(0.1)
                break
