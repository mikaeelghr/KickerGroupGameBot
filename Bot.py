import copy
import os
import threading
import time

import telegram
from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, CallbackQueryHandler

from Models.Game import Game
from Models.Player import Player
import Messages
from Models.StaticMethods import turn_to_2d_array, get_query_data
'''
proxy = 'http://127.0.0.1:41177/'

os.environ['http_proxy'] = proxy
os.environ['HTTP_PROXY'] = proxy
os.environ['https_proxy'] = proxy
os.environ['HTTPS_PROXY'] = proxy
'''

TOKEN = '1107549294:AAHwx42GH_pnGtD3r9K6KvDiOOwvRJThYkY'
updater = Updater(TOKEN, use_context=True)

bot = telegram.Bot(token=TOKEN)
game = Game(-1001279873630)


def send_to_group(message):
    bot.send_message(chat_id=game.group_id, text=message)


def say(update: telegram.Update, context: telegram.ext.CallbackContext):
    text_to_say = update.message.text[4:]
    context.bot.send_message(chat_id=game.group_id, text=text_to_say)


def start(update: telegram.Update, context: telegram.ext.CallbackContext):
    print(update.effective_user.id)
    if update.effective_chat.id != update.effective_user.id:
        Messages.send_message(context.bot, update.effective_chat.id, Messages.SEND_START_ON_GROUP_ERROR)
        return
    response = bot.get_chat_member(chat_id=game.group_id, user_id=update.effective_user.id)
    print(response.status)
    if not response.status == 'member' and not response.status == 'creator' and not response.status == 'restricted':
        Messages.send_message(context.bot, update.effective_chat.id,
                              Messages.SEND_START_WHEN_IS_NOT_JOINED_ON_GROUP_ERROR)
        return
    try:
        game.add_player(Player(update.effective_user.id, update.effective_user.first_name))
        Messages.send_message(context.bot, update.effective_chat.id,
                              Messages.USER_JOINED_SUCCESSFULLY)
    except Exception as e:
        Messages.send_message(context.bot, update.effective_chat.id, str(e))


def text(update: telegram.Update, context: telegram.ext.CallbackContext):
    print(update.effective_chat)
    print(update.effective_message)


def receive_private_messages(update: telegram.Update, context: telegram.ext.CallbackContext):
    print(update.message)


def get_players_can_vote(update: telegram.Update, context: telegram.ext.CallbackContext):
    player_id = int(update.message.text.split()[1])
    players = game.players[player_id].get_players_can_vote(game)
    players_buttons = []
    for player in players:
        players_buttons.append(InlineKeyboardButton(text=player.first_name,
                                                    callback_data=get_query_data(Messages.SUGGEST_CARD,
                                                                                 Messages.SELECT_CARD, player.id,
                                                                                 game)))

    bot.send_message(chat_id=update.effective_chat.id, parse_mode=telegram.ParseMode.MARKDOWN,
                     text=Messages.SUGGEST_CARD_TEXT,
                     reply_markup=InlineKeyboardMarkup(
                         turn_to_2d_array(players_buttons)))


def suggest_card_select_card(update, context):
    query = update.callback_query
    try:
        game.validate_query(query.data)
        player = game.players[update.effective_user.id]
        selected_id = int(query.data.split(' ')[1])

        if player.selected_card_id == selected_id:
            player.selected_card_id = None
        else:
            player.selected_card_id = selected_id
        player.selected_suggested_players_for_card_id = []
        reply_markup = player.get_suggest_card_inline_keyboard(game)
        query.edit_message_text(
            text=Messages.SUGGEST_CARD_TEXT,
            reply_markup=reply_markup
        )
    except Exception as e:
        print(e)
        query.answer('خطا:' + str(e))
        query.edit_message_text(
            text="deleted message",
            reply_markup=None
        )


def suggest_card_select_player(update, context):
    query = update.callback_query
    try:
        game.validate_query(query.data)
        player = game.players[update.effective_user.id]
        selected_id = int(query.data.split(' ')[1])
        if selected_id in player.selected_suggested_players_for_card_id:
            player.selected_suggested_players_for_card_id.remove(selected_id)
        else:
            player.selected_suggested_players_for_card_id.append(selected_id)
        reply_markup = player.get_suggest_card_inline_keyboard(game)
        query.edit_message_text(
            text=Messages.SUGGEST_CARD_TEXT,
            reply_markup=reply_markup
        )
    except Exception as e:
        print(e)
        query.answer('خطا:' + str(e))
        query.edit_message_text(
            text="deleted message",
            reply_markup=None
        )


def suggest_card_submit(update, context):
    query = update.callback_query
    try:
        game.validate_query(query.data)
        player = game.players[update.effective_user.id]
        player.suggest_card_submit(game)
        reply_markup = player.get_suggest_card_inline_keyboard(game)
        query.edit_message_text(
            text=Messages.SUGGEST_CARD_TEXT,
            reply_markup=reply_markup
        )
        query.answer('حله')
    except Exception as e:
        print(e)
        query.answer('خطا:' + str(e))
        query.edit_message_text(
            text="deleted message",
            reply_markup=None
        )


def vote_select_player(update, context):
    query = update.callback_query
    try:
        game.validate_query(query.data)
        player = game.players[update.effective_user.id]
        selected_id = int(query.data.split(' ')[1])
        if selected_id in player.selected_players_on_this_turn:
            player.selected_players_on_this_turn.remove(selected_id)
        else:
            player.selected_players_on_this_turn.append(selected_id)
        reply_markup = player.get_vote_inline_keyboard(game)
        query.edit_message_text(
            text=Messages.VOTE_TEXT + ', وزن رای شما در این دست: ' + str(player.get_vote_weight(game)),
            reply_markup=reply_markup
        )
    except Exception as e:
        print(e)
        query.answer('خطا:' + str(e))
        query.edit_message_text(
            text="deleted message",
            reply_markup=None
        )


game_started = False


def start_game(update, context):
    global game_started
    game_started = True


updater.dispatcher.add_handler(CallbackQueryHandler(suggest_card_select_card,
                                                    pattern='^' + Messages.SUGGEST_CARD +
                                                            ';' + Messages.SELECT_CARD + ';.*$'))

updater.dispatcher.add_handler(CallbackQueryHandler(suggest_card_select_player,
                                                    pattern='^' + Messages.SUGGEST_CARD +
                                                            ';' + Messages.SELECT_PLAYER + ';.*$'))

updater.dispatcher.add_handler(CallbackQueryHandler(suggest_card_submit,
                                                    pattern='^' + Messages.SUGGEST_CARD +
                                                            ';' + Messages.SUBMIT + ';.*$'))

updater.dispatcher.add_handler(CallbackQueryHandler(vote_select_player,
                                                    pattern='^' + Messages.VOTE +
                                                            ';' + Messages.SELECT_PLAYER + ';.*$'))

updater.dispatcher.add_handler(CommandHandler('say', say))
updater.dispatcher.add_handler(CommandHandler('start', start))
updater.dispatcher.add_handler(CommandHandler('st99', start_game))


# updater.dispatcher.add_handler(CommandHandler('get_players_can_vote', get_players_can_vote))


def receive_group_messages(update: telegram.Update, context: telegram.ext.CallbackContext):
    # all_messages.append(update.message)
    print("Group Message:")
    print(update.message)


def run_game():
    while not game_started:
        time.sleep(10)
    all_players = copy.deepcopy(game.players)
    while len(game.players) > 1:
        send_to_group(" دست " + str(game.turn_number) + " شروع شد!")
        game.send_suggest_card_messages(bot)
        sleep_time = max(30, min(300, len(game.players) * 5))
        send_to_group("تعداد بازیکنان این دست: " + str(len(game.players)) + '\n' + 'شما ' + str(
            sleep_time) + ' ثانیه فرصت دارید تا کارت پیشنهاد بدهید')
        time.sleep(sleep_time)
        game.start_vote_time(bot)
        sleep_time = max(30, min(40, len(game.players) * 5))
        send_to_group("زمان رای دهی شروع شد " + '\n' + 'شما ' + str(
            sleep_time) + ' ثانیه فرصت دارید تا رای بدهید')
        time.sleep(sleep_time)
        game.end_turn(bot)
        game.start_new_turn(bot)
    for player in game.players.values():
        send_to_group("" + str(player.first_name) + "\n" + " برنده شدی!")
        send_to_group("🥳")
    for player in all_players.values():
        bot.restrict_chat_member(chat_id=game.group_id, user_id=player.real_id,
                                 permissions=telegram.ChatPermissions(can_send_messages=True))


th = threading.Thread(target=run_game)

th.start()

message_handler = MessageHandler(Filters.group, receive_group_messages)
updater.dispatcher.add_handler(message_handler)

updater.dispatcher.add_handler(MessageHandler((~Filters.group), receive_private_messages))

updater.start_polling()
updater.idle()
