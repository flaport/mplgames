#############
## Imports ##
#############

import numpy as np
from scipy.signal import convolve2d


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
