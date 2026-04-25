from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError
from app.models import User

class LoginForm(FlaskForm):
    username = StringField('用户名', validators=[DataRequired(message='请输入用户名')])
    password = PasswordField('密码', validators=[DataRequired(message='请输入密码')])
    remember_me = BooleanField('记住我')
    submit = SubmitField('登录')

class RegistrationForm(FlaskForm):
    username = StringField('用户名', validators=[DataRequired(message='请输入用户名'), Length(min=2, max=64, message='用户名长度应在2-64个字符之间')])
    email = StringField('邮箱', validators=[DataRequired(message='请输入邮箱'), Email(message='请输入有效的邮箱地址')])
    password = PasswordField('密码', validators=[DataRequired(message='请输入密码'), Length(min=6, message='密码至少6个字符')])
    password2 = PasswordField('确认密码', validators=[DataRequired(message='请确认密码'), EqualTo('password', message='两次密码不一致')])
    submit = SubmitField('注册')
    
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('该用户名已被使用')
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('该邮箱已被注册')

class EditProfileForm(FlaskForm):
    signature = StringField('个性签名', validators=[Length(max=200, message='签名最多200个字符')])
    submit = SubmitField('保存')

class PostForm(FlaskForm):
    title = StringField('标题', validators=[DataRequired(message='请输入标题'), Length(max=140, message='标题最多140个字符')])
    content = TextAreaField('内容', validators=[DataRequired(message='请输入内容')])
    submit = SubmitField('发布')

class CommentForm(FlaskForm):
    content = TextAreaField('评论', validators=[DataRequired(message='请输入评论内容')])
    submit = SubmitField('发表评论')

class CategoryForm(FlaskForm):
    name = StringField('板块名称', validators=[DataRequired(message='请输入板块名称'), Length(max=64)])
    description = StringField('板块描述', validators=[Length(max=200)])
    icon = StringField('图标', validators=[Length(max=50)])
    submit = SubmitField('创建板块')
