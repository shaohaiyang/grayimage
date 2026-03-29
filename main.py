import sys
import os
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.image import Image as KivyImage
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from PIL import Image
from datetime import datetime  # 用于生成时间戳文件名

import platform
import sys
from kivy.utils import platform as kivy_platform

SYSTEM = platform.system()


def is_android():
    """检测是否运行在 Android 平台"""
    return kivy_platform == "android" or "ANDROID_ARGUMENT" in os.environ


if SYSTEM == "Darwin":
    CHINESE_FONT = "/System/Library/Fonts/STHeiti Medium.ttc"
elif SYSTEM == "Windows":
    CHINESE_FONT = "simsun.ttc"
elif is_android():
    CHINESE_FONT = "DroidSansFallback"  # Android 支持中文的字体
else:
    CHINESE_FONT = "DroidSansFallback"

IMAGE_EXTS = {
    ".png",
    ".jpg",
    ".jpeg",
    ".bmp",
    ".gif",
    ".webp",
    ".PNG",
    ".JPG",
    ".JPEG",
    ".BMP",
    ".GIF",
    ".WEBP",
}


def font_props(size=None, bold=False):
    props = {}
    if CHINESE_FONT:
        props["font_name"] = CHINESE_FONT
    if size:
        props["font_size"] = size
    if bold:
        props["bold"] = bold
    return props


def get_font_name():
    return CHINESE_FONT if CHINESE_FONT else "Roboto"


class FileBrowserPopup(Popup):
    def __init__(self, callback, **kwargs):
        super().__init__(**kwargs)
        self.callback = callback

        # 根据平台设置正确的默认路径
        if is_android():
            try:
                from plyer import storagepath

                # 尝试使用 Downloads 或 Pictures 目录
                downloads_dir = storagepath.get_downloads_dir()
                if downloads_dir and os.path.exists(downloads_dir):
                    self.current_path = downloads_dir
                else:
                    pictures_dir = storagepath.get_pictures_dir()
                    if pictures_dir and os.path.exists(pictures_dir):
                        self.current_path = pictures_dir
                    else:
                        # 备选：使用外部存储根目录
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
        self.title_font = CHINESE_FONT
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


class GrayImageApp(App):
    def build(self):
        layout = BoxLayout(orientation="vertical", padding=20, spacing=15)

        title = Label(
            text="图片灰度转换器",
            font_name=get_font_name(),
            font_size="28sp",
            bold=True,
            color=(0.2, 0.2, 0.2, 1),
        )
        layout.add_widget(title)

        self.select_btn = Button(
            text="选择图片",
            font_name=get_font_name(),
            font_size="18sp",
            size_hint_y=None,
            height=60,
            background_color=(0.6, 0.75, 0.9, 1),
            color=(1, 1, 1, 1),
        )
        self.select_btn.bind(on_press=self.show_file_selector)
        layout.add_widget(self.select_btn)

        self.status_label = Label(
            text="请选择一张图片",
            font_name=get_font_name(),
            font_size="14sp",
            color=(0.5, 0.5, 0.5, 1),
        )
        layout.add_widget(self.status_label)

        img_layout = BoxLayout(orientation="horizontal", spacing=20, size_hint_y=1)

        left_box = BoxLayout(orientation="vertical", padding=5)
        left_box.add_widget(
            Label(
                text="原图",
                font_name=get_font_name(),
                font_size="16sp",
                bold=True,
                color=(0.2, 0.2, 0.2, 1),
                size_hint_y=None,
                height=30,
            )
        )
        self.original_img = KivyImage()
        left_box.add_widget(self.original_img)
        img_layout.add_widget(left_box)

        right_box = BoxLayout(orientation="vertical", padding=5)
        right_box.add_widget(
            Label(
                text="灰度图",
                font_name=get_font_name(),
                font_size="16sp",
                bold=True,
                color=(0.2, 0.2, 0.2, 1),
                size_hint_y=None,
                height=30,
            )
        )
        self.gray_img = KivyImage()
        right_box.add_widget(self.gray_img)
        img_layout.add_widget(right_box)

        layout.add_widget(img_layout)

        self.save_btn = Button(
            text="保存到下载目录",
            font_name=get_font_name(),
            font_size="16sp",
            size_hint_y=None,
            height=50,
            background_color=(0.7, 0.85, 0.7, 1),
            color=(0, 0, 0, 1),
            disabled=True,
        )
        self.save_btn.bind(on_press=self.save_image)
        layout.add_widget(self.save_btn)

        self.original_image = None
        self.gray_image = None
        self.original_path = None

        return layout

    def show_file_selector(self, instance):
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
                import traceback

                traceback.print_exc()
        else:
            # 桌面平台使用自定义文件浏览器
            popup = FileBrowserPopup(callback=self.load_image)
            popup.open()

    def load_image(self, path):
        try:
            self.status_label.text = "加载中..."
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
                from plyer import storagepath

                # 使用应用专属缓存目录
                app_dir = storagepath.get_application_dir()
                if app_dir:
                    cache_dir = os.path.join(app_dir, "cache")
                else:
                    # 备选：使用外部存储的应用目录
                    external_dir = storagepath.get_external_storage_dir()
                    if external_dir:
                        cache_dir = os.path.join(
                            external_dir, "Android/data/org.example.grayimage/cache"
                        )
                    else:
                        cache_dir = "/sdcard/Android/data/org.example.grayimage/cache"

                # 确保目录存在
                os.makedirs(cache_dir, exist_ok=True)
                save_path = os.path.join(cache_dir, "original.png")
            else:
                save_path = "/tmp/original.png"

            self.original_image.save(save_path)
            self.original_img.source = save_path
            self.original_img.reload()

            self.process_image()
            self.save_btn.disabled = False

            basename = os.path.basename(path)
            self.status_label.text = f"已加载: {basename}"

        except Exception as e:
            self.status_label.text = f"错误: {str(e)}"

    def process_image(self):
        if self.original_image:
            self.gray_image = self.original_image.convert("L")

            # 使用正确的临时文件路径
            if is_android():
                from plyer import storagepath

                # 使用应用专属缓存目录
                app_dir = storagepath.get_application_dir()
                if app_dir:
                    cache_dir = os.path.join(app_dir, "cache")
                else:
                    # 备选：使用外部存储的应用目录
                    external_dir = storagepath.get_external_storage_dir()
                    if external_dir:
                        cache_dir = os.path.join(
                            external_dir, "Android/data/org.example.grayimage/cache"
                        )
                    else:
                        cache_dir = "/sdcard/Android/data/org.example.grayimage/cache"

                # 确保目录存在
                os.makedirs(cache_dir, exist_ok=True)
                save_path = os.path.join(cache_dir, "gray.png")
            else:
                save_path = "/tmp/gray.png"

            self.gray_image.save(save_path)
            self.gray_img.source = save_path
            self.gray_img.reload()

    def save_image(self, instance):
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
                            self.status_label.text = "保存成功!"
                        except Exception as e:
                            self.status_label.text = f"保存错误: {str(e)}"

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
                            self.status_label.text = f"已保存到相册: {filename}"
                        else:
                            self.status_label.text = "无法访问相册目录"

                    except Exception as e2:
                        self.status_label.text = f"保存失败: {str(e2)}"
                        import traceback

                        traceback.print_exc()
            else:
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
                    self.status_label.text = f"已保存到下载目录!"
                except Exception as e:
                    self.status_label.text = f"错误: {str(e)}"


if __name__ == "__main__":
    GrayImageApp().run()
