import pygame


class Cell():
    def __init__(self, pos, win):
        self.pos = pos  # (x,y) grid position
        self.win = win
        voff = win.voffset
        self.absolute_pos = (pos[0]*self.win.square_length,
                             pos[1]*self.win.square_length + voff)
        # Rect((left, top), (width, height))
        self.rect = pygame.Rect(self.absolute_pos,
                                (self.win.square_length,
                                 self.win.square_length))
        self.num = 0  # 0 for blank, 1-8 for numbers, -1 for bomb
        self.bomb = 0  # useful for counting nearby bombs
        self.flagged = False
        self.exposed = False

    def toggle_flag(self):
        if self.flagged:
            pygame.draw.rect(self.win.screen, 'gray60', self.overlay)
            self.win.update_mine_counter(1)
        else:
            self.overlay = pygame.draw.circle(self.win.screen, 'blue',
                                              self.rect.center,
                                              self.win.square_length / 3)
            self.win.update_mine_counter(-1)
        self.flagged = not self.flagged

    def expose(self):
        """ Expose a cell by writing its number in its rectangle (or showing
            the bomb hidden behind it) """
        self.exposed = True
        # write the number and color in the rectangle
        if self.num < 0:
            # self is a bomb
            # only show the bomb if it's not flagged already
            if not self.flagged:
                pygame.draw.circle(self.win.screen, 'red', self.rect.center,
                                   self.win.square_length / 3)
        else:
            pygame.draw.rect(self.win.screen, 'gray80', self.rect)
            # re-draw the gridlines
            self.win.make_grid()
            self.win.num_of_unexposed_cells -= 1
            if self.num == 0:
                # don't display zeroes as text
                return
            number = self.win.numfont.render(
                str(self.num), True, self.win.colors[self.num-1])
            num_rect = number.get_rect(center=self.rect.center)
            self.win.screen.blit(number, num_rect)
