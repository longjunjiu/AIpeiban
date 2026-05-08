# AI陪伴 V2 - 渐进式Web应用 (PWA)

这是一个渐进式Web应用，可以直接在浏览器中使用，也可以安装到手机桌面或打包成APK。

## 功能特性

- 💬 文字对话
- 🎤 语音交互（语音输入和语音回复）
- 👤 人格档案管理
- 🤖 多种AI模型支持
- 📱 支持手机和平板

## 本地运行

```bash
# 安装依赖
pip install -r requirements.txt

# 启动语音版应用
python app_v2.py

# 或启动基础版应用
python app.py
```

## 手机端使用

### 方法1：直接访问
1. 在电脑上启动服务: `python app_v2.py --share`
2. 用手机浏览器访问生成的链接
3. 可以添加到手机桌面（Web App）

### 方法2：打包成APK

使用 [Capacitor](https://capacitorjs.com/) 打包：

```bash
# 1. 安装 Capacitor CLI
npm install -g @capacitor/core @capacitor/cli

# 2. 创建 web 构建
mkdir -p www
# 将 app_v2.py 的功能迁移到 web 目录

# 3. 初始化 Capacitor
npx cap init "AI陪伴" "org.aipeiban.app"

# 4. 添加 Android 平台
npx cap add android

# 5. 构建并同步
npx cap copy android
npx cap sync android

# 6. 打开 Android Studio 构建 APK
npx cap open android
```

## 部署到服务器

```bash
# 使用 gunicorn
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:7860 app_v2:demo

# 或使用 Docker
docker build -t aipeiban .
docker run -p 7860:7860 aipeiban
```

## 技术栈

- **后端**: Python + Gradio + Ollama
- **语音识别**: OpenAI Whisper
- **语音合成**: Microsoft Edge TTS
- **前端**: Gradio Web UI
- **移动端**: Capacitor

## 系统要求

- Python 3.8+
- 4GB+ 内存
- 网络连接（下载模型）或本地 Ollama

## 许可证

MIT License
