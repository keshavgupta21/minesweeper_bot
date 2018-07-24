from random import sample
class Board:
    def __init__(self, width, height, bombs):
        self.board = {(x, y): 0 for x in range(width) for y in range(height)}
        self.visible = {(x, y): False for x in range(width) for y in range(height)}
        self.width = width
        self.height = height
        self.bombs = bombs
        self.state = 'ongoing'
        self.new = True

    def placeBombs(self, clicked):
        covered = []
        for box in self.board:
            if box != clicked:
                covered.append(box)
        bombLocations = sample(covered, self.bombs)
        for (x, y) in bombLocations:
            for dx in range(-1, 2):
                for dy in range(-1, 2):
                    x_ = x + dx
                    y_ = y + dy
                    if 0 <= x_ < self.width and 0 <= y_ < self.height and isinstance(self.board[(x_, y_)], int):
                        self.board[(x_, y_)] += 1
            self.board[(x, y)] = None

    def update2DBoard(self):
        self.board2D = []
        for y in range(self.height):
            row = []
            for x in range(self.width):
                if self.visible[(x, y)]:
                    row.append(self.board[(x, y)])
                else:
                    row.append(None)
            self.board2D.append(row)

    def check(self):
        if self.state != 'defeat':
            victory = True
            for x in range(self.width):
                for y in range(self.height):
                    if (not self.visible[(x, y)]) and (self.board[(x, y)] is not None):
                        victory = False
                        break
                if not victory:
                    break
            if victory:
                self.state = 'victory'
        return self.state

    def dig(self, x, y):
        if self.new:
            self.placeBombs((x, y))
            self.new = False
        if self.state == 'ongoing':
            uncovered = set()
            if 0 <= x < self.width and 0 <= y < self.height:
                if self.visible[(x, y)]:
                    return uncovered
                this = self.board[(x, y)]
                if this is None:
                    self.state = 'defeat'
                    return None
                elif this == 0:
                    self.visible[(x, y)] = True
                    uncovered.add((x, y))
                    for dx in range(-1, 2):
                        for dy in range(-1, 2):
                            x_ = x + dx
                            y_ = y + dy
                            if 0 <= x_ < self.width and 0 <= y_ < self.height and (dx, dy) != (0, 0):
                                if not self.visible[(x_, y_)]:
                                    uncovered |= self.dig(x_, y_)
                    return uncovered
                else:
                    self.visible[(x, y)] = True
                    uncovered.add((x, y))
                    return uncovered
            return uncovered
        else:
            return None
