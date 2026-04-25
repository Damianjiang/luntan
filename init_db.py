import os
import sys

project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_dir)

from app import create_app, db
from app.models import User, Category

def init_db():
    app = create_app()
    with app.app_context():
        db.create_all()
        
        if User.query.filter_by(username='admin').first() is None:
            admin = User(username='admin', email='admin@example.com', is_admin=True)
            admin.set_password('admin123')
            db.session.add(admin)
            
            categories = [
                Category(name='公告区', description='论坛公告和重要通知', icon='📢', order=0, admin_only=True),
                Category(name='技术讨论', description='技术交流与问题讨论', icon='💻', order=1),
                Category(name='休闲娱乐', description='闲聊灌水、分享趣事', icon='🎮', order=2),
                Category(name='求助问答', description='有问题？来这里寻求帮助', icon='❓', order=3),
            ]
            
            for category in categories:
                db.session.add(category)
            
            db.session.commit()
            print('数据库初始化完成！')
            print('管理员账号: admin')
            print('管理员密码: admin123')
        else:
            print('数据库已存在，跳过初始化')

if __name__ == '__main__':
    init_db()
