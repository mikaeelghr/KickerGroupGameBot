from Models.Card import Card, all_cards


class TurnCard(Card):
    def __init__(self, name, description, turns_count, vote_count):
        super().__init__(name, description, turns_count)
        self.vote_count = vote_count

    def get_default_card_data(self):
        return self.vote_count

    def deleted(self, active_card, game):
        if active_card.card_data == 0 or super().deleted(active_card, game):
            return True
        return False


all_turn_cards = [
    TurnCard("نوبت ۱ 🎴", "این دست نوبتم مال تو", 1, 1),
    TurnCard("نوبت ۲ 🎴", "از الان تا ۳ دست بعد یکی از نوبتام مال تو", 3, 1),
    TurnCard("نوبت ۳ 🎴", "از الان تا ۱۰ دست  ۳ تا از نوبتام مال تو", 10, 3)
]

all_cards.extend(all_turn_cards)
