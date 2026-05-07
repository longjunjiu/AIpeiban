# APK打包指南

本指南介绍如何将AI陪伴系统打包成Android APK文件。

## 方法一：使用Buildozer（推荐）

### 环境要求

- Ubuntu/Debian Linux（推荐）或 macOS
- Python 3.6+
- 足够的磁盘空间（至少10GB）

### 安装步骤

#### 1. 安装依赖

```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装依赖
sudo apt install -y git python3-pip python3-dev build-essential \
    openjdk-17-jdk unzip ant ccache libncurses5:i386 libstdc++6:i386 \
    libgtk2.0-0:i386 libpangox-1.0-0:i386 libpangoxft-1.0-0:i386 \
    libidn11:i386 python3-setuptools

# 安装Buildozer
pip3 install buildozer
```

#### 2. 克隆项目

```bash
git clone https://github.com/longjunjiu/AIpeiban.git
cd AIpeiban
```

#### 3. 准备资源文件

创建必要的图标和启动画面：

```bash
mkdir -p res
```

你需要准备以下文件：
- `res/icon.png` - 应用图标（512x512）
- `res/adaptive_icon.png` - 自适应图标
- `res/splash.png` - 启动画面

#### 4. 构建APK

```bash
# 首次构建（会自动下载NDK/SDK等依赖）
buildozer android debug deploy run

# 或者只构建不部署
buildozer android debug
```

构建完成后，APK文件会在 `bin/` 目录下生成。

### 构建选项

```bash
# 构建release版本
buildozer android release

# 构建并安装到设备
buildozer android debug deploy run

# 清理构建缓存
buildozer android clean

# 查看构建日志
buildozer android logcat
```

## 方法二：使用Docker（更简单）

使用预配置的Docker镜像来构建：

```bash
# 拉取镜像
docker pull kivy/buildozer

# 运行构建
docker run -v $(pwd):/home/user/hostcwd kivy/buildozer buildozer android debug
```

## 方法三：使用GitHub Actions（CI/CD）

创建 `.github/workflows/build-apk.yml` 文件：

```yaml
name: Build APK

on:
  push:
    branches: [ main ]

jobs:
  build:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'
    
    - name: Install dependencies
      run: |
        sudo apt update
        sudo apt install -y openjdk-17-jdk ant
        pip install buildozer
    
    - name: Build APK
      run: buildozer android debug
    
    - name: Upload APK
      uses: actions/upload-artifact@v3
      with:
        name: aipeiban.apk
        path: bin/*.apk
```

## 常见问题

### 内存不足

```bash
# 增加swap空间
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

### NDK版本问题

编辑 `buildozer.spec` 文件：

```ini
android.ndk = 25b
```

### 构建时间过长

首次构建会下载大量依赖，可能需要30分钟以上，请耐心等待。

## 生成的APK

构建成功后，你会得到：
- `bin/aipeiban-0.1.0-debug.apk` - 调试版本
- `bin/aipeiban-0.1.0-release-unsigned.apk` - 未签名的发布版本

## 签名发布版本

```bash
# 生成密钥库
keytool -genkey -v -keystore my-release-key.keystore \
    -alias aipeiban -keyalg RSA -keysize 2048 -validity 10000

# 签名APK
jarsigner -verbose -sigalg SHA1withRSA -digestalg SHA1 \
    -keystore my-release-key.keystore \
    bin/aipeiban-0.1.0-release-unsigned.apk aipeiban

# 优化APK
zipalign -v 4 bin/aipeiban-0.1.0-release-unsigned.apk \
    bin/aipeiban-0.1.0-release.apk
```

## 测试APK

```bash
# 安装到设备
adb install bin/aipeiban-0.1.0-debug.apk

# 启动应用
adb shell am start -n org.aipeiban.aipeiban/org.aipeiban.aipeiban.AICompanionApp

# 查看日志
adb logcat | grep python
```

## 注意事项

1. 首次构建需要下载大量依赖，请确保网络畅通
2. 建议使用Linux环境进行构建
3. 构建过程可能需要较长时间，请耐心等待
4. 生成的APK文件较大（约100MB+），包含Python运行时和依赖库

## 参考链接

- [Buildozer文档](https://buildozer.readthedocs.io/)
- [Kivy官方文档](https://kivy.org/doc/stable/)
- [Android开发者指南](https://developer.android.com/)
