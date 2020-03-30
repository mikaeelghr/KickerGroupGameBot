import threading
import time

from Models.Game import Game
from Models.Player import Player

game = Game(0)
for i in range(0, 10):
    game.add_player(Player(i, "user " + str(i)))


def run_game():
    while len(game.players) > 2:
        print("number of players in this turn: " + str(len(game.players)))
        print("turn started, you can suggest cards")
        time.sleep(20)
        game.start_vote_time()
        print("vote time started, you can vote")
        time.sleep(20)
        print("turn ended")
        game.end_turn()
        game.start_new_turn()


th = threading.Thread(target=run_game)
th.start()

while True:
    print("you can perform query")
    query = input()
    if query.split()[0] == 'suggest_card':
        game.suggest_card(int(query.split()[1]), int(query.split()[2]), int(query.split()[3]))
    if query.split()[0] == 'vote':
        game.players[int(query.split()[1])].vote(int(query.split()[2]), game)
    if query.split()[0] == 'get_vote_weight':
        print(game.players[int(query.split()[1])].get_vote_weight(game))
    if query.split()[0] == 'get_players_can_vote':
        print(game.players[int(query.split()[1])].get_players_can_vote(game))
    if query.split()[0] == 'get_cards_can_suggest':
        print(game.players[int(query.split()[1])].get_cards_can_suggest(game))
    if query.split()[0] == 'get_players_can_suggest_card':
        print(game.players[int(query.split()[1])].get_players_can_suggest_card(int(query.split()[2]), game))

'''
get_cards_can_suggest 3 
get_players_can_suggest_card 3 0
get_players_can_suggest_card 3 1
get_players_can_suggest_card 3 2
get_players_can_suggest_card 3 3
get_players_can_suggest_card 3 4


suggest_card 1 2 0
suggest_card 1 3 1
suggest_card 1 9 1
suggest_card 1 5 0
suggest_card 2 3 0
suggest_card 2 1 0
get_vote_weight 0
get_vote_weight 1
get_vote_weight 2
get_vote_weight 3
get_players_can_vote 0
get_players_can_vote 1
get_players_can_vote 2
get_players_can_vote 3
get_players_can_vote 4
get_players_can_vote 5
get_players_can_vote 6
vote 1 2 4


'''