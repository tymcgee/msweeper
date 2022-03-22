import pygame


class Cell:
    def __init__(self, pos, square_length, voff):
        self.grid_pos = pos
        self.absolute_pos = (pos[0]*square_length, pos[1]*square_length + voff)
        self.rect = pygame.Rect(
            self.absolute_pos, (square_length, square_length))
        self.num = 0  # 0 for blank, 1-8 for numbers, -1 for bomb
        self.bomb = 0  # 0 or 1 (not T/F since this way is nice for counting)
        self.flagged = False
        self.exposed = False
