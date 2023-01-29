"""
config.py
"""
import os

API_KEY = os.getenv("MAP_SERVICE_API_KEY")
API_URL_BASE_GEOCODE = os.getenv(
    "API_URL_BASE_GEOCODE", "https://api.tomtom.com/search/2/geocode/"
)
API_URL_BASE_REVERSE_GEOCODE = os.getenv(
    "API_URL_BASE_REVERSE_GEOCODE", "https://api.tomtom.com/search/2/reverseGeocode/"
)
CHAT_DEV_ID = os.getenv("DEV_ID")
PORT = int(os.environ.get("PORT", "8443"))
MODE = os.getenv("MODE", "polling")
TG_TOKEN = os.getenv("TELEGRAM_TOKEN")
URL_PATH = os.getenv("URL_PATH", "")
CERT = os.getenv("CERT")
KEY = os.getenv("KEY")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET")
