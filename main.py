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

import platform
import sys

SYSTEM = platform.system()

if SYSTEM == "Darwin":
    CHINESE_FONT = "/System/Library/Fonts/STHeiti Medium.ttc"
elif SYSTEM == "Windows":
    CHINESE_FONT = "simsun.ttc"
elif "android" in sys.platform:
    CHINESE_FONT = None
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

        for name, path in [
            ("Home", "~"),
            ("图片", "~/Pictures"),
            ("桌面", "~/Desktop"),
        ]:
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
        self.current_path = os.path.expanduser(path)
        self.refresh_files()

    def refresh_files(self, *args):
        self.file_grid.clear_widgets()

        if not os.path.isdir(self.current_path):
            return

        if self.current_path != os.path.expanduser("~"):
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
        popup = FileBrowserPopup(callback=self.load_image)
        popup.open()

    def load_image(self, path):
        try:
            self.status_label.text = "加载中..."
            self.original_path = path

            img = Image.open(path)

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
            save_path = "/tmp/gray.png"
            self.gray_image.save(save_path)
            self.gray_img.source = save_path
            self.gray_img.reload()

    def save_image(self, instance):
        if self.gray_image:
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
