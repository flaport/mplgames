#############
## Imports ##
#############

import sys
from snake import SnakeGame


###########
## Play! ##
###########

speed = 15
if len(sys.argv) > 1:
    speed = float(sys.argv[1])

snake_game = SnakeGame(speed=speed)
snake_game.start()
