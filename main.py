from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.image import Image as KivyImage
from kivy.uix.label import Label
from PIL import Image
import os
import sys


class GrayImageApp(App):
    def build(self):
        layout = BoxLayout(orientation="vertical", padding=20, spacing=15)

        title = Label(
            text="Image Gray", font_size="28sp", bold=True, color=(0.2, 0.2, 0.2, 1)
        )
        layout.add_widget(title)

        btn_layout = BoxLayout(
            orientation="horizontal", spacing=15, size_hint_y=None, height=50
        )

        self.select_btn = Button(
            text="Select Image", background_color=(0.9, 0.9, 0.9, 1), color=(0, 0, 0, 1)
        )
        self.select_btn.bind(on_press=self.select_image)
        btn_layout.add_widget(self.select_btn)

        self.save_btn = Button(
            text="Save Gray",
            background_color=(0.9, 0.9, 0.9, 1),
            color=(0, 0, 0, 1),
            disabled=True,
        )
        self.save_btn.bind(on_press=self.save_image)
        btn_layout.add_widget(self.save_btn)

        layout.add_widget(btn_layout)

        self.status_label = Label(
            text="Select an image", font_size="14sp", color=(0.5, 0.5, 0.5, 1)
        )
        layout.add_widget(self.status_label)

        img_layout = BoxLayout(orientation="horizontal", spacing=20)

        left_box = BoxLayout(orientation="vertical")
        left_box.add_widget(
            Label(
                text="Original", font_size="16sp", bold=True, color=(0.2, 0.2, 0.2, 1)
            )
        )
        self.original_img = KivyImage()
        left_box.add_widget(self.original_img)
        img_layout.add_widget(left_box)

        right_box = BoxLayout(orientation="vertical")
        right_box.add_widget(
            Label(text="Gray", font_size="16sp", bold=True, color=(0.2, 0.2, 0.2, 1))
        )
        self.gray_img = KivyImage()
        right_box.add_widget(self.gray_img)
        img_layout.add_widget(right_box)

        layout.add_widget(img_layout)

        self.original_image = None
        self.gray_image = None
        self.original_path = None

        return layout

    def select_image(self, instance):
        # 尝试使用 tkinter 对话框
        try:
            import tkinter as tk
            from tkinter import filedialog

            root = tk.Tk()
            root.withdraw()
            root.attributes("-topmost", True)

            file_path = filedialog.askopenfilename(
                title="Select Image",
                filetypes=[
                    ("Images", "*.png;*.jpg;*.jpeg;*.webp;*.bmp;*.gif"),
                    ("All Files", "*.*"),
                ],
            )
            root.destroy()

            if file_path:
                self.load_image(file_path)
        except Exception as e:
            self.status_label.text = f"Error: {str(e)}"

    def load_image(self, path):
        try:
            self.status_label.text = f"Loading: {os.path.basename(path)}"
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
            self.status_label.text = "Done - click Save Gray"

        except Exception as e:
            self.status_label.text = f"Error: {str(e)}"

    def process_image(self):
        if self.original_image:
            self.gray_image = self.original_image.convert("L")
            save_path = "/tmp/gray.png"
            self.gray_image.save(save_path)
            self.gray_img.source = save_path
            self.gray_img.reload()

    def save_image(self, instance):
        if self.gray_image:
            try:
                import tkinter as tk
                from tkinter import filedialog

                root = tk.Tk()
                root.withdraw()
                root.attributes("-topmost", True)

                default_name = (
                    os.path.splitext(os.path.basename(self.original_path))[0]
                    + "_gray.png"
                )
                file_path = filedialog.asksaveasfilename(
                    title="Save Gray Image",
                    defaultextension=".png",
                    filetypes=[
                        ("PNG", "*.png"),
                        ("JPEG", "*.jpg"),
                        ("All Files", "*.*"),
                    ],
                    initialfile=default_name,
                )
                root.destroy()

                if file_path:
                    self.gray_image.save(file_path)
                    self.status_label.text = f"Saved: {os.path.basename(file_path)}"
            except Exception as e:
                self.status_label.text = f"Error: {str(e)}"


if __name__ == "__main__":
    GrayImageApp().run()
