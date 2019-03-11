from telegram.ext import Updater, CommandHandler
import requests
import re

token = os.environ['TELEGRAM_TOKEN']
some_api_token = os.environ['SOME_API_TOKEN']
port = int(os.environ.get('PORT', '8443'))

def get_url():
    contents = requests.get('https://random.dog/woof.json').json()
    url = contents['url']
    return url

def bop(bot, update):
    url = get_url()
    chat_id = update.message.chat_id
    bot.send_photo(chat_id=chat_id, photo=url)

def main():
    updater = Updater(token)
    dp = updater.dispatcher
    
    dp.add_handler(CommandHandler('bop',bop))

    updater.start_webhook(listen="0.0.0.0",
                          port=port,
                          url_path=token)
    updater.bot.set_webhook("https://whereisitbot.herokuapp.com/" + token)
    updater.idle()

if __name__ == '__main__':
    main()
    