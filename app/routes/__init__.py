from flask import Blueprint

auth = Blueprint('auth', __name__)
main = Blueprint('main', __name__)
forum = Blueprint('forum', __name__)

from app.routes import auth, main, forum
