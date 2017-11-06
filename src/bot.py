from steem.blockchain import Blockchain
from steem.post import Post
from toolz import thread_last
from operator import methodcaller
from collections import deque
from contextlib import suppress
from funcy import (
    complement,
    silent,
    keep,
    cache,
)

from rq import Queue
from redis import Redis

from .stm import AnalyzePost, send_nsfw_warning

def get_redis():
    redis_conn = Redis()
    return redis_conn

def get_queue():
    redis_conn = get_redis()
    q = Queue(connection=redis_conn)

    return q

def is_nsfw(post):
    return 'nsfw' in post.json_metadata.get('tags', [])

@cache(60)
def update_redis_head(redis_conn: Redis, b: Blockchain):
    return redis_conn.set(
        'nsfw_bot_head',
        b.get_current_block_num()
    )

def run():
    """ Scrape the blockchain and feed RQ Worker. """
    cache = deque(maxlen=100_000)
    redis_conn = get_redis()
    queue = get_queue()
    b = Blockchain()

    comments = b.stream(
        filter_by='comment',
        start_block=int(redis_conn.get('nsfw_bot_head') or 0),
    )
    stream = thread_last(
        comments,
        (keep, silent(Post)),
        (filter, methodcaller('is_main_post')),
        (filter, complement(is_nsfw)),
    )
    for post in stream:
        if post.identifier in cache:
            continue

        cache.append(post.identifier)
        queue.enqueue(
            'src.bot.analyze_task',
            post.identifier,
            timeout='5m',
            ttl='1h',
            result_ttl='30m',
        )
        update_redis_head(redis_conn, b)


def analyze_task(post_identifier):
    """ RQ Worker

    Returns True if nsfw found, otherwise False
    """
    a = AnalyzePost(post_identifier)

    for result in a.analyze_images_iter(labels=False):
        if result['nsfw']:
            send_nsfw_warning(post_identifier)
            return True

    return False

if __name__ == '__main__':
    with suppress(KeyboardInterrupt):
        run()
