from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, PasswordField, BooleanField, SubmitField, FileField
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

class EditUsernameForm(FlaskForm):
    username = StringField('新用户名', validators=[DataRequired(message='请输入用户名'), Length(min=2, max=64, message='用户名长度应在2-64个字符之间')])
    submit = SubmitField('修改用户名')
    
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('该用户名已被使用')

class EditPasswordForm(FlaskForm):
    old_password = PasswordField('当前密码', validators=[DataRequired(message='请输入当前密码')])
    password = PasswordField('新密码', validators=[DataRequired(message='请输入新密码'), Length(min=6, message='密码至少6个字符')])
    password2 = PasswordField('确认新密码', validators=[DataRequired(message='请确认新密码'), EqualTo('password', message='两次密码不一致')])
    submit = SubmitField('修改密码')

class UploadAvatarForm(FlaskForm):
    avatar = FileField('头像图片')
    submit = SubmitField('上传头像')

class SetUserTitleForm(FlaskForm):
    title = StringField('用户头衔', validators=[Length(max=50, message='头衔最多50个字符')])
    submit = SubmitField('设置头衔')

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
