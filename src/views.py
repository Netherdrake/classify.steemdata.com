import datetime as dt
import binascii

from flask import (
    render_template,
    request,
    make_response,
    jsonify
)
from funcy import last

from . import app
from .analyze import nsfw, labels


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

    # import pdb; pdb.set_trace()
    return render_template(
        '_result.html',
        nsfw=nsfw(upload),
        labels=labels(upload),
        img_b64=img_b64,
        img_type=img_type,
    )

if __name__ == '__main__':
    pass
