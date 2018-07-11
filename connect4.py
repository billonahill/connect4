#!/usr/bin/python

import time
import curses

class ConnectFour:
  WIDTH = 7
  HEIGHT = 7
  CONNECT = 4
  TOKENS = ['x','o']
  MESSAGE = "Player %d (%s), enter column from 1 to " + str(WIDTH) + " (hit q to exit): "

  def __init__(self, stdscr):
    self.stdscr = stdscr
    self.grid = [[None for x in range(self.WIDTH)] for y in range(self.HEIGHT)]

    print("grid height: %s" % len(self.grid[0]))
    curses.echo()
    self.bheight,self.bwidth=[self.HEIGHT*2+2, self.WIDTH*2+1]
    self.board = curses.newpad(self.bheight, self.bwidth)

    curses.init_pair(1, curses.COLOR_RED, curses.COLOR_WHITE)
    curses.init_pair(2, curses.COLOR_BLUE, curses.COLOR_WHITE)
    self.draw_board()

  def refresh(self):
    self.stdscr.refresh()
    xoffset, yoffset = [20, 3]
    self.board.refresh(0, 0, yoffset, xoffset, self.bheight + yoffset, self.bwidth + xoffset)

  def grid_to_board(self, x, y):
    return [x * 2 + 1, y * 2 + 1]

  def draw_board(self):
    for y in range(0, self.HEIGHT):
      for x in range(0, self.WIDTH):
        bx, by = self.grid_to_board(x, y)
        self.board.addch(by, bx - 1, curses.ACS_VLINE)
        self.board.addch(by, bx + 1, curses.ACS_VLINE)
        self.board.addch(by - 1, bx, curses.ACS_HLINE)
        self.board.addch(by + 1, bx, curses.ACS_HLINE)

        if y == 0 and x != self.WIDTH - 1: # set top tees
          self.board.addch(by - 1, bx + 1, curses.ACS_TTEE)
        if x == 0 and y != self.HEIGHT - 1: # set left tees
          self.board.addch(by + 1, bx - 1, curses.ACS_LTEE)

        # set lower right cell to bottom or right or intersection edge
        if x == self.WIDTH - 1:
          lr_char = curses.ACS_RTEE
        elif y == self.HEIGHT - 1:
          lr_char = curses.ACS_BTEE
        else:
          lr_char = curses.ACS_PLUS

        self.board.addch(by + 1, bx + 1, lr_char)

    self.board.addch(0, 0, curses.ACS_ULCORNER)
    self.board.addch(0, self.WIDTH * 2, curses.ACS_URCORNER)
    self.board.addch(self.HEIGHT * 2, 0, curses.ACS_LLCORNER)
    self.board.addch(self.HEIGHT * 2, self.WIDTH * 2, curses.ACS_LRCORNER)
    for x in range(0, self.WIDTH):
      bx, by = self.grid_to_board(x, self.HEIGHT - 1)
      self.board.addch(by + 2, bx, str(x+1))

  def play(self):
    turn = 0
    game_over = False
    while True:
      player = (turn % 2) + 1
      c = self.prompt(player)
      if c == ord('q'):
        break  # Exit the while loop

      column = int(c) - 49
      if not game_over and column < self.WIDTH and self.place_piece(player, column) >= 0:
        if self.check_winner():
          self.stdscr.addstr(2, 0, "!!!!!! Player %d wins !!!!!!" % player)
          self.stdscr.refresh()
          game_over = True
        turn = turn + 1

  def get_token(self, player):
    return self.TOKENS[player - 1]

  def prompt(self, player):
    self.stdscr.addstr(0, 0, self.MESSAGE % (player, self.get_token(player)))
    self.stdscr.addstr(1, 0, '> ')
    editwin = curses.newwin(1, 30, 1, 2)
    self.refresh()
    return editwin.getch()

  def place_piece(self, player, column):
    token = self.get_token(player)
    color_pair = curses.color_pair(player)
    for y in range(0, self.HEIGHT):
      if self.grid[column][y] is None: # go up until first empty cell
        for h in range(0, self.HEIGHT - y - 1):
          bx, by = self.grid_to_board(column, h)
          self.board.addch(by, bx, token, color_pair)
          self.refresh()
          time.sleep(.25)
          self.board.addch(by, bx, ' ', curses.color_pair(0))

        bx, by = self.grid_to_board(column, y)
        self.board.addch(2 * self.HEIGHT - by, bx, token, color_pair)
        self.grid[column][y] = player
        self.stdscr.delch(0, len(self.MESSAGE) - 1)
        return y
    return -1

  # if row is empty return -1
  # if no match return 0
  # if match return 1
  def check_consecutive(self, array):
    run = 0
    last = None
    row_empty = True
    for value in array:
      if value:
        row_empty = False
        if value == last:
          run = run + 1
        else:
          run = 1
      if run == self.CONNECT:
        return 1
      last = value
    if row_empty:
      return -1
    return 0

  def right_diag(self, grid, x):
    diag = [] 
    for h in range(0, self.HEIGHT):
      try:
        if x + h >= (self.WIDTH - 1) or grid[x + h][h] == None:
          return diag
        diag.append(grid[x + h][h])
      except IndexError:
        print("right_diag x=%s, h=%s, w=%s, H=%s" % (x, h, self.WIDTH, self.HEIGHT))
        return diag

    return diag

  def left_diag(self, grid, x):
    diag = [] 
    for h in range(0, self.HEIGHT):
      try:
        if x - h < 0 or grid[x - h][h] == None:
          return diag
        diag.append(grid[x - h][h])
      except IndexError:
        print("left_diag x=%s, h=%s, w=%s, H=%s" % (x, h, self.WIDTH, self.HEIGHT))
        return diag
    return diag
      
  def check_winner(self):
    # check all rows
    for row in self.grid:
      check = self.check_consecutive(row)
      if check == -1:  # row is empty
        break
      if check > 0:
        return check
    # check all columns
    for w in range(0, self.WIDTH):
      check = self.check_consecutive([row[w] for row in self.grid])
      if check > 0: # row is empty or a match
        return check

    for x in range(0, self.WIDTH):
      diag = self.right_diag(self.grid, x)
      if self.check_consecutive(diag) == 1:
        return True
      diag = self.left_diag(self.grid, x)
      if self.check_consecutive(diag) == 1:
        return True

    return False

def main(stdscr):
  game = ConnectFour(stdscr)
  game.play()

curses.wrapper(main)