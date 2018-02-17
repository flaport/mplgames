#############
## Imports ##
#############

import random
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
    ''' The classic Tetris Game '''
    def __init__(self, height=5):
        ''' Canvas __init__ '''
        ## Constants
        self.X, self.Y = (10, 20) # Hardcoded for now

        ## Canvas
        f = float(height)/self.Y
        self.fig, self.ax = plt.subplots(figsize=(f*self.X, f*self.Y))
        self.fig.canvas.set_window_title('Tetris')
        self.fig.subplots_adjust(left=0,right=1,bottom=0,top=1)
        self.ax.set_title('test')
        try:
            plt.get_current_fig_manager().window.wm_iconbitmap("tetris.ico")
        except:
            pass
        plt.axis('scaled')
        plt.xlim(-0.5, self.X-0.5)
        plt.ylim(self.Y-0.5, -0.5)
        plt.xticks([x-0.5 for x in range(self.X)], ['' for i in range(self.X)])
        plt.yticks([y-0.5 for y in range(self.Y)], ['' for i in range(self.Y)])
        self.ax.tick_params(color='none')
        plt.grid()

        ## Timer
        self.timer = self.fig.canvas.new_timer(interval=100)
        self.timer.single_shot = False


############
## Blocks ##
############
class Block(object):
    name = ''
    color = None
    def __init__(self):
        self.x = None
        self.y = None
        self.fixed = False
    def create(self):
        markersize = 5.8*plt.gcf().get_size_inches()[0]
        self.plot, = plt.plot(self.x, self.y, 's', color=self.color, markersize=markersize)
    def update(self):
        self.plot.set_data(self.x, self.y)
        plt.draw()

    def move_down(self, game):
        newx = self.x
        newy = self.y + 1

        if (newy >= game.canvas.Y).any() or game.board[newx[newy>0], newy[newy>0]].any():
            self.fixed = True
            game.board[self.x[self.y>0], self.y[self.y>0]] = True
            return

        self.x = newx
        self.y = newy
        self.update()

    def rotate_clockwise(self, game, rot_axis=1):
        x0 = self.x[rot_axis]
        y0 = self.y[rot_axis]
        x_ = self.x - x0
        y_ = self.y - y0
        x, y = zip(*sorted(zip(x0+y_, y0-x_)))
        dx = x[rot_axis] - x0
        dy = y[rot_axis] - y0
        x = np.array(x-dx)
        y = np.array(y-dy)

        test = (x>=game.canvas.X).any() or (x<0).any() or (y>=game.canvas.Y).any() or (y<0).any()
        for i in range(4):
            test = test or (game.board[x[i], y[i]] > 0)
        if test and rot_axis != 0:
            self.rotate_clockwise(game, rot_axis=(rot_axis+1)%4)
        elif rot_axis == 0:
            return # No rotation
        else:
            self.x = x
            self.y = y
        self.update()

    def rotate_anticlockwise(self, game, rot_axis=1):
        for i in range(3):
            self.rotate_clockwise(game, rot_axis=rot_axis)

class IBlock(Block):
    name = 'I'
    color = 'C0'
    def __init__(self):
        Block.__init__(self)
        self.x = np.array([4,4,4,4])
        self.y = np.array([-3,-2,-1,0])

class ZBlock(Block):
    name = 'Z'
    color = 'C1'
    def __init__(self):
        Block.__init__(self)
        self.x = np.array([4,4,5,5])
        self.y = np.array([-2,-1,-1,0])

class SBlock(Block):
    name = 'S'
    color = 'C2'
    def __init__(self):
        Block.__init__(self)
        self.x = np.array([5,5,4,4])
        self.y = np.array([-2,-1,-1,0])

class TBlock(Block):
    name = 'S'
    color = 'C3'
    def __init__(self):
        Block.__init__(self)
        self.x = np.array([4,4,4,5])
        self.y = np.array([-2,-1,0,-1])

class LBlock(Block):
    name = 'L'
    color = 'C4'
    def __init__(self):
        Block.__init__(self)
        self.x = np.array([4,4,4,5])
        self.y = np.array([-2,-1,0,0])

class JBlock(Block):
    name = 'J'
    color = 'C5'
    def __init__(self):
        Block.__init__(self)
        self.x = np.array([5,4,4,4])
        self.y = np.array([-2,-2,-1,0])

class OBlock(Block):
    name = 'O'
    color = 'C6'
    def __init__(self):
        Block.__init__(self)
        self.x = np.array([4,4,5,5])
        self.y = np.array([-1,0,-1,0])

class BlockGenerator(np.random.RandomState):
    blocks = [IBlock,ZBlock,SBlock,TBlock,LBlock,JBlock,OBlock]
    def next(self):
        block = self.choice(self.blocks)()
        return block
    def preview(self):
        state = self.get_state()
        block = self.next()
        self.set_state(state)
        return block


#################
## Tetris Game ##
#################

class Tetris(object):
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
        self.block = self.block_generator.next()
        self.block.create()

    def start(self):
        self.canvas.timer.add_callback(self.update)
        self.canvas.fig.canvas.mpl_connect('key_press_event', self.on_key)
        self.canvas.timer.start()
        plt.show()

    def on_key(self, event):
        if event.key == 'up':
            self.block.rotate_clockwise(self)

    def update(self):
        self.block.move_down(self)
        if self.block.fixed:
            self.block.plot.remove()
            for x, y in zip(self.block.x, self.block.y):
                self.board_plots[x,y].set_color(self.block.color)
            self.block = self.block_generator.next()
            self.block.create()
            plt.draw()





if __name__ == '__main__':
    tetris = Tetris(seed=0)
    tetris.start()