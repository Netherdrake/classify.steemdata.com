import os

from flask import Flask

app = Flask(
    __name__,
    template_folder='templates',
    static_folder='static'
)

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'test_key')
app.config['UPLOADER_URI'] = os.getenv('UPLOADER_URI', 'http://localhost:5005')

# workaround flask issue #1907
if not os.getenv('PRODUCTION', False):
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.jinja_env.auto_reload = True
    app.jinja_env.cache = {}
