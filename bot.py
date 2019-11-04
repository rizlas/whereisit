from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InlineQueryResultLocation,
    InputVenueMessageContent,
)
from telegram.ext import (
    Updater,
    CommandHandler,
    InlineQueryHandler,
    CallbackQueryHandler,
    MessageHandler,
    Filters,
)
from location import Location
from emoji import emojize

# from uuid import uuid4
import requests
import re
import json
import logging
import math
import os

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

logger = logging.getLogger(__name__)

# TODO move to config file
# TODO remove global variables
token = os.environ["TELEGRAM_TOKEN"]
api_key = os.environ["Map_Service_Api_Key"]
api_url_base_geocode = os.environ["Api_Url_Base_Geocode"]
api_url_base_reverse_geocode = os.environ["Api_Url_Base_Reverse_Geocode"]
map_emoji = "\U0001F5FA"
data_json = None

locations = []
location_count = 0

message_title = "<b>Showing results for "
message_title_tail = "</b>\n\n"

port = int(os.environ.get("PORT", "8443"))

# Try to put business logic in this section :|
def get_locations(param):
    # TODO add docstring
    api_url = f"{api_url_base_geocode}{param}.json?key={api_key}"
    logger.info("Api url: " + api_url_base_geocode)
    response = requests.get(api_url)

    if response.status_code == 200:
        global data_json
        global location_count
        global locations

        data_json = json.loads(response.content.decode("utf-8"))
        location_count = int(data_json["summary"]["numResults"])
        locations = []

        if location_count > 0:
            for i in data_json["results"]:
                loc_tmp = Location(
                    location_id=i["id"].replace("/", "_"),
                    address=i["address"]["freeformAddress"],
                    country=i["address"]["country"],
                    country_subdivision=None,
                    country_secondary_subdivision=None,
                    country_subdivision_name=None,
                    latitude=i["position"]["lat"],
                    longitude=i["position"]["lon"],
                    locType=i["type"],
                )

                if i["address"].get("country_subdivision") is not None:
                    loc_tmp.country_subdivision = i["address"]["country_subdivision"]

                if i["address"].get("country_secondary_subdivision") is not None:
                    loc_tmp.country_secondary_subdivision = i["address"][
                        "country_secondary_subdivision"
                    ]

                if i["address"].get("country_subdivision_name") is not None:
                    loc_tmp.country_subdivision_name = i["address"][
                        "country_subdivision_name"
                    ]

                locations.append(loc_tmp)

            return response.status_code

        else:
            return 204  # HTTP No content
    else:
        logger.error("Error response code: " + response.status_code)
        return response.status_code


# Inline keyboard generator
def inline_keyboard(user_input, key_selected=0):
    # TODO add docstring
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

            keyboard[0].append(
                InlineKeyboardButton(button_text, callback_data=f"{i+1}:{user_input}")
            )

        reply_markup = InlineKeyboardMarkup(keyboard)

    return reply_markup


def coordinate_search(lat, lon):
    # TODO add docstring
    api_url = f"{api_url_base_reverse_geocode}{lat}, {lon}.json?key={api_key}"

    logger.info("Api requests url: " + api_url)

    response = requests.get(api_url)
    status_code = response.status_code

    if status_code == 200:
        json_data = json.loads(response.content.decode("utf-8"))

        if json_data["addresses"][0]["address"].get("country") is not None:
            title = json_data["addresses"][0]["address"]["country"]
            if (
                json_data["addresses"][0]["address"].get("countrySubdivision")
                is not None
            ):
                title += (
                    ", " + json_data["addresses"][0]["address"]["countrySubdivision"]
                )
        else:
            title = "{0}, {1}".format(lat, lon)

        if json_data["addresses"][0]["address"].get("freeformAddress") is not None:
            address = json_data["addresses"][0]["address"]["freeformAddress"]
        else:
            address = "{0}, {1}".format(lat, lon)

        return status_code, title, address
    elif status_code == 400:
        return status_code, "One or more parameters were incorrectly specified.", ""
    else:
        return status_code, "An error has occured", ""


def is_coordinate_search(param):
    # TODO add docstring
    lat, lon = param.split(",")
    logger.info("is_coordinate_search: " + param)

    lat = lat.strip()
    lon = lon.strip()

    try:
        float(lat)
        float(lon)
        return True
    except ValueError:
        return False


def where(bot, update, args):
    # TODO add docstring
    chat_id = update.message.chat_id
    user_input = ""

    user_input = " ".join(args) if isinstance(args, list) else args
    logger.info("User input: " + user_input)

    ret = get_locations(user_input)

    if ret == 200:
        reply_markup = inline_keyboard(user_input)

        # Message with only first three results
        message = f"{message_title}'{user_input}'{message_title_tail}"

        for location in locations[:3]:
            message += f"{map_emoji} {location}\n\n"

        bot.send_message(
            chat_id=chat_id, text=message, parse_mode="HTML", reply_markup=reply_markup
        )

    elif ret == 204:
        bot.send_message(
            chat_id=chat_id, text="No locations was found for '{user_input}'"
        )
    else:
        bot.send_message(chat_id=chat_id, text="An error has occured")


# Location with coordinates
def f_location(bot, update, args):
    # TODO add docstring

    chat_id = update.message.chat_id
    user_input = " ".join(args)
    lat, lon = user_input.split(",")

    logger.info("User input: " + user_input)

    status_code, title, address = coordinate_search(lat, lon)

    if status_code == 200:
        bot.send_venue(
            chat_id=chat_id,
            latitude=float(lat),
            longitude=float(lon),
            title=title,
            address=address,
        )
    elif status_code == 400:
        bot.send_message(
            chat_id=chat_id, text="One or more parameters were incorrectly specified."
        )
    else:
        bot.send_message(chat_id=chat_id, text="An error has occured")


# Inline keyboard callback
def button(bot, update):
    # TODO add docstring
    query = (
        update.callback_query
    )  # Contains data on the message including user information
    key_selected, user_input = query.data.split(":")

    message = f"{message_title}'{user_input}'{message_title_tail}"

    for i in range(len(locations)):
        # TODO can change with range(math.ceil(i + 1) / 3) ?
        a = math.ceil((i + 1) / 3)
        if a == int(key_selected):
            message += f"{map_emoji} {locations[i]}\n\n"
        elif a > int(key_selected):
            break

    reply_markup = inline_keyboard(user_input, int(key_selected) - 1)
    query.edit_message_text(text=message, parse_mode="HTML", reply_markup=reply_markup)

    # NOTE: After the user presses a callback button,
    # Telegram clients will display a progress bar until
    # you call answerCallbackQuery.
    # It is, therefore, necessary to react by calling
    # answerCallbackQuery even if no notification to the user is needed
    # (e.g., without specifying any of the optional parameters).
    bot.answer_callback_query(callback_query_id=update.callback_query.id)


# Inline query via @botname query
def inlinequery(bot, update):
    """Handle the inline query."""
    query = update.inline_query.query.strip()
    logger.info(query)

    if "," in query:
        if is_coordinate_search(query):
            logger.info("is_coordinate_search True")
            lat, lon = query.split(",")
            status_code, title, address = coordinate_search(lat, lon)

            logger.info(f"{lat} {lon}\n{status_code}\n{title}\n{address}")

            if status_code == 200:
                results = []
                results.append(
                    InlineQueryResultLocation(
                        type="location",
                        id="single_location",
                        latitude=float(lat),
                        longitude=float(lon),
                        live_period=60,
                        input_message_content=InputVenueMessageContent(
                            latitude=float(lat),
                            longitude=float(lon),
                            title="You've searched: " + query.capitalize(),
                            address=address,
                        ),
                        title=title,
                    )
                )

                bot.answerInlineQuery(update.inline_query.id, results)
                return
            elif status_code == 400:
                results = []
                results.append(
                    # FIXME this classes are not even imported, why are they here?
                    InlineQueryResultArticle(
                        id="single_location",
                        title=title,
                        input_message_content=InputTextMessageContent(title),
                    )
                )

                bot.answerInlineQuery(update.inline_query.id, results)
            else:
                results = []
                results.append(
                    InlineQueryResultArticle(
                        id="single_location",
                        title=title,
                        input_message_content=InputTextMessageContent(title),
                    )
                )

                bot.answerInlineQuery(update.inline_query.id, results)
    elif query:
        ret = get_locations(query)

        if ret == 200:
            results = []
            address_venue_str = ""
            title_str = ""
            for location in locations:
                address_venue_str = location.subDivision()
                title_str = f"{location.address}, {location.country}"

                if address_venue_str == "":
                    address_venue_str = location.address
                else:
                    title_str += f" ({address_venue_str})"

                results.append(
                    InlineQueryResultLocation(
                        type="location",
                        id=location.id,
                        latitude=location.latitude,
                        longitude=location.longitude,
                        live_period=60,
                        input_message_content=InputVenueMessageContent(
                            latitude=location.latitude,
                            longitude=location.longitude,
                            title="You've searched: " + query.capitalize(),
                            address=address_venue_str,
                        ),
                        title=title_str,
                    )
                )

            bot.answerInlineQuery(update.inline_query.id, results)


# Show location selected on bot answer
def startswithslash(bot, update):
    user_message = update.message.text[1:]
    chat_id = update.message.chat_id

    for location in locations:
        if location.id == user_message:
            bot.send_location(
                chat_id=chat_id,
                latitude=location.latitude,
                longitude=location.longitude,
            )
            break
    else:
        bot.send_message(
            chat_id=chat_id,
            text=(
                "I can show you where a location is in the world. "
                "Simply send me a query like 'Rome' or "
                "use /where 'location' command",
            ),
        )


def non_command(bot, update):
    """Handle messages that doesn't starts with / aka messages :D
    """
    user_message = update.message.text
    where(bot, update, user_message)


# Show help message
def help(bot, update):
    chat_id = update.message.chat_id
    help_text = os.environ["Help_Text"]

    bot.send_message(chat_id=chat_id, text=help_text, parse_mode="HTML")


# Show infos about bot
def info(bot, update):
    chat_id = update.message.chat_id
    info_text = os.environ["Info_Text"]

    bot.send_message(
        chat_id=chat_id, text=emojize(info_text, use_aliases=True), parse_mode="HTML"
    )


# Show infos about how to use inline mode
def inline(bot, update):
    chat_id = update.message.chat_id
    inline_info_text = os.environ["Inline_Info_Text"]

    bot.send_message(chat_id=chat_id, text=inline_info_text, parse_mode="HTML")


# Log Errors caused by Updates
def error(update, context):
    logger.warning(f"Update {update} caused error {context.error}")


def main():
    updater = Updater(token)

    # Dispatcher for handlers
    dp = updater.dispatcher

    # Telegram commands
    dp.add_handler(CommandHandler("where", where, pass_args=True))
    dp.add_handler(CallbackQueryHandler(button))

    dp.add_handler(CommandHandler("location", f_location, pass_args=True))

    dp.add_handler(CommandHandler("inline", inline))
    dp.add_handler(CommandHandler("info", info))
    dp.add_handler(CommandHandler("help", help))

    # Inline query handler (via @botname query)
    dp.add_handler(InlineQueryHandler(inlinequery))

    # on command not defined
    dp.add_handler(MessageHandler(Filters.command, startswithslash))

    # on non_command i.e message
    dp.add_handler(MessageHandler(Filters.text, non_command))

    # log all errors
    dp.add_error_handler(error)

    updater.start_webhook(listen="0.0.0.0", port=port, url_path=token)
    updater.bot.set_webhook("https://whereisitbot.herokuapp.com/" + token)

    # Block until the user presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == "__main__":
    main()
