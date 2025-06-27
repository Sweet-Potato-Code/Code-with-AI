from flask import Flask, render_template_string, redirect
from flask_login import LoginManager, login_user, logout_user, UserMixin, current_user
from sqlalchemy import create_engine, MetaData
from flask_blogging import SQLAStorage, BloggingEngine
from markupsafe import escape

# 1. Initialize Flask app
app = Flask(__name__)
app.config.update({
    'SECRET_KEY':            'secure-key',
    'BLOGGING_URL_PREFIX':   '/blog',
    'BLOGGING_SITEURL':      'http://localhost:5000',
    'BLOGGING_SITENAME':     'My Flask Blog',
    'BLOGGING_KEYWORDS':     ['flask', 'blog', 'markdown'],
    'FILEUPLOAD_IMG_FOLDER': 'static/uploads',
    'FILEUPLOAD_PREFIX':     '/uploads',
    'FILEUPLOAD_ALLOWED_EXTENSIONS': ['png','jpg','jpeg','gif'],
})

# 2. Set up storage (SQLite example)
engine = create_engine('sqlite:///blog.db')
meta   = MetaData()
storage = SQLAStorage(engine, metadata=meta)
meta.create_all(bind=engine)

# 3. Initialize blogging engine
db_blog = BloggingEngine(app, storage)

# 4. User authentication setup
login_manager = LoginManager(app)

class User(UserMixin):
    def __init__(self, id):
        self.id = id
    def get_name(self):
        return 'Guest User'

@login_manager.user_loader
@db_blog.user_loader
def load_user(user_id):
    return User(user_id)

# 5. Basic routes (home, login, logout)
index_html = '''
<html><body>
  {% if current_user.is_authenticated %}
    <a href="/logout/">Logout</a>
  {% else %}
    <a href="/login/">Login</a>
  {% endif %}
  &nbsp;<a href="{{ url_for('blogging.index') }}">Blog Home</a>
</body></html>
'''

@app.route('/')
def index():
    return render_template_string(index_html)

@app.route('/login/')
def login():
    user = User('testuser')
    login_user(user)
    return redirect('/blog/')

@app.route('/logout/')
def logout():
    logout_user()
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)
