from flask import Blueprint
from app import app

api = Blueprint('api', __name__)

from .deteksi import *

app.register_blueprint(api, url_prefix='/api')