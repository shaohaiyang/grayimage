"""
图片灰度化应用 - Material Design 界面
支持多平台，优化的移动端竖屏体验
现代化轻量设计风格
"""

import sys
import os
import tempfile
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.image import Image as KivyImage
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.core.window import Window
from PIL import Image
from datetime import datetime

import platform
from kivy.utils import platform as kivy_platform

# KivyMD imports
from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDRaisedButton, MDFloatingActionButton
from kivymd.uix.label import MDLabel
from kivymd.uix.card import MDCard
from kivymd.uix.tab import MDTabs, MDTabsBase
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.theming import ThemableBehavior
from kivy.properties import ObjectProperty
from kivymd.uix.screen import MDScreen
from kivymd.icon_definitions import md_icons
from kivymd.uix.behaviors import TouchBehavior
from kivy.animation import Animation

SYSTEM = platform.system()


# 中文字体配置
def get_chinese_font():
    """获取适合当前平台的中文字体"""
    if SYSTEM == "Darwin":
        # macOS 优先使用系统字体
        fonts = [
            "/System/Library/Fonts/PingFang.ttc",
            "/System/Library/FontsFonts.STHeiti Medium.ttc",
            "/System/Library/Fonts/Hiragino Sans GB.ttc",
            "/System/Library/Fonts/STHeiti Light.ttc"
        ]
        for font in fonts:
            if os.path.exists(font):
                return font
    elif SYSTEM == "Windows":
        return "simsun.ttc"
    elif is_android():
        return "DroidSansFallback"
    return "DroidSansFallback"

# 立即获取字体路径
CHINESE_FONT = get_chinese_font()

def is_android():
    """检测是否运行在 Android 平台"""
    return kivy_platform == "android"


def get_platform():
    """获取当前平台名称"""
    if is_android():
        return "android"
    elif SYSTEM == "Darwin":
        return "macos"
    elif SYSTEM == "Windows":
        return "windows"
    else:
        return "linux"


def get_app_title():
    """获取平台特定的应用标题"""
    platform_name = get_platform()
    if platform_name == "android":
        return "图片灰度化"
    elif platform_name == "macos":
        return "图片灰度化 (macOS版)"
    elif platform_name == "windows":
        return "图片灰度化 (Windows版)"
    elif platform_name == "linux":
        return "图片灰度化 (Linux版)"
    else:
        return "图片灰度化"


IMAGE_EXTS = {
    ".png", ".jpg", ".jpeg", ".bmp", ".gif", ".webp",
    ".PNG", ".JPG", ".JPEG", ".BMP", ".GIF", ".WEBP",
}


def get_font_name():
    """获取注册的中文字体名称 - 优先使用已注册的中文字体"""
    from kivy.core.text import LabelBase

    # 如果中文字体已注册，直接使用
    if 'ChineseFont' in LabelBase._fonts:
        return 'ChineseFont'

    # 如果没有注册，尝试注册
    if CHINESE_FONT and os.path.exists(CHINESE_FONT):
        try:
            LabelBase.register(name='ChineseFont', fn_regular=CHINESE_FONT)
            print(f"✓ 中文字体已注册: {CHINESE_FONT}")
            return 'ChineseFont'
        except Exception as e:
            print(f"✗ 字体注册失败: {e}")

    # 都失败则返回默认字体
    return 'Roboto'


def register_chinese_font():
    """注册中文字体到Kivy"""
    from kivy.core.text import LabelBase
    if CHINESE_FONT and os.path.exists(CHINESE_FONT):
        try:
            LabelBase.register(name='ChineseFont', fn_regular=CHINESE_FONT)
            print(f"✓ 中文字体已注册: {CHINESE_FONT}")
            return 'ChineseFont'
        except Exception as e:
            print(f"✗ 字体注册失败: {e}")
            return 'Roboto'
    return 'Roboto'


class Tab(BoxLayout, MDTabsBase):
    '''选项卡内容类'''
    pass


class FileBrowserPopup(Popup):
    def __init__(self, callback, **kwargs):
        super().__init__(**kwargs)
        self.callback = callback

        # 根据平台设置正确的默认路径
        if is_android():
            try:
                from plyer import storagepath

                # 优先级：Downloads > Pictures > 应用缓存 > 外部存储
                downloads_dir = storagepath.get_downloads_dir()
                if downloads_dir and os.path.exists(downloads_dir):
                    self.current_path = downloads_dir
                else:
                    pictures_dir = storagepath.get_pictures_dir()
                    if pictures_dir and os.path.exists(pictures_dir):
                        self.current_path = pictures_dir
                    else:
                        # 备选：使用应用缓存目录
                        try:
                            from jnius import autoclass
                            from android import mActivity

                            Context = autoclass("android.content.Context")
                            context = mActivity.getApplicationContext()
                            cache_dir = context.getCacheDir().getAbsolutePath()
                            self.current_path = cache_dir
                        except:
                            # 最后备选：使用外部存储根目录
                            external_dir = storagepath.get_external_storage_dir()
                            self.current_path = external_dir if external_dir else "/sdcard"
            except:
                # 如果 plyer 不可用，使用默认 Android 路径
                self.current_path = "/sdcard"
        else:
            # macOS/Linux 使用 Pictures 目录
            self.current_path = os.path.expanduser("~/Pictures")

        self.build()

    def build(self):
        self.title = "选择图片"
        self.title_font = get_font_name()
        self.title_size = "18sp"
        self.size_hint = (0.9, 0.9)
        self.auto_dismiss = False

        layout = BoxLayout(orientation="vertical", padding=10, spacing=10)

        path_layout = BoxLayout(size_hint_y=None, height=35, spacing=5)

        # 根据平台定义不同的快捷路径
        if is_android():
            # Android 平台路径
            quick_paths = [
                ("根目录", "/sdcard"),
                ("下载", "/sdcard/Download"),
                ("图片", "/sdcard/Pictures"),
            ]
        else:
            # macOS/Linux 平台路径
            quick_paths = [
                ("Home", "~"),
                ("图片", "~/Pictures"),
                ("桌面", "~/Desktop"),
            ]

        for name, path in quick_paths:
            btn = Button(
                text=name, font_name=get_font_name(), font_size="11sp", size_hint_x=0.2
            )
            btn.bind(on_press=lambda x, p=path: self.go_to_path(p))
            path_layout.add_widget(btn)

        layout.add_widget(path_layout)

        scroll = ScrollView(size_hint_y=1)
        self.file_grid = GridLayout(cols=1, size_hint_y=None, padding=5, spacing=3)
        self.file_grid.bind(minimum_height=self.file_grid.setter("height"))
        scroll.add_widget(self.file_grid)
        layout.add_widget(scroll)

        btn_layout = BoxLayout(size_hint_y=None, height=40, spacing=10)

        cancel_btn = Button(text="取消", font_name=get_font_name(), font_size="14sp")
        select_btn = Button(
            text="选择",
            font_name=get_font_name(),
            font_size="14sp",
            background_color=(0.6, 0.75, 0.9, 1),
        )

        cancel_btn.bind(on_press=self.dismiss)
        select_btn.bind(on_press=lambda x: self.select_current())

        btn_layout.add_widget(cancel_btn)
        btn_layout.add_widget(select_btn)

        layout.add_widget(btn_layout)

        self.content = layout
        self.refresh_files()

    def go_to_path(self, path):
        if is_android():
            # Android 直接使用路径（不展开 ~）
            self.current_path = path
        else:
            # macOS/Linux 使用 expanduser 展开 ~
            self.current_path = os.path.expanduser(path)
        self.refresh_files()

    def refresh_files(self, *args):
        self.file_grid.clear_widgets()

        if not os.path.isdir(self.current_path):
            return

        # 根据平台判断是否在根目录
        if is_android():
            root_path = "/sdcard"
        else:
            root_path = os.path.expanduser("~")

        if self.current_path != root_path:
            parent = os.path.dirname(self.current_path)
            btn = Button(
                text=".. 返回上级",
                font_name=get_font_name(),
                font_size="13sp",
                size_hint_y=None,
                height=35,
                background_color=(0.85, 0.85, 0.9, 1),
            )
            btn.bind(on_press=lambda x, p=parent: self.go_to_path(p))
            self.file_grid.add_widget(btn)

        try:
            items = os.listdir(self.current_path)
        except:
            return

        dirs = []
        files = []

        for item in sorted(items):
            if item.startswith("."):
                continue
            full_path = os.path.join(self.current_path, item)
            if os.path.isdir(full_path):
                dirs.append.append((item, full_path))
            else:
                ext = os.path.splitext(item)[1]
                if ext in IMAGE_EXTS:
                    files.append((item, full_path))

        for name, path in dirs:
            btn = Button(
                text=f"📁 {name}",
                font_name=get_font_name(),
                font_size="14sp",
                size_hint_y=None,
                height=35,
                background_color=(0.8, 0.85, 0.95, 1),
                halign="left",
                text_size=(380, None),
                padding=(10, 5),
            )
            btn.bind(on_press=lambda x, p=path: self.go_to_path(p))
            self.file_grid.add_widget(btn)

        for name, path in files:
            btn = Button(
                text=f"🖼️ {name}",
                font_name=get_font_name(),
                font_size="14sp",
                size_hint_y=None,
                height=35,
                background_color=(0.95, 0.95, 0.95, 1),
                halign="left",
                text_size=(380, None),
                padding=(10, 5),
            )
            btn.bind(on_press=lambda x, p=path: self.select_file(p))
            self.file_grid.add_widget(btn)

    def select_file(self, path):
        self.callback(path)
        self.dismiss()

    def select_current(self):
        pass


class GrayImageApp(MDApp):
    '''图片灰度化应用主类'''

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # 注册中文字体
        self.chinese_font_name = register_chinese_font()

        # 现代轻量设计配色
        self.theme_cls.primary_palette = "Teal"
        self.theme_cls.theme_style = "Light"
        self.theme_cls.font_style = "Roboto"
        self.title = get_app_title()

        # 设置窗口大小（仅桌面端）
        if not is_android():
            Window.size = (375, 667)  # 模拟现代手机竖屏尺寸

        self.original_image = None
        self.gray_image = None
        self.original_path = None

    def build(self):
        '''构建UI界面'''
        self.root = MDScreen(
            md_bg_color=(0.98, 0.98, 1.0, 1.0)
        )

        # 主布局
        main_layout = MDBoxLayout(
            orientation="vertical",
            padding=0,
            spacing=0
        )

        # 1. 顶部标题栏（轻量设计）
        title_wrapper = MDBoxLayout(
            size_hint_y=None,
            height=70,
            padding=[15, 15, 15, 10],
            md_bg_color=(0.2, 0.8, 0.9, 1.0)
        )

        title_layout = MDBoxLayout(
            orientation="horizontal",
            spacing=12
        )

        title_icon = MDLabel(
            text="📷",
            font_size="28sp",
            halign="center",
            theme_text_color="Custom",
            text_color=(1, 1, 1, 1),
            size_hint_x=None,
            width=55
        )

        title_label = MDLabel(
            text=self.title,
            font_name=self.chinese_font_name,
            font_size="24sp",
            bold=False,
            theme_text_color="Custom",
            text_color=(1, 1, 1, 1),
            halign="left"
        )

        title_layout.add_widget(title_icon)
        title_layout.add_widget(title_label)
        title_wrapper.add_widget(title_layout)
        main_layout.add_widget(title_wrapper)

        # 2. 主操作按钮区域
        button_wrapper = MDBoxLayout(
            size_hint_y=None,
            height=100,
            padding=[20, 10, 20, 10]
        )

        self.select_btn = MDRaisedButton(
            text="选择图片",
            font_name=self.chinese_font_name,
            font_size="18sp",
            size_hint_y=None,
            height=60,
            elevation=6,
            md_bg_color=(0.2, 0.8, 0.9, 1.0),
            theme_text_color="Custom",
            text_color=(1, 1, 1, 1),
            ripple_color=(0.95, 0.95, 0.95, 0.3),
        )
        self.select_btn.bind(on_press=self.animate_selection)
        button_wrapper.add_widget(self.select_btn)
        main_layout.add_widget(button_wrapper)

        # 3. 状态提示区域（柔和背景）
        status_wrapper = MDBoxLayout(
            size_hint_y=None,
            height=55,
            padding=[20, 10, 20, 10]
        )

        self.status_card = MDCard(
            size_hint=(1, 1),
            elevation=0,
            md_bg_color=(0.95, 0.95, 0.97, 1.0),
            padding=15
        )

        self.status_label = MDLabel(
            text="请选择一张图片开始转换",
            font_name=self.chinese_font_name,
            font_size="15sp",
            halign="center",
            theme_text_color="Secondary",
        )

        self.status_card.add_widget(self.status_label)
        status_wrapper.add_widget(self.status_card)
        main_layout.add_widget(status_wrapper)

        # 4. 图片显示区域（选项卡）
        image_wrapper = MDBoxLayout(
            size_hint_y=1,
            padding=[20, 10, 20, 10]
        )

        image_card = MDCard(
            size_hint=(1, 1),
            elevation=3,
            md_bg_color=(1, 1, 1, 1),
            padding=10
        )

        # 创建选项卡
        self.tabs = MDTabs()
        self.tabs.default_tab = 0

        # 注册选项卡中文字体
        tab_font = self.chinese_font_name

        # 原图选项卡
        self.original_tab = Tab(title="原图")
        self.original_tab.tab_label.font_name = tab_font
        self.original_tab.tab_label.font_size = "16sp"
        self.original_tab.tab_label.theme_text_color = "Custom"
        self.original_tab.tab_label.text_color = (0.2, 0.5, 0.7, 1.0)
        self.original_img = KivyImage()
        self.original_tab.add_widget(self.original_img)

        # 灰度图选项卡
        self.gray_tab = Tab(title="灰度图")
        self.gray_tab.tab_label.font_name = tab_font
        self.gray_tab.tab_label.font_size = "16sp"
        self.gray_tab.tab_label.theme_text_color = "Custom"
        self.gray_tab.tab_label.text_color = (0.2, 0.5, 0.7, 1.0)
        self.gray_img = KivyImage()
        self.gray_tab.add_widget(self.gray_img)

        self.tabs.add_widget(self.original_tab)
        self.tabs.add_widget(self.gray_tab)

        image_card.add_widget(self.tabs)
        image_wrapper.add_widget(image_card)
        main_layout.add_widget(image_wrapper)

        # 5. 保存按钮区域
        save_wrapper = MDBoxLayout(
            size_hint_y=None,
            height=90,
            padding=[20, 10, 20, 15]
        )

        self.save_btn = MDRaisedButton(
            text="💾 保存图片",
            font_name=self.chinese_font_name,
            font_size="16sp",
            size_hint_y=None,
            height=55,
            elevation=6,
            md_bg_color=(0.2, 0.8, 0.9, 1.0),
            theme_text_color="Custom",
            text_color=(1, 1, 1, 1),
            ripple_color=(0.95, 0.95, 0.95, 0.3),
            disabled=True
        )
        self.save_btn.bind(on_press=self.save_image)
        save_wrapper.add_widget(self.save_btn)
        main_layout.add_widget(save_wrapper)

        self.root.root = main_layout

        return self.root

    def animate_selection(self, instance):
        """选择按钮点击动画效果"""
        self.status_label.text = "正在准备..."
        self.status_label.theme_text_color = "Secondary"

        # 模拟加载延迟
        from kivy.clock import Clock
        Clock.schedule_once(self.show_file_selector, 0.1)

    def show_file_selector(self, *args):
        '''显示文件选择器'''
        if is_android():
            # Android上使用plyer文件选择器
            try:
                from plyer import filechooser

                # 定义回调函数处理选择的文件（Android 是异步的）
                def on_file_selected(selection):
                    if selection and len(selection) > 0:
                        self.load_image(selection[0])

                # 使用 MIME 类型过滤，不是通配符
                filechooser.open_file(
                    title="选择图片",
                    filters=["image"],  # MIME type: image/*
                    on_selection=on_file_selected,  # Android 必须使用回调
                )
            except Exception as e:
                self.status_label.text = f"文件选择错误: {str(e)}"
                self.status_label.theme_text_color = "Error"
                import traceback
                traceback.print_exc()
        else:
            # 桌面平台使用自定义文件浏览器
            popup = FileBrowserPopup(callback=self.load_image)
            popup.open()

    def load_image(self, path):
        '''加载并处理图片'''
        try:
            self.status_label.text = "正在加载图片..."
            self.status_label.theme_text_color = "Primary"
            self.original_path = path

            img = Image.open(path)

            # 验证图片完整性
            try:
                img.verify()
                # 重新打开图片，因为 verify() 会关闭文件
                img = Image.open(path)
            except Exception as e:
                raise Exception(f"图片文件损坏或不完整: {str(e)}")

            if img.mode in ("RGBA", "P", "LA"):
                background = Image.new("RGB", img.size, (255, 255, 255))
                if img.mode == "P":
                    img = img.convert("RGBA")
                background.paste(
                    img, mask=img.split()[-1] if img.mode in ("RGBA", "LA") else None
                )
                self.original_image = background
            else:
                self.original_image = img.convert("RGB")

            # 使用正确的临时文件路径
            if is_android():
                # 使用 Android Context.getCacheDir() 获取缓存目录
                try:
                    from jnius import autoclass
                    from android import mActivity

                    Context = autoclass("android.content.Context")
                    context = mActivity.getApplicationContext()
                    cache_dir = context.getCacheDir().getAbsolutePath()
                except Exception:
                    # 备选方案：使用 plyer.storagepath
                    from plyer import storagepath

                    app_dir = storagepath.get_application_dir()
                    if app_dir:
                        cache_dir = os.path.join(app_dir, "cache")
                    else:
                        # 最后备选：使用外部存储
                        external_dir = storagepath.get_external_storage_dir()
                        if external_dir:
                            cache_dir = os.path.join(
                                external_dir, "Android/data/org.example.grayimage/cache"
                            )
                        else:
                            cache_dir = (
                                "/sdcard/Android/data/org.example.grayimage/cache"
                            )

                # 确保目录存在
                os.makedirs(cache_dir, exist_ok=True)
                save_path = os.path.join(cache_dir, "original.png")
            else:
                cache_dir = tempfile.gettempdir()
                save_path = os.path.join(cache_dir, "original.png")

            self.original_image.save(save_path)
            self.original_img.source = save_path
            self.original_img.reload()

            # 模拟处理延迟显示进度
            self.status_label.text = "正在处理图片..."
            from kivy.clock import Clock
            Clock.schedule_once(self.process_image, 0.1)

        except Exception as e:
            self.status_label.text = f"错误: {str(e)}"
            self.status_label.theme_text_color = "Error"

    def process_image(self, *args):
        '''处理图片为灰度图'''
        if self.original_image:
            self.status_label.text = "正在转换为灰度图..."
            self.status_label.theme_text_color = "Primary"

            self.gray_image = self.original_image.convert("L")

            # 使用正确的临时文件路径
            if is_android():
                # 使用 Android Context.getCacheDir() 获取缓存目录
                try:
                    from jnius import autoclass
                    from android import mActivity

                    Context = autoclass("android.content.Context")
                    context = mActivity.getApplicationContext()
                    cache_dir = context.getCacheDir().getAbsolutePath()
                except Exception:
                    # 备选方案：使用 plyer.storagepath
                    from plyer import storagepath

                    app_dir = storagepath.get_application_dir()
                    if app_dir:
                        cache_dir = os.path.join(app_dir, "cache")
                    else:
                        # 最后备选：使用外部存储
                        external_dir = storagepath.get_external_storage_dir()
                        if external_dir:
                            cache_dir = os.path.join(
                                external_dir, "Android/data/org.example.grayimage/cache"
                            )
                        else:
                            cache_dir = (
                                "/sdcard/Android/data/org.example.grayimage/cache"
                            )

                # 确保目录存在
                os.makedirs(cache_dir, exist_ok=True)
                save_path = os.path.join(cache_dir, "gray.png")
            else:
                cache_dir = tempfile.gettempdir()
                save_path = os.path.join(cache_dir, "gray.png")

            self.gray_image.save(save_path)
            self.gray_img.source = save_path
            self.gray_img.reload()

            # 完成处理
            basename = os.path.basename(self.original_path)
            self.status_label.text = f"✓ 已转换完成: {basename}"
            self.status_label.theme_text_color = "Success"
            self.save_btn.disabled = False
            self.save_btn.md_bg_color = (0.2, 0.8, 0.9, 1.0)

    def save_image(self, instance):
        '''保存灰度图片'''
        if self.gray_image:
            if is_android():
                # Android 上保存（选项 1：让用户选择保存位置）
                try:
                    from plyer import filechooser
                    from plyer import storagepath
                    from io import BytesIO

                    # 生成默认文件名
                    if self.original_path:
                        base_name = os.path.splitext(
                            os.path.basename(self.original_path)
                        )[0]
                        default_name = f"{base_name}_gray.png"
                    else:
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        default_name = f"gray_{timestamp}.png"

                    # 定义保存回调函数
                    def save_callback(file_output_stream):
                        """Android 保存回调函数"""
                        try:
                            # 将 PIL 图片保存到字节流
                            buffer = BytesIO()
                            self.gray_image.save(buffer, format="PNG")
                            file_output_stream.write(buffer.getvalue())
                            file_output_stream.close()
                            self.status_label.text = "✓ 保存成功!"
                            self.status_label.theme_text_color = "Success"
                        except Exception as e:
                            self.status_label.text = f"❌ 保存错误: {str(e)}"
                            self.status_label.theme_text_color = "Error"

                    # 尝试使用 filechooser.save_file()
                    filechooser.save_file(
                        title="保存灰度图",
                        filters=["image"],  # MIME type
                        default_name=default_name,
                        callback=save_callback,  # Android 必需
                    )

                except Exception as e:
                    # 如果 save_file() 失败（plyer bug #816），使用备选方案
                    try:
                        # 备选方案：直接保存到相册目录
                        from plyer import storagepath

                        pictures_dir = storagepath.get_pictures_dir()
                        if not pictures_dir:
                            # 尝试使用外部存储
                            external_dir = storagepath.get_external_storage_dir()
                            if external_dir:
                                pictures_dir = os.path.join(external_dir, "Pictures")

                        if pictures_dir and os.path.exists(pictures_dir):
                            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                            filename = f"gray_{timestamp}.png"
                            save_path = os.path.join(pictures_dir, filename)

                            self.gray_image.save(save_path)
                            self.status_label.text = f"✓ 已保存到相册: {filename}"
                            self.status_label.theme_text_color = "Success"
                        else:
                            self.status_label.text = "❌ 无法访问相册目录"
                            self.status_label.theme_text_color = "Error"

                    except Exception as e2:
                        self.status_label.text = f"❌ 保存失败: {str(e2)}"
                        self.status_label.theme_text_color = "Error"
                        import traceback
                        traceback.print_exc()
                # 桌面平台原逻辑
                if self.original_path:
                    default_name = (
                        os.path.splitext(os.path.basename(self.original_path))[0]
                        + "_gray.png"
                    )
                else:
                    default_name = "gray.png"

                download_path = os.path.expanduser("~/Downloads")
                final_path = os.path.join(download_path, default_name)
                try:
                    self.gray_image.save(final_path)
                    self.status_label.text = f"✓ 已保存到下载目录!"
                    self.status_label.theme_text_color = "Success"
                except Exception as e:
                    self.status_label.text = f"❌ 错误: {str(e)}"
                    self.status_label.theme_text_color = "Error"


if __name__ == "__main__":
    GrayImageApp().run()