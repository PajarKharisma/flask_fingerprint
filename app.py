from flask import Flask, app, render_template
app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello World'

@app.route('/biodata')
def biodata():
    bio = 'nama : Pajar <br> alamat : Bandarlampung'
    return bio

@app.route('/about')
def about():
    return render_template('index.html')

if __name__ == '__main__':
    app.run()