from flask import Blueprint
from app import app

deteksi = Blueprint('deteksi', __name__)
from .deteksi_view import *
app.register_blueprint(deteksi)
