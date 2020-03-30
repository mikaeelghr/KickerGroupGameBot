from random import randrange

from Models.ActiveCard import ActiveCard
from Models.Card import all_cards
from Models.Player import Player
import Messages


class Game:
    last_id = 1

    def __init__(self, group_id):
        self.group_id = group_id
        self.players = {}
        self.removed_players = []
        self.game_id = Game.last_id
        Game.last_id += 1
        self.turn_number = 1
        self.vote_time = False

    def send_turn_result(self, bot):
        text = 'آمار رای های این دست:\n\n'
        for player in self.players.values():
            text += player.get_received_votes_description() + '\n\n'
        bot.send_message(chat_id=self.group_id, text=text)

    def send_suggest_card_messages(self, bot):
        for player in self.players.values():
            try:
                reply_markup = player.get_suggest_card_inline_keyboard(self)
                bot.send_message(
                    text=Messages.SUGGEST_CARD_TEXT,
                    chat_id=player.id,
                    reply_markup=reply_markup
                )
            except Exception as e:
                print(e)

    def validate_query(self, query):
        command_type = query.split(';')[0]
        game_id = int(query.split(';')[2])
        turn_number = int(query.split(';')[3])
        if game_id != self.game_id or turn_number != self.turn_number:
            raise Exception(Messages.EXPIRED_MESSAGE)
        if command_type == Messages.VOTE and not self.vote_time:
            raise Exception(Messages.NOT_VOTE_TIME)
        if command_type == Messages.SUGGEST_CARD and self.vote_time:
            raise Exception(Messages.NOT_SUGGEST_CARD_TIME)

    def suggest_card(self, seller_player_id, owner_player_id, card_id):
        active_card = ActiveCard(all_cards[card_id], self.turn_number + 1, seller_player_id, owner_player_id)
        self.players[seller_player_id].suggested_cards.append(active_card)

    def add_player(self, player: Player):
        for player_id in self.players:
            if player_id == player.id:
                raise Exception(Messages.USER_ALREADY_JOINED_ERROR)
        self.players[player.id] = player

    def get_voted_player(self):
        voted_players = []
        for player_id, player in self.players.items():
            if len(voted_players) == 0 or \
                    player.collected_votes_in_this_turn > voted_players[0].collected_votes_in_this_turn or \
                    (player.collected_votes_in_this_turn == voted_players[0].collected_votes_in_this_turn and
                     player.total_collected_votes > voted_players[0].total_collected_votes):
                voted_players.clear()
                voted_players.append(player)
            elif (player.collected_votes_in_this_turn == voted_players[0].collected_votes_in_this_turn and
                  player.total_collected_votes == voted_players[0].total_collected_votes):
                voted_players.append(player)
        return voted_players[randrange(len(voted_players))]

    def end_turn(self, bot):
        for player_id, player in self.players.items():
            player.end_turn(self)
        voted_player = self.get_voted_player()
        print("Player " + str(voted_player.id) + " removed by game")
        self.removed_players.append(voted_player.id)
        self.send_turn_result(bot)

    def start_vote_time(self, bot):
        self.vote_time = True
        for player in self.players.values():
            player.send_suggest_card_result(bot, self)
        for player in self.players.values():
            player.vote_time()
        for player in self.players.values():
            player.send_vote_message(bot, self)

    def start_new_turn(self, bot):
        print(self.removed_players)
        self.kick_removed_players(bot)
        for player_id in self.removed_players:
            if player_id in self.players.keys():
                self.players.pop(player_id)
        self.removed_players.clear()
        self.turn_number += 1
        self.vote_time = False
        for player in self.players.values():
            player.send_sold_cards_message(bot, self)

    def kick_removed_players(self, bot):
        for player_id in self.removed_players:
            self.players[player_id].kick(bot, self)
