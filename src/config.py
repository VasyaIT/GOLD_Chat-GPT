from os import environ

from dotenv import load_dotenv
from loguru import logger

load_dotenv()

# SECRET KEYS
API_KEY = environ.get('API_KEY')
BOT_TOKEN = environ.get('BOT_TOKEN')

# REDIS
REDIS_HOST = environ.get('REDIS_HOST')
REDIS_PORT = environ.get('REDIS_PORT')

ADMINS = environ.get('ADMINS').split(' ')

# LOGGING
logger.add('src/logs/main.log',
           format='{time:D MMMM - YYYY > HH:mm:ss} | {file} | {level} | {message}',
           rotation='10 MB', compression='zip', serialize=False, level='ERROR')
