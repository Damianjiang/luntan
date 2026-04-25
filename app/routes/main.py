from flask import render_template
from app.routes import main
from app.models import Category, Post

@main.route('/')
@main.route('/index')
def index():
    categories = Category.query.order_by(Category.order).all()
    recent_posts = Post.query.order_by(Post.created_at.desc()).limit(10).all()
    hot_posts = Post.query.order_by(Post.views.desc()).limit(5).all()
    return render_template('index.html', categories=categories, recent_posts=recent_posts, hot_posts=hot_posts)

@main.route('/about')
def about():
    return render_template('about.html', title='关于我们')
