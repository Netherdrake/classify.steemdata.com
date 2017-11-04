from steem.blockchain import Blockchain
from steem.post import Post
from toolz import thread_last
from operator import methodcaller
from collections import deque

cache = deque(maxlen=100_000)

b = Blockchain()

stream = thread_last(
    b.stream(filter_by='comment'),
    (map, Post),
    (filter, methodcaller('is_main_post')),
)

def run():
    for post in stream:
        if post.identifier in cache:
            continue

        cache.append(post.identifier)

        # TODO
        # send the post trough queue worker

if __name__ == '__main__':
    run()
