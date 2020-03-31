from Models.Card import Card, all_cards


class FriendCard(Card):
    def __init__(self, name, description, turns_count=10000):
        super().__init__(name, description, turns_count)

    def vote_effect(self, from_player_id: int, to_player_id: int, active_card, game) -> None:
        have_owner_died = (
                active_card.seller_player_id == from_player_id and active_card.owner_player_id == to_player_id)
        have_seller_died = (
                active_card.seller_player_id == to_player_id and active_card.owner_player_id == from_player_id)
        if have_owner_died and have_seller_died:
            active_card.deleted = True
        elif have_seller_died:
            game.removed_players.append(active_card.seller_player_id)
        elif have_owner_died:
            game.removed_players.append(active_card.owner_player_id)


all_friend_cards = [
    FriendCard("دوستی👬", "بیا دوست شیم. تا زمانی که ما با هم دوستیم(تا وقتی که کارت باطل نشده)," +
               " هر دومون رای مون یدونه بیشتر از حالت عادی حساب میشه." +
               " ولی اگه یکیمون تو یه دست خیانت کنه و به اونیکی رای بده, اونیکی در جا حذف میشه از گروه" +
               "اگر هم هر دو به هم تو یه دست رای بدن, کارت باطل میشه")
]

all_cards.extend(all_friend_cards)
