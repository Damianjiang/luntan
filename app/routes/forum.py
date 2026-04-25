from flask import render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from app import db
from app.routes import forum
from app.forms import PostForm, CommentForm, CategoryForm
from app.models import Category, Post, Comment, User, SiteConfig
from datetime import datetime, timedelta

@forum.route('/category/<int:id>')
def category(id):
    category = Category.query.get_or_404(id)
    page = request.args.get('page', 1, type=int)
    posts = Post.query.filter_by(category_id=id).order_by(Post.is_pinned.desc(), Post.created_at.desc()).paginate(page=page, per_page=20, error_out=False)
    return render_template('forum/category.html', category=category, posts=posts)

@forum.route('/post/<int:id>', methods=['GET', 'POST'])
def post(id):
    post = Post.query.get_or_404(id)
    post.views += 1
    db.session.commit()
    form = CommentForm()
    if form.validate_on_submit():
        if not current_user.is_authenticated:
            flash('请先登录', 'warning')
            return redirect(url_for('auth.login'))
        if current_user.is_banned:
            flash('您已被封禁，无法评论', 'danger')
            return redirect(url_for('forum.post', id=id))
        if post.is_locked:
            flash('该帖子已被锁定，无法回复', 'warning')
            return redirect(url_for('forum.post', id=id))
        comment = Comment(content=form.content.data, user_id=current_user.id, post_id=id)
        db.session.add(comment)
        db.session.commit()
        flash('评论发表成功', 'success')
        return redirect(url_for('forum.post', id=id) + '#comments')
    page = request.args.get('page', 1, type=int)
    comments = Comment.query.filter_by(post_id=id, parent_id=None).order_by(Comment.created_at.asc()).paginate(page=page, per_page=10, error_out=False)
    return render_template('forum/post.html', post=post, form=form, comments=comments)

@forum.route('/create', methods=['GET', 'POST'])
@login_required
def create_post():
    if current_user.is_banned:
        flash('您已被封禁，无法发帖', 'danger')
        return redirect(url_for('main.index'))
    form = PostForm()
    category_id = request.args.get('category_id', type=int)
    if form.validate_on_submit():
        selected_category_id = request.form.get('category_id', type=int)
        if not selected_category_id:
            flash('请选择板块', 'danger')
            categories = Category.query.all()
            return render_template('forum/create_post.html', form=form, categories=categories, selected_category=category_id)
        cat = Category.query.get(selected_category_id)
        if cat and cat.admin_only and not current_user.is_admin:
            flash('该板块只有管理员可以发帖', 'danger')
            categories = Category.query.all()
            return render_template('forum/create_post.html', form=form, categories=categories, selected_category=category_id)
        post = Post(title=form.title.data, content=form.content.data, user_id=current_user.id, category_id=selected_category_id)
        db.session.add(post)
        db.session.commit()
        flash('帖子发布成功', 'success')
        return redirect(url_for('forum.post', id=post.id))
    categories = Category.query.all()
    if not categories:
        flash('请先创建板块', 'warning')
        return redirect(url_for('main.index'))
    return render_template('forum/create_post.html', form=form, categories=categories, selected_category=category_id)

@forum.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_post(id):
    post = Post.query.get_or_404(id)
    if post.author != current_user and not current_user.is_admin:
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        post.updated_at = datetime.utcnow()
        db.session.commit()
        flash('帖子更新成功', 'success')
        return redirect(url_for('forum.post', id=post.id))
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
    return render_template('forum/edit_post.html', form=form, post=post)

@forum.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete_post(id):
    post = Post.query.get_or_404(id)
    if post.author != current_user and not current_user.is_admin:
        abort(403)
    category_id = post.category_id
    db.session.delete(post)
    db.session.commit()
    flash('帖子已删除', 'success')
    if category_id:
        return redirect(url_for('forum.category', id=category_id))
    return redirect(url_for('main.index'))

@forum.route('/pin/<int:id>')
@login_required
def pin_post(id):
    if not current_user.is_admin:
        abort(403)
    post = Post.query.get_or_404(id)
    post.is_pinned = not post.is_pinned
    db.session.commit()
    flash('操作成功', 'success')
    return redirect(url_for('forum.post', id=id))

@forum.route('/lock/<int:id>')
@login_required
def lock_post(id):
    if not current_user.is_admin:
        abort(403)
    post = Post.query.get_or_404(id)
    post.is_locked = not post.is_locked
    db.session.commit()
    flash('操作成功', 'success')
    return redirect(url_for('forum.post', id=id))

@forum.route('/reply/<int:comment_id>', methods=['GET', 'POST'])
@login_required
def reply_comment(comment_id):
    if current_user.is_banned:
        flash('您已被封禁，无法回复', 'danger')
        return redirect(url_for('main.index'))
    parent = Comment.query.get_or_404(comment_id)
    form = CommentForm()
    if form.validate_on_submit():
        comment = Comment(content=form.content.data, user_id=current_user.id, post_id=parent.post_id, parent_id=comment_id)
        db.session.add(comment)
        db.session.commit()
        flash('回复成功', 'success')
        return redirect(url_for('forum.post', id=parent.post_id))
    return render_template('forum/reply.html', form=form, parent=parent)

@forum.route('/delete_comment/<int:id>', methods=['POST'])
@login_required
def delete_comment(id):
    if not current_user.is_admin:
        abort(403)
    comment = Comment.query.get_or_404(id)
    post_id = comment.post_id
    db.session.delete(comment)
    db.session.commit()
    flash('评论已删除', 'success')
    return redirect(url_for('forum.post', id=post_id) + '#comments')

@forum.route('/admin')
@login_required
def admin():
    if not current_user.is_admin:
        abort(403)
    total_users = User.query.count()
    total_posts = Post.query.count()
    total_comments = Comment.query.count()
    total_categories = Category.query.count()
    today = datetime.utcnow().date()
    today_posts = Post.query.filter(Post.created_at >= today).count()
    today_users = User.query.filter(User.created_at >= today).count()
    recent_posts = Post.query.order_by(Post.created_at.desc()).limit(10).all()
    recent_users = User.query.order_by(User.created_at.desc()).limit(10).all()
    return render_template('forum/admin.html', 
        total_users=total_users, total_posts=total_posts, 
        total_comments=total_comments, total_categories=total_categories,
        today_posts=today_posts, today_users=today_users,
        recent_posts=recent_posts, recent_users=recent_users)

@forum.route('/admin/users')
@login_required
def admin_users():
    if not current_user.is_admin:
        abort(403)
    page = request.args.get('page', 1, type=int)
    users = User.query.order_by(User.created_at.desc()).paginate(page=page, per_page=20, error_out=False)
    return render_template('forum/admin_users.html', users=users)

@forum.route('/admin/ban/<int:id>', methods=['POST'])
@login_required
def ban_user(id):
    if not current_user.is_admin:
        abort(403)
    user = User.query.get_or_404(id)
    if user.is_admin:
        flash('不能封禁管理员', 'danger')
        return redirect(url_for('forum.admin_users'))
    user.is_banned = not user.is_banned
    db.session.commit()
    flash('操作成功', 'success')
    return redirect(url_for('forum.admin_users'))

@forum.route('/admin/delete_user/<int:id>', methods=['POST'])
@login_required
def delete_user(id):
    if not current_user.is_admin:
        abort(403)
    user = User.query.get_or_404(id)
    if user.is_admin:
        flash('不能删除管理员', 'danger')
        return redirect(url_for('forum.admin_users'))
    db.session.delete(user)
    db.session.commit()
    flash('用户已删除', 'success')
    return redirect(url_for('forum.admin_users'))

@forum.route('/admin/category', methods=['GET', 'POST'])
@login_required
def admin_category():
    if not current_user.is_admin:
        abort(403)
    form = CategoryForm()
    if form.validate_on_submit():
        category = Category(name=form.name.data, description=form.description.data, icon=form.icon.data)
        db.session.add(category)
        db.session.commit()
        flash('板块创建成功', 'success')
        return redirect(url_for('forum.admin_category'))
    categories = Category.query.order_by(Category.order).all()
    return render_template('forum/admin_category.html', form=form, categories=categories)

@forum.route('/admin/delete_category/<int:id>', methods=['POST'])
@login_required
def delete_category(id):
    if not current_user.is_admin:
        abort(403)
    category = Category.query.get_or_404(id)
    if category.posts.count() > 0:
        flash('该板块下有帖子，请先删除帖子', 'danger')
        return redirect(url_for('forum.admin_category'))
    db.session.delete(category)
    db.session.commit()
    flash('板块已删除', 'success')
    return redirect(url_for('forum.admin_category'))

@forum.route('/admin/category/<int:id>/toggle_admin', methods=['POST'])
@login_required
def toggle_category_admin(id):
    if not current_user.is_admin:
        abort(403)
    category = Category.query.get_or_404(id)
    category.admin_only = not category.admin_only
    db.session.commit()
    flash('设置已更新', 'success')
    return redirect(url_for('forum.admin_category'))

@forum.route('/admin/settings', methods=['GET', 'POST'])
@login_required
def admin_settings():
    if not current_user.is_admin:
        abort(403)
    config = SiteConfig.get_config()
    if request.method == 'POST':
        site_name = request.form.get('site_name')
        if site_name:
            config.site_name = site_name
            config.updated_at = datetime.utcnow()
            db.session.commit()
            flash('网站名称已更新', 'success')
            return redirect(url_for('forum.admin_settings'))
    return render_template('forum/admin_settings.html', config=config)

@forum.route('/admin/promote/<int:id>', methods=['POST'])
@login_required
def promote_user(id):
    if not current_user.is_admin:
        abort(403)
    user = User.query.get_or_404(id)
    if user.is_admin:
        flash('该用户已经是管理员', 'warning')
    else:
        user.is_admin = True
        db.session.commit()
        flash(f'已将 {user.username} 设为管理员', 'success')
    return redirect(url_for('forum.admin_users'))

@forum.route('/admin/demote/<int:id>', methods=['POST'])
@login_required
def demote_user(id):
    if not current_user.is_admin:
        abort(403)
    user = User.query.get_or_404(id)
    if not user.is_admin:
        flash('该用户不是管理员', 'warning')
    elif user.id == current_user.id:
        flash('不能取消自己的管理员权限', 'danger')
    else:
        user.is_admin = False
        db.session.commit()
        flash(f'已取消 {user.username} 的管理员权限', 'success')
    return redirect(url_for('forum.admin_users'))
