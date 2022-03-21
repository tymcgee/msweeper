# Tynan McGee
# 3/18/22
# Minesweeper clone using pygame

import sys
import pygame
import random

from cell import Cell

# DONE:
# generate the board when you click
# make a lose condition
# make a win condition
# generate the board with a given number of bombs, instead of random number
# show all the mines when you lose
# give different colors to different cell numbers
# add a top bar (for displaying things like # of mines left, timer)
# add the num of mines left to the top bar
# add a timer to the top bar

# TODO:
# fix when the grid is not square (more offsets?)
# add some kind of menu for choosing difficulty/stuff like that?


class Sweeper:
    def __init__(self, screenw, screenh, gridw, gridh, num_of_mines):
        self.screen_size = self.sw, self.sh = screenw, screenh
        self.grid_size = self.gw, self.gh = gridw, gridh
        self.square_length = self.sw / self.gw
        self.num_of_mines = num_of_mines
        self.num_of_flags = self.num_of_mines
        # this assumes the screen is taller than it is wide
        self.voffset = self.sh - self.sw
        self.screen = pygame.display.set_mode(self.screen_size)
        self.top_section = pygame.Rect(0, 0, self.sw, self.voffset)
        self.grid = [[Cell((x, y), self) for y in range(self.gh)]
                     for x in range(self.gw)]
        self.colors = ["blue", "DarkGreen", "red", "DarkSlateBlue",
                       "DarkRed", "LightSeaGreen", "black", "gray90"]
        self.first_click = True
        self.lost = False
        self.won = False
        # this count assume a rectangular grid
        self.num_of_unexposed_cells = len(self.grid)*len(self.grid[0])
        self.timer = None
        self.time = 0

    def get_neighbors(self, cell):
        """ Return a list of all of a cell's neighbors """
        x = cell.pos[0]
        y = cell.pos[1]
        neighbors = []
        for i in (-1, 0, 1):
            for j in (-1, 0, 1):
                if i == 0 and j == 0:  # skip the cell itself
                    continue
                if not (x+i < 0 or y+j < 0 or x+i > self.gw-1 or y+j > self.gh-1):
                    neighbors.append(self.grid[x+i][y+j])
        return neighbors

    def make_grid(self):
        for i in range(self.gw):
            vert_pos = i*self.square_length + self.voffset
            for j in range(self.gh):
                # initialize cell
                horz_pos = j*self.square_length
                # vertical lines
                pygame.draw.line(self.screen, 'black', (horz_pos, self.voffset),
                                 (horz_pos, self.sh), 1)
            # horizontal lines
            pygame.draw.line(self.screen, 'black', (0, vert_pos),
                             (self.sw, vert_pos), 1)

    def place_bombs(self):
        """ Choose (num_of_mines) random indices to place the bombs into """
        self.bombs_left = 0
        bomb_list = []
        for _ in range(self.num_of_mines):
            # assuming the grid is rectangular
            x = random.randrange(len(self.grid))
            y = random.randrange(len(self.grid[0]))
            if (x, y) not in bomb_list:
                cell = self.grid[x][y]
                cell.num = -1
                cell.bomb = 1
                bomb_list.append((x, y))

    def fill_numbers(self):
        """ Give the cells numbers based on nearby bombs """
        for i in range(self.gw):
            for j in range(self.gh):
                cell = self.grid[i][j]
                if not cell.bomb:
                    for neighbor in self.get_neighbors(cell):
                        cell.num += neighbor.bomb

    def clear_board(self):
        """ Reset all cells back to default, with no numbers or bombs """
        for row in self.grid:
            for cell in row:
                cell.num = 0
                cell.bomb = 0
                if cell.flagged:
                    pygame.draw.rect(self.screen, 'gray60', cell.overlay)
                cell.flagged = False
                cell.exposed = False
                pygame.draw.rect(self.screen, 'gray60', cell.rect)
        self.make_grid()

    def reset_top_section(self):
        pygame.draw.rect(self.screen, "gray90", self.top_section)

    def new_game(self):
        # reset the look of the board
        self.reset_top_section()
        self.update_mine_counter(0)
        self.update_timer(0)
        self.clear_board()
        self.place_bombs()
        self.fill_numbers()
        # reset variables
        self.first_click = True
        self.lost = False
        self.won = False
        self.num_of_unexposed_cells = len(self.grid)*len(self.grid[0])
        self.time = 0

    def flood_fill(self, cell):
        """ Expose all the cells around a zero until they aren't zero """
        for c in self.get_neighbors(cell):
            if not c.exposed and not c.flagged:
                if c.num == 0:
                    c.expose()
                    self.flood_fill(c)
                elif c.num > 0:
                    c.expose()

    def expose_all(self):
        """ Expose all the cells """
        for row in self.grid:
            for cell in row:
                cell.expose()

    def show_text(self, text, color):
        """ Display text at the top center of the screen """
        text = self.textfont.render(text, True, color, 'gray20')
        location = text.get_rect(midtop=(self.sw / 2, 0))
        self.screen.blit(text, location)

    def update_mine_counter(self, diff):
        num = self.num_of_flags + diff
        self.num_of_flags = num
        # pad one-digit numbers
        if num < 10:
            num = '0' + str(num)
        text = self.textfont.render(str(num), True, 'white', 'gray20')
        location = text.get_rect(topleft=(0, 0))
        self.screen.blit(text, location)

    def update_timer(self, time):
        text = self.textfont.render(str(time), True, 'white', 'gray20')
        location = text.get_rect(topright=(self.sw, 0))
        self.screen.blit(text, location)

    def process_click(self, cell):
        """ Figure out what to do after clicking cell """
        if self.first_click:
            # make sure the first click isn't a bomb by creating the game
            # after the first click
            self.new_game()
            while cell.bomb:
                self.new_game()
            self.first_click = False
            self.timer = pygame.time.set_timer(pygame.USEREVENT+1, 1000)
        if cell.flagged:
            return
        if cell.num < 0:
            self.lost = True
            self.expose_all()
            # make the grid again just to be safe
            self.make_grid()
            self.show_text("YOU LOSE (press r to restart)", "red")
            return
        if not cell.exposed:
            if cell.num == 0:
                cell.expose()
                self.flood_fill(cell)
            else:
                cell.expose()

    def run(self):
        pygame.init()
        pygame.display.set_caption('msweeper')
        self.screen.fill('gray60')
        self.numfont = pygame.font.SysFont('courier new',
                                           int(self.square_length / 2), True)
        self.textfont = pygame.font.SysFont('courier new',
                                            int(self.square_length / 2.5))
        # maybe a bit redundant to do new_game here when
        # it happens again after first click, but whatever
        self.new_game()

        #######################
        ## Main Loop ##########
        #######################
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()
                if not self.lost and not self.won:
                    if not self.first_click and event.type == pygame.USEREVENT+1:
                        self.time += 1
                        self.update_timer(self.time)
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        # find the grid cell that you clicked on
                        mousex, mousey = event.pos
                        gridx = int(mousex // self.square_length)
                        gridy = int((mousey - self.voffset) //
                                    self.square_length)
                        # gridy < 0 means you clicked in the top bar
                        if gridy >= 0:
                            clicked_cell = self.grid[gridx][gridy]
                            # 1 is left, 2 is middle, 3 is right
                            if event.button == 1:
                                self.process_click(clicked_cell)
                            elif event.button == 3 and not clicked_cell.exposed and not self.first_click:
                                if self.num_of_flags > 0:
                                    clicked_cell.toggle_flag()
                if event.type == pygame.KEYDOWN:
                    # q
                    if event.key == 113:
                        sys.exit()
                    # esc
                    elif event.key == 27:
                        print('escape')
                    # r
                    elif event.key == 114:
                        self.new_game()

            if self.num_of_mines == self.num_of_unexposed_cells:
                # you win!
                self.won = True
                self.expose_all()
                # make the grid again just to be safe
                self.make_grid()
                self.show_text("YOU WIN! (press r to restart)", "green")
            pygame.event.pump()
            pygame.display.update()


if __name__ == '__main__':
    # easy is something like 10x10 with 10 mines (10% density)
    # intermediate is something like 15x15 with 40 mines (17.8% density)
    # expert is 16x30 with 99 mines (20.6% density)
    game = Sweeper(750, 800, 10, 10, 10)
    game.run()
