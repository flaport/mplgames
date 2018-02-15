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

class Game(object):
    def __init__(self, M=30, N=20, speed=15):
        self.M = M
        self.N = N
        self.fig, self.ax=plt.subplots()
        plt.axis('scaled')
        plt.xlim(-0.5, M-0.5)
        plt.ylim(-0.5, N-0.5)
        plt.grid(False)
        self.timer = self.fig.canvas.new_timer(interval=1000/speed)
        self.timer.single_shot = False
        self.ax.set_title("Score: 0")
        self.fig.canvas.set_window_title("Snake")
        plt.xticks([])
        plt.yticks([])

        self.snake = Snake(self, speed=speed)
        self.food = Food(self)
    def start(self):
        self.timer.start()
        self.fig.canvas.mpl_connect('key_press_event', self.snake.on_key)
        plt.show()


###########
## Snake ##
###########

class Snake():
    def __init__(self, game, speed=15):
        self.game = game
        self.speed = 15
        self.length = 10
        self.x = list(range(self.game.M//2+self.length, self.game.M//2,-1))
        self.y = [self.game.N//2]*self.length
        self.direction = "right"
        self.next_directions = ["right"]
        self.opposites = {"left":"right", "right":"left", "up":"down", "down":"up"}
        self.plot, = plt.plot(self.x, self.y, "ro")
        self.game.timer.add_callback(self.move)
    def on_key(self, event):
        if len(self.next_directions)<=2:
            self.next_directions += [event.key]
    @property
    def head(self):
        return (self.x[0], self.y[0])
    @property
    def points(self):
        return list(zip(self.x, self.y))
    @property
    def opposite_direction(self):
        return self.opposites[self.direction]
    def move(self):
        if self.next_directions != []:
            next_direction = self.next_directions.pop(0)
            if next_direction != self.opposite_direction:
                self.direction = next_direction
        if self.head in self.points[1:]:
            self.dead()
            return
        if self.x[0] == self.game.food.x and self.y[0] == self.game.food.y:
            self.game.food.new_pos()
            self.eat()
        if self.direction=="right":
            self.x = [(self.x[0]+1)%self.game.M] + self.x[:-1]
            self.y = [self.y[0]] + self.y[:-1]
        elif self.direction=="left":
            self.x = [(self.x[0]-1)%self.game.M] + self.x[:-1]
            self.y = [self.y[0]] + self.y[:-1]
        elif self.direction=="up":
            self.y = [(self.y[0]+1)%self.game.N] + self.y[:-1]
            self.x = [self.x[0]] + self.x[:-1]
        elif self.direction=="down":
            self.y = [(self.y[0]-1)%self.game.N] + self.y[:-1]
            self.x = [self.x[0]] + self.x[:-1]
        else:
            raise ValueError("No valid direction for the snake")
        self.plot.set_data(self.x, self.y)
        plt.draw()
    def eat(self):
        if self.direction=="right":
            self.x = [(self.x[0]+1)%self.game.M] + self.x
            self.y = [self.y[0]] + self.y
        elif self.direction=="left":
            self.x = [(self.x[0]-1)%self.game.M] + self.x
            self.y = [self.y[0]] + self.y
        elif self.direction=="up":
            self.y = [(self.y[0]+1)%self.game.N] + self.y
            self.x = [self.x[0]] + self.x
        elif self.direction=="down":
            self.y = [(self.y[0]-1)%self.game.N] + self.y
            self.x = [self.x[0]] + self.x
        else:
            raise ValueError("No valid direction for the snake")
        self.plot.set_data(self.x, self.y)
        self.game.ax.set_title("Score: "+str(len(self.x)-self.length))
        plt.draw()
    def dead(self):
        print('dead')
        self.game.timer.single_shot=True
        del self.x[0]
        del self.y[0]
        message = "DEAD!\nscore: "+str(len(self.x)-self.length+1)
        self.game.ax.annotate(message, xy=(self.game.M/2, self.game.N/2), fontsize=24,
                              horizontalalignment='center', verticalalignment='center',
                              bbox=dict(facecolor='red', alpha=0.5))


##########
## Food ##
##########

class Food():
    def __init__(self, game):
        self.game = game
        self.plot, = plt.plot(0, 0, "go")
        self.new_pos()
    def new_pos(self):
        self.x = int(random()*self.game.M)
        self.y = int(random()*self.game.N)
        self.plot.set_data(self.x, self.y)


#########
## Run ##
#########

if __name__ == '__main__':
    snake_game = Game()
    snake_game.start()
