from Models.Card import all_cards

max_len = 4


def turn_to_2d_array(array):
    part_counts = (len(array) + max_len - 1) // max_len
    answer = []
    while len(array) > 0:
        size = (len(array) + part_counts - 1) // part_counts
        in_while_array = []
        for i in range(size - 1, -1, -1):
            in_while_array.append(array[i])
            array.pop(i)
        answer.append(in_while_array)
        part_counts -= 1
    return answer


def get_query_data(command_type, command_name, data, game):
    return command_type + ';' + command_name + ';' + str(game.game_id) + ';' + str(game.turn_number) + '; ' + str(data)


def get_cards_description():
    description = 'توضیحات کارت ها:\n'
    for card in all_cards:
        description += '**'+card.name+'**' + ': ' + card.description + '\n\n'
    return description
