# CreatorBlog - 个人创作者博客系统

面向个人创作者的现代博客平台，支持富文本编辑与Markdown渲染。

## 技术栈

**后端:**
- Django 4.2 + Django REST Framework
- SQLite 轻量级数据库
- Token 认证

**前端:**
- Vue 3 (Composition API)
- Vite 构建工具
- TailwindCSS + Typography 插件
- Tiptap 富文本编辑器
- Marked + Highlight.js (Markdown 渲染)

## 核心功能

- 文章 CRUD (创建、查看、编辑、删除)
- 富文本 / Markdown 双模式编辑器
- 标签分类系统
- 评论系统 (支持嵌套回复)
- 阅读统计
- 草稿自动保存 (30秒间隔)
- 图片上传
- SEO 优化 (sitemap.xml, robots.txt, meta 标签)
- 用户注册登录
- 响应式移动端适配

## 快速开始

### 后端

```bash
# 安装 Python 依赖
pip install -r requirements.txt

# 数据库迁移
python manage.py migrate

# 创建管理员
python manage.py createsuperuser

# 启动后端服务
python manage.py runserver
```

### 前端

```bash
cd frontend

# 安装依赖
npm install

# 开发模式 (含 API 代理)
npm run dev

# 生产构建
npm run build
```

### 访问

- 前端: http://localhost:3000
- 后端 API: http://localhost:8000/api/
- 管理后台: http://localhost:8000/admin/

## API 接口

| 接口 | 方法 | 说明 |
|------|------|------|
| /api/articles/ | GET/POST | 文章列表/创建 |
| /api/articles/:slug/ | GET/PUT/DELETE | 文章详情/编辑/删除 |
| /api/articles/:slug/record_view/ | POST | 记录阅读 |
| /api/tags/ | GET/POST | 标签列表/创建 |
| /api/comments/ | GET/POST | 评论列表/创建 |
| /api/images/ | POST | 图片上传 |
| /api/stats/ | GET | 站点统计 |
| /api/auth/register/ | POST | 用户注册 |
| /api/auth/login/ | POST | 用户登录 |
| /api/auth/logout/ | POST | 退出登录 |
| /api/auth/profile/ | GET/PUT | 用户资料 |

## 项目结构

```
├── config/             # Django 项目配置
├── blog/               # 博客应用 (文章、标签、评论、图片)
├── accounts/           # 用户认证应用
├── media/              # 上传文件存储
├── frontend/           # Vue 3 前端
│   ├── src/
│   │   ├── views/      # 页面组件
│   │   ├── stores/     # Pinia 状态管理
│   │   ├── router/     # 路由配置
│   │   └── api/        # API 封装
│   └── ...
├── requirements.txt    # Python 依赖
└── manage.py
```
