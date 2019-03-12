from telegram.ext import Updater, CommandHandler
import requests
import re
import os
import json

token = os.environ['TELEGRAM_TOKEN']
api_key = os.environ['Map_Service_Api_Key']
api_url_base = os.environ['Api_Url_Base']
map_ico = '\U0001F5FA'

port = int(os.environ.get('PORT', '8443'))

def get_url():
    contents = requests.get('https://random.dog/woof.json').json()
    url = contents['url']
    return url

def get_locations(param):
    api_url = '{0}{1}.json?key={2}'.format(api_url_base, param, api_key)
    response = requests.get(api_url)
    print(api_url)
    print(response.status_code)

    if response.status_code == 200:
        jsonTom = json.loads(response.content.decode('utf-8'))
        number = jsonTom['summary']['numResults']

        retstr = "<b>Showing results for '{0}'</b>\n\n".format(param)

        print(retstr)

        for i in jsonTom['results']:
            if i['address'].get('countrySubdivision') is not None:
                retstr += "{6} <b>Address: {0}\n</b>Country: {1} - {2}\nLat: {3} Lon: {4}\nType: {5}\n\n".format(i['address']['freeformAddress'], i['address']['country'], i['address']['countrySubdivision'], i['position']['lat'], i['position']['lon'], i['type'], map_ico)
                #print("Type: {0}, Country: {1}, Address: {2}, Subdivision: {3}, Lat: {4}, Lon: {5}".format(i['type'], i['address']['country'], i['address']['freeformAddress'], i['address']['countrySubdivision'], i['position']['lat'], i['position']['lon']))
            else:
                restr += "{5} <b>Address: {0}\n</b>Country: {1}\nLat: {2} Lon: {3}\nType: {4}\n\n".format(i['address']['freeformAddress'], i['address']['country'], i['position']['lat'], i['position']['lon'], i['type'], map_ico)
                #print("Type: {0}, Country: {1}, Address: {2}, Lat: {3}, Lon: {4}".format(i['type'], i['address']['country'], i['address']['freeformAddress'], i['position']['lat'], i['position']['lon']))

    else:
        restr = 'Error {0}'.format(response.status_code)

    return retstr

def where(bot, update, args):
    try:
        user_input = " ".join(args)
        print(user_input)
        ret = get_locations(user_input)
        chat_id = update.message.chat_id
        #update.message.reply_text(ret)
        bot.send_message(chat_id = chat_id, 
                         text = ret, 
                         parse_mode = 'HTML')


        #url = get_url()
        #bot.send_photo(chat_id=chat_id, photo=url)
        #bot.send_location(chat_id=chat_id, latitude=37.3399964, longitude=-4.5811614)
    except Exception as e:
        print ("error in level argument",e.args[0])
        raise

def main():
    updater = Updater(token)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler('where',where, pass_args=True))

    updater.start_webhook(listen="0.0.0.0",
                          port=port,
                          url_path=token)
    updater.bot.set_webhook("https://whereisitbot.herokuapp.com/" + token)
    updater.idle()

if __name__ == '__main__':
    main()
    