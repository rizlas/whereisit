from telegram import InlineKeyboardButton, InlineKeyboardMarkup, InlineQueryResultLocation, InputLocationMessageContent
from telegram.ext import Updater, CommandHandler, InlineQueryHandler, CallbackQueryHandler, MessageHandler, Filters
from location import Location
#from uuid import uuid4
import requests
import re
import json
import logging
import math
import os

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

token = os.environ['TELEGRAM_TOKEN']
api_key = os.environ['Map_Service_Api_Key']
api_url_base = os.environ['Api_Url_Base']
map_emoji = '\U0001F5FA'
data_json = None

locations = []
location_count = 0

message_title = "<b>Showing results for "
message_title_tail = "</b>\n\n"

port = int(os.environ.get('PORT', '8443'))

# Try to put business logic in this section :|

def get_locations(param):
    api_url = '{0}{1}.json?key={2}'.format(api_url_base, param, api_key)
    logger.info('Api url: {0}'.format(api_url_base))
    response = requests.get(api_url)

    if response.status_code == 200:
        global data_json
        global location_count
        global locations

        data_json = json.loads(response.content.decode('utf-8'))
        location_count = int(data_json['summary']['numResults'])
        locations = []

        if location_count > 0:
            for i in data_json['results']:
                if i['address'].get('countrySubdivision') is not None:
                    locations.append(Location(Id = i['id'].replace('/', '_'), 
                                              address = i['address']['freeformAddress'],
                                              country = i['address']['country'],
                                              countrySubdivision = i['address']['countrySubdivision'],
                                              latitude = i['position']['lat'],
                                              longitude = i['position']['lon'],
                                              locType = i['type']))
                else:
                    locations.append(Location(Id = i['id'].replace('/', '_'), 
                                              address = i['address']['freeformAddress'],
                                              country = i['address']['country'],
                                              countrySubdivision = None,
                                              latitude = i['position']['lat'],
                                              longitude = i['position']['lon'],
                                              locType = i['type']))
            
            return response.status_code

        else:
            return 204  # HTTP No content
    else:
        logger.error('Error response code: {0}'.format(response.status_code))
        return response.status_code

# inline keyboard generator

def inline_keyboard(user_input, key_selected = 0):
    buttonNumber = math.ceil(int(location_count) / 3)
    reply_markup = None
    button_text = ""

    if buttonNumber > 1:
        keyboard = [[]]

        for i in range(buttonNumber):
            if i != key_selected:
                button_text = "{0}".format(i + 1)
            else:
                button_text = "• {0} •".format(i + 1)

            keyboard[0].append(InlineKeyboardButton(button_text, callback_data = "{0}:{1}".format((i + 1), user_input)))

        reply_markup = InlineKeyboardMarkup(keyboard)

    return reply_markup

#################################################################################################

def where(bot, update, args):
    chat_id = update.message.chat_id
    user_input = ""

    if isinstance(args, list) == True:
        user_input = " ".join(args)
    else:
        user_input = args

    logger.info('User input: {0}'.format(user_input))

    ret = get_locations(user_input)

    if ret == 200:
        reply_markup = inline_keyboard(user_input)

        # Message with only first three results
        message = "{0}'{1}'{2}".format(message_title, user_input, message_title_tail)
        c = 0

        for location in locations:
            c += 1
            message += "{0} {1}\n\n".format(map_emoji, location.toString())
            if c == 3:
                break

        bot.send_message(chat_id = chat_id, 
                         text = message, 
                         parse_mode = 'HTML',
                         reply_markup = reply_markup)

    elif ret == 204:
        bot.send_message(chat_id = chat_id, 
                         text = "No locations was found for '{0}'".format(user_input))
    else:
        bot.send_message(chat_id = chat_id, 
                         text = 'An error has occured')

    #bot.send_location(chat_id=chat_id, latitude=37.3399964, longitude=-4.5811614)

# inline keyboard callback

def button(bot, update):
    query = update.callback_query   # Contains data on the message including user information
    key_selected, user_input = query.data.split(":")

    #logger.info(key_selected)
    message = "{0}'{1}'{2}".format(message_title, user_input, message_title_tail)

    #log_msg = "\n\n"
    #for i in range(len(locations)):
    #    log_msg += "Index: {0}\nData: {1}\n\n".format(i, locations[i].toString())
    #logger.info(log_msg)

    for i in range(len(locations)):
        if math.ceil((i + 1) / 3) == int(key_selected):
            message += "{0} {1}\n\n".format(map_emoji, locations[i].toString())
        elif math.ceil((i + 1) / 3) > int(key_selected):
            break

    # keyboard = [[InlineKeyboardButton("<<", callback_data='key <<'),
    #          InlineKeyboardButton("1", callback_data='key 1'),
    #          InlineKeyboardButton("2", callback_data='key 2'),
    #          InlineKeyboardButton("3", callback_data='key 3'),
    #          InlineKeyboardButton(">>", callback_data='key >>'),]]

    reply_markup = inline_keyboard(user_input, int(key_selected) - 1)
    query.edit_message_text(text = message,
                            parse_mode = 'HTML',
                            reply_markup = reply_markup)

    # NOTE: After the user presses a callback button, Telegram clients will display a progress bar until you call answerCallbackQuery. It is, therefore, necessary to react by calling answerCallbackQuery even if no notification to the user is needed (e.g., without specifying any of the optional parameters).
    bot.answer_callback_query(callback_query_id = update.callback_query.id)

# inline query via @botname query

def inlinequery(bot, update):
    """Handle the inline query."""
    query = update.inline_query.query.strip()
    logger.info(query)

    if query:
        ret = get_locations(query)

        if ret == 200:
            results = []
            for location in locations:
                results.append(InlineQueryResultLocation(type = 'location', 
                                                         id = location.id, 
                                                         latitude = location.latitude, 
                                                         longitude = location.longitude,
                                                         live_period = 60,
                                                         input_message_content = InputLocationMessageContent(latitude = location.latitude, longitude = location.longitude),
                                                         title = "{0}, {1}".format(location.address, location.country)))
            
            #results = [InlineQueryResultLocation(type='location',id=uuid4(),latitude=42.74459,longitude=42.74459,title='Oih boh')]

            bot.answerInlineQuery(update.inline_query.id, results)

# Show location selected on bot answer

def startswithslash(bot, update):
    user_message = update.message.text[1:]
    chat_id = update.message.chat_id
    founded = False

    for location in locations:
        if location.id == user_message:
            founded = True
            bot.send_location(chat_id = chat_id, latitude = location.latitude, longitude = location.longitude)
            break

    if founded == False:
        bot.send_message(chat_id = chat_id, 
                         text = "I can show you where a location is in the world. Simply send me a query like 'Rome' or use /where 'location' command")

# handle messages that doesn't starts with / aka messages :D

def noncommand(bot, update):
    user_message = update.message.text
    chat_id = update.message.chat_id

    where(bot, update, user_message)

# show help message

def help(bot, update):
    chat_id = update.message.chat_id

    bot.send_message(chat_id = chat_id, 
                     text = ("<b>Commands for WhereIsItBot</b>\n\n"
                             "<b>/start</b> - Give life to this amazing bot\n"
                             "<b>/where</b> - With the name of a city or street will show where is it in the world (e.g. /where Rome)\n"
                             "<b>/info</b> - Shows information about how this bot works\n"
                             "<b>/help</b> - Shows this list"),
                     parse_mode = 'HTML')

# show infos about bot

def info(bot, update):
    chat_id = update.message.chat_id

    bot.send_message(chat_id = chat_id, 
                     text = ("Hi fellows,\nI was developed in Italy with the aim of make Italy great again, oh no just joking.\n"
                             "\n<i>How can you do such great things?</i>\n"
                             "My life is tied to TomTom's Api and I'm speaking to you thanks to python language. \U0001F40D\n"
                             "\n<i>What did you just say? Do you speak Parseltongue? Bwahhh anyway you work great!</i>\n"
                             "I don't know if the guy who made me did a good job but you can check it here: https://github.com/rizlas/whereisit"),
                     parse_mode = 'HTML')

# Log Errors caused by Updates

def error(update, context):
    logger.warning('Update {0} caused error {1}'.format(update, context.error))


def main():
    updater = Updater(token)

    # Dispatcher for handlers
    dp = updater.dispatcher

    # Telegram commands
    dp.add_handler(CommandHandler('where', where, pass_args = True))
    dp.add_handler(CallbackQueryHandler(button))

    dp.add_handler(CommandHandler('info', info))
    dp.add_handler(CommandHandler('help', help))

    # Inline query handler (via @botname query)
    dp.add_handler(InlineQueryHandler(inlinequery))

    # on command not defined
    dp.add_handler(MessageHandler(Filters.command, startswithslash))

    # on noncommand i.e message
    dp.add_handler(MessageHandler(Filters.text, noncommand))

    # log all errors
    dp.add_error_handler(error)

    updater.start_webhook(listen = "0.0.0.0",
                          port = port,
                          url_path = token)
    updater.bot.set_webhook("https://whereisitbot.herokuapp.com/" + token)

    # Block until the user presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()

if __name__ == '__main__':
    main()

# todo

# new format for american addresses
# check uk addresses
# check russian addresses
# tests with most common city name

# send location with coordinates as params