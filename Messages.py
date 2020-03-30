SUGGEST_CARD = 'suggest_card'
VOTE = 'vote'
SELECT_CARD = 'select_card'
SELECT_PLAYER = 'select_player'
SUBMIT = 'submit'

EXPIRED_MESSAGE = 'این پیام متعلق به این دست بازی نیست!'
SEND_START_ON_GROUP_ERROR = 'تو پی وی باید استارتو بفرستی:|'
SEND_START_WHEN_IS_NOT_JOINED_ON_GROUP_ERROR = 'خب تو گروه نیستی هنوز تو چی عضوت کنم؟'
USER_ALREADY_JOINED_ERROR = 'عضوت کردم دیگه. اینقد رو استارت کلیک نکن'
USER_JOINED_SUCCESSFULLY = 'شما با موفقیت به بازی اضافه شدی'
NOT_VOTE_TIME = 'الان وقت رای دادن با این پیام نیست!'
NOT_SUGGEST_CARD_TIME = 'الان وقت رای دادن با این پیام نیست!'
SELECT_TEXT = " ✔️"
SUGGEST_CARD_TEXT = 'کارت پیشنهاد بدهید'
VOTE_TEXT = 'رای بدهید'
SUGGEST_CARD_RESULT_FIRST_LINE = 'در این دست بازیکنان زیر به شما این کارت ها را پیشنهاد داده اند:\n\n'
SUGGEST_CARD_RESULT_FIRST_LINE_EMPTY = 'در این دست بازیکنان به شما کارتی پیشنهاد ندادند☹️\n\n'
YOU_LOSE = 'شما باختی, خدافظ'
NO_SOLD_CARDS = 'شما کارت فروخته شده فعالی ندارید'
SOLD_CARD_FIRST_LINE = 'کارت های فعال فروخته شده شما:\n\n'
NO_VOTE_OPTIONS = 'شما در این دست انتخابی برای رای ندارید!'


def send_message(bot, chat_id, message):
    bot.send_message(chat_id=chat_id, text=message)
