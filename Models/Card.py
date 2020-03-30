class Card:
    maximum_turns_count = 20
    last_id = 0

    def __init__(self, name, description, turns_count):
        self.id = Card.last_id
        Card.last_id += 1
        self.name = name
        self.description = description
        self.turns_count = turns_count

    def get_default_card_data(self):
        return None

    def vote_effect(self, from_player_id: int, to_player_id: int, active_card, game) -> None:
        pass

    def deleted(self, active_card, game):
        if active_card.seller_player_id in game.players.keys() and active_card.owner_player_id in game.players.keys():
            return False
        return True


all_cards = []
