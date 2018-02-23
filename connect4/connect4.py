#############
## Imports ##
#############

import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import convolve2d

##############
## Settings ##
##############
plt.rcParams['toolbar'] = 'None'
plt.rcParams['keymap.xscale'] = 'None'
plt.rcParams['keymap.yscale'] = 'None'
plt.rcParams['axes.grid']=True

############
## Player ##
############

class Player(object):
    def __init__(self, idx, name=None, color=None):
        self.idx = idx # A player knows of himself if he is player 1 or player 2.
        self.name = 'Player %i'%idx if name is None else name
        self.color = {1:'C0',2:'C1'}[idx] if color is None else color
    def play(self, array):
        ''' The player makes a decision where to do his next move according to the provided array '''
        pass

class Person(Player):
    def play(self, array):
        try:
            x = input('%s: Where do you want to play?\t'%self.name)
            return int(x)
        except ValueError:
            return self.play(array)

class Ai(Player):
    def play(self, array):
        return int(np.random.rand()*array.shape[0])


##########
## Game ##
##########

class Game(object):
    ''' The connect 4 "board game" '''
    def __init__(self, X=7, Y=6, first=1, players=(), verbose=True):
        '''
        Create a connect 4 game.

        args:
            X = 7: size in X-dimension
            Y = 6: size in Y-dimension
            first = 1: which player is starting
            players = (): a tuple containing the two players

        '''
        self.X, self.Y = X,Y
        self.turn = first # Which player will start [1,2]
        self.array = np.zeros((X, Y), dtype=int)
        self.players = (Ai(1), Ai(2)) if len(players) != 2 else players
        self.verbose = verbose

    def get_player(self, idx):
        ''' Get player with index idx '''
        return self.players[idx - 1]

    @property
    def current_player(self):
        ''' Get current player '''
        return self.get_player(self.turn)

    def switch_player(self):
        ''' switch player '''
        self.turn = {1:2, 2:1}[self.turn]

    def play(self):
        ''' Updates board location according the the x-position specified by a player '''
        while self.state() == 0:
            self.one_turn()
        self.visualize()
        if self.verbose: print('%s WON'%self.get_player(self.state()).name)

    def one_turn(self):
        success = False
        while not success:
            self.visualize()
            x = self.current_player.play(self.array)
            success = self.update_array(self.current_player, x)
        self.switch_player() # switch player

    def update_array(self, player, x):
        ''' update array according to who played and the x position of the play '''
        y = np.sum(self.array[x] > 0)
        if y >= self.array.shape[1]: # Move not allowed
            return 0 # fail
        self.array[x,y] = player.idx
        return 1

    def visualize(self):
        ''' visualize the array in a Person friendly way '''
        if self.verbose:
            print('\n\n\n')
            A = np.array(self.array.T[::-1], dtype=str)
            A[A=='0'] = '.'
            A[A=='1'] = 'O'
            A[A=='2'] = 'X'
            for row in A:
                row = ' '.join(list(row))
                print(row)

    def state(self):
        ''' Determines the state of the board. 0: undecided; 1: player 1 won; 2: player2 won. '''
        for p in [1,2]:
            array = np.array((self.array == p), dtype=int)
            K = [np.diag(np.ones(4, dtype=int)), # diagonal 1
                     np.diag(np.ones(4, dtype=int))[::-1], # diagonal 2
                     np.ones((4,1), dtype=int), # horizontal
                     np.ones((1,4), dtype=int)] # vertical
            for k in K:
                result = convolve2d(array, k, 'valid')
                if (result == 4).any():
                    return p
        return 0


#############
## MplGame ##
#############

class MplGame(Game):
  ''' a simple connect 4 Game Visualized with matplotlib'''
  def __init__(self, X=7, Y=6, first=1, players=(), bgcolor='#ececec'):
    '''
    Create a connect 4 game implemented in matplotlib.

    args:
      X = 7: size in X-dimension
      Y = 6: size in Y-dimension
      first = 1: which player is starting
      players = (): a tuple containing the two players
      bgcolor = '#ececec': background color of the canvas

    '''
    # Initialize game
    Game.__init__(self, X, Y, first, players)

    # Matplotlib settings
    self.bgcolor = bgcolor
    self.fig, self.ax = plt.subplots()
    self.ax.set_facecolor(self.bgcolor)
    self.fig.patch.set_facecolor(self.bgcolor)
    self.fig.canvas.set_window_title('Connect 4')
    self.timer = self.fig.canvas.new_timer(interval=100)
    self.timer.add_callback(self.visualize)
    self.timer.single_shot = False

    # Initialize Game board
    self.plots = np.zeros((self.X,self.Y), dtype=object)
    for i, j in zip(*np.where(self.array == 0)):
      self.plots[i,j] = plt.scatter(i+0.5, j+0.5, s=1000, color=self.bgcolor)

    self.ax.set_title("%s's turn"%self.current_player.name, color=self.current_player.color)
    plt.xticks(range(self.X), ['']*self.X)
    plt.yticks(range(self.Y), ['']*self.Y)
    plt.axis('scaled')
    plt.xlim(0,self.X)
    plt.ylim(0,self.Y)

    try: #try to change the icon of the window
      from PyQt5 import QtGui
      plt.get_current_fig_manager().window.setWindowIcon(QtGui.QIcon('./img/icon.ico'))
    except:
      pass # keep standard matplotlib icon

  def switch_player(self):
    self.turn = {1:2, 2:1}[self.turn]
    self.ax.set_title("%s's turn"%self.current_player.name, color=self.current_player.color)


  def play(self):
    self.timer.start()
    ai_speed = 100 #[ms]
    self.players[0].timer = self.fig.canvas.new_timer(interval=ai_speed)
    self.players[1].timer = self.fig.canvas.new_timer(interval=ai_speed)

    self.cid = None
    if type(self.players[0]) == Person:
      self.cid = self.fig.canvas.mpl_connect('button_press_event', self.play_person)
    if type(self.players[1]) == Person and self.cid is None:
      self.cid = self.fig.canvas.mpl_connect('button_press_event', self.play_person)
    if type(self.players[1]) == Ai:
      self.players[1].timer.add_callback(self.play_ai)
    if type(self.players[0]) == Ai:
      self.players[0].timer.add_callback(self.play_ai)
      self.players[0].timer.start()

    plt.show()

  def play_person(self, event):
    '''
    play_person changes the internal array and replots the result
    according to where in the canvas was clicked
    '''
    x = int(event.xdata)
    success = self.update_array(self.current_player, x)
    if success:
      self.switch_player()
    if type(self.current_player) == Ai:
      self.current_player.timer.start()

  def play_ai(self):
    '''
    on_click changes the internal array and replots the result
    according to where in the canvas was clicked
    '''
    self.current_player.timer.stop()
    x = self.current_player.play(self.array)
    success = self.update_array(self.current_player, x)
    if success:
      self.switch_player()
    if type(self.current_player) == Ai:
      self.current_player.timer.start()

  def visualize(self):
    '''
    replots the array.
    In fact, all the circles are already plotted in the background
    color. This function just changes the color of these circles.
    To the color of the respective player
    '''
    if self.state() != 0:
      player = self.get_player(self.state())
      self.ax.set_title('%s WON'%player.name, color=player.color)
      self.fig.canvas.mpl_disconnect(self.cid)
      self.timer.stop()
      self.players[0].timer.stop()
      self.players[1].timer.stop()

    for i, j in zip(*np.where(self.array == 0)):
        self.plots[i,j].set_color(self.bgcolor)
    for i, j in zip(*np.where(self.array == 1)):
      self.plots[i,j].set_color(self.get_player(1).color)
    for i, j in zip(*np.where(self.array == 2)):
      self.plots[i,j].set_color(self.get_player(2).color)
    plt.draw()