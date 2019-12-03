import os

token = os.environ["TELEGRAM_TOKEN"]
image_url = os.environ["Image_Url"]
api_key = os.environ["Map_Service_Api_Key"]
api_url_base_geocode = os.environ["Api_Url_Base_Geocode"]
api_url_base_reverse_geocode = os.environ["Api_Url_Base_Reverse_Geocode"]
map_emoji = "\U0001F5FA"
mode = os.environ["MODE"]
port = int(os.environ.get("PORT", "8443"))
chat_dev_id = os.environ["dev_id"]
