from app import app
from flask import render_template

# This is for rendering the home page
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about_us')
def about_us():
    return render_template('about_us.html')

@app.route('/profile')
def profile():
    return render_template('profilemy.html')

@app.route('/posts')
def posts():
    return render_template('posts.html')

@app.route('/inbox')
def inbox():
    return render_template('inbox.html')