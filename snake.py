''' Snake Game '''

#############
## Imports ##
#############

from random import random
import matplotlib.pyplot as plt

##############
## Settings ##
##############

plt.rcParams['toolbar'] = 'None'


##########
## Grid ##
##########

class SnakeGame(object):
    ''' The snake game '''
    def __init__(self, M=30, N=20, speed=15):
        ''' SnakeGame __init__

        Arguments
        ---------
        M : Horizontal number of grid points
        N : Vertical number of grid points
        speed : speed of the snake
        '''
        # save parameters
        self.M = M
        self.N = N

        # create matplotlib figure
        self.fig, self.ax = plt.subplots()
        plt.axis('scaled')
        plt.xlim(-0.5, M-0.5)
        plt.ylim(-0.5, N-0.5)
        plt.grid(False)
        self.timer = self.fig.canvas.new_timer(interval=1000.0/speed)
        self.timer.single_shot = False
        self.ax.set_title("Score: 0")
        self.fig.canvas.set_window_title("Snake")
        plt.xticks([])
        plt.yticks([])
        self.snake = Snake(self, speed=speed)
        self.food = Food(self)

    def start(self):
        ''' Start the game '''
        self.timer.start()
        self.fig.canvas.mpl_connect('key_press_event', self.on_key)
        plt.show()

    def on_key(self, event):
        ''' a keypress sends you here '''
        if event.key in ['left', 'right', 'up', 'down']:
            self.snake.change_direction(event.key)


###########
## Snake ##
###########

class Snake(object):
    ''' The Snake Class holds all relevant parameters and actions corresponding to the snake '''
    def __init__(self, game, speed=15, start_length=10):
        ''' Snake __init__

        Arguments
        ---------
        game : the game the snake is situated in
        speed : the speed of the snake
        start_length : the starting length of the snake

        Note
        ----
        The Snake constructor is called automatically by the SnakeGame constructor.
        '''
        # store the game the snake is playing in
        self.game = game
        # Store the relevant parameters
        self.speed = speed
        self.length = start_length
        self.x = list(range(self.game.M//2+self.length, self.game.M//2,-1))
        self.y = [self.game.N//2]*self.length
        self.direction = "right"
        self.next_directions = ["right"]
        self.opposites = {"left":"right", "right":"left", "up":"down", "down":"up"}

        # relevant matplotlib parameters:
        self.plot, = plt.plot(self.x, self.y, "rs", markersize=8)
        self.game.timer.add_callback(self.move)

    def change_direction(self, direction):
        ''' Store new directions in a list '''
        if len(self.next_directions) <= 2:
            self.next_directions += [direction]

    def move(self):
        ''' Move the snake one gridpoint '''
        # Check if direction was changed:
        if self.next_directions != []:
            next_direction = self.next_directions.pop(0)
            opposite_direction = self.opposites[self.direction]
            if next_direction != opposite_direction:
                self.direction = next_direction

        # check if the snake bites its tail
        if (self.x[0], self.y[0]) in list(zip(self.x[1:], self.y[1:])):
            self.dead()
            return

        # check if the snake is at a food location
        if self.x[0] == self.game.food.x and self.y[0] == self.game.food.y:
            self.game.food.new_location()
            self.eat()

        # move in the specified direction:
        if self.direction == "right":
            self.x = [(self.x[0]+1)%self.game.M] + self.x[:-1]
            self.y = [self.y[0]] + self.y[:-1]
        elif self.direction == "left":
            self.x = [(self.x[0]-1)%self.game.M] + self.x[:-1]
            self.y = [self.y[0]] + self.y[:-1]
        elif self.direction == "up":
            self.y = [(self.y[0]+1)%self.game.N] + self.y[:-1]
            self.x = [self.x[0]] + self.x[:-1]
        elif self.direction == "down":
            self.y = [(self.y[0]-1)%self.game.N] + self.y[:-1]
            self.x = [self.x[0]] + self.x[:-1]

        # Visualize the snake in its new location
        self.plot.set_data(self.x, self.y)
        plt.draw()

    def eat(self):
        ''' Eat the food and become one point longer. '''
        # prepend a new head to the tail:
        if self.direction == "right":
            self.x = [(self.x[0]+1)%self.game.M] + self.x
            self.y = [self.y[0]] + self.y
        elif self.direction == "left":
            self.x = [(self.x[0]-1)%self.game.M] + self.x
            self.y = [self.y[0]] + self.y
        elif self.direction == "up":
            self.y = [(self.y[0]+1)%self.game.N] + self.y
            self.x = [self.x[0]] + self.x
        elif self.direction == "down":
            self.y = [(self.y[0]-1)%self.game.N] + self.y
            self.x = [self.x[0]] + self.x

        # Visualize the snake in its new location
        self.plot.set_data(self.x, self.y)
        self.game.ax.set_title("Score: "+str(len(self.x)-self.length))
        plt.draw()

    def dead(self):
        ''' The snake bites its own tail and is now dead '''
        print('dead')

        # stop the timer (and give time to display the Game Over message)
        self.game.timer.single_shot = True

        # delete the head (this is kind of a hack)
        del self.x[0]
        del self.y[0]

        # show a final Game Over message
        message = "DEAD!\nscore: "+str(len(self.x)-self.length+1)
        self.game.ax.annotate(message, xy=(self.game.M/2, self.game.N/2), fontsize=24,
                              horizontalalignment='center', verticalalignment='center',
                              bbox=dict(facecolor='red', alpha=0.5))


##########
## Food ##
##########

class Food(object):
    ''' Rumour has it, a snake has to eat... '''
    def __init__(self, game):
        ''' Food __init__

        Arguments
        ---------
        game : the game the food is situated in

        Note
        ----
        The Food constructor is called automatically by the SnakeGame constructor.
        '''
        # store the game the snake is playing in
        self.game = game

        # relevant matplotlib parameters:
        self.plot, = plt.plot(0, 0, "go")
        self.new_location()

    def new_location(self):
        ''' Move the food to a random grid point '''
        # Visualize the food in its new location
        self.x = int(random()*self.game.M)
        self.y = int(random()*self.game.N)
        forbidden_points = list(zip(self.game.snake.x, self.game.snake.y))
        while (self.x, self.y) in forbidden_points:
            self.new_location()
        self.plot.set_data(self.x, self.y)


#########
## Run ##
#########

if __name__ == '__main__':
    import sys
    speed = 15
    if len(sys.argv) > 1:
        speed = float(sys.argv[1])
    snake_game = SnakeGame(speed=speed)
    snake_game.start()