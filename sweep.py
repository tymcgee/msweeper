# Tynan McGee
# 3/18/22 - 3/21/22
# Minesweeper clone using pygame

import sys
import random
import pygame

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
# fix when the grid is not square (more offsets?)

# TODO:
# add some kind of menu for choosing difficulty/stuff like that?


class Window:
    def __init__(self, screenw, screenh, gridw, gridh, num_of_mines):
        # --- SCREEN STUFF ---
        self.sw, self.sh = screenw, screenh
        self.gw, self.gh = gridw, gridh
        # assuming the game screen is square (so use self.sw to avoid
        # worrying about the vertical offset)
        if self.gw > self.gh:
            self.square_length = self.sw / self.gw
        else:
            self.square_length = self.sw / self.gh
        # assumes screen height is larger than screen width
        self.voffset = self.sh - self.sw
        self.screen = pygame.display.set_mode((self.sw, self.sh))
        self.top_section = pygame.Rect(0, 0, self.sw, self.voffset)
        self.bg_color = 'gray60'

        # --- SETUP STUFF ---
        self.grid = [[Cell((x, y), self.square_length, self.voffset) for y in range(self.gh)]
                     for x in range(self.gw)]
        self.colors = ["blue", "DarkGreen", "red", "DarkSlateBlue",
                       "DarkRed", "LightSeaGreen", "black", "gray90"]
        self.num_of_unexposed_cells = self.gw * self.gh
        self.num_of_mines = num_of_mines
        self.num_of_flagged_cells = 0
        self.first_click = True
        self.can_play = True
        self.timer = None
        self.time = 0

    #### MAIN FUNCTIONALITY ####
    def run(self):
        pygame.init()
        pygame.display.set_caption('msweeper')
        self.screen.fill(self.bg_color)
        self.numfont = pygame.font.SysFont(
            'courier new', int(self.square_length / 2), True)
        self.timerfont = pygame.font.SysFont(
            'courier new', int(self.top_section.height))
        self.textfont = pygame.font.SysFont(
            'courier new', int(self.top_section.height / 1.5))
        # draw the grid but don't place any mines or anything yet
        self.initialize_screen()

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()
                if self.can_play:
                    # don't update the timer if you haven't started the game yet
                    if not self.first_click and event.type == self.CLOCK_TICK:
                        self.time += 1
                        self.update_timer(self.time)
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        # find the grid cell you clicked on
                        mousex, mousey = event.pos
                        gridx = int(mousex // self.square_length)
                        gridy = int((mousey - self.voffset) //
                                    self.square_length)
                        # 0 <= gridx <= self.gw
                        # 0 <= gridy <= self.gh
                        x_in_bounds = gridx >= 0 and gridx <= self.gw
                        y_in_bounds = gridy >= 0 and gridy <= self.gh
                        if x_in_bounds and y_in_bounds:
                            cell = self.grid[gridx][gridy]
                            self.process_click(cell, event.button)
                if event.type == pygame.KEYDOWN:
                    if event.key == 113:    # q
                        sys.exit()
                    elif event.key == 27:   # esc
                        print('escape')
                    elif event.key == 114:  # r
                        self.initialize_screen()
                        # self.new_game()
                pygame.event.pump()
                pygame.display.update()

    def process_click(self, cell, button):
        """ Determines what to do after a cell is clicked.
            - If left clicking a cell (to expose it):
                - If it is the first click, generate a board until the clicked
                  cell is not a bomb and start the timer.
                - If the cell is a bomb, trigger a loss.
                - If the cell is not already exposed and not flagged:
                    - Expose the cell, flood fill if needed.
                    - Update the number of unexposed cells.
                    - Trigger a win if the new number of unexposed cells
                      equals the number of mines.
            - If right clicking a cell (to flag it):
                - If the cell is not already exposed, it was not the first
                  click, and the max number of flags has not been placed yet:
                    - Flag the cell and update the number of flagged cells.
        """
        # 1 is left click, 2 is middle click, 3 is right click
        if button == 1:
            if self.first_click:
                self.new_game()
                while cell.bomb:
                    self.new_game()
                self.first_click = False
                self.CLOCK_TICK = pygame.USEREVENT+1
                self.timer = pygame.time.set_timer(self.CLOCK_TICK, 1000)
            if cell.flagged:
                return
            if cell.bomb:
                # you lose :(
                self.trigger_win_or_loss(
                    "YOU LOSE (press r to restart)", "red")
                return
            if not cell.exposed:
                self.expose(cell)
                if cell.num == 0:
                    self.flood_fill(cell)
                if self.num_of_unexposed_cells == self.num_of_mines:
                    # you win!
                    self.trigger_win_or_loss(
                        "YOU WIN! (press r to restart)", "green")

        elif button == 3:
            # right click an unexposed cell
            a = not cell.exposed
            # not your first click
            b = not self.first_click
            if a and b:
                self.toggle_flag(cell)

    #### HELPER FUNCTIONS (CREATE A NEW GAME) ####
    def new_game(self):
        """ Generate the board and reset all the game variables. """
        self.initialize_screen()
        self.place_bombs()
        self.fill_numbers()
        self.first_click = True  # technically redundant but whatever
        self.can_play = True
        self.num_of_unexposed_cells = self.gw * self.gh
        self.time = 0

    def initialize_screen(self):
        """ Clear the board and all the cells in it. Stop the timer. """
        self.reset_top_section()
        self.update_mine_counter(0)
        self.update_timer(0)
        for row in self.grid:
            for cell in row:
                cell.num = 0
                cell.bomb = 0
                cell.flagged = False
                cell.exposed = False
                pygame.draw.rect(self.screen, self.bg_color, cell.rect)
        self.make_grid()
        self.first_click = True

    def make_grid(self):
        # draw the horizontal lines
        for i in range(self.gh+1):
            vert_pos = i*self.square_length + self.voffset
            right = self.square_length * self.gw
            # horizontal lines
            pygame.draw.line(self.screen, 'black', (0, vert_pos),
                             (right, vert_pos), 1)
        # draw the vertical lines
        for j in range(self.gw+1):
            horz_pos = j*self.square_length
            bottom = self.square_length*self.gh + self.voffset
            # vertical lines
            pygame.draw.line(self.screen, 'black', (horz_pos, self.voffset),
                             (horz_pos, bottom), 1)

    def place_bombs(self):
        """ Choose (num_of_mines) random indices to place the bombs into. """
        self.bombs_left = 0
        bomb_list = []
        for _ in range(self.num_of_mines):
            row = random.choice(self.grid)
            cell = random.choice(row)
            while cell in bomb_list:
                row = random.choice(self.grid)
                cell = random.choice(row)
            cell.num = -1
            cell.bomb = 1
            bomb_list.append(cell)

    def fill_numbers(self):
        """ Give the cells numbers based on nearby bombs """
        for i in range(self.gw):
            for j in range(self.gh):
                cell = self.grid[i][j]
                if not cell.bomb:
                    for neighbor in self.get_neighbors(cell):
                        cell.num += neighbor.bomb

    def get_neighbors(self, cell):
        """ Return a list of all of a cell's neighbors. """
        x = cell.grid_pos[0]
        y = cell.grid_pos[1]
        neighbors = []
        for i in (-1, 0, 1):
            for j in (-1, 0, 1):
                if i == 0 and j == 0:  # skip the cell itself
                    continue
                if not (x+i < 0 or y+j < 0 or x+i > self.gw-1 or y+j > self.gh-1):
                    neighbors.append(self.grid[x+i][y+j])
        return neighbors

    def reset_top_section(self):
        pygame.draw.rect(self.screen, "gray90", self.top_section)

    #### HELPER FUNCTIONS (VISUAL STUFF) ####
    def update_mine_counter(self, num):
        """ Set the mine counter in the top left to display num. """
        self.num_of_flagged_cells = num
        mines_left = self.num_of_mines - num
        # pad one-digit numbers
        if mines_left < 10:
            mines_left = '0' + str(mines_left)
        text = self.timerfont.render(str(mines_left), True, 'white', 'gray20')
        location = text.get_rect(topleft=(0, 0))
        self.screen.blit(text, location)

    def update_timer(self, time):
        """ Set the timer in the top right to display time. """
        text = self.timerfont.render(str(time), True, 'white', 'gray20')
        location = text.get_rect(topright=(self.sw, 0))
        self.screen.blit(text, location)

    def trigger_win_or_loss(self, text, color):
        """ Exposes all grid cells, renders the game unplayable until a restart,
            and shows text at the top of the screen. """
        self.can_play = False
        self.expose_all()
        self.make_grid()
        self.show_text(text, color)

    def show_text(self, text, color):
        """ Display text at the top center of the screen """
        text = self.textfont.render(text, True, color, 'gray20')
        location = text.get_rect(midtop=(self.sw / 2, 0))
        self.screen.blit(text, location)

    def expose_all(self):
        for row in self.grid:
            for cell in row:
                self.expose(cell)

    #### HELPER FUNCTIONS (PLAY THE GAME) ####
    def expose(self, cell):
        """ Expose a cell by writing its number in its rectangle (or showing
            the bomb hidden behind it). """
        cell.exposed = True
        if cell.bomb and not cell.flagged:
            pygame.draw.circle(self.screen, 'red', cell.rect.center,
                               self.square_length / 3)
        elif cell.flagged and not cell.bomb:
            self.toggle_flag(cell)
            self.expose(cell)
        elif cell.flagged and cell.bomb:
            return
        else:
            pygame.draw.rect(self.screen, 'gray80', cell.rect)
            self.make_grid()
            self.num_of_unexposed_cells -= 1
            # don't display zeroes as text
            if cell.num > 0:
                num = self.numfont.render(
                    str(cell.num), True, self.colors[cell.num-1])
                num_rect = num.get_rect(center=cell.rect.center)
                self.screen.blit(num, num_rect)

    def flood_fill(self, cell):
        for c in self.get_neighbors(cell):
            if not c.exposed and not c.flagged:
                self.expose(c)
                if c.num == 0:
                    self.flood_fill(c)

    def toggle_flag(self, cell):
        diff = 0
        if cell.flagged:
            pygame.draw.rect(self.screen, 'gray60', cell.overlay)
            diff = -1
            cell.flagged = not cell.flagged
        elif not (self.num_of_flagged_cells == self.num_of_mines):
            cell.overlay = pygame.draw.circle(self.screen, 'blue',
                                              cell.rect.center,
                                              self.square_length / 3)
            diff = 1
            cell.flagged = not cell.flagged
        self.update_mine_counter(self.num_of_flagged_cells + diff)


if __name__ == '__main__':
    # easy:         10x10 with 10 mines
    # intermediate: 15x15 with 40 mines
    # expert:       16x30 with 99 mines
    args = [
        750,  # screen width
        800,  # screen height
        10,   # grid width
        10,   # grid height
        10    # num of bombs
    ]
    win = Window(*args)
    win.run()
