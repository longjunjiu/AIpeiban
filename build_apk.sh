#!/bin/bash

# AI陪伴 APK 打包脚本 (简化版)
# 依赖: Python 3.8+, Java JDK, Android SDK

set -e

echo "=== AI陪伴 APK 打包脚本 ==="

# 检查依赖
command -v python3 >/dev/null 2>&1 || { echo "需要 Python 3"; exit 1; }
command -v java >/dev/null 2>&1 || { echo "需要 Java JDK"; exit 1; }

# 创建临时目录
BUILD_DIR=$(mktemp -d)
cd "$BUILD_DIR"

echo "创建构建目录: $BUILD_DIR"

# 下载 Android SDK command line tools
if [ ! -d "cmdline-tools" ]; then
    echo "下载 Android SDK..."
    wget -q "https://dl.google.com/android/repository/commandlinetools-linux-11076708_latest.zip" -O cmdline-tools.zip
    unzip -q cmdline-tools.zip
    mkdir -p cmdline-tools/latest
    mv cmdline-tools/* cmdline-tools/latest/ 2>/dev/null || true
    rm cmdline-tools.zip
fi

export ANDROID_HOME="$BUILD_DIR/android-sdk"
export PATH="$ANDROID_HOME/cmdline-tools/latest/bin:$PATH"

# 安装 Android SDK 组件
echo "安装 Android SDK 组件..."
yes | sdkmanager --licenses > /dev/null 2>&1 || true
sdkmanager "platforms;android-33" "build-tools;30.0.3" "platform-tools" > /dev/null

# 复制项目文件
echo "复制项目文件..."
cp -r /workspace/AIpeiban "$BUILD_DIR/aipeiban"

# 创建 Gradle 项目
cd "$BUILD_DIR/aipeiban"

cat > settings.gradle << 'EOF'
rootProject.name = "AIpeiban"
include ':app'
EOF

cat > build.gradle << 'EOF'
buildscript {
    repositories {
        google()
        mavenCentral()
    }
    dependencies {
        classpath 'com.android.tools.build:gradle:8.1.0'
    }
}

allprojects {
    repositories {
        google()
        mavenCentral()
    }
}

task clean(type: Delete) {
    delete rootProject.buildDir
}
EOF

mkdir -p app
cat > app/build.gradle << 'EOF'
apply plugin: 'com.android.application'

android {
    namespace 'org.aipeiban.app'
    compileSdk 33
    
    defaultConfig {
        applicationId "org.aipeiban.app"
        minSdk 24
        targetSdk 33
        versionCode 1
        versionName "2.0.0"
    }
    
    buildTypes {
        release {
            minifyEnabled false
            proguardFiles getDefaultProguardFile('proguard-android-optimize.txt'), 'proguard-rules.pro'
        }
    }
    
    compileOptions {
        sourceCompatibility JavaVersion.VERSION_1_8
        targetCompatibility JavaVersion.VERSION_1_8
    }
}

dependencies {
    implementation 'androidx.appcompat:appcompat:1.6.1'
    implementation 'com.google.android.material:material:1.9.0'
    implementation 'org.python:python-android:3.11'
}
EOF

cat > app/src/main/AndroidManifest.xml << 'EOF'
<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    package="org.aipeiban.app">
    
    <uses-permission android:name="android.permission.INTERNET"/>
    <uses-permission android:name="android.permission.RECORD_AUDIO"/>
    <uses-permission android:name="android.permission.WRITE_EXTERNAL_STORAGE"/>
    
    <application
        android:allowBackup="true"
        android:label="AI陪伴"
        android:icon="@mipmap/ic_launcher"
        android:theme="@style/Theme.AppCompat.Light.DarkActionBar">
        
        <activity
            android:name=".MainActivity"
            android:exported="true">
            <intent-filter>
                <action android:name="android.intent.action.MAIN"/>
                <category android:name="android.intent.category.LAUNCHER"/>
            </intent-filter>
        </activity>
    </application>
</manifest>
EOF

mkdir -p app/src/main/java/org/aipeiban/app
cat > app/src/main/java/org/aipeiban/app/MainActivity.java << 'EOF'
package org.aipeiban.app;

import android.os.Bundle;
import android.webkit.WebView;
import android.webkit.WebSettings;
import android.webkit.WebViewClient;
import androidx.appcompat.app.AppCompatActivity;

public class MainActivity extends AppCompatActivity {
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        
        WebView webView = new WebView(this);
        setContentView(webView);
        
        WebSettings settings = webView.getSettings();
        settings.setJavaScriptEnabled(true);
        settings.setDomStorageEnabled(true);
        settings.setMediaPlaybackRequiresUserGesture(false);
        
        webView.setWebViewClient(new WebViewClient());
        
        // 加载本地HTML文件或远程服务
        webView.loadUrl("file:///android_asset/index.html");
    }
}
EOF

# 复制Web文件
mkdir -p app/src/main/assets
cp www/index.html app/src/main/assets/
cp -r skills app/src/main/assets/

# 创建 APK
echo "构建 APK..."
./gradlew assembleDebug

# 复制 APK
APK_PATH="$BUILD_DIR/aipeiban/app/build/outputs/apk/debug/app-debug.apk"
if [ -f "$APK_PATH" ]; then
    cp "$APK_PATH" /workspace/AIpeiban/aipeiban-v2.apk
    echo "=== 构建成功 ==="
    echo "APK 位置: /workspace/AIpeiban/aipeiban-v2.apk"
else
    echo "构建失败"
    exit 1
fi

# 清理
rm -rf "$BUILD_DIR"
