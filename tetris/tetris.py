#############
## Imports ##
#############

import numpy as np
import matplotlib.pyplot as plt

##############
## Settings ##
##############

plt.switch_backend('TkAgg')
plt.rcParams['toolbar'] = 'none'
plt.rcParams['font.size'] = 14


############
## Canvas ##
############

class Canvas(object):
    ''' The Canvas holds the plot data of the Tetris Game '''
    def __init__(self, height=5):
        ''' Canvas __init__

        Arguments
        ---------
        Height of the tetris figure window (in inches).
        '''
        ## Constants
        self.X, self.Y = (10, 21) # Hardcoded for now

        ## Canvas
        f = float(height)/self.Y
        self.fig, self.ax = plt.subplots(figsize=(f*self.X, f*(self.Y-1)))
        self.fig.canvas.set_window_title('Tetris')
        self.fig.subplots_adjust(left=0,right=1,bottom=0,top=1)
        self.ax.set_title('test')
        try: # this only works on windows:
            plt.get_current_fig_manager().window.wm_iconbitmap("img/tetris.ico")
        except:
            pass
        plt.axis('scaled') # squares should be squares
        plt.xlim(-0.5, self.X-0.5)
        plt.ylim(self.Y-0.5, 0.5) # Note that row 0 will not be shown

        # We need xticks to visualize the grid but we don't want to see the numbers
        plt.xticks([x-0.5 for x in range(self.X)], ['' for i in range(self.X)])
        plt.yticks([y-0.5 for y in range(1, self.Y)], ['' for i in range(1, self.Y)])
        self.ax.tick_params(color='none') # We also don't want to see the ticks itself
        # show grid
        plt.grid()

        ## Timer
        self.timer = self.fig.canvas.new_timer(interval=100)
        self.timer.single_shot = False


############
## Blocks ##
############
class Block(object):
    ''' A Generic Tetris Block Contains all the Actions a Block can make '''
    name = ''
    color = None
    def __init__(self):
        ''' Block __init__ '''
        self.x = None # x location of the block
        self.y = None # y location of the block
        self.fixed = False # if the block is fixed in place
        self.waiting_time = 5 # Standard waiting time before fixing a block in place
        self.wait = 0 # How much time is left before the block will be fixed in place

    def create(self):
        ''' Creates the plot on the canvas '''
        markersize = 5.8*plt.gcf().get_size_inches()[0]
        self.plot, = plt.plot(self.x, self.y, 's', color=self.color, markersize=markersize)

    def update(self):
        ''' Updates the plot on the canvas with the new x and y data '''
        self.plot.set_data(self.x, self.y)
        plt.draw()

    def move_down(self, game, recursive=False):
        ''' Move the block one step down, if possible. If recursive = True, the block will
        go to the lowest possible point on the board '''

        newy = self.y + 1 # next location

        # check if the proposed move will fail
        failed_move = (newy >= game.canvas.Y).any()
        if not failed_move:
            failed_move = failed_move or game.board[self.x[newy>0], newy[newy>0]].any()

        if not failed_move: # if the move won't fail, perform move:
            self.y += 1
            if recursive: # as long as the move won't fail, perform move if recursive:
                self.move_down(game, recursive=True)
        else:
            if self.wait > 0: # reduce waiting time:
                self.wait -= 1
            else: # if we ran out of waiting time, fix the block in place:
                self.fixed = True
                game.board[self.x[self.y>0], self.y[self.y>0]] = True
                return

        # immediately show new position on board
        self.update()

    def put_down(self, game):
        ''' Put the block down immedeately '''
        self.move_down(game, recursive=True)
        self.wait = 0

    def move_right(self, game):
        ''' Move the block one position to the right '''

        # check if proposed move will fail:
        failed_move = (self.x+1>game.canvas.X-1).any()
        if not failed_move:
            failed_move = failed_move or game.board[self.x[self.y>0]+1, self.y[self.y>0]].any()

        if not failed_move: # if the mvoe won't fail, perform move:
            self.x += 1

        # Because we did a move, the waiting time to fix the block in place is reset:
        self.wait = self.waiting_time

    def move_left(self, game):
        ''' Move the block one position to the left '''

        # check if proposed move will fail:
        failed_move = (self.x-1<0).any()
        if not failed_move:
            failed_move = failed_move or game.board[self.x[self.y>0]-1, self.y[self.y>0]].any()

        if not failed_move: # if the move won't fail, perform move:
            self.x -= 1

        # Because we did a move, the waiting time to fix the block in place is reset:
        self.wait = self.waiting_time

    def _rotate(self, game, rot_axis, action):
        ''' Generic roation '''
        # we perform the rotation in the complex plane:
        xy = self.x + 1j*self.y
        xy0 = xy[rot_axis]
        xy -= xy0
        xy *= action
        xy += xy0
        x = np.int32(np.real(xy))
        y = np.int32(np.imag(xy))

        # check if the proposed rotation will fail:
        failed_rotation = (x>=game.canvas.X).any() or (x<0).any() or (y>=game.canvas.Y).any()
        if not failed_rotation:
            failed_rotation = failed_rotation or game.board[x[y>0],y[y>0]].any()

        if not failed_rotation: # if the rotation won't fail:
            self.x = x
            self.y = y
            self.update()
            self.wait = self.waiting_time
        elif rot_axis > 0: # if the rotation fails, try rotating around a different axis:
            self._rotate(game, (rot_axis+1)%4, action)

    def rotate_clockwise(self, game, rot_axis=1):
        ''' Rotate the block clockwise '''
        self._rotate(game, rot_axis, -1j)

    def rotate_anticlockwise(self, game, rot_axis=1):
        ''' Rotate the block anti clockwise '''
        self._rotate(game, rot_axis, +1j)

class IBlock(Block):
    ''' I Block '''
    name = 'I'
    color = 'C0'
    def __init__(self):
        Block.__init__(self)
        self.x = np.array([4,4,4,4])
        self.y = np.array([-4,-3,-2,-1])

class ZBlock(Block):
    ''' Z Block '''
    name = 'Z'
    color = 'C1'
    def __init__(self):
        Block.__init__(self)
        self.x = np.array([4,4,5,5])
        self.y = np.array([-3,-2,-2,-1])

class SBlock(Block):
    ''' S Block '''
    name = 'S'
    color = 'C2'
    def __init__(self):
        Block.__init__(self)
        self.x = np.array([5,5,4,4])
        self.y = np.array([-3,-2,-2,-1])

class TBlock(Block):
    ''' T Block '''
    name = 'S'
    color = 'C3'
    def __init__(self):
        Block.__init__(self)
        self.x = np.array([4,4,4,5])
        self.y = np.array([-3,-2,-1,-2])

class LBlock(Block):
    ''' L Block '''
    name = 'L'
    color = 'C4'
    def __init__(self):
        Block.__init__(self)
        self.x = np.array([4,4,4,5])
        self.y = np.array([-3,-2,-1,-1])

class JBlock(Block):
    ''' J Block '''
    name = 'J'
    color = 'C5'
    def __init__(self):
        Block.__init__(self)
        self.x = np.array([5,4,4,4])
        self.y = np.array([-3,-3,-2,-1])

class OBlock(Block):
    ''' O Block '''
    name = 'O'
    color = 'C6'
    def __init__(self):
        Block.__init__(self)
        self.x = np.array([4,4,5,5])
        self.y = np.array([-2,-1,-2,-1])
    def _rotate(*args):
        pass # OBlock cannot rotate.

class BlockGenerator(np.random.RandomState):
    ''' The BlockGenerator generates a block of a random type '''
    blocks = [IBlock,ZBlock,SBlock,TBlock,LBlock,JBlock,OBlock]
    def next(self):
        ''' Generate the next block '''
        block = self.choice(self.blocks)()
        return block
    def preview(self):
        ''' Have a look at the next block, without altering the random state '''
        state = self.get_state()
        block = self.next()
        self.set_state(state)
        return block


#################
## Tetris Game ##
#################

class Tetris(object):
    ''' The classic Tetris Game '''
    def __init__(self, seed=None):
        ''' Tetris __init__

        Arguments
        ---------
        seed = None: random seed for the block generation
        '''
        # canvas
        self.canvas = Canvas()

        # Block Generator
        self.block_generator = BlockGenerator(seed=seed)

        # Create Board:
        self.board = np.zeros((self.canvas.X, self.canvas.Y), dtype=bool)
        self.board_plots = np.zeros(self.board.shape, dtype=object)
        markersize = 5.8*plt.gcf().get_size_inches()[0]
        for i in range(self.canvas.X):
            for j in range(self.canvas.Y):
                self.board_plots[i,j] = plt.plot(i,j,'s', color='none', markersize=markersize)[0]

        # Create block
        self.block = self.block_generator.next()
        self.block.create()

    def start(self):
        ''' Start the Tetris Game '''
        self.canvas.timer.add_callback(self.update)
        self.canvas.fig.canvas.mpl_connect('key_press_event', self.on_key)
        self.canvas.timer.start()
        plt.show()

    def on_key(self, event):
        ''' Decide what to do during a key press event '''
        if event.key == 'up':
            self.block.rotate_anticlockwise(self)
        if event.key == 'down':
            self.block.move_down(self)
        if event.key == 'left':
            self.block.move_left(self)
        if event.key == 'right':
            self.block.move_right(self)
        if event.key == ' ':
            self.block.put_down(self)

    def game_over(self):
        ''' Game Over '''
        self.canvas.ax.set_title('Game Over')
        self.canvas.timer.single_shot = True
        self.canvas.timer.stop()

    def update(self):
        ''' Update the board '''
        self.block.move_down(self)
        if self.block.fixed:
            self.block.plot.remove()
            for x, y in zip(self.block.x, self.block.y):
                if y > 0:
                    self.board_plots[x,y].set_color(self.block.color)
            self.remove_lines()
            self.block = self.block_generator.next()
            self.block.create()
            plt.draw()
            if (self.board.sum(axis=0)[1:] > 0).all():
                self.game_over()
                return

    def remove_lines(self):
        ''' Remove lines '''
        lines = self.board.prod(axis=0)
        if lines.any():
            line = np.where(lines)[0][0]
            for i in range(self.canvas.X):
                self.board_plots[i,line].set_color('none')
                self.board_plots[i,line].set_ydata(0)
            for i in range(self.canvas.X):
                for j in range(line):
                    self.board_plots[i,j].set_ydata(j+1)
            self.board_plots = np.concatenate((
                self.board_plots[:,line:line+1],
                self.board_plots[:, :line],
                self.board_plots[:, line+1:]
            ), axis=-1)
            self.board = np.concatenate((
                np.zeros_like(self.board[:,line:line+1]),
                self.board[:,:line],
                self.board[:,line+1:],
            ), axis=-1)
            self.remove_lines()
