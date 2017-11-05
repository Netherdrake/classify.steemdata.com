from steem.blockchain import Blockchain
from steem.post import Post
from toolz import thread_last
from operator import methodcaller
from collections import deque
from funcy import complement, silent, keep

from .stm import AnalyzePost, send_nsfw_warning

def get_queue():
    from rq import Queue
    from redis import Redis

    redis_conn = Redis()
    q = Queue(connection=redis_conn)

    return q

def is_nsfw(post):
    return 'nsfw' in post.json_metadata.get('tags', [])

def run():
    """ Scrape the blockchain and feed RQ Worker. """
    cache = deque(maxlen=100_000)
    queue = get_queue()
    b = Blockchain()

    stream = thread_last(
        b.stream(filter_by='comment'),
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
    run()
