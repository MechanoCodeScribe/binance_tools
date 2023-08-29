from aiogram import Bot
from binance.client import Client
import os
from dotenv import load_dotenv

load_dotenv()


TOKEN = os.getenv('BOT_TOKEN')
API_KEY = os.getenv('API_KEY')
SECRET_KEY = os.getenv('SECRET_KEY')



# Create a Bot instance using the provided token with HTML parsing mode
bot = Bot(TOKEN, parse_mode='HTML')

# Create a Client instance using the provided API key and secret key
client = Client(API_KEY, SECRET_KEY)

