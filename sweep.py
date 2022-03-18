# Tynan McGee
# 3/18/22
# Minesweeper clone using pygame

import sys
import pygame
import random

# TODO:
# generate the board when you click
# generate the board with a given number of bombs, instead of random number
# give different colors to different cell numbers
# fix when the grid is not square
# make a win condition

class Cell():
    def __init__(self, pos, win):
        self.pos = pos  # (x,y) grid position
        self.win = win
        self.absolute_pos = (pos[0]*self.win.square_length,
                             pos[1]*self.win.square_length)
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
        else:
            self.overlay = pygame.draw.circle(self.win.screen, 'blue',
                                              self.rect.center,
                                              self.win.square_length / 3)
        self.flagged = not self.flagged

    def expose(self):
        self.exposed = True
        # write the number and color in the rectangle
        pygame.draw.rect(self.win.screen, 'gray80', self.rect)
        # re-draw the gridlines
        self.win.make_grid()
        if self.num == 0:
            return
        number = self.win.font.render(str(self.num), True, "black")
        num_rect = number.get_rect(center = self.rect.center)
        self.win.screen.blit(number, num_rect)



class Sweeper:
    def __init__(self, sh, sw, gh, gw):
        self.screen_size = self.sw, self.sh = sh, sw
        self.grid_size = self.gw, self.gh = gh, gw
        self.square_length = self.sw / self.gw
        self.screen = pygame.display.set_mode(self.screen_size)
        self.grid = [[Cell((x,y), self) for y in range(self.gh)]
                     for x in range(self.gw)]

    def get_neighbors(self, cell):
        """ Return a list of all of a cell's neighbors """
        x = cell.pos[0]
        y = cell.pos[1]
        x_range = (-1, 0, 1)
        y_range = (-1, 0, 1)
        if x == 0:
            x_range = (0, 1)
        if x == self.gw-1:
            x_range = (-1, 0)
        if y == 0:
            y_range = (0, 1)
        if y == self.gh-1:
            y_range = (-1, 0)

        neighbors = []
        for i in x_range:
            for j in y_range:
                if i == 0 and j == 0:  # skip the cell itself
                    continue
                neighbors.append(self.grid[x+i][y+j])
        return neighbors

    def make_grid(self):
        for i in range(self.gw):
            vert_pos = i*self.square_length
            for j in range(self.gh):
                # initialize cell
                horz_pos = j*self.square_length
                # vertical lines
                pygame.draw.line(self.screen, 'black', (horz_pos, 0),
                                 (horz_pos, self.sh), 1)
            # horizontal lines
            pygame.draw.line(self.screen, 'black', (0, vert_pos),
                             (self.sw, vert_pos), 1)

    def place_bombs(self):
        for i in range(self.gw):
            for j in range(self.gh):
                if random.random() < 0.1:
                    # 10% chance for a  cell to have a mine
                    cell = self.grid[i][j]
                    # pygame.draw.circle(self.screen, 'red', cell.rect.center,
                    #                    self.square_length / 3)
                    cell.num = -1
                    cell.bomb = 1

    def fill_numbers(self):
        for i in range(self.gw):
            for j in range(self.gh):
                cell = self.grid[i][j]
                if not cell.bomb:
                    for neighbor in self.get_neighbors(cell):
                        cell.num += neighbor.bomb

    def flood_fill(self, cell):
        """ Expose all the cells around a zero until they aren't zero """
        for c in self.get_neighbors(cell):
            if not c.exposed:
                if c.num == 0:
                    c.expose()
                    self.flood_fill(c)
                elif c.num > 0:
                    c.expose()

    def process_click(self, cell):
        """ Figure out what to do after clicking cell """
        if cell.flagged:
            return
        if cell.num < 0:
            print('explosion boom boom boom you lose')
            return
        if not cell.exposed:
            if cell.num == 0:
                self.flood_fill(cell)
            else:
                cell.expose()


    def run(self):
        pygame.init()
        pygame.display.set_caption('msweeper')
        self.screen.fill('gray60')
        self.font = pygame.font.SysFont('courier new',
                                        int(self.square_length // 2))
        self.make_grid()
        self.place_bombs()
        self.fill_numbers()

        #######################
        ## Main Loop ##########
        #######################
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    # find the grid cell that you clicked on
                    mousex, mousey = event.pos
                    gridx = int(mousex // self.square_length)
                    gridy = int(mousey // self.square_length)
                    clicked_cell = self.grid[gridx][gridy]
                    # 1 is left, 2 is middle, 3 is right
                    if event.button == 1:
                        self.process_click(clicked_cell)
                    elif event.button == 3:
                        clicked_cell.toggle_flag()

            pygame.event.pump()
            pygame.display.update()


if __name__ == '__main__':
    game = Sweeper(750, 750, 10, 10)
    game.run()
