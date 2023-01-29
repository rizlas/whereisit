"""
main.py
"""
import logging
import math
import sys
import traceback
from uuid import uuid4
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InlineQueryResultLocation,
    InputVenueMessageContent,
    InlineQueryResultArticle,
    InputTextMessageContent,
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    InlineQueryHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes,
)
from emoji import emojize
import helpers
import config as cfg
from constants import (
    IMAGE_URL,
    MAP_EMOJI,
    MESSAGE_TITLE,
    MESSAGE_TITLE_TAIL,
    INFO_TEXT,
    INLINE_INFO_TEXT,
    HELP_TEXT,
    ERROR_TEXT,
)


# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

logger = logging.getLogger(__name__)


# Inline keyboard generator
def inline_keyboard(
    user_input: str, location_count: int, key_selected: int = 0
) -> InlineKeyboardMarkup:
    """
    Generated an inline keyboard based on location_count.

    e.g. location_count = 10, 10 / 3 = 3.333 -> math.ceil(3.333) = 4
    4 button will be generated

    Highlight the button selected with a different text.

    Incapsulate user_input in callback_data (without the keyboard will not work)

    Args:
        user_input (str): Venue asked by the user
        location_count (int): How many venue founded by the api
        key_selected (int, optional): Key selected by the user. Defaults to 0.

    Returns:
        InlineKeyboardMarkup: Generated keyboard
    """
    buttons_count = math.ceil(location_count / 3)
    reply_markup = None
    button_text = ""

    if buttons_count > 1:
        keyboard = [[]]

        for i in range(buttons_count):
            if i != key_selected:
                button_text = f"{i + 1}"
            else:
                button_text = f"• {i + 1} •"

            keyboard[0].append(
                InlineKeyboardButton(button_text, callback_data=f"{i+1}:{user_input}")
            )

        reply_markup = InlineKeyboardMarkup(keyboard)

    return reply_markup


async def where(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle the command /where. User must specify a query parameter
    (e.g. /where Roma)

    Param will be searched via TomTom Api and the results
    will be available via an inline keyboard.

    Args:
        update (Update): Incoming update
        context (ContextTypes.DEFAULT_TYPE): Context object
    """
    chat_id = update.message.chat_id

    user_input = (
        " ".join(context.args) if isinstance(context.args, list) else context.args
    )

    logger.info("User input %s", user_input)

    # If input is none, where function was triggered from a non-command
    if user_input is None:
        user_input = update.message.text

    if not user_input:
        await context.bot.send_message(
            chat_id=chat_id, text="You must specify an input!"
        )
        return

    status_code, locations, location_count = helpers.get_locations(
        user_input, cfg.API_URL_BASE_GEOCODE, cfg.API_KEY
    )

    if status_code == 200:
        reply_markup = inline_keyboard(user_input, location_count)

        # Message with only first three results
        message = f"{MESSAGE_TITLE}'{user_input}'{MESSAGE_TITLE_TAIL}"

        for location in locations[:3]:
            message += f"{MAP_EMOJI} {location}\n\n"

        await context.bot.send_message(
            chat_id=chat_id, text=message, parse_mode="HTML", reply_markup=reply_markup
        )

    elif status_code == 204:
        await context.bot.send_message(
            chat_id=chat_id, text=f"No locations was found for '{user_input}'"
        )
    else:
        await context.bot.send_message(chat_id=chat_id, text="An error has occured")


async def f_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle the command /location. User must input latitude and longitude
    as decimal and separated by comma.

    /location -27.122295, -109.288839

    Bot will return a Venue object.

    Args:
        update (Update): Incoming update
        context (ContextTypes.DEFAULT_TYPE): Context object
    """

    chat_id = update.message.chat_id
    user_input = " ".join(context.args)

    try:
        lat, lon = user_input.split(",")
    except ValueError:
        await context.bot.send_message(
            chat_id=chat_id,
            text="Invalid format use something like: /location -27.122295, -109.288839)",
        )
        return

    logger.debug("lat %s, lon %s", lat, lon)

    if helpers.lat_lon_parse(lat, lon):
        logger.info("User input %s", user_input)

        status_code, title, address = helpers.coordinate_search(
            lat, lon, cfg.API_URL_BASE_REVERSE_GEOCODE, cfg.API_KEY
        )

        if status_code == 200:
            await context.bot.send_venue(
                chat_id=chat_id,
                latitude=float(lat),
                longitude=float(lon),
                title=title,
                address=address,
            )
        elif status_code == 400:
            await context.bot.send_message(chat_id=chat_id, text=title)
        else:
            await context.bot.send_message(chat_id=chat_id, text=title)
    else:
        await context.bot.send_message(chat_id=chat_id, text="Unformed input!")


# Inline keyboard callback
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle clicks on inline keyboard. At each click get_locations is called.
    Results from get_locations are in set of three elements.
    "Set" number that correspond to the page select is shown.

    Args:
        update (Update): Incoming update
        context (ContextTypes.DEFAULT_TYPE): Context object
    """
    logger.info(update.callback_query.data)

    query = (
        update.callback_query
    )  # Contains data on the message including user information

    page_selected, user_input = query.data.split(":")

    status_code, locations, location_count = helpers.get_locations(
        user_input, cfg.API_URL_BASE_GEOCODE, cfg.API_KEY
    )

    if status_code == 200:
        message = f"{MESSAGE_TITLE}'{user_input}'{MESSAGE_TITLE_TAIL}"

        for i, location in enumerate(locations):
            current_set = math.ceil((i + 1) / 3)
            if current_set == int(page_selected):
                message += f"{MAP_EMOJI} {location}\n\n"
            elif current_set > int(page_selected):
                break

        reply_markup = inline_keyboard(
            user_input, location_count, int(page_selected) - 1
        )
        await query.edit_message_text(
            text=message, parse_mode="HTML", reply_markup=reply_markup
        )
    else:
        await query.edit_message_text(text="An error has occured", parse_mode="HTML")

    # NOTE: After the user presses a callback button,
    # Telegram clients will display a progress bar until
    # you call answerCallbackQuery.
    # It is, therefore, necessary to react by calling
    # answerCallbackQuery even if no notification to the user is needed
    # (e.g., without specifying any of the optional parameters).
    await context.bot.answer_callback_query(callback_query_id=query.id)


# Inline query via @botname query
async def inlinequery(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle inline queries. Inline support both lat lon and venue search.

    Args:
        update (Update): Incoming update
        context (ContextTypes.DEFAULT_TYPE): Context object
    """
    query = update.inline_query.query.strip()
    logger.info(query)

    if "," in query:
        if helpers.is_coordinate_search(query):
            logger.info("is_coordinate_search True")
            lat, lon = query.split(",")
            status_code, title, address = helpers.coordinate_search(
                lat, lon, cfg.API_URL_BASE_REVERSE_GEOCODE, cfg.API_KEY
            )

            logger.info("%s %s\n%s\n%s\n%s", lat, lon, status_code, title, address)

            if status_code == 200:
                results = []
                results.append(
                    InlineQueryResultLocation(
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

                await context.bot.answerInlineQuery(update.inline_query.id, results)
            else:
                results = []
                results.append(
                    InlineQueryResultArticle(
                        id="single_location",
                        title=title,
                        input_message_content=InputTextMessageContent(title),
                    )
                )

                await context.bot.answerInlineQuery(update.inline_query.id, results)
    elif query:
        status_code, locations, _ = helpers.get_locations(
            query, cfg.API_URL_BASE_GEOCODE, cfg.API_KEY
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

            await context.bot.answerInlineQuery(update.inline_query.id, inline_result)
        elif status_code == 204:
            inline_result = []
            inline_result.append(
                InlineQueryResultArticle(
                    id=str(uuid4()),
                    title="What are you searching?",
                    input_message_content=InputTextMessageContent(
                        "You need to add more infos in your inline query."
                    ),
                    thumb_url=IMAGE_URL,
                )
            )

            await context.bot.answerInlineQuery(update.inline_query.id, inline_result)


# Show location selected on bot answer
async def startswithslash(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle any message that starts with a forward slash.
    Main purpose of this function is the handling of encoded location queries
    generated by a where command.

    Args:
        update (Update): Incoming update
        context (ContextTypes.DEFAULT_TYPE): Context object
    """
    user_message = update.message.text[1:]
    chat_id = update.message.chat_id

    try:
        lat, lon = helpers.decode_lat_lon(user_message).split(",")

        assert helpers.lat_lon_parse(lat, lon)

        await context.bot.send_location(chat_id=chat_id, latitude=lat, longitude=lon)
    except Exception:
        await context.bot.send_message(
            chat_id=chat_id,
            text=(
                "I can show you where a location is in the world. "
                "Simply send me a query like 'Rome' or "
                "use /where 'location' command"
            ),
        )


async def non_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle messages that doesn't starts with / aka messages :D
    Shortcut to where.

    Args:
        update (Update): Incoming update
        context (ContextTypes.DEFAULT_TYPE): Context object
    """
    await where(update, context)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Shows the help message.

    Args:
        update (Update): Incoming update
        context (ContextTypes.DEFAULT_TYPE): Context object
    """

    chat_id = update.message.chat_id
    help_text = HELP_TEXT

    await context.bot.send_message(chat_id=chat_id, text=help_text, parse_mode="HTML")


async def info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Shows the info message.

    Args:
        update (Update): Incoming update
        context (ContextTypes.DEFAULT_TYPE): Context object
    """

    chat_id = update.message.chat_id
    info_text = INFO_TEXT

    await context.bot.send_message(
        chat_id=chat_id, text=emojize(info_text), parse_mode="HTML"
    )


async def inline(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Show infos about how to use inline mode

    Args:
        update (Update): Incoming update
        context (ContextTypes.DEFAULT_TYPE): Context object
    """

    chat_id = update.message.chat_id
    inline_info_text = INLINE_INFO_TEXT

    await context.bot.send_message(
        chat_id=chat_id, text=inline_info_text, parse_mode="HTML"
    )


async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle errors generated by any incoming update and warn bot user and developer.

    Args:
        update (Update): Incoming update
        context (ContextTypes.DEFAULT_TYPE): Context object
    """

    # User
    chat_id = update.message.chat_id
    error_text = ERROR_TEXT
    await context.bot.send_message(chat_id=chat_id, text=error_text, parse_mode="HTML")

    # Developer
    trace = "".join(traceback.format_tb(sys.exc_info()[2]))
    log_text = f"Update: {update}\n\ncaused error: {context.error}\n\nTrace: \n{trace}"

    logger.warning(log_text)

    if cfg.CHAT_DEV_ID:
        await context.bot.send_message(chat_id=cfg.CHAT_DEV_ID, text=log_text)


def main():
    """
    Entry point
    """
    application = ApplicationBuilder().token(cfg.TG_TOKEN).build()

    # Telegram commands
    application.add_handler(CommandHandler("where", where))
    application.add_handler(CallbackQueryHandler(button))

    application.add_handler(CommandHandler("location", f_location))

    application.add_handler(CommandHandler("inline", inline))
    application.add_handler(CommandHandler("info", info))
    application.add_handler(CommandHandler("help", help_command))

    # Inline query handler (via @botname query)
    application.add_handler(InlineQueryHandler(inlinequery))

    # on command not defined
    application.add_handler(MessageHandler(filters.COMMAND, startswithslash))

    # on non_command i.e message
    application.add_handler(MessageHandler(filters.TEXT, non_command))

    # log all errors
    application.add_error_handler(error)

    if cfg.MODE == "polling":
        application.run_polling()
    elif cfg.MODE == "webhook":
        application.run_webhook(
            listen="0.0.0.0",
            port=cfg.PORT,
            url_path=cfg.URL_PATH,
            cert=cfg.CERT,
            key=cfg.KEY,
            webhook_url=cfg.WEBHOOK_URL,
            secret_token=cfg.WEBHOOK_SECRET,
        )


if __name__ == "__main__":
    main()
