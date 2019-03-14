from telegram import InlineKeyboardButton, InlineKeyboardMarkup, InlineQueryResultLocation
from telegram.ext import Updater, CommandHandler, InlineQueryHandler, CallbackQueryHandler
from location import Location
from uuid import uuid4
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

# Try to put business logic in this section

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
                    locations.append(Location(Id = i['id'], 
                                              address = i['address']['freeformAddress'],
                                              country = i['address']['country'],
                                              countrySubdivision = i['address']['countrySubdivision'],
                                              latitude = i['position']['lat'],
                                              longitude = i['position']['lon'],
                                              locType = i['type']))
                else:
                    locations.append(Location(Id = i['id'], 
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

#################################################################################################

def where(bot, update, args):
    #try:
    chat_id = update.message.chat_id
    user_input = " ".join(args)
    logger.info('User input: {0}'.format(user_input))

    ret = get_locations(user_input)

    if ret == 200:
        buttonNumber = math.ceil(int(location_count) / 3)

        # inlinekeyboard

        keyboard = [[]]

        for i in range(buttonNumber):
            keyboard[0].append(InlineKeyboardButton("{0}".format(i + 1), callback_data="{0}".format(i)))

        reply_markup = InlineKeyboardMarkup(keyboard)

        ################

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
                         text = 'No locations was found for {0}'.format(user_input))
    else:
        bot.send_message(chat_id = chat_id, 
                         text = 'An error has occured')

        #bot.send_location(chat_id=chat_id, latitude=37.3399964, longitude=-4.5811614)
    # except Exception as e:
    #     logger.error("Error in level argument",e.args[0])
    #     raise

# inline keyboard callback

def button(bot, update):
    query = update.callback_query
    # keyboard = [[InlineKeyboardButton("<<", callback_data='tasto <<'),
    #          InlineKeyboardButton("1", callback_data='tasto 1'),
    #          InlineKeyboardButton("2", callback_data='tasto 2'),
    #          InlineKeyboardButton("3", callback_data='tasto 3'),
    #          InlineKeyboardButton(">>", callback_data='tasto >>'),]]

    # reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text="Selected option: {}".format(query.data))#, reply_markup=reply_markup)

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
                                                         title = "{0}, {1}".format(location.address, location.country)))
            
            #results = [InlineQueryResultLocation(type='location',id=uuid4(),latitude=42.74459,longitude=42.74459,title='Oih boh')]

            bot.answerInlineQuery(update.inline_query.id, results)

# test command logging purpose

def testcommand(bot, update):
    logger.info(json.dumps(data_json, indent=4, sort_keys=True))
    logger.info("Location count {0}".format(location_count))

    # string = ""
    # for i in data_json['results']:
    #     if i['address'].get('countrySubdivision') is not None:
    #         string += "{6} <b>Address: {0}\n</b>Country: {1} - {2}\nLat: {3} Lon: {4}\nType: {5}\n\n".format(i['address']['freeformAddress'], i['address']['country'], i['address']['countrySubdivision'], i['position']['lat'], i['position']['lon'], i['type'], map_emoji)
    #     else:
    #         string += "{5} <b>Address: {0}\n</b>Country: {1}\nLat: {2} Lon: {3}\nType: {4}\n\n".format(i['address']['freeformAddress'], i['address']['country'], i['position']['lat'], i['position']['lon'], i['type'], map_emoji)

    #     logger.info(string)


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update {0} caused error {1}'.format(update, context.error))


def main():
    updater = Updater(token)

    # Dispatcher for handlers
    dp = updater.dispatcher

    # Telegram commands
    dp.add_handler(CommandHandler('where',where, pass_args=True))
    dp.add_handler(CommandHandler('testcommand',testcommand))
    dp.add_handler(CallbackQueryHandler(button))

    # Inline query handler (via @botname query)
    dp.add_handler(InlineQueryHandler(inlinequery))

    # log all errors
    dp.add_error_handler(error)

    updater.start_webhook(listen="0.0.0.0",
                          port=port,
                          url_path=token)
    updater.bot.set_webhook("https://whereisitbot.herokuapp.com/" + token)

    # Block until the user presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()

if __name__ == '__main__':
    main()

# todo
# no keyboard if only one page
# new format for american addresses
# check uk addresses
# check russian addresses