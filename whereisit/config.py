import os

token = os.environ["TELEGRAM_TOKEN"]
api_key = os.environ["MAP_SERVICE_API_KEY"]
api_url_base_geocode = os.environ["API_URL_BASE_GEOCODE"]
api_url_base_reverse_geocode = os.environ["API_URL_BASE_REVERSE_GEOCODE"]
mode = os.environ["MODE"]
port = int(os.environ.get("PORT", "8443"))
chat_dev_id = os.environ["DEV_ID"]
