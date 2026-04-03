"""
测试中文字体显示
"""

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
        print(f'✓ 中文字体已注册: {font_path}')
    except Exception as e:
        print(f'✗ 字体注册失败: {e}')
        font_path = None
else:
    print(f'✗ 字体文件不存在: {font_path}')
    font_path = None

class TestChineseApp(App):
    def build(self):
        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)

        # 测试不同的中文文本
        texts = [
            '图片灰度化应用',
            '选择图片',
            '请选择一张图片',
            '保存图片',
            '✓ 中文显示测试通过',
            '📷 灰度转换工具'
        ]

        for text in texts:
            if font_path:
                label = Label(
                    text=text,
                    font_name='ChineseFont',
                    font_size='20sp',
                    halign='center',
                    size_hint_y=None,
                    height=40
                )
            else:
                label = Label(text=text, font_size='20sp')
            layout.add_widget(label)

        return layout

if __name__ == '__main__':
    TestChineseApp().run()