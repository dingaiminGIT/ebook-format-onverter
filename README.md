# 电子书格式转换器

一个支持多种电子书格式转换的Web应用，支持TXT、EPUB、PDF等格式之间的相互转换。

## ✨ 功能特性

- 📁 支持拖拽上传文件
- 🔄 TXT → EPUB 转换
- 📄 EPUB → PDF 转换
- 🎨 现代化用户界面
- ⚡ 快速转换处理
- 📱 响应式设计

## 🛠️ 技术栈

### 后端
- **Python 3.8+** - 编程语言
- **FastAPI** - 现代Web框架
- **ebooklib** - EPUB处理库
- **reportlab** - PDF生成库
- **python-multipart** - 文件上传支持

### 前端
- **React 18** - 用户界面框架
- **TypeScript** - 类型安全的JavaScript
- **Ant Design** - 企业级UI组件库
- **Axios** - HTTP客户端

## 📁 项目结构

```
ebook-format-converter/
├── .claude/                # Claude配置文件
├── backend/                # 后端代码
│   ├── app/
│   │   ├── main.py         # FastAPI应用入口
│   │   ├── models/         # 数据模型
│   │   ├── routers/        # API路由
│   │   ├── services/       # 转换服务
│   │   └── utils/          # 工具函数
│   ├── requirements.txt    # Python依赖
│   ├── venv/              # Python虚拟环境
│   └── uploads/           # 临时文件存储
├── frontend/               # 前端代码
│   ├── public/            # 静态资源
│   ├── src/               # React源码
│   │   ├── components/    # React组件
│   │   ├── services/      # API调用
│   │   ├── types/         # TypeScript类型
│   │   └── App.tsx        # 主应用组件
│   ├── package.json       # 前端依赖配置
│   ├── tsconfig.json      # TypeScript配置
│   └── .gitignore         # Git忽略文件
├── start_backend.sh        # 后端启动脚本
├── start_frontend.sh       # 前端启动脚本
├── test_sample.txt         # 测试文件
└── README.md              # 项目说明文档
```

## 🔄 支持的转换格式

| 源格式 | 目标格式 | 状态 | 描述 |
|--------|----------|------|------|
| TXT | EPUB | ✅ | 文本文件转电子书格式 |
| EPUB | PDF | ✅ | 电子书转PDF文档 |
| 更多格式 | - | 🚧 | 开发中... |

## 🚀 快速开始

### 方式一：使用启动脚本（推荐）

1. **启动后端服务**
   ```bash
   ./start_backend.sh
   ```

2. **启动前端服务**（新开终端）
   ```bash
   ./start_frontend.sh
   ```

### 方式二：手动启动

#### 启动后端
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### 启动前端
```bash
cd frontend
npm install
npm start
```

### 访问应用

- **前端界面**: http://localhost:3000
- **后端API**: http://localhost:8000
- **API文档**: http://localhost:8000/docs

## 📖 使用说明

1. 打开浏览器访问 http://localhost:3000
2. 拖拽或点击选择要转换的文件（支持 .txt, .epub, .pdf）
3. 选择目标格式
4. 填写书籍信息（可选）
5. 点击"开始转换"
6. 转换完成后点击下载按钮获取文件

## 🧪 测试

项目包含一个测试文件 `test_sample.txt`，可用于测试 TXT → EPUB 转换功能。

## 📝 API接口

### 主要端点

- `POST /api/v1/convert` - 文件转换
- `GET /api/v1/download/{filename}` - 文件下载
- `GET /api/v1/formats` - 获取支持的格式

详细API文档请访问: http://localhost:8000/docs

## 🔧 开发说明

### 环境要求

- Python 3.8+
- Node.js 16+
- npm 或 yarn

### 开发模式

后端开发服务器会在文件变更时自动重载，前端支持热更新。

## 📄 许可证

MIT License

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

---

**享受电子书格式转换的便利！** 🎉