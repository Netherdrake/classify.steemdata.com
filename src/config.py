from os import getenv

BOT_USERNAME = 'nsfw-bot'
STEEM_POSTING_KEY = getenv('STEEM_POSTING_KEY', '')

NSFW_WARNING_MSG = \
    "This post *may* contain adult themed images. " \
    "Have you forgotten to add the `nsfw` tag?"

