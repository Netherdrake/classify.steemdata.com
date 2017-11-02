import datetime as dt

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
    upload = request.files['file'].stream.read()
    assert len(upload) < 5 * 1000 * 1000, "File too large"

    return render_template(
        '_result.html',
        nsfw=nsfw(upload),
        labels=labels(upload),
    )



if __name__ == '__main__':
    pass
