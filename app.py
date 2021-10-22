from flask import Flask, app
app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello World'

@app.route('/biodata')
def biodata():
    bio = 'nama : Pajar <br> alamat : Bandarlampung'
    return bio

if __name__ == '__main__':
    app.run()