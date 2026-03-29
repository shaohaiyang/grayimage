# 图片灰度化 - Android 应用

一个简单的图片灰度化处理应用，支持选择图片、转换为灰度图、保存结果。

## 功能
- 选择图片（支持 PNG, JPG, WEBP, BMP 等格式）
- 显示原图和灰度图对比
- 保存灰度图到手机

## 技术栈
- Kivy - Python 跨平台 UI 框架
- PIL - 图片处理
- Plyer - 文件选择器

## 本地开发

```bash
# 安装依赖
pip install kivy pillow plyer

# 运行应用
python main.py
```

## 打包 Android APK

### 方式 1: GitHub Actions (推荐)
1. 创建 GitHub 仓库，上传代码
2. 推送代码后，GitHub Actions 会自动构建
3. 在 Actions 页面下载 APK

### 方式 2: 本地打包
```bash
pip install buildozer cython
buildozer android debug
```

## 项目文件
- `main.py` - 应用主代码
- `buildozer.spec` - 打包配置
- `.github/workflows/android.yml` - GitHub Actions 配置
