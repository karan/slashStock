# Built-in imports
import datetime
import logging
import os
import random
import re
import shutil
import time

# Third-party dependencies
import requests
import tweepy
from ttp import ttp

# Custom imports
from create_image import create_image
from share import get_quote
try:
    import config
except:
    import config_example as config


# Gloabl variable init
DEFAULT_TIME_SPAN = '1d'
TWEET_LENGTH = 140
IMAGE_URL_LENGTH = 23
STOCK_URL_LENGTH = 23
MAX_TWEET_TEXT_LENGTH = TWEET_LENGTH - IMAGE_URL_LENGTH - STOCK_URL_LENGTH - 2
DOTS = '...'
BACKOFF = 0.5 # Initial wait time before attempting to reconnect
MAX_BACKOFF = 300 # Maximum wait time between connection attempts
MAX_IMAGE_SIZE = 3072 * 1024 # bytes
USERNAME = 'slashstock'

YAHOO_URL = 'http://finance.yahoo.com/q?s=%s'  # symbol
CHART_API = 'http://chart.finance.yahoo.com/z?s=%s&t=%s&q=l&l=off&z=s'  # symbol, time

SYMBOL_NOT_FOUND = '@%s I could not find "%s". Is it a real symbol?'
STOCK_REPLY_TEMPLATE = ('$%s: $%s (%s%%)\n'         # symbol, price, change
                        # 'Mkt cap: $%s, P/E: %s\n'   # cap, pe
                        '%s\n\n'                    # link
                        '%s')                       # users

# BLACKLIST
# Do not respond to queries by these accounts
BLACKLIST = [
    'pixelsorter',
    'lowpolybot',
    'slashkarebear',
    'slashgif',
    'slashremindme'
]


logging.basicConfig(filename='logger.log',
                    level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


# Twitter client
auth = tweepy.OAuthHandler(config.twitter['key'], config.twitter['secret'])
auth.set_access_token(config.twitter['access_token'],
                      config.twitter['access_token_secret'])
api = tweepy.API(auth)
# Tweet parser
parser = ttp.Parser()
# backoff time
backoff = BACKOFF


def strip_symbol(term):
    return term.strip('$')


def now_str():
    now = datetime.datetime.now()
    return now.strftime('%Y-%m-%d-%H-%M-%S-%f')


def get_out_filename(symbol, time_span, quote):
    r = requests.get(CHART_API % (symbol, time_span), stream=True)

    filename = ''
    if r.status_code == 200:
        filename = 'charts/%s-%s.png' % (symbol, now_str())
        final_filename = 'charts/%s-%s-final.png' % (symbol, now_str())
        with open(filename, 'wb') as f:
            r.raw.decode_content = True
            shutil.copyfileobj(r.raw, f)
        create_image(quote, filename, final_filename)

    logging.info('get_chart_filename: %s--%s--%s' % (symbol, time_span,
                                                     filename))
    return final_filename


def parse_tweet(tweet_from, tweet_text):
    query = tweet_text[tweet_text.index('@%s' % USERNAME) + len('@%s' % USERNAME) + 1:]

    result = parser.parse(tweet_text)
    tagged_users = result.users + [tweet_from]
    tagged_hashtags = result.tags
    tagged_urls = result.urls

    for user in tagged_users:
        query = query.replace('@%s' % user, '')
    for tag in tagged_hashtags:
        query = query.replace('#%s' % tag, '')
    for url in tagged_urls:
        query = query.replace('%s' % url, '')

    logging.info('parse_tweet: %s--%s' % (tagged_users, query))

    splits = re.compile('\s+').split(query.strip())

    symbol, time_span = splits[0].strip(), DEFAULT_TIME_SPAN

    if len(splits) > 1:
        time_span = splits[1].strip()

    logging.info('parse_tweet: %s--%s--%s' % (tagged_users, symbol, time_span))
    return tagged_users, strip_symbol(symbol), time_span


def generate_reply_tweet(users, symbol, quote):
    reply = STOCK_REPLY_TEMPLATE % (symbol.upper(),
                                    quote['price'], quote['change_percent'],
                                    YAHOO_URL % symbol,
                                    ' '.join(['@%s' % user for user in users if user != USERNAME]))
    if len(reply) > MAX_TWEET_TEXT_LENGTH:
        reply = reply[:MAX_TWEET_TEXT_LENGTH - len(DOTS) - 1] + DOTS

    logging.info('generate_reply_tweet: %s' % reply)
    return reply


class StreamListener(tweepy.StreamListener):

    def on_status(self, status):
        global backoff

        backoff = BACKOFF
        # Collect logging and debugging data
        tweet_id = status.id
        tweet_text = status.text
        tweet_from = status.user.screen_name

        if tweet_from.lower() != USERNAME and tweet_from.lower() not in BLACKLIST and not hasattr(status, 'retweeted_status'):
            logging.info('on_status: %s--%s' % (tweet_id, tweet_text))

            # Parse tweet for search term
            tagged_users, symbol, time_span = parse_tweet(tweet_from, tweet_text.lower())

            if symbol:
                # Get the quote, or quit if invalid symbol
                quote = get_quote(symbol)
                logging.info('on_status_quote: %s' % quote)

                if not (quote.get('open_price', None) and quote.get('price', None) and quote.get('change', None)):
                    # Symbol could be wrong. Send an error tweet
                    err_tweet = SYMBOL_NOT_FOUND % (tweet_from, symbol)
                    reply_status = api.update_status(status=err_tweet,
                        in_reply_to_status_id=tweet_id)
                    logging.info('on_err_status_sent: %s %s' % (
                            reply_status.id_str, reply_status.text))
                else:
                    # Search and save the image
                    filename = get_out_filename(symbol, time_span, quote)

                    if filename:
                        # Generate and send the the reply tweet
                        reply_tweet = generate_reply_tweet(tagged_users, symbol, quote)
                        reply_status = api.update_with_media(filename=filename,
                            status=reply_tweet, in_reply_to_status_id=tweet_id)

                        logging.info('on_status_sent: %s %s' % (
                            reply_status.id_str, reply_status.text))
                    else:
                        logging.info('on_status_failed: No images for %s' % symbol)
            else:
                logging.info('on_status_failed: No search terms')

    def on_error(self, status_code):
        global backoff
        logging.info('on_error: %d' % status_code)

        if status_code == 420:
            backoff = backoff * 2
            logging.info('on_error: backoff %s seconds' % backoff)
            time.sleep(backoff)
            return True


if not os.path.exists('charts/'):
    os.makedirs('charts/')

stream_listener = StreamListener()
stream = tweepy.Stream(auth=api.auth, listener=stream_listener)
try:
    stream.userstream(_with='user', replies='all')
except Exception as e:
    logging.ERROR('stream_exception: %s' % e)
    raise e
