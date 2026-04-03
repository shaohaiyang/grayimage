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
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.uix.image import Image as KivyImage
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.core.window import Window
from PIL import Image, ImageEnhance, ImageFilter
from datetime import datetime

import platform
from kivy.utils import platform as kivy_platform

# KivyMD imports
from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDRaisedButton, MDFloatingActionButton
from kivymd.uix.label import MDLabel, MDIcon
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


def get_chinese_font():
    """获取适合当前平台的中文字体"""
    if SYSTEM == "Darwin":
        fonts = [
            "/System/Library/Fonts/PingFang.ttc",
            "/System/Library/Fonts/STHeiti Medium.ttc",
            "/System/Library/Fonts/Hiragino Sans GB.ttc",
        ]
        for font in fonts:
            if os.path.exists(font):
                return font
    elif SYSTEM == "Windows":
        return "simsun.ttc"
    return "DroidSansFallback"

def register_chinese_font():
    """注册中文字体到Kivy - 简化版本"""
    from kivy.core.text import LabelBase
    
    if is_android():
        try:
            LabelBase.register(
                name='Chinese',
                fn_regular='/system/fonts/DroidSansFallback.ttf'
            )
            return 'Chinese'
        except:
            return 'Roboto'
    else:
        font_path = get_chinese_font()
        if font_path and os.path.exists(font_path):
            try:
                LabelBase.register(name='Chinese', fn_regular=font_path)
                return 'Chinese'
            except:
                return 'Roboto'
        return 'Roboto'

def get_font_name():
    """获取已注册的中文字体名称"""
    from kivy.core.text import LabelBase
    
    if 'Chinese' in LabelBase._fonts:
        return 'Chinese'
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

                downloads_dir = storagepath.get_downloads_dir()
                if downloads_dir and os.path.exists(downloads_dir):
                    self.current_path = downloads_dir
                else:
                    pictures_dir = storagepath.get_pictures_dir()
                    if pictures_dir and os.path.exists(pictures_dir):
                        self.current_path = pictures_dir
                    else:
                        try:
                            from jnius import autoclass
                            PythonActivity = autoclass('org.kivy.android.PythonActivity')
                            activity = PythonActivity.mActivity
                            context = activity.getApplicationContext()
                            cache_dir = context.getCacheDir().getAbsolutePath()
                            self.current_path = cache_dir
                        except Exception:
                            external_dir = storagepath.get_external_storage_dir()
                            self.current_path = external_dir if external_dir else "/sdcard"
            except Exception:
                self.current_path = "/sdcard"
        else:
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
                dirs.append((item, full_path))
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
        self.enhanced_image = None
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

        title_icon = MDIcon(
            icon="camera",
            font_size="28sp",
            halign="center",
            size_hint_x=None,
            width=55,
            theme_text_color="Custom",
            text_color=(1, 1, 1, 1)
        )

        title_label = Label(
            text=self.title,
            font_name=self.chinese_font_name,
            font_size="24sp",
            bold=False,
            halign="left",
            color=(1, 1, 1, 1)
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

        self.select_btn = Button(
            text="选择图片",
            font_name=self.chinese_font_name,
            font_size="18sp",
            size_hint_y=None,
            height=60,
            background_color=(0.2, 0.8, 0.9, 1.0),
            color=(1, 1, 1, 1),
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

        self.status_label = Label(
            text="请选择一张图片开始转换",
            font_name=self.chinese_font_name,
            font_size="15sp",
            halign="center",
            color=(0.5, 0.5, 0.5, 1),
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

        # 创建选项卡 - 设置中文字体
        self.tabs = MDTabs(font_name=self.chinese_font_name)
        self.tabs.default_tab = 0

        # 原图选项卡
        self.original_tab = Tab(title="原图")
        self.original_tab.tab_label.font_size = "16sp"
        self.original_tab.tab_label.theme_text_color = "Primary"
        
        # 创建柔和背景的占位符（使用 FloatLayout 防止图片覆盖背景）
        original_placeholder = MDFloatLayout(
            md_bg_color=(0.95, 0.97, 0.99, 1.0)
        )
        
        original_placeholder_label = Label(
            text='图片展示区\n请选择一张图片',
            font_name=self.chinese_font_name,
            font_size='18sp',
            halign='center',
            color=(0.6, 0.65, 0.7, 1.0),
            text_size=(None, None),
            pos_hint={'center_x': 0.5, 'center_y': 0.5},
            size_hint=(None, None),
            size=(300, 100)
        )
        
        original_placeholder.add_widget(original_placeholder_label)
        
        # 创建实际的图片组件（初始隐藏）
        self.original_img = KivyImage(
            opacity=0,
            allow_stretch=True,
            keep_ratio=True,
            pos_hint={'center_x': 0.5, 'center_y': 0.5}
        )
        
        original_placeholder.add_widget(self.original_img)
        self.original_tab.add_widget(original_placeholder)
        self.original_placeholder = original_placeholder

        # 灰度图选项卡
        self.gray_tab = Tab(title="灰度图")
        self.gray_tab.tab_label.font_size = "16sp"
        self.gray_tab.tab_label.theme_text_color = "Primary"
        
        # 创建柔和背景的占位符（使用 FloatLayout 防止图片覆盖背景）
        gray_placeholder = MDFloatLayout(
            md_bg_color=(0.95, 0.97, 0.99, 1.0)
        )
        
        gray_placeholder_label = Label(
            text='灰度图展示区\n点击下方按钮转换',
            font_name=self.chinese_font_name,
            font_size='18sp',
            halign='center',
            color=(0.6, 0.65, 0.7, 1.0),
            text_size=(None, None),
            pos_hint={'center_x': 0.5, 'center_y': 0.5},
            size_hint=(None, None),
            size=(300, 100)
        )
        
        gray_placeholder.add_widget(gray_placeholder_label)
        
        # 创建实际的图片组件（初始隐藏）
        self.gray_img = KivyImage(
            opacity=0,
            allow_stretch=True,
            keep_ratio=True,
            pos_hint={'center_x': 0.5, 'center_y': 0.5}
        )
        
        gray_placeholder.add_widget(self.gray_img)
        self.gray_tab.add_widget(gray_placeholder)
        self.gray_placeholder = gray_placeholder

        # 美化图选项卡
        self.enhanced_tab = Tab(title="美化图")
        self.enhanced_tab.tab_label.font_size = "16sp"
        self.enhanced_tab.tab_label.theme_text_color = "Primary"
        
        # 创建柔和背景的占位符（使用 FloatLayout 防止图片覆盖背景）
        enhanced_placeholder = MDFloatLayout(
            md_bg_color=(0.95, 0.97, 0.99, 1.0)
        )
        
        enhanced_placeholder_label = Label(
            text='美化图展示区\n点击下方按钮美化',
            font_name=self.chinese_font_name,
            font_size='18sp',
            halign='center',
            color=(0.6, 0.65, 0.7, 1.0),
            text_size=(None, None),
            pos_hint={'center_x': 0.5, 'center_y': 0.5},
            size_hint=(None, None),
            size=(300, 100)
        )
        
        enhanced_placeholder.add_widget(enhanced_placeholder_label)
        
        # 创建实际的图片组件（初始隐藏）
        self.enhanced_img = KivyImage(
            opacity=0,
            allow_stretch=True,
            keep_ratio=True,
            pos_hint={'center_x': 0.5, 'center_y': 0.5}
        )
        
        enhanced_placeholder.add_widget(self.enhanced_img)
        self.enhanced_tab.add_widget(enhanced_placeholder)
        self.enhanced_placeholder = enhanced_placeholder

        self.tabs.add_widget(self.original_tab)
        self.tabs.add_widget(self.gray_tab)
        self.tabs.add_widget(self.enhanced_tab)
        
        # 绑定 Tab 切换事件
        self.tabs.bind(on_tab_switch=self.on_tab_switch)

        image_card.add_widget(self.tabs)
        image_wrapper.add_widget(image_card)
        main_layout.add_widget(image_wrapper)

        # 5. 美化和保存按钮区域
        action_wrapper = MDBoxLayout(
            size_hint_y=None,
            height=90,
            padding=[20, 10, 20, 15]
        )

        action_layout = MDBoxLayout(
            orientation='horizontal',
            spacing=10
        )

        self.action_btn = Button(
            text="一键灰度",
            font_name=self.chinese_font_name,
            font_size="16sp",
            size_hint_x=0.5,
            height=55,
            background_color=(0.3, 0.8, 0.7, 1.0),
            color=(1, 1, 1, 1),
            disabled=True
        )
        self.action_btn.bind(on_press=self.on_action_button_click)
        action_layout.add_widget(self.action_btn)

        self.save_btn = Button(
            text="保存图片",
            font_name=self.chinese_font_name,
            font_size="16sp",
            size_hint_x=0.5,
            height=55,
            background_color=(0.2, 0.8, 0.9, 1.0),
            color=(1, 1, 1, 1),
            disabled=True
        )
        self.save_btn.bind(on_press=self.save_image)
        action_layout.add_widget(self.save_btn)

        action_wrapper.add_widget(action_layout)
        main_layout.add_widget(action_wrapper)

        self.root.add_widget(main_layout)

        return self.root

    def on_tab_switch(self, instance_tabs, instance_tab, instance_tab_label, tab_text):
        '''Tab 切换事件回调'''
        if self.original_image is None:
            # 如果没有加载图片，禁用按钮
            self.action_btn.disabled = True
            return
        
        # 根据当前 Tab 修改按钮文字
        if tab_text == "灰度图":
            self.action_btn.text = "一键灰度"
            self.action_btn.background_color = (0.3, 0.8, 0.7, 1.0)
        elif tab_text == "美化图":
            self.action_btn.text = "一键美化"
            self.action_btn.background_color = (0.7, 0.5, 0.9, 1.0)
        else:  # 原图
            self.action_btn.text = "原图模式"
            self.action_btn.background_color = (0.5, 0.7, 0.9, 1.0)
        
        # 检查是否已经处理过，决定是否启用按钮
        if tab_text == "灰度图" and self.gray_image is not None:
            self.action_btn.disabled = False
        elif tab_text == "美化图" and self.enhanced_image is not None:
            self.action_btn.disabled = False
        else:
            self.action_btn.disabled = False

    def on_action_button_click(self, instance):
        '''操作按钮点击事件'''
        current_tab_text = ""
        
        # 使用 MDTabs 的 get_current_tab 方法获取当前选项卡
        current_tab = self.tabs.get_current_tab()
        
        # 从当前选项卡获取标题
        if current_tab:
            current_tab_text = current_tab.title
        
        # 根据当前 Tab 执行相应操作
        if current_tab_text == "灰度图":
            self.process_gray()
        elif current_tab_text == "美化图":
            self.enhance_image(instance)

    def animate_selection(self, instance):
        """选择按钮点击动画效果"""
        self.status_label.text = "正在准备..."

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
                        from kivy.clock import Clock
                        Clock.schedule_once(lambda dt: self.load_image(selection[0]), 0)

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
            self.original_path = path
            
            # 确保使用绝对路径
            if not os.path.isabs(path):
                path = os.path.abspath(path)

            # 隐藏占位符标签，显示图片组件
            self.original_img.opacity = 1
            
            # 直接使用原图路径设置 Image 组件（参考 kivy_mobile_image）
            self.original_img.source = path
            self.original_img.reload()

            # 用 PIL 打开图片用于后续处理
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

            # 完成加载，启用操作按钮
            basename = os.path.basename(self.original_path)
            self.status_label.text = f"✓ 已加载: {basename}"
            self.action_btn.disabled = False

        except Exception as e:
            self.status_label.text = f"错误: {str(e)}"

    def process_gray(self):
        '''处理图片为灰度图'''
        if self.original_image is None:
            self.status_label.text = "请先选择图片"
            return
            
        if self.gray_image is not None:
            # 已经处理过了
            self.status_label.text = "已经转换为灰度图"
            return
        
        try:
            self.status_label.text = "正在转换为灰度图..."

            self.gray_image = self.original_image.convert("L")

            # 保存到临时文件并显示
            temp_path = 'temp_gray.png'
            self.gray_image.save(temp_path)
            
            # 显示灰度图组件
            self.gray_img.opacity = 1
            self.gray_img.source = temp_path
            self.gray_img.reload()

            # 完成处理，启用保存按钮
            basename = os.path.basename(self.original_path)
            self.status_label.text = f"✓ 已转换为灰度图: {basename}"
            self.save_btn.disabled = False
        except Exception as e:
            self.status_label.text = f"灰度转换错误: {str(e)}"

    def enhance_image(self, instance):
        '''一键美化图片'''
        if self.original_image is None:
            self.status_label.text = "请先选择图片"
            return
            
        if self.enhanced_image is not None:
            # 已经处理过了
            self.status_label.text = "已经美化过图片"
            return

        try:
            self.status_label.text = "正在美化图片..."
            from kivy.clock import Clock
            Clock.schedule_once(self._do_enhance_image, 0.1)
        except Exception as e:
            self.status_label.text = f"美化错误: {str(e)}"

    def _do_enhance_image(self, *args):
        '''执行图片美化（在时钟回调中）'''
        try:
            # 复制原图进行美化
            image = self.original_image.copy()
            
            # 对比度增强 1.2x
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(1.2)
            
            # 亮度调整 1.1x
            enhancer = ImageEnhance.Brightness(image)
            image = enhancer.enhance(1.1)
            
            # 色彩增强 1.15x
            enhancer = ImageEnhance.Color(image)
            image = enhancer.enhance(1.15)
            
            # 锐度增强 1.3x
            enhancer = ImageEnhance.Sharpness(image)
            image = enhancer.enhance(1.3)
            
            self.enhanced_image = image
            
            # 保存到临时文件并显示
            temp_path = 'temp_enhanced.png'
            self.enhanced_image.save(temp_path)
            
            # 显示美化图组件
            self.enhanced_img.opacity = 1
            self.enhanced_img.source = temp_path
            self.enhanced_img.reload()
            
            # 完成美化
            basename = os.path.basename(self.original_path)
            self.status_label.text = f"✓ 美化完成: {basename}"
            
        except Exception as e:
            self.status_label.text = f"美化失败: {str(e)}"

    def save_image(self, instance):
        '''保存灰度图片或美化图片'''
        # 获取当前激活的 Tab
        current_tab = self.tabs.get_current_tab()
        if not current_tab:
            self.status_label.text = "❌ 无法确定当前 Tab"
            return
        
        tab_text = current_tab.title
        
        # 根据当前 Tab 决定保存哪个图片
        image_to_save = None
        image_type = ""
        
        if tab_text == "灰度图":
            image_to_save = self.gray_image
            image_type = "灰度图"
        elif tab_text == "美化图":
            image_to_save = self.enhanced_image
            image_type = "美化图"
        else:
            self.status_label.text = "❌ 原图无需保存"
            return
        
        if image_to_save is None:
            self.status_label.text = f"❌ 没有{image_type}可保存，请先处理"
            return
        
        if is_android():
            try:
                from plyer import filechooser
                from plyer import storagepath
                from io import BytesIO

                if self.original_path:
                    base_name = os.path.splitext(
                        os.path.basename(self.original_path)
                    )[0]
                    default_name = f"{base_name}_{image_type}.png"
                else:
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    default_name = f"{image_type}_{timestamp}.png"

                def save_callback(file_output_stream):
                    """Android 保存回调函数"""
                    from kivy.clock import Clock
                    
                    def do_save(dt):
                        try:
                            buffer = BytesIO()
                            image_to_save.save(buffer, format="PNG")
                            file_output_stream.write(buffer.getvalue())
                            file_output_stream.close()
                            self.status_label.text = "✓ 保存成功!"
                        except Exception as e:
                            self.status_label.text = f"❌ 保存错误: {str(e)}"
                    
                    Clock.schedule_once(do_save, 0)

                filechooser.save_file(
                    title=f"保存{image_type}",
                    filters=["image"],
                    default_name=default_name,
                    callback=save_callback,
                )

            except Exception as e:
                try:
                    from plyer import storagepath

                    pictures_dir = storagepath.get_pictures_dir()
                    if not pictures_dir:
                        external_dir = storagepath.get_external_storage_dir()
                        if external_dir:
                            pictures_dir = os.path.join(external_dir, "Pictures")

                    if pictures_dir and os.path.exists(pictures_dir):
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        filename = f"{image_type}_{timestamp}.png"
                        save_path = os.path.join(pictures_dir, filename)

                        image_to_save.save(save_path)
                        self.status_label.text = f"✓ 已保存到相册\n{save_path}"
                    else:
                        self.status_label.text = "❌ 无法访问相册目录"

                except Exception as e2:
                    self.status_label.text = f"❌ 保存失败: {str(e2)}"
        else:
            if self.original_path:
                default_name = (
                    os.path.splitext(os.path.basename(self.original_path))[0]
                    + f"_{image_type}.png"
                )
                save_path = os.path.join(os.path.dirname(self.original_path), default_name)
            else:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                default_name = f"{image_type}_{timestamp}.png"
                download_path = os.path.expanduser("~/Downloads")
                save_path = os.path.join(download_path, default_name)

            try:
                image_to_save.save(save_path)
                self.status_label.text = f"✓ 已保存\n{save_path}"
            except Exception as e:
                self.status_label.text = f"❌ 错误: {str(e)}"


if __name__ == "__main__":
    GrayImageApp().run()