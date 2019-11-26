from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InlineQueryResultLocation,
    InputVenueMessageContent,
    InlineQueryResultArticle,
    InlineQueryResultPhoto,
    InputTextMessageContent,
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
from uuid import uuid4
from config import *

import logic
import requests
import re
import json
import logging
import math

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

logger = logging.getLogger(__name__)

if mode == "develop":

    def run(updater):
        updater.start_polling()


elif mode == "production":

    def run(updater):
        updater.start_webhook(listen="0.0.0.0", port=port, url_path=token)
        updater.bot.set_webhook("https://whereisitbot.herokuapp.com/" + token)


else:
    logger.error("You need to specify a working mode")

message_title = "<b>Showing results for "
message_title_tail = "</b>\n\n"


# Inline keyboard generator
def inline_keyboard(user_input, location_count, key_selected=0):
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


def where(update, context):
    # TODO add docstring
    chat_id = update.message.chat_id

    user_input = (
        " ".join(context.args) if isinstance(context.args, list) else context.args
    )

    logger.info("User input: " + user_input)

    status_code, locations, location_count = logic.get_locations(
        user_input, api_url_base_geocode, api_key
    )

    if status_code == 200:
        reply_markup = inline_keyboard(user_input, location_count)

        # Message with only first three results
        message = f"{message_title}'{user_input}'{message_title_tail}"

        for location in locations[:3]:
            message += f"{map_emoji} {location}\n\n"

        context.bot.send_message(
            chat_id=chat_id, text=message, parse_mode="HTML", reply_markup=reply_markup
        )

    elif status_code == 204:
        context.bot.send_message(
            chat_id=chat_id, text="No locations was found for '{user_input}'"
        )
    else:
        context.bot.send_message(chat_id=chat_id, text="An error has occured")


# Location with coordinates
def f_location(update, context):
    # TODO add docstring

    chat_id = update.message.chat_id
    user_input = " ".join(context.args)
    lat, lon = user_input.split(",")

    if logic.lat_lon_parse(lat, lon):
        logger.info("User input: " + user_input)

        status_code, title, address = logic.coordinate_search(
            lat, lon, api_url_base_reverse_geocode, api_key
        )

        if status_code == 200:
            context.bot.send_venue(
                chat_id=chat_id,
                latitude=float(lat),
                longitude=float(lon),
                title=title,
                address=address,
            )
        elif status_code == 400:
            context.bot.send_message(chat_id=chat_id, text=title)
        else:
            context.bot.send_message(chat_id=chat_id, text=title)
    else:
        context.bot.send_message(chat_id=chat_id, text="Unformed input!")


# Inline keyboard callback
def button(update, context):
    # TODO add docstring
    logger.info(update.callback_query.data)

    query = (
        update.callback_query
    )  # Contains data on the message including user information

    key_selected, user_input = query.data.split(":")
    status_code, locations, location_count = logic.get_locations(
        user_input, api_url_base_geocode, api_key
    )

    if status_code == 200:
        message = f"{message_title}'{user_input}'{message_title_tail}"

        for i in range(len(locations)):
            x = math.ceil((i + 1) / 3)
            if x == int(key_selected):
                message += f"{map_emoji} {locations[i]}\n\n"
            elif x > int(key_selected):
                break

        reply_markup = inline_keyboard(
            user_input, location_count, int(key_selected) - 1
        )
        query.edit_message_text(
            text=message, parse_mode="HTML", reply_markup=reply_markup
        )
    else:
        query.edit_message_text(text="An error has occured", parse_mode="HTML")

    # NOTE: After the user presses a callback button,
    # Telegram clients will display a progress bar until
    # you call answerCallbackQuery.
    # It is, therefore, necessary to react by calling
    # answerCallbackQuery even if no notification to the user is needed
    # (e.g., without specifying any of the optional parameters).
    context.bot.answer_callback_query(callback_query_id=query.id)


# Inline query via @botname query
def inlinequery(update, context):
    """Handle the inline query."""
    query = update.inline_query.query.strip()
    logger.info(query)

    if "," in query:
        if logic.is_coordinate_search(query):
            logger.info("is_coordinate_search True")
            lat, lon = query.split(",")
            status_code, title, address = logic.coordinate_search(
                lat, lon, api_url_base_reverse_geocode, api_key
            )

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

                context.bot.answerInlineQuery(update.inline_query.id, results)
                return
            elif status_code == 400:
                results = []
                results.append(
                    InlineQueryResultArticle(
                        id="single_location",
                        title=title,
                        input_message_content=InputTextMessageContent(title),
                    )
                )

                context.bot.answerInlineQuery(update.inline_query.id, results)
            else:
                results = []
                results.append(
                    InlineQueryResultArticle(
                        id="single_location",
                        title=title,
                        input_message_content=InputTextMessageContent(title),
                    )
                )

                context.bot.answerInlineQuery(update.inline_query.id, results)
    elif query:
        status_code, locations, _ = logic.get_locations(
            query, api_url_base_geocode, api_key
        )

        if status_code == 200:
            inline_result = []
            address_venue_str = ""
            title_str = ""
            for location in locations:
                address_venue_str = location.sub_division()
                title_str = f"{location.address}, {location.country}"

                if address_venue_str == "":
                    address_venue_str = location.address
                else:
                    title_str += f" ({address_venue_str})"

                inline_result.append(
                    InlineQueryResultLocation(
                        type="location",
                        id=location.location_id,
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

            context.bot.answerInlineQuery(update.inline_query.id, inline_result)
        elif status_code == 204:
            inline_result = []
            inline_result.append(
                InlineQueryResultArticle(
                    type="article",
                    id=str(uuid4()),
                    title="What are you searching?",
                    input_message_content=InputTextMessageContent(
                        "You need to add more infos in your inline query."
                    ),
                    thumb_url=image_url,
                )
            )

            context.bot.answerInlineQuery(update.inline_query.id, inline_result)


# Show location selected on bot answer
def startswithslash(update, context):
    user_message = update.message.text[1:]
    chat_id = update.message.chat_id

    try:
        lat, lon = logic.decode_lat_lon(user_message).split(",")

        assert logic.lat_lon_parse(lat, lon)

        context.bot.send_location(chat_id=chat_id, latitude=lat, longitude=lon)
    except Exception:
        context.bot.send_message(
            chat_id=chat_id,
            text=(
                "I can show you where a location is in the world. "
                "Simply send me a query like 'Rome' or "
                "use /where 'location' command"
            ),
        )


def non_command(update, context):
    """Handle messages that doesn't starts with / aka messages :D"""
    where(update, context)


# Show help message
def help(update, context):
    chat_id = update.message.chat_id
    help_text = os.environ["Help_Text"]

    context.bot.send_message(chat_id=chat_id, text=help_text, parse_mode="HTML")


# Show infos about bot
def info(update, context):
    chat_id = update.message.chat_id
    info_text = os.environ["Info_Text"]

    context.bot.send_message(
        chat_id=chat_id, text=emojize(info_text, use_aliases=True), parse_mode="HTML"
    )


# Show infos about how to use inline mode
def inline(update, context):
    chat_id = update.message.chat_id
    inline_info_text = os.environ["Inline_Info_Text"]

    context.bot.send_message(chat_id=chat_id, text=inline_info_text, parse_mode="HTML")


# Log Errors caused by Updates
def error(update, context):
    logger.warning(f"Update {update} caused error {context.error}")


def main():
    updater = Updater(token)

    # Dispatcher for handlers
    dp = updater.dispatcher

    # Telegram commands
    dp.add_handler(CommandHandler("where", where))
    dp.add_handler(CallbackQueryHandler(button))

    dp.add_handler(CommandHandler("location", f_location))

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

    run(updater)

    # Block until the user presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == "__main__":
    main()
