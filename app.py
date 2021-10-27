from flask import Flask
import os
import sys

app = Flask(__name__)
app.secret_key = os.urandom(24)

from views import *
from api import *

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True, port=80)

# os.system("clear-cache.sh")