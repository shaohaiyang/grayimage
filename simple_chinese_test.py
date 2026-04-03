"""
简单的中文显示测试
"""

from kivy.config import Config
# 设置窗口大小避免全屏
Config.set('graphics', 'width', '500')
Config.set('graphics', 'height', '400')

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.core.text import LabelBase
import os

# 注册中文字体
font_path = '/System/Library/Fonts/PingFang.ttc'
if os.path.exists(font_path):
    try:
        LabelBase.register(name='ChineseFont', fn_regular=font_path)
        print(f'✓ 中文字体已注册')
    except Exception as e:
        print(f'✗ 字体注册失败: {e}')
        font_path = None
else:
    print(f'✗ 字体文件不存在')

class SimpleChineseApp(App):
    def build(self):
        layout = BoxLayout(orientation='vertical', padding=20, spacing=15)

        # 测试文本
        tests = [
            ('默认字体', None, '图片灰度化'),
            ('中文字体', 'ChineseFont', '图片灰度化'),
            ('文件选择器', 'ChineseFont', '选择图片'),
            ('状态提示', 'ChineseFont', '请选择一张图片'),
            ('保存按钮', 'ChineseFont', '保存图片'),
        ]

        for title, font, text in tests:
            # 标题
            label_title = Label(
                text=title,
                font_size='14sp',
                color=(0.3, 0.3, 0.3, 1),
                size_hint_y=None,
                height=25
            )
            layout.add_widget(label_title)

            # 内容
            font_dict = {'font_name': font} if font else {}
            label_text = Label(
                text=text,
                font_size='18sp',
                color=(0, 0, 0, 1),
                size_hint_y=None,
                height=40,
                **font_dict
            )
            layout.add_widget(label_text)

        return layout

if __name__ == '__main__':
    SimpleChineseApp().run()