# TCraft服务器论坛

一个基于 Flask 开发的现代化论坛系统，提供简洁高效的用户交流平台。

## 功能特点

### 用户系统
- 用户注册与登录
- 密码加密存储
- 记住登录状态
- 用户个人主页
- 用户封禁功能

### 论坛功能
- 多板块分类讨论
- 发布、编辑、删除帖子
- 评论与回复功能
- 帖子浏览计数
- 帖子置顶与锁定

### 管理功能
- 后台数据统计
- 用户管理（查看、封禁、删除）
- 板块管理（创建、删除、权限设置）
- 评论管理（删除评论）

### 安全特性
- CSRF 保护
- 密码哈希存储
- 权限验证
- 表单验证

## 技术栈

- **后端框架**: Flask 3.0
- **数据库**: SQLite (SQLAlchemy ORM)
- **用户认证**: Flask-Login
- **表单处理**: Flask-WTF
- **前端**: HTML5 + CSS3

## 目录结构

```
论坛/
├── app/
│   ├── routes/              # 路由模块
│   │   ├── __init__.py
│   │   ├── auth.py          # 用户认证路由
│   │   ├── forum.py         # 论坛功能路由
│   │   └── main.py          # 主页路由
│   ├── static/              # 静态资源
│   │   ├── css/
│   │   │   └── style.css
│   │   └── images/
│   ├── templates/           # 模板文件
│   │   ├── auth/            # 认证相关页面
│   │   └── forum/           # 论坛相关页面
│   ├── __init__.py          # 应用初始化
│   ├── forms.py             # 表单类
│   └── models.py            # 数据库模型
├── config.py                # 配置文件
├── init_db.py               # 数据库初始化脚本
├── requirements.txt         # 依赖列表
├── run.py                   # 启动脚本
└── README.md                # 说明文档
```

## 安装教程

### 环境要求

- Python 3.8 或更高版本
- pip 包管理器

### 安装步骤

#### 1. 克隆或下载项目

将项目文件下载到本地目录。

#### 2. 创建虚拟环境（推荐）

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

#### 3. 安装依赖

```bash
pip install -r requirements.txt
```

#### 4. 初始化数据库

```bash
python init_db.py
```

初始化完成后会显示：
```
数据库初始化完成！
管理员账号: admin
管理员密码: admin123
```

#### 5. 启动服务器

```bash
python run.py
```

服务器启动后访问 http://127.0.0.1:5000 即可使用论坛。

## 默认账号

| 角色 | 用户名 | 密码 |
|------|--------|------|
| 管理员 | admin | admin123 |

## 默认板块

| 板块名称 | 描述 | 发帖权限 |
|----------|------|----------|
| 公告区 | 论坛公告和重要通知 | 仅管理员 |
| 技术讨论 | 技术交流与问题讨论 | 所有用户 |
| 休闲娱乐 | 闲聊灌水、分享趣事 | 所有用户 |
| 求助问答 | 有问题？来这里寻求帮助 | 所有用户 |

## 功能说明

### 普通用户
- 注册账号
- 登录/退出登录
- 发布帖子（非管理员专属板块）
- 评论和回复
- 编辑自己的帖子
- 删除自己的帖子

### 管理员
- 所有普通用户功能
- 访问后台管理
- 查看数据统计
- 管理用户（封禁/解封/删除）
- 管理板块（创建/删除/设置权限）
- 置顶/锁定帖子
- 删除任何帖子和评论

## 配置说明

配置文件位于 `config.py`，可修改以下配置：

```python
class Config:
    SECRET_KEY = 'your-secret-key'  # 安全密钥，生产环境请修改
    SQLALCHEMY_DATABASE_URI = 'sqlite:///forum.db'  # 数据库路径
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 最大上传大小
```

## 生产环境部署

### 使用 Gunicorn（Linux）

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 run:app
```

### 使用 Waitress（Windows）

```bash
pip install waitress
waitress-serve --port=8000 run:app
```

### 注意事项

1. 修改 `SECRET_KEY` 为随机字符串
2. 使用环境变量存储敏感配置
3. 使用 HTTPS
4. 配置防火墙规则
5. 定期备份数据库

## 常见问题

### Q: 忘记管理员密码怎么办？

A: 删除 `forum.db` 文件，重新运行 `python init_db.py` 初始化数据库。

### Q: 如何修改端口？

A: 修改 `run.py` 中的 `app.run(debug=True, port=5000)`。

### Q: 如何添加新板块？

A: 使用管理员账号登录，进入后台 -> 板块管理 -> 创建新板块。

## 许可证

MIT License

## 作者

Damian2012

---

如有问题或建议，欢迎在论坛中发帖讨论。
