from game import Board
from time import sleep
from numpy import random
import pygame
from pygame.locals import *

class SDLBoard(Board):
    def __init__(self, width, height, bombs, mineSize):
        Board.__init__(self, width, height, bombs)
        displayW = width * mineSize + 10
        displayH = height * mineSize + 110
        self.mineSize = mineSize
        self.border = max(1, self.mineSize/20)
        pygame.init()
        self.screen = pygame.display.set_mode((displayW, displayH))
        pygame.display.set_caption("MineSweeper")
        self.background = pygame.Surface(self.screen.get_size()).convert()
        self.background.fill((255, 255, 255))
        self.cleanBackground = self.background.copy()
        self.refreshScreen()

    def refreshScreen(self, bombSquares = None, safeSquares = None, boundaryPieces = None):
        if bombSquares is None:
            bombSquares = set()
        if safeSquares is None:
            safeSquares = set()
        if boundaryPieces is None:
            boundaryPieces = []
        colors = list([tuple(random.choice(range(256), size=3)) for _ in range(len(boundaryPieces))])
        self.update2DBoard()
        self.background = self.cleanBackground.copy()
        for y in range(self.height):
            for x in range(self.width):
                left = self.background.get_rect().centerx + (x - self.width/2.0)*self.mineSize
                top = self.background.get_rect().centery + (y - self.height/2.0)*self.mineSize - 50
                rect = pygame.Rect((left, top), (self.mineSize, self.mineSize))
                val = self.board2D[y][x]
                if val is not None:
                    pygame.draw.rect(self.background, (127, 127, 127), rect)
                    if val != 0:
                        font = pygame.font.Font(None, self.mineSize)
                        text = font.render(str(val), 1, (0, 0, 0))
                        textpos = text.get_rect()
                        textpos.centerx = rect.centerx
                        textpos.centery = rect.centery
                        self.background.blit(text, textpos)
                else:
                    pygame.draw.rect(self.background, (191, 191, 191), rect)
                if (x, y) in bombSquares:
                    pygame.draw.rect(self.background, (0, 0, 0), rect)
                if (x, y) in safeSquares:
                    pygame.draw.rect(self.background, (255, 255, 255), rect)
                for i in range(len(boundaryPieces)):
                    if (x, y) in boundaryPieces[i]:
                        pygame.draw.rect(self.background, colors[i], rect)
                pygame.draw.rect(self.background, (63, 63, 63), rect, self.border)
        self.screen.blit(self.background, (0, 0))
        pygame.display.flip()

    def updateState(self):
        if self.state != "ongoing":
            font = pygame.font.Font(None, 36)
            text = font.render(self.state, 1, (10, 10, 10))
            textpos = text.get_rect()
            textpos.centery = self.background.get_rect().bottom-50
            textpos.centerx = self.background.get_rect().centerx
            self.background.blit(text, textpos)
            self.screen.blit(self.background, (0, 0))
            pygame.display.flip()

if __name__ == "__main__":
    width = 10
    height = 10
    bombs = 10
    mineSize = 20
    sdlBoard = SDLBoard(width, height, bombs, mineSize)
    while True:
        event = pygame.event.wait()
        if event.type == QUIT:
            exit()
        elif event.type == MOUSEBUTTONDOWN and event.button == 1:
            pos = pygame.mouse.get_pos()
            sdlBoard.dig((pos[0]-5)/mineSize, (pos[1]-5)/mineSize)
            sdlBoard.check()
            sdlBoard.refreshScreen()
        if sdlBoard.state != "ongoing":
            sdlBoard.updateState()
            sleep(3)
            exit()
