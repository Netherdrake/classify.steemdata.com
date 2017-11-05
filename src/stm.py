import requests
import binascii
from steem import Steem
from steem.post import Post
from steem.account import Account
from steemdata import SteemData
from steembase.exceptions import RPCError
from funcy import take, some
from contextlib import suppress

from .analyze import nsfw, labels
from .config import (
    BOT_USERNAME,
    STEEM_POSTING_KEY,
    NSFW_WARNING_MSG,
)

class AnalyzePost:
    sd = SteemData()

    def __init__(self, post_identifier):
        self.post_identifier = post_identifier
        self.post = Post(self.post_identifier)
        self.results = None

    def list_images(self):
        return self.post.json_metadata['image']

    def analyze_images_iter(self, **kwargs):
        for img_url in self.list_images():
            img_b = self.get_image(img_url)
            img_b64 = binascii.b2a_base64(img_b).decode()
            result = {
                'data': img_b64,
            }
            if kwargs.get('nsfw', True):
                result['nsfw'] = nsfw(img_b)
            if kwargs.get('labels', True):
                result['labels'] = labels(img_b)

            yield result

    def analyze_images(self):
        self.results = list(self.analyze_images_iter())
        return self.results

    def comment_match_steemdata(self):
        conditions = {
            'account': BOT_USERNAME,
            'type':'comment',
            'parent_permlink': self.post.permlink,
        }
        return self.sd.AccountOperations.find_one(conditions)

    def comment_match_steemd(self):
        a = Account(BOT_USERNAME)
        recent_history = take(
            1000,
            a.history_reverse(filter_by='comment')
        )
        match = some(
            lambda x: x['parent_permlink'] == self.post.permlink,
            recent_history
        )
        return match

    def has_warned_already(self):
        """ Check if our bot already commented on a post. """
        return any([
            self.comment_match_steemdata(),
            self.comment_match_steemd(),
        ])

    @staticmethod
    def get_image(image_url: str):
        return requests.get(image_url)._content


def send_nsfw_warning(post_identifier):
    # By constructing the static identifier,
    # we avoid the need to check Account history.
    s = Steem(keys=[STEEM_POSTING_KEY])
    post_permlink = post_identifier.split("/")[-1]
    permlink = f're-{post_permlink}'
    with suppress(RPCError):
        s.commit.post(
            reply_identifier=post_identifier,
            permlink=permlink,
            title='nsfw-bot-warning',
            body=NSFW_WARNING_MSG,
            author=BOT_USERNAME,
            self_vote=True,
        )


if __name__ == '__main__':
    permlink = '@azzurra92/naked-in-the-car'
    a = AnalyzePost(permlink)
    print(a.analyze_images())

