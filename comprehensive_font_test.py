"""
测试中文字体在所有组件中的显示
"""

from kivy.config import Config
Config.set('graphics', 'width', '600')
Config.set('graphics', 'height', '500')

from kivy.app import App
from kivymd.app import MDApp
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.tab import MDTabs, MDTabsBase
from kivymd.uix.card import MDCard
from kivy.uix.boxlayout import BoxLayout
from kivy.core.text import LabelBase
from kivy.uix.button import Button
import os

# 注册中文字体
font_path = '/System/Library/Fonts/PingFang.ttc'
if os.path.exists(font_path):
    LabelBase.register(name='ChineseFont', fn_regular=font_path)
    CHINESE_FONT = 'ChineseFont'
else:
    CHINESE_FONT = 'Roboto'

class Tab(BoxLayout, MDTabsBase):
    '''选项卡内容类'''
    pass

class FontTestApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.theme_cls.primary_palette = "Blue"
        self.chinese_font_name = CHINESE_FONT

    def build(self):
        layout = MDBoxLayout(orientation='vertical', padding=20, spacing=15)

        # 1. 测试MDLabel (标题)
        title_card = MDCard(
            size_hint_y=None,
            height=60,
            padding=10,
            elevation=2
        )
        title = MDLabel(
            text="图片灰度化 (macOS版)",
            font_name=self.chinese_font_name,
            font_size="22sp",
            bold=True,
            halign="center"
        )
        title_card.add_widget(title)
        layout.add_widget(title_card)

        # 2. 测试MDRaisedButton
        button = MDRaisedButton(
            text="选择图片",
            font_name=self.chinese_font_name,
            font_size="18sp",
            size_hint_y=None,
            height=50
        )
        layout.add_widget(button)

        # 3. 测试状态标签
        status_card = MDCard(
            size_hint_y=None,
            height=50,
            padding=10,
            elevation=2
        )
        status = MDLabel(
            text="请选择一张图片",
            font_name=self.chinese_font_name,
            font_size="14sp",
            halign="center"
        )
        status_card.add_widget(status)
        layout.add_widget(status_card)

        # 4. 测试选项卡
        tabs_card = MDCard(
            size_hint_y=1,
            padding=10,
            elevation=2
        )
        tabs = MDTabs()

        # 原图选项卡
        original_tab = Tab(title="原图")
        original_tab.tab_label.font_name = self.chinese_font_name
        original_tab.tab_label.font_size = "16sp"

        # 灰度图选项卡
        gray_tab = Tab(title="灰度")
        gray_tab.tab_label.font_name = self.chinese_font_name
        gray_tab.tab_label.font_size = "16sp"

        tabs.add_widget(original_tab)
        tabs.add_widget(gray_tab)

        tabs_card.add_widget(tabs)
        layout.add_widget(tabs_card)

        # 5. 测试保存按钮
        save_button = MDRaisedButton(
            text="💾 保存图片",
            font_name=self.chinese_font_name,
            font_size="16sp",
            size_hint_y=None,
            height=50
        )
        layout.add_widget(save_button)

        # 6. 测试普通Button (文件选择器)
        button_layout = BoxLayout(
            size_hint_y=None,
            height=40,
            spacing=10
        )
        cancel_btn = Button(
            text="取消",
            font_name=self.chinese_font_name,
            font_size="14sp"
        )
        select_btn = Button(
            text="选择",
            font_name=self.chinese_font_name,
            font_size="14sp"
        )
        button_layout.add_widget(cancel_btn)
        button_layout.add_widget(select_btn)
        layout.add_widget(button_layout)

        return layout

if __name__ == '__main__':
    print('=== 组件中文字体测试 ===')
    print(f'使用字体: {CHINESE_FONT}')
    print('请检查窗口中所有中文文本是否显示正常')
    FontTestApp().run()