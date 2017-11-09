import datetime as dt
import binascii
import pickle

from flask import (
    render_template,
    request,
    make_response,
    jsonify
)
from funcy import last

from . import app
from .analyze import nsfw, labels
from .stm import AnalyzePost


# router
# ------
@app.route('/')
def index():
    return render_template(
        'index.html'
    )

@app.route('/upload', methods=['POST'])
def uploader():
    img_type = request.files['file'].headers[1][1]
    upload = request.files['file'].stream.read()
    assert len(upload) < 5 * 1000 * 1000, "File too large"

    img_b64 = binascii.b2a_base64(upload).decode()

    return render_template(
        '_result.html',
        nsfw=nsfw(upload),
        labels=labels(upload),
        img_b64=img_b64,
        img_type=img_type,
    )

@app.route('/steem-post', methods=['POST'])
def steem_post():
    post_identifier = request.form['identifier']
    a = AnalyzePost(post_identifier)
    a.analyze_images()

    return render_template(
        '_result-steem.html',
        results=a.results,
        post=a.post,
    )

if __name__ == '__main__':
    pass
