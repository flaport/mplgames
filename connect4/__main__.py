
#############
## Imports ##
#############

from connect4 import Ai
from connect4 import Person
from connect4 import MplGame


###########
## Play! ##
###########


player1 = Person(1, name='Tom')
player2 = Ai(2, name='David')
game = MplGame(players=(player1, player2))
game.play()
