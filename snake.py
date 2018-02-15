from random import random
import matplotlib.pyplot as plt
plt.rcParams['toolbar'] = 'None'

SPEED = 21
M = 30
N = 20

class Snake():
    def __init__(self):
        self.fig,self.ax=plt.subplots()
        plt.axis('scaled')
        plt.xlim(-0.5,M-0.5)
        plt.ylim(-0.5,N-0.5)
        plt.grid(False)
        self.timer = self.fig.canvas.new_timer(interval=1000/SPEED)
        self.timer.add_callback(self.move)
        self.timer.single_shot=False
        self.l = 10
        self.x = list(range(M//2+self.l,M//2,-1))
        self.y = [N//2]*self.l
        self.ax.set_title("Score: 0")
        self.fig.canvas.set_window_title("Snake")
        self.direction = "right"
        self.opposites = {"left":"right","right":"left","up":"down","down":"up"}
        self.plot, = plt.plot(self.x,self.y,"ro")
        self.food = Food()
        plt.xticks([])
        plt.yticks([])
    def __call__(self):
        self.timer.start()
        self.fig.canvas.mpl_connect('key_press_event',self.on_key)
        plt.show()
    def on_key(self, event):
        if event.key != self.opposite_direction and event.key in ["left","right","up","down"]:
            self.direction = event.key
        if event.key == 'm':
            self.dead()
    @property
    def head(self):
        return (self.x[0],self.y[0])
    @property
    def points(self):
        return list(zip(self.x,self.y))
    @property
    def opposite_direction(self):
        return self.opposites[self.direction]
    def move(self):
        if self.head in self.points[1:]:
            self.dead()
            return
        if self.x[0] == self.food.x and self.y[0] == self.food.y:
            self.food.new_pos()
            self.eat()
        if self.direction=="right":
            self.x = [(self.x[0]+1)%M] + self.x[:-1]
            self.y = [self.y[0]] + self.y[:-1]
        elif self.direction=="left":
            self.x = [(self.x[0]-1)%M] + self.x[:-1]
            self.y = [self.y[0]] + self.y[:-1]
        elif self.direction=="up":
            self.y = [(self.y[0]+1)%N] + self.y[:-1]
            self.x = [self.x[0]] + self.x[:-1]
        elif self.direction=="down":
            self.y = [(self.y[0]-1)%N] + self.y[:-1]
            self.x = [self.x[0]] + self.x[:-1]
        else:
            raise ValueError("No valid direction for the snake")
        self.plot.set_data(self.x,self.y)
        plt.draw()
    def eat(self):
        if self.direction=="right":
            self.x = [(self.x[0]+1)%M] + self.x
            self.y = [self.y[0]] + self.y
        elif self.direction=="left":
            self.x = [(self.x[0]-1)%M] + self.x
            self.y = [self.y[0]] + self.y
        elif self.direction=="up":
            self.y = [(self.y[0]+1)%N] + self.y
            self.x = [self.x[0]] + self.x
        elif self.direction=="down":
            self.y = [(self.y[0]-1)%N] + self.y
            self.x = [self.x[0]] + self.x
        else:
            raise ValueError("No valid direction for the snake")
        self.plot.set_data(self.x,self.y)
        self.ax.set_title("Score: "+str(len(self.x)-self.l))
        plt.draw()
    def dead(self):
        print('dead')
        self.timer.single_shot=True
        del self.x[0]
        del self.y[0]
        message = "DEAD!\nscore: "+str(len(self.x)-self.l+1)
        self.ax.annotate(message, xy=(M/2,N/2), fontsize=24,
                            horizontalalignment='center', verticalalignment='center',
                            bbox=dict(facecolor='red', alpha=0.5))

class Food():
    def __init__(self):
        self.plot, = plt.plot(0,0,"go")
        self.new_pos()
    def new_pos(self):
        self.x = int(random()*M)
        self.y = int(random()*N)
        self.plot.set_data(self.x,self.y)

snake = Snake()
snake()
