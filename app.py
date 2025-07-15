from flask import Flask, render_template, request, redirect, session, g
import sqlite3

app = Flask(__name__)
app.secret_key = 'supersecretkey'

DATABASE = 'chat.db'

# Predefined credentials
USERNAME = 'root'
PASSWORD = 'toor'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():
    with app.app_context():
        db = get_db()
        db.execute('CREATE TABLE IF NOT EXISTS messages (id INTEGER PRIMARY KEY, username TEXT, message TEXT)')
        db.commit()

@app.route('/', methods=['GET', 'POST'])
def index():
    error = ''
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == USERNAME and password == PASSWORD:
            session['user'] = username
            return redirect('/chat')
        else:
            error = 'Access Denied.'
    return render_template('index.html', error=error)

@app.route('/chat', methods=['GET', 'POST'])
def chat():
    if 'user' not in session:
        return redirect('/')

    db = get_db()
    if request.method == 'POST':
        message = request.form['message']
        db.execute('INSERT INTO messages (username, message) VALUES (?, ?)', (session['user'], message))
        db.commit()

    cur = db.execute('SELECT username, message FROM messages ORDER BY id DESC')
    messages = cur.fetchall()
    return render_template('chat.html', messages=messages)

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/')

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=10000)