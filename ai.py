import pygame
from pygame.locals import *
from sdlBased import SDLBoard
from time import sleep
from time import time

class MineSweeper:
    def __init__(self, board):
        self.board = board
        self.safeSquares = set()
        self.bombSquares = set()
        self.uncovered = set()
        self.allSquares = {(x, y) for x in range(self.board.width) for y in range(self.board.height)}

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
            for (bestX, bestY) in self.safeSquares:
                uncovered = self.board.dig(bestX, bestY)
                if uncovered is not None:
                    self.uncovered |= uncovered
            self.safeSquares = set()
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

if __name__ == "__main__":
    width = 96
    height = 54
    bombs = 700
    mineSize = 5
    sdlBoard = SDLBoard(width, height, bombs, mineSize)
    minesweeper = MineSweeper(sdlBoard)
    i = 0
    last = time()
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
        if i % 100 == 0:
            print(time() - last)
            last = time()
            sdlBoard.refreshScreen(minesweeper.bombSquares, minesweeper.safeSquares)
        if sdlBoard.state != "ongoing":
            sdlBoard.updateState()
            sleep(1)
            exit()
