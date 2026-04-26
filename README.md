# 智剪 - AI智能视频剪辑

> 一款基于浏览器的AI智能视频剪辑工具，支持视频裁剪、合并、AI智能剪辑等功能

## 🎯 功能特点

- 📤 **视频上传** - 支持 MP4、AVI、MOV、MKV 等主流格式
- ✂️ **视频裁剪** - 精确设置起止时间，支持拖拽定位
- 🤖 **AI智能剪辑** - 自动识别高光时刻、精彩片段
- 📱 **移动端适配** - 完美支持手机、平板等移动设备
- 💾 **历史记录** - 本地保存剪辑历史，随时查看下载
- ⚡ **本地处理** - 视频在本地浏览器中处理，保护隐私

## 🛠️ 技术栈

### 前端
- Vue 3 + Composition API
- Vite 构建工具
- Tailwind CSS 样式
- FFmpeg WASM 视频处理
- 响应式设计

### 后端（可选）
- Python FastAPI
- 支持 Serverless 部署

## 🚀 快速开始

### 前端开发
```bash
cd frontend
npm install
npm run dev
```

### 后端开发（可选）
```bash
cd backend
pip install -r requirements.txt
python main.py
```

### Docker 部署
```bash
docker build -t zhijian .
docker run -p 8000:8000 zhijian
```

## 📁 项目结构

```
智剪项目/
├── frontend/           # 前端代码
│   ├── src/
│   │   ├── App.vue    # 主应用组件
│   │   ├── main.js    # 入口文件
│   │   └── style.css  # 全局样式
│   ├── index.html     # HTML模板
│   ├── package.json   # 依赖配置
│   ├── vite.config.js # Vite配置
│   └── tailwind.config.js
├── backend/           # 后端代码
│   ├── main.py       # FastAPI应用
│   └── requirements.txt
├── api/              # Vercel Serverless函数
├── vercel.json       # Vercel配置
└── README.md         # 项目文档
```

## 🌐 部署指南

### Vercel 部署（推荐）

1. Fork 本项目到您的 GitHub
2. 登录 [Vercel](https://vercel.com)
3. 点击 "Import Project" 导入项目
4. 配置项目设置并部署

### Railway 部署

1. 登录 [Railway](https://railway.app)
2. 创建新项目，选择 "Deploy from GitHub"
3. 连接您的仓库并部署

### 本地运行

```bash
# 克隆项目
git clone <your-repo-url>
cd 智剪项目

# 安装前端依赖
cd frontend
npm install
npm run dev

# 打开浏览器访问
# http://localhost:3000
```

## 📱 移动端使用

1. 使用手机浏览器打开部署后的网址
2. 点击"上传视频"选择要剪辑的视频
3. 使用播放控制定位要裁剪的位置
4. 设置起止时间或使用AI智能剪辑
5. 点击"开始剪辑"等待处理完成
6. 点击"下载"保存剪辑后的视频

## 🔧 API 接口

### 上传视频
```
POST /api/v1/upload
Content-Type: multipart/form-data

file: <视频文件>

Response:
{
  "success": true,
  "video_id": "uuid",
  "duration": 120.5,
  "message": "上传成功"
}
```

### 剪辑视频
```
POST /api/v1/clip
Content-Type: application/json

{
  "video_id": "uuid",
  "start_time": 10.5,
  "end_time": 30.0,
  "ai_mode": "highlight"
}

Response:
{
  "success": true,
  "task_id": "uuid",
  "status": "processing"
}
```

### 查询状态
```
GET /api/v1/status/{task_id}

Response:
{
  "task_id": "uuid",
  "status": "completed",
  "progress": 100,
  "result_url": "/api/v1/download/xxx.mp4"
}
```

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License

## 🙏 致谢

- [FFmpeg](https://ffmpeg.org/) - 视频处理引擎
- [Vue.js](https://vuejs.org/) - 前端框架
- [Tailwind CSS](https://tailwindcss.com/) - 样式框架

---

## 🎉 项目已完成

本项目包含以下组件：

### 📱 静态部署版 (index.html)
- **可直接部署**：上传到任何静态托管服务
- **无需后端**：使用浏览器端 FFmpeg WASM 处理视频
- **最佳兼容性**：适合快速上线和测试

### 🖥️ Vue3 前端版 (frontend/)
- **完整前端项目**：使用 Vite + Vue 3 + Tailwind CSS
- **组件化开发**：更好的代码结构和维护性
- **开发模式**：支持热重载和开发调试

### ⚙️ FastAPI 后端版 (backend/)
- **可选后端服务**：支持更强大的视频处理
- **API接口**：支持上传、剪辑、状态查询
- **Docker部署**：一键容器化部署

## 🚀 快速部署

### 方式一：Vercel 部署（推荐）

1. 将整个项目推送到 GitHub
2. 登录 [Vercel](https://vercel.com)
3. Import 项目并部署
4. 等待完成，获取访问 URL

### 方式二：Netlify 部署

1. 将 `index.html` 推送到 GitHub
2. 登录 [Netlify](https://netlify.com)
3. 拖拽文件夹或连接 GitHub
4. 立即获得 HTTPS 访问地址

### 方式三：Cloudflare Pages 部署

1. 登录 [Cloudflare Dashboard](https://dash.cloudflare.com)
2. 选择 Pages → Create a project
3. 连接 GitHub 仓库
4. 配置构建命令（留空）和输出目录（/）
5. 部署完成

### 方式四：本地测试

```bash
# 使用 Python 启动本地服务器
cd 智剪项目
python run_local.py

# 或使用 Node.js
npx serve .
```

## 📦 技术亮点

- ✅ **纯前端处理**：视频在本地浏览器处理，保护隐私
- ✅ **FFmpeg WASM**：强大的浏览器端视频编解码能力
- ✅ **响应式设计**：完美支持桌面和移动设备
- ✅ **离线可用**：加载一次后可在无网络环境使用
- ✅ **中文界面**：全中文 UI设计
- ✅ **历史记录**：本地保存剪辑历史

## ⚠️ 注意事项

1. **浏览器兼容性**：建议使用 Chrome/Firefox/Safari 最新版
2. **视频大小**：由于浏览器内存限制，建议使用 200MB 以下的视频
3. **移动端**：首次加载需要下载 FFmpeg WASM（约25MB）
4. **隐私安全**：视频文件不会上传到任何服务器
