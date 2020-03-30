import copy

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from Models.ActiveCard import ActiveCard, valid_list_of_sold_card
from Models.Card import Card, all_cards
from Models.FriendCard import FriendCard
from Models.StaticMethods import turn_to_2d_array, get_query_data
from Models.TurnCard import TurnCard
import Messages


class Player:
    def __init__(self, player_id, first_name, fake=False):
        if fake:
            self.real_id = 827691955
        else:
            self.real_id = player_id
        self.id = player_id
        self.first_name = first_name
        self.sold_cards = []
        self.suggested_cards = []
        self.selected_card_id = None
        self.selected_suggested_players_for_card_id = []
        self.selected_players_on_this_turn = []
        self.total_collected_votes = 0
        self.collected_votes_in_this_turn = 0
        self.collected_player_votes_in_this_turn = []

    def suggest_card_submit(self, game):
        for player_id in self.selected_suggested_players_for_card_id:
            game.suggest_card(self.id, player_id, self.selected_card_id)
        self.selected_card_id = None
        self.selected_suggested_players_for_card_id = []

    def kick(self, bot, game):
        Messages.send_message(bot, self.real_id, Messages.YOU_LOSE)
        bot.kick_chat_member(game.group_id, self.real_id)

    def send_suggest_card_message(self, bot, game):
        reply_markup = self.get_suggest_card_inline_keyboard(game)
        bot.send_message(chat_id=self.real_id,
                         text=Messages.SUGGEST_CARD_TEXT,
                         reply_markup=reply_markup)

    def send_suggest_card_result(self, bot, game):
        text = Messages.SUGGEST_CARD_RESULT_FIRST_LINE
        cards = self.get_suggested_card_received(game)
        for active_card in cards:
            text += active_card.get_description(game)
        if len(cards) == 0:
            text = Messages.SUGGEST_CARD_RESULT_FIRST_LINE_EMPTY
        bot.send_message(chat_id=self.real_id, text=text)

    def send_sold_cards_message(self, bot, game):
        text = Messages.SOLD_CARD_FIRST_LINE
        cards = self.sold_cards
        for active_card in cards:
            text += active_card.get_general_description_for_seller(game)
        if len(cards) == 0:
            text = Messages.NO_SOLD_CARDS
        bot.send_message(chat_id=self.real_id, text=text)

    def send_vote_message(self, bot, game):
        reply_markup = self.get_vote_inline_keyboard(game)
        if reply_markup is None:
            bot.send_message(chat_id=self.real_id, text=Messages.NO_VOTE_OPTIONS)
        else:
            bot.send_message(chat_id=self.real_id,
                             text=Messages.VOTE_TEXT + ', وزن رای شما در این دست: ' + str(self.get_vote_weight(game)),
                             reply_markup=reply_markup)

    def get_received_votes_description(self):
        description = self.first_name + ':\n' + 'مجموع آرا در این دست ' + str(self.collected_votes_in_this_turn) + '\n'
        description += 'مجموع آرا در دست های قبلی: ' + str(self.total_collected_votes) + '\n'
        if len(self.collected_player_votes_in_this_turn) > 0:
            description += 'رای دهندگان:\n'
            for player in self.collected_player_votes_in_this_turn:
                description += player.first_name + ' ,'
            description = description[:len(description) - 1]
        return description

    def get_vote_weight(self, game):
        vote_weight = 1
        for active_card in self.sold_cards:
            if isinstance(active_card.card, FriendCard) and not active_card.deleted(game):
                vote_weight += 1
        for other_player_id, other_player in game.players.items():
            if other_player.get_vote_owner(game) == self.id:
                vote_weight += 1
        return vote_weight

    def get_vote_owner(self, game, real_ask=False):
        vote_sum = [0] * Card.maximum_turns_count
        best_active_card = None
        for active_card in self.sold_cards:
            if isinstance(active_card.card, TurnCard):
                if best_active_card is None or best_active_card.expiration_time() > active_card.expiration_time():
                    best_active_card = active_card
                vote_sum[active_card.expiration_time() - game.turn_number - 1] += active_card.card_data
        for i in range(0, Card.maximum_turns_count):
            vote_sum[i] += vote_sum[i - 1]
            if vote_sum[i] == i + 1:
                if real_ask:
                    best_active_card.card_data -= 1
                return best_active_card.owner_player_id
        return None

    def get_suggest_card_inline_keyboard(self, game):
        buttons = []
        card_not_selected = True
        cards = self.get_cards_can_suggest(game)
        for card in cards:
            print(card.id)
            button_text = str(card.id)
            if self.selected_card_id == card.id:
                button_text += Messages.SELECT_TEXT
                card_not_selected = False
            buttons.append(InlineKeyboardButton(text=button_text,
                                                callback_data=get_query_data(Messages.SUGGEST_CARD,
                                                                             Messages.SELECT_CARD, card.id, game)))
        buttons2d = turn_to_2d_array(buttons)
        buttons = []
        if card_not_selected:
            self.selected_card_id = None
        else:
            new_selected_list = []
            additional_active_cards = []
            players = []
            for player_id in self.selected_suggested_players_for_card_id:
                players.append(game.players[player_id])
                additional_active_cards.append(
                    ActiveCard(all_cards[self.selected_card_id], game.turn_number + 1, self.id, player_id))
            players.extend(self.get_players_can_suggest_card(self.selected_card_id, game,
                                                             additional_active_cards=additional_active_cards))
            players.sort(key=lambda some_player: some_player.first_name)
            for player in players:
                button_text = str(player.first_name)
                if player.id in self.selected_suggested_players_for_card_id:
                    new_selected_list.append(player.id)
                    button_text += Messages.SELECT_TEXT
                buttons.append(InlineKeyboardButton(text=button_text,
                                                    callback_data=get_query_data(Messages.SUGGEST_CARD,
                                                                                 Messages.SELECT_PLAYER, player.id,
                                                                                 game)))
            self.selected_suggested_players_for_card_id = new_selected_list
            buttons2d.extend(turn_to_2d_array(buttons))
            if len(new_selected_list) > 0:
                buttons2d.append([InlineKeyboardButton(text="Submit",
                                                       callback_data=get_query_data(Messages.SUGGEST_CARD,
                                                                                    Messages.SUBMIT, 0, game))])
        reply_markup = InlineKeyboardMarkup(buttons2d)
        return reply_markup

    def get_vote_inline_keyboard(self, game):
        buttons = []
        self.selected_card_id = None
        new_selected_list = []
        players = self.get_players_can_vote(game)
        for player in players:
            button_text = str(player.first_name)
            if player.id in self.selected_players_on_this_turn:
                new_selected_list.append(player.id)
                button_text += Messages.SELECT_TEXT
            buttons.append(InlineKeyboardButton(text=button_text,
                                                callback_data=
                                                get_query_data(Messages.VOTE, Messages.SELECT_PLAYER, player.id, game)))
        if len(buttons) == 0:
            return None
        buttons2d = turn_to_2d_array(buttons)
        reply_markup = InlineKeyboardMarkup(buttons2d)
        return reply_markup

    def vote_effect_on_sold_cards(self, player_id, active_cards, game, fake_effect=True):
        deleted_list = []
        for active_card in active_cards:
            if not fake_effect or not isinstance(active_card.card, FriendCard):
                active_card.card.vote_effect(self.id, player_id, active_card, game)
            if active_card.deleted(game):
                deleted_list.append(active_card)
        for active_card in deleted_list:
            active_cards.remove(active_card)

    def vote(self, player_id, game):
        player = game.players[player_id]
        game.players[player_id].collected_votes_in_this_turn += self.get_vote_weight(game)
        game.players[player_id].collected_player_votes_in_this_turn.append(self)
        self.vote_effect_on_sold_cards(player_id, self.sold_cards, game, fake_effect=False)
        deleted_list = []
        for active_card in game.players[player_id].sold_cards:
            active_card.card.vote_effect(self.id, player_id, active_card, game)
            if active_card.deleted(game):
                deleted_list.append(active_card)
        for active_card in deleted_list:
            player.sold_cards.remove(active_card)

    def get_players_can_vote(self, game):
        players_can_vote = []
        for player_id, player in game.players.items():
            if player_id != self.id:
                active_cards = copy.deepcopy(self.sold_cards)
                print(active_cards)
                self.vote_effect_on_sold_cards(player_id, active_cards, game)
                if valid_list_of_sold_card(game.turn_number + 1, game, active_cards):
                    players_can_vote.append(player)
        return players_can_vote

    def get_suggested_card_received(self, game):
        suggested_card_received = []
        for player in game.players.values():
            for active_card in player.suggested_cards:
                if active_card.owner_player_id == self.id:
                    suggested_card_received.append(active_card)
        return suggested_card_received

    def get_cards_can_suggest(self, game):
        cards_can_suggest = []
        active_cards = []
        active_cards.extend(self.sold_cards)
        active_cards.extend(self.suggested_cards)
        for card in all_cards:
            active_card = ActiveCard(card, game.turn_number + 1, self.id, None)
            active_cards.append(active_card)
            if valid_list_of_sold_card(game.turn_number, game, active_cards):
                cards_can_suggest.append(card)
            active_cards.pop(-1)
        return cards_can_suggest

    def get_players_can_suggest_card(self, card_id: int, game, additional_active_cards=None):
        if additional_active_cards is None:
            additional_active_cards = []
        players_can_suggest_card = []
        active_cards = []
        active_cards.extend(self.sold_cards)
        active_cards.extend(self.suggested_cards)
        active_cards.extend(additional_active_cards)
        for player in game.players.values():
            active_card = ActiveCard(all_cards[card_id], game.turn_number + 1, self.id, player.id)
            active_cards.append(active_card)
            if valid_list_of_sold_card(game.turn_number, game, active_cards):
                players_can_suggest_card.append(player)
            active_cards.pop(-1)
        return players_can_suggest_card

    def vote_time(self):
        self.selected_card_id = None
        self.selected_suggested_players_for_card_id = []

    def end_turn(self, game):
        self.get_vote_owner(game, real_ask=True)
        for player_id in self.selected_players_on_this_turn:
            self.vote(player_id, game)
        for active_card in self.suggested_cards:
            bought = True
            for player in self.collected_player_votes_in_this_turn:
                if player.id == active_card.owner_player_id:
                    bought = False
            if bought:
                active_card.buy()
                self.sold_cards.append(active_card)
        self.suggested_cards = []
        self.selected_players_on_this_turn = []
        self.total_collected_votes += self.collected_votes_in_this_turn
        self.collected_votes_in_this_turn = 0
        self.collected_player_votes_in_this_turn = []
        remove_list = []
        for card in self.sold_cards:
            if card.deleted(game):
                remove_list.append(card)
        for card in remove_list:
            self.sold_cards.remove(card)
