import requests
from steem.post import Post

from .analyze import nsfw, labels


class AnalyzePost:
    def __init__(self, post_identifier):
        self.post_identifier = post_identifier
        self.results = None

    def list_images(self):
        p = Post(self.post_identifier)
        return p.json_metadata['image']

    def run(self):
        results = dict()
        for img_url in self.list_images():
            img_b = self.get_image(img_url)
            results[img_url] = {
                'nsfw': nsfw(img_b),
                'labels': labels(img_b),
            }
        self.results = results
        return self.results

    @staticmethod
    def get_image(image_url: str):
        return requests.get(image_url)._content


if __name__ == '__main__':
    permlink = '@nspart/nspart-a-shot-from-new-series-i-shot-with-cj-sparxx-a-steemit-first-post'
    a = AnalyzePost(permlink)

