from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user
from urllib.parse import urlparse
from werkzeug.utils import secure_filename
from app import db
from app.routes import auth
from app.forms import LoginForm, RegistrationForm, EditUsernameForm, EditPasswordForm, UploadAvatarForm
from app.models import User, SiteConfig
import os
import uuid

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('注册成功！现在可以登录了', 'success')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', title='注册', form=form)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('用户名或密码错误', 'danger')
            return redirect(url_for('auth.login'))
        if user.is_banned:
            flash('您的账号已被封禁', 'danger')
            return redirect(url_for('auth.login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or urlparse(next_page).netloc != '':
            next_page = url_for('main.index')
        flash('登录成功！', 'success')
        return redirect(next_page)
    return render_template('auth/login.html', title='登录', form=form)

@auth.route('/logout')
def logout():
    logout_user()
    flash('已退出登录', 'info')
    return redirect(url_for('main.index'))

@auth.route('/profile/<username>')
def profile(username):
    user = User.query.filter_by(username=username).first_or_404()
    posts = user.posts.order_by(Post.created_at.desc()).limit(10).all()
    return render_template('auth/profile.html', user=user, posts=posts)

@auth.route('/edit', methods=['GET', 'POST'])
def edit_profile():
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))
    config = SiteConfig.get_config()
    username_form = EditUsernameForm()
    password_form = EditPasswordForm()
    avatar_form = UploadAvatarForm()
    
    if username_form.validate_on_submit() and 'submit_username' in request.form:
        if not config.allow_change_username:
            flash('修改用户名功能已关闭', 'danger')
        else:
            current_user.username = username_form.username.data
            db.session.commit()
            flash('用户名修改成功', 'success')
            return redirect(url_for('auth.edit_profile'))
    
    if password_form.validate_on_submit() and 'submit_password' in request.form:
        if not config.allow_change_password:
            flash('修改密码功能已关闭', 'danger')
        elif not current_user.check_password(password_form.old_password.data):
            flash('当前密码错误', 'danger')
        else:
            current_user.set_password(password_form.password.data)
            db.session.commit()
            flash('密码修改成功', 'success')
            return redirect(url_for('auth.edit_profile'))
    
    if avatar_form.validate_on_submit() and 'submit_avatar' in request.form:
        if not config.allow_upload_avatar:
            flash('上传头像功能已关闭', 'danger')
        else:
            file = request.files.get('avatar')
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                ext = filename.rsplit('.', 1)[1].lower()
                new_filename = f"{uuid.uuid4().hex}.{ext}"
                upload_dir = os.path.join('app', 'static', 'uploads', 'avatars')
                os.makedirs(upload_dir, exist_ok=True)
                file_path = os.path.join(upload_dir, new_filename)
                file.save(file_path)
                current_user.avatar = f"uploads/avatars/{new_filename}"
                db.session.commit()
                flash('头像上传成功', 'success')
                return redirect(url_for('auth.edit_profile'))
            else:
                flash('请上传有效的图片文件（png, jpg, jpeg, gif）', 'danger')
    
    return render_template('auth/edit_profile.html', 
                          username_form=username_form, 
                          password_form=password_form, 
                          avatar_form=avatar_form,
                          config=config)

from app.models import Post
