from Models.Card import Card, all_cards


class DefenseCard(Card):
    def __init__(self, name, description, turns_count, maximum_vote_count):
        super().__init__(name, description, turns_count)
        self.maximum_vote_count = maximum_vote_count

    def get_default_card_data(self):
        return self.maximum_vote_count

    def vote_effect(self, from_player_id: int, to_player_id: int, active_card, game) -> None:
        if active_card.seller_player_id == from_player_id and active_card.owner_player_id == to_player_id:
            active_card.card_data -= 1

    def deleted(self, active_card, game):
        if game.turn_number >= active_card.sold_at_turn + self.turns_count or super().deleted(active_card, game):
            return True
        return False


all_defense_cards = [
    DefenseCard("کارت دفاعی ۱", "این دست بهت رای نمیدم", 1, 0),
    DefenseCard("کارت دفاعی ۲", "از الان تا ۳ دست بعد بهت رای نمیدم", 3, 0),
    DefenseCard("کارت دفاعی ۳", "از الان تا ۱۰ دست بعد بهت حداکثر یک بار رای میدم", 10, 1)
]

all_cards.extend(all_defense_cards)
