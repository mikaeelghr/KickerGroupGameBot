from Models.DefenseCard import DefenseCard
from Models.TurnCard import TurnCard
from Models.FriendCard import FriendCard
from Models.Card import Card


class ActiveCard:
    def __init__(self, card: Card, sold_at_turn, seller_player_id, owner_player_id):
        self.card = card
        self.bought = False
        self.sold_at_turn = sold_at_turn
        self.seller_player_id = seller_player_id
        self.owner_player_id = owner_player_id
        self.card_data = card.get_default_card_data()

    def buy(self):
        self.bought = True

    def expiration_time(self):
        return self.sold_at_turn + self.card.turns_count

    def deleted(self, game):
        return self.card.deleted(self, game)

    def get_description(self, game):
        return game.players[self.seller_player_id].first_name + ': ' + self.card.name + '\n'

    def get_general_description_for_seller(self, game):
        if self.deleted(game):
            return ''
        else:
            return self.card.name + ' به ' + game.players[
                self.owner_player_id].first_name + ' در دست شماره ' + str(self.sold_at_turn) + '\n'

    def get_general_description_for_owner(self, game):
        if self.deleted(game):
            return ''
        else:
            return self.card.name + ' از ' + game.players[
                self.owner_player_id].first_name + ' در دست شماره ' + str(self.sold_at_turn) + '\n'


def valid_list_of_sold_card(turn_number: int, game, active_cards):
    vote_sum = [0] * Card.maximum_turns_count
    vote_sum_bought = [0] * Card.maximum_turns_count
    have_suggest = {}
    friends = {}
    for active_card in active_cards:
        if not active_card.deleted(game) and game.turn_number >= active_card.expiration_time():
            return False
        if active_card.deleted(game):
            continue
        if active_card.seller_player_id == active_card.owner_player_id:
            return False
        if active_card.owner_player_id is not None:
            print((active_card.sold_at_turn, active_card.owner_player_id, active_card.seller_player_id))
            if (active_card.sold_at_turn, active_card.owner_player_id, active_card.seller_player_id) in have_suggest:
                return False
            have_suggest[(active_card.sold_at_turn, active_card.owner_player_id, active_card.seller_player_id)] = True
        if isinstance(active_card.card, DefenseCard) and active_card.card_data < 0:
            return False
        if isinstance(active_card.card, TurnCard):
            if active_card.bought:
                vote_sum_bought[active_card.expiration_time() - turn_number] += active_card.card_data
            else:
                vote_sum[active_card.expiration_time() - turn_number] += active_card.card_data
        if isinstance(active_card.card, FriendCard):
            if (active_card.owner_player_id, active_card.seller_player_id) in friends:
                return False
            friends[(active_card.owner_player_id, active_card.seller_player_id)] = True
            friends[(active_card.seller_player_id, active_card.owner_player_id)] = True
    for i in range(0, Card.maximum_turns_count):
        vote_sum[i] += vote_sum[i - 1]
        vote_sum_bought[i] += vote_sum_bought[i - 1]
        if vote_sum_bought[i] + vote_sum[i] > i or (0 < i == vote_sum[i]):
            return False
    return True
