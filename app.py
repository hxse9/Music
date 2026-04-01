from flask import Flask, render_template, request, redirect, url_for, g, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'super_secret_dev_key'

if os.environ.get('VERCEL') == '1':
    DATABASE = '/tmp/music.db'
else:
    DATABASE = 'music.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
        
        # Vercel 환경에서 DB 초기화하기
        if os.environ.get('VERCEL') == '1':
            cursor = db.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='posts'")
            if not cursor.fetchone():
                try:
                    with open('schema.sql', 'r', encoding='utf-8') as f:
                        cursor.executescript(f.read())
                    db.commit()
                except Exception as e:
                    print(f"Schema loading error: {e}")
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash("로그인이 필요한 서비스입니다.", "warning")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    db = get_db()
    cursor = db.cursor()
    # 글 목록을 불러옵니다. 현재 작성자 이름(`nickname`)을 가져오기 위해 users 테이블과 JOIN 합니다.
    query = """
    SELECT posts.*, users.nickname 
    FROM posts 
    LEFT JOIN users ON posts.user_id = users.id 
    ORDER BY posts.created_at DESC
    """
    cursor.execute(query)
    posts = cursor.fetchall()

    # 모든 댓글을 불러와서 딕셔너리로 묶습니다. (post_id 기준)
    cursor.execute("""
        SELECT comments.*, users.nickname 
        FROM comments 
        JOIN users ON comments.user_id = users.id 
        ORDER BY comments.created_at ASC
    """)
    all_comments = cursor.fetchall()
    
    comments_by_post = {}
    for c in all_comments:
        post_id = c['post_id']
        if post_id not in comments_by_post:
            comments_by_post[post_id] = []
        comments_by_post[post_id].append(c)

    user_likes = []
    if 'user_id' in session:
        cursor.execute("SELECT post_id FROM post_likes WHERE user_id = ?", (session['user_id'],))
        user_likes = [row['post_id'] for row in cursor.fetchall()]

    return render_template('index.html', posts=posts, comments_by_post=comments_by_post, user_likes=user_likes)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        nickname = request.form['nickname']
        password = request.form['password']
        
        db = get_db()
        cursor = db.cursor()
        
        # 중복 아이디 확인
        cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
        if cursor.fetchone() is not None:
            flash("이미 존재하는 아이디입니다.", "error")
            return redirect(url_for('register'))
            
        hashed_pw = generate_password_hash(password)
        cursor.execute("INSERT INTO users (username, nickname, password) VALUES (?, ?, ?)",
                       (username, nickname, hashed_pw))
        db.commit()
        flash("회원가입이 완료되었습니다! 로그인해주세요.", "success")
        return redirect(url_for('login'))
        
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        
        if user and check_password_hash(user['password'], password):
            session.clear()
            session['user_id'] = user['id']
            session['nickname'] = user['nickname']
            return redirect(url_for('index'))
        else:
            flash("아이디 또는 비밀번호가 올바르지 않습니다.", "error")
            
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/write', methods=['GET', 'POST'])
@login_required
def write():
    if request.method == 'POST':
        title = request.form['title']
        artist = request.form['artist']
        genre_tag = request.form.get('genre_tag', '')
        youtube_url = request.form.get('youtube_url', '')
        content = request.form['content']
        user_id = session['user_id']
        
        db = get_db()
        cursor = db.cursor()
        cursor.execute("""
            INSERT INTO posts (user_id, title, artist, genre_tag, youtube_url, content)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (user_id, title, artist, genre_tag, youtube_url, content))
        db.commit()
        return redirect(url_for('index'))
        
    return render_template('write.html')

@app.route('/post/<int:post_id>/comment', methods=['POST'])
@login_required
def comment(post_id):
    body = request.form['body']
    user_id = session['user_id']
    
    db = get_db()
    cursor = db.cursor()
    cursor.execute("""
        INSERT INTO comments (post_id, user_id, body)
        VALUES (?, ?, ?)
    """, (post_id, user_id, body))
    db.commit()
    return redirect(url_for('index'))

@app.route('/post/<int:post_id>/like', methods=['POST'])
@login_required
def like_post(post_id):
    user_id = session['user_id']
    db = get_db()
    cursor = db.cursor()
    
    cursor.execute("SELECT * FROM post_likes WHERE user_id = ? AND post_id = ?", (user_id, post_id))
    like_record = cursor.fetchone()
    
    if like_record:
        cursor.execute("DELETE FROM post_likes WHERE user_id = ? AND post_id = ?", (user_id, post_id))
        cursor.execute("UPDATE posts SET likes_count = likes_count - 1 WHERE id = ?", (post_id,))
    else:
        cursor.execute("INSERT INTO post_likes (user_id, post_id) VALUES (?, ?)", (user_id, post_id))
        cursor.execute("UPDATE posts SET likes_count = likes_count + 1 WHERE id = ?", (post_id,))
        
    db.commit()
    return redirect(url_for('index'))

@app.route('/post/<int:post_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM posts WHERE id = ?", (post_id,))
    post = cursor.fetchone()
    
    if not post or post['user_id'] != session['user_id']:
        flash("권한이 없습니다.", "error")
        return redirect(url_for('index'))
        
    if request.method == 'POST':
        title = request.form['title']
        artist = request.form['artist']
        genre_tag = request.form.get('genre_tag', '')
        youtube_url = request.form.get('youtube_url', '')
        content = request.form['content']
        
        cursor.execute("""
            UPDATE posts SET title = ?, artist = ?, genre_tag = ?, youtube_url = ?, content = ?
            WHERE id = ?
        """, (title, artist, genre_tag, youtube_url, content, post_id))
        db.commit()
        return redirect(url_for('index'))
        
    return render_template('edit.html', post=post)

@app.route('/post/<int:post_id>/delete', methods=['POST'])
@login_required
def delete_post(post_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT user_id FROM posts WHERE id = ?", (post_id,))
    post = cursor.fetchone()
    
    if post and post['user_id'] == session['user_id']:
        cursor.execute("DELETE FROM posts WHERE id = ?", (post_id,))
        db.commit()
    return redirect(url_for('index'))

@app.route('/comment/<int:comment_id>/delete', methods=['POST'])
@login_required
def delete_comment(comment_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT user_id FROM comments WHERE id = ?", (comment_id,))
    comment = cursor.fetchone()
    
    if comment and comment['user_id'] == session['user_id']:
        cursor.execute("DELETE FROM comments WHERE id = ?", (comment_id,))
        db.commit()
    return redirect(url_for('index'))


if __name__ == '__main__':
    # 웹 브라우저에서 서버를 띄워 확인하도록 합니다.
    app.run(debug=True, port=5000)
