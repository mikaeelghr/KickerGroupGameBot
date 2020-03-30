'''

from telegram import InlineKeyboardButton
max_len = 4




def get_player_inline_keyboard_buttons(user_id):
    player = all_players[user_id]
    players = []
    for other_user_id in all_players:
        if other_user_id != user_id and not player.had_suggested(other_user_id):
            print(all_players[other_user_id].id)
            for i in range(0, 19):
                players.append(InlineKeyboardButton(text=all_players[other_user_id].first_name,
                                                    callback_data=all_players[other_user_id].id))

    return turn_to_2d_array(players)
'''
