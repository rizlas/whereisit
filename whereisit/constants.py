"""
Constants.py
"""

IMAGE_URL = (
    "https://raw.githubusercontent.com/rizlas/whereisit/master/images/question.png"
)
MAP_EMOJI = "\U0001F5FA"
MESSAGE_TITLE = "<b>Showing results for "
MESSAGE_TITLE_TAIL = "</b>\n\n"
ERROR_TEXT = """Hey. I'm sorry to inform you that an error happened while
I tried to handle your update. My developer(s) will be notified."""
HELP_TEXT = """<b>Commands for WhereIsItBot</b>

<b>/start</b> - Give life to this amazing bot
<b>/where</b> - With the name of a city or street will show where is it in the world (e.g. /where Rome)
<b>/location</b> - add latitude and longitude and separate them with comma to get a location (e.g. /location -27.122295, -109.288839)
<b>/info</b> - Shows information about how this bot works
<b>/inline</b> - Will explain how to use bot inline mode
<b>/help</b> - Shows this list"""

INFO_TEXT = """Hi fellows,
I was developed in Italy with the aim of make Italy great again, oh no just joking.

<i>How can you do such great things?</i>

My life is tied to TomTom's Api and I'm speaking to you thanks to python language. :snake:

<i>What did you just say? Do you speak Parseltongue? Bwahhh anyway you work great!</i>
I don't know if the guy who made me did a good job but you can check it here: https://github.com/rizlas/whereisit"""
INLINE_INFO_TEXT = """As you may already know, Telegram has also inline mode for bots.
Inline mode allows you to use bots also in private chats using the @name_of_bot string (like @gif john doe).
For 'Where Is It' bot you can use this mode to search a location and there are two types of search that you can use:

- @WhereIsItMapBot Rome will display results that matches with Rome
- @WhereIsItMapBot -27.122295, -109.288839 (latitude, longitude) allow you to send a specific location using coordinates (pay attention to use a comma between latitude and longitude)"""
