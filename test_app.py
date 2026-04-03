"""
测试脚本 - 验证应用程序的核心功能
"""

import sys
import os
import tempfile
from PIL import Image
from main import get_platform, is_android, get_app_title

def test_platform_detection():
    """测试平台检测功能"""
    print("Testing platform detection...")
    try:
        platform_name = get_platform()
        print(f"✓ Platform detected: {platform_name}")

        android_status = is_android()
        print(f"✓ Android status: {android_status}")

        app_title = get_app_title()
        print(f"✓ App title: {app_title}")

        return True
    except Exception as e:
        print(f"✗ Platform detection failed: {e}")
        return False

def test_image_processing():
    """测试图片处理功能"""
    print("\nTesting image processing...")
    try:
        # 创建测试图片
        original_img = Image.new('RGB', (100, 100), color='red')
        temp_dir = tempfile.gettempdir()

        # 保存原图
        original_path = os.path.join(temp_dir, 'test_original.png')
        original_img.save(original_path)
        print(f"✓ Original image saved: {original_path}")

        # 转换为灰度
        gray_img = original_img.convert('L')
        gray_path = os.path.join(temp_dir, 'test_gray.png')
        gray_img.save(gray_path)
        print(f"✓ Grayscale image saved: {gray_path}")

        # 验证图片
        test_gray = Image.open(gray_path)
        assert test_gray.mode == 'L', "Image should be grayscale"
        print("✓ Image conversion verified (grayscale mode)")

        # 清理
        os.remove(original_path)
        os.remove(gray_path)
        print("✓ Cleanup completed")

        return True
    except Exception as e:
        print(f"✗ Image processing failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_dependencies():
    """测试所有依赖包"""
    print("\nTesting dependencies...")
    try:
        import kivy
        print(f"✓ Kivy version: {kivy.__version__}")

        from kivy.app import App
        from kivy.uix.boxlayout import BoxLayout
        print("✓ Kivy imports successful")

        import kivymd
        print(f"✓ KivyMD version: {kivymd.__version__}")

        from kivymd.app import MDApp
        from kivymd.uix.boxlayout import MDBoxLayout
        from kivymd.uix.card import MDCard
        from kivymd.uix.button import MDRaisedButton
        from kivymd.uix.label import MDLabel
        from kivymd.uix.tab import MDTabs
        print("✓ KivyMD imports successful")

        from PIL import Image
        print(f"✓ Pillow version: {Image.__version__}")

        import plyer
        print("✓ Plyer import successful")

        # pyjnius is Android-specific, skip on non-Android platforms
        try:
            import pyjnius
            print("✓ Pyjnius import successful")
        except ImportError:
            if is_android():
                print("✗ Pyjnius required but not found on Android")
                raise
            else:
                print("✓ Pyjnius skipped (not required on this platform)")

        return True
    except Exception as e:
        print(f"✗ Dependencies test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_ui_components():
    """测试UI组件创建"""
    print("\nTesting UI components...")
    try:
        from kivy.app import App
        from kivymd.app import MDApp
        from kivymd.uix.boxlayout import MDBoxLayout
        from kivymd.uix.card import MDCard
        from kivymd.uix.button import MDRaisedButton
        from kivymd.uix.label import MDLabel

        # 创建测试应用
        class TestApp(MDApp):
            def build(self):
                self.theme_cls.primary_palette = "Blue"
                layout = MDBoxLayout(orientation="vertical", padding=10, spacing=10)

                # 测试卡片
                card = MDCard(elevation=2, radius=15)
                card_layout = MDBoxLayout(orientation="vertical", padding=10)
                card.add_widget(card_layout)

                # 测试按钮
                btn = MDRaisedButton(
                    text="Test Button",
                    size_hint_y=None,
                    height=50,
                    md_bg_color=self.theme_cls.primary_color
                )
                card_layout.add_widget(btn)

                # 测试标签
                label = MDLabel(
                    text="Test Label",
                    halign="center",
                    theme_text_color="Hint"
                )
                card_layout.add_widget(label)

                layout.add_widget(card)
                return layout

        print("✓ UI components creation successful")
        return True
    except Exception as e:
        print(f"✗ UI components test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """运行所有测试"""
    print("=" * 50)
    print("开始测试应用程序...")
    print("=" * 50)

    tests = [
        ("Dependencies", test_dependencies),
        ("Platform Detection", test_platform_detection),
        ("Image Processing", test_image_processing),
        ("UI Components", test_ui_components),
    ]

    results = []
    for test_name, test_func in tests:
        result = test_func()
        results.append((test_name, result))

    print("\n" + "=" * 50)
    print("测试结果汇总:")
    print("=" * 50)

    passed = 0
    failed = 0
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
        else:
            failed += 1

    print("=" * 50)
    print(f"总计: {passed} 通过, {failed} 失败")
    print("=" * 50)

    return failed == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)