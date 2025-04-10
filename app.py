import os
from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename
import sqlite3

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB max

# Veritabanı oluşturma
def init_db():
    with sqlite3.connect('videos.db') as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS videos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                title TEXT NOT NULL
            )
        ''')

@app.route('/')
def index():
    conn = sqlite3.connect('videos.db')
    videos = conn.execute('SELECT * FROM videos').fetchall()
    conn.close()
    return render_template('index.html', videos=videos)

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        file = request.files['video']
        title = request.form['title']
        if file:
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            with sqlite3.connect('videos.db') as conn:
                conn.execute('INSERT INTO videos (filename, title) VALUES (?, ?)', (filename, title))
            return redirect(url_for('index'))
    return render_template('upload.html')

@app.route('/watch/<int:video_id>')
def watch(video_id):
    conn = sqlite3.connect('videos.db')
    video = conn.execute('SELECT * FROM videos WHERE id = ?', (video_id,)).fetchone()
    conn.close()
    return render_template('watch.html', video=video)

if __name__ == '__main__':
    if not os.path.exists('videos.db'):
        init_db()
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    app.run(debug=True)
