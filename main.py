# -*- coding: utf-8 -*-
"""
Вимірювач площі листка (APK-версія).
Камера: camera4kivy (CameraX). Вибір фото: Plyer (системний файловий вибір).
Обробка зображення: Pillow (HSV, найбільший білий контур).
"""

import os
import csv
import shutil
import datetime
from PIL import Image, ImageFilter
from collections import deque

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.utils import platform

# Камера
from camera4kivy import Preview
# Системний вибір файлів
from plyer import filechooser


# ---------- ЕКРАН КАМЕРИ ----------
class CameraScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.preview = None

    def on_enter(self):
        if not self.preview:
            self.preview = Preview(aspect_ratio='4:3')
            self.add_widget(self.preview)
            btn_layout = BoxLayout(
                size_hint=(1, 0.1), pos_hint={'center_x': 0.5, 'y': 0.02}
            )
            btn_capture = Button(
                text='📷 Зняти', size_hint=(0.5, 1),
                background_color=(0.2, 0.6, 0.2, 1), font_size='20sp',
                color=(1, 1, 1, 1)
            )
            btn_back = Button(
                text='↩ Назад', size_hint=(0.5, 1),
                background_color=(0.6, 0.2, 0.2, 1), font_size='20sp',
                color=(1, 1, 1, 1)
            )
            btn_layout.add_widget(btn_back)
            btn_layout.add_widget(btn_capture)
            self.add_widget(btn_layout)
            btn_capture.bind(on_press=self.capture_photo)
            btn_back.bind(on_press=self.go_back)

    def capture_photo(self, instance):
        app = App.get_running_app()
        main_screen = app.root.get_screen('main')
        path = main_screen.get_temp_photo_path()
        self.preview.capture(path, self.on_photo_captured)

    def on_photo_captured(self, path):
        if path:
            app = App.get_running_app()
            main_screen = app.root.get_screen('main')
            main_screen.process_captured_photo(path)
            self.go_back(None)

    def go_back(self, instance):
        self.manager.current = 'main'

    def on_leave(self):
        if self.preview:
            self.preview.stop()


# ---------- ГОЛОВНИЙ ЕКРАН ----------
class MainScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.photo_path = None
        self.hybrids = ["Гібрид/сорт 1"]
        self.variants = ["Варіант 1 (контроль)"]
        self.reps = ["Повторність 1"]
        self.build_ui()

    def build_ui(self):
        layout = BoxLayout(orientation='vertical', padding=dp(15), spacing=dp(10))
        scroll = ScrollView()
        content = BoxLayout(orientation='vertical', spacing=dp(10), size_hint_y=None)
        content.bind(minimum_height=content.setter('height'))

        content.add_widget(Label(
            text="🌻 Вимірювач площі листка",
            size_hint_y=None, height=dp(50),
            font_size='22sp', bold=True, color=(0, 0.3, 0, 1)
        ))

        # Гібрид
        content.add_widget(Label(text="Гібрид / сорт:", size_hint_y=None, height=dp(30), font_size='18sp', color=(0,0,0,1)))
        h_box = BoxLayout(orientation='horizontal', spacing=5, size_hint_y=None, height=dp(50))
        self.h_spin = Spinner(text=self.hybrids[0], values=self.hybrids, size_hint_x=0.7,
                              background_color=(1,1,1,1), color=(0,0,0,1), font_size='16sp')
        h_box.add_widget(self.h_spin)
        h_box.add_widget(Button(text="-", size_hint_x=0.15, background_color=(0.8,0.2,0.2,1), font_size='20sp',
                                on_press=lambda x: self.rem('hybrid')))
        h_box.add_widget(Button(text="+", size_hint_x=0.15, background_color=(0.2,0.6,0.2,1), font_size='20sp',
                                on_press=lambda x: self.add('hybrid')))
        content.add_widget(h_box)

        # Варіант
        content.add_widget(Label(text="Варіант:", size_hint_y=None, height=dp(30), font_size='18sp', color=(0,0,0,1)))
        v_box = BoxLayout(orientation='horizontal', spacing=5, size_hint_y=None, height=dp(50))
        self.v_spin = Spinner(text=self.variants[0], values=self.variants, size_hint_x=0.7,
                              background_color=(1,1,1,1), color=(0,0,0,1), font_size='16sp')
        v_box.add_widget(self.v_spin)
        v_box.add_widget(Button(text="-", size_hint_x=0.15, background_color=(0.8,0.2,0.2,1), font_size='20sp',
                                on_press=lambda x: self.rem('variant')))
        v_box.add_widget(Button(text="+", size_hint_x=0.15, background_color=(0.2,0.6,0.2,1), font_size='20sp',
                                on_press=lambda x: self.add('variant')))
        content.add_widget(v_box)

        # Повторність
        content.add_widget(Label(text="Повторність:", size_hint_y=None, height=dp(30), font_size='18sp', color=(0,0,0,1)))
        r_box = BoxLayout(orientation='horizontal', spacing=5, size_hint_y=None, height=dp(50))
        self.r_spin = Spinner(text=self.reps[0], values=self.reps, size_hint_x=0.7,
                              background_color=(1,1,1,1), color=(0,0,0,1), font_size='16sp')
        r_box.add_widget(self.r_spin)
        r_box.add_widget(Button(text="-", size_hint_x=0.15, background_color=(0.8,0.2,0.2,1), font_size='20sp',
                                on_press=lambda x: self.rem('rep')))
        r_box.add_widget(Button(text="+", size_hint_x=0.15, background_color=(0.2,0.6,0.2,1), font_size='20sp',
                                on_press=lambda x: self.add('rep')))
        content.add_widget(r_box)

        # Номер листка
        content.add_widget(Label(text="Номер листка:", size_hint_y=None, height=dp(30), font_size='18sp', color=(0,0,0,1)))
        self.leaf_num = TextInput(hint_text="Ціле число", input_filter='int', size_hint_y=None, height=dp(50),
                                  multiline=False, background_color=(1,1,1,1), foreground_color=(0,0,0,1), font_size='16sp')
        content.add_widget(self.leaf_num)

        # Площа еталона
        content.add_widget(Label(text="Площа еталона (см²):", size_hint_y=None, height=dp(30), font_size='18sp', color=(0,0,0,1)))
        self.ref_area = TextInput(text="623.7", size_hint_y=None, height=dp(50), multiline=False,
                                  background_color=(1,1,1,1), foreground_color=(0,0,0,1), font_size='16sp')
        content.add_widget(self.ref_area)

        # Кнопки фото
        btn_box = BoxLayout(orientation='horizontal', spacing=5, size_hint_y=None, height=dp(55))
        btn_camera = Button(text="📷 Зробити фото", background_color=(0.2,0.6,0.2,1), font_size='18sp', color=(1,1,1,1),
                            on_press=self.open_camera)
        btn_gallery = Button(text="📁 Вибрати фото", background_color=(0.2,0.4,0.8,1), font_size='18sp', color=(1,1,1,1),
                             on_press=self.choose_photo)
        btn_box.add_widget(btn_camera)
        btn_box.add_widget(btn_gallery)
        content.add_widget(btn_box)

        # Статус фото
        self.photo_status = Label(text="Фото не вибрано", size_hint_y=None, height=dp(30),
                                  color=(0.8,0,0,1), font_size='16sp')
        content.add_widget(self.photo_status)

        # Кнопка розрахунку
        content.add_widget(Button(text="🔍 Розрахувати площу", size_hint_y=None, height=dp(55),
                                  background_color=(0.9,0.6,0.0,1), font_size='18sp', color=(1,1,1,1),
                                  on_press=self.calculate_area))
        self.result_label = Label(text="Тут з'явиться результат", size_hint_y=None, height=dp(100),
                                  halign='center', valign='middle', color=(0,0,0,1), font_size='16sp')
        content.add_widget(self.result_label)

        # Кнопка наступного листка
        content.add_widget(Button(text="🔄 Наступний листок", size_hint_y=None, height=dp(55),
                                  background_color=(0.5,0.5,0.5,1), font_size='18sp', color=(1,1,1,1),
                                  on_press=self.next_leaf))

        scroll.add_widget(content)
        layout.add_widget(scroll)
        self.add_widget(layout)

    # ---------- ДИНАМІЧНІ СПИСКИ ----------
    def add(self, cat):
        if cat == 'hybrid':
            n = len(self.hybrids) + 1
            it = f"Гібрид/сорт {n}"
            if it not in self.hybrids:
                self.hybrids.append(it)
                self.h_spin.values = self.hybrids
        elif cat == 'variant':
            n = len(self.variants) + 1
            it = f"Варіант {n}"
            if it not in self.variants:
                self.variants.append(it)
                self.v_spin.values = self.variants
        elif cat == 'rep':
            n = len(self.reps) + 1
            it = f"Повторність {n}"
            if it not in self.reps:
                self.reps.append(it)
                self.r_spin.values = self.reps

    def rem(self, cat):
        if cat == 'hybrid' and len(self.hybrids) > 1:
            r = self.hybrids.pop()
            self.h_spin.values = self.hybrids
            if self.h_spin.text == r: self.h_spin.text = self.hybrids[0]
        elif cat == 'variant' and len(self.variants) > 1:
            r = self.variants.pop()
            self.v_spin.values = self.variants
            if self.v_spin.text == r: self.v_spin.text = self.variants[0]
        elif cat == 'rep' and len(self.reps) > 1:
            r = self.reps.pop()
            self.r_spin.values = self.reps
            if self.r_spin.text == r: self.r_spin.text = self.reps[0]

    # ---------- ДОПОМІЖНІ МЕТОДИ ----------
    def get_temp_photo_path(self):
        return os.path.join(App.get_running_app().user_data_dir, "temp_leaf.jpg")

    def open_camera(self, instance):
        if not self.leaf_num.text.strip().isdigit():
            self._toast("❌ Введіть номер листка!")
            return
        self.manager.current = 'camera'

    def choose_photo(self, instance):
        if not self.leaf_num.text.strip().isdigit():
            self._toast("❌ Введіть номер листка!")
            return
        try:
            filechooser.open_file(
                on_selection=self._on_gallery_selection,
                filters=[("Images", "*.jpg", "*.jpeg", "*.png")]
            )
        except Exception as e:
            self._toast(f"Помилка відкриття вибору: {e}")

    def _on_gallery_selection(self, selection):
        if selection:
            self.process_captured_photo(selection[0])

    def process_captured_photo(self, src):
        """Копіює фото в Structured_Photos з правильним іменем."""
        h = self.h_spin.text
        v = self.v_spin.text
        r = self.r_spin.text
        leaf = self.leaf_num.text.strip()
        stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        name = f"{h}_{v}_{r}_Листок{leaf}_{stamp}.jpg"
        dest_dir = os.path.join(App.get_running_app().user_data_dir, 'Structured_Photos')
        os.makedirs(dest_dir, exist_ok=True)
        dest = os.path.join(dest_dir, name)
        shutil.copy2(src, dest)
        self.photo_path = dest
        self.photo_status.text = f"✅ {name[:30]}..."
        self.photo_status.color = (0, 0.6, 0, 1)
        self._toast("Фото збережено")

    # ---------- ОБРОБКА ЗОБРАЖЕННЯ (PILLOW) ----------
    def calculate_area(self, instance):
        if not self.photo_path or not os.path.exists(self.photo_path):
            self._toast("❌ Зробіть або виберіть фото!")
            return
        try:
            S_ref = float(self.ref_area.text) if self.ref_area.text else 623.7
        except:
            self._toast("❌ Площа еталона — число!")
            return

        try:
            self._toast("⏳ Аналіз...")
            img = Image.open(self.photo_path)
            # Зменшення для швидкості
            if img.width > 1500 or img.height > 1500:
                ratio = min(1500 / img.width, 1500 / img.height)
                img = img.resize((int(img.width * ratio), int(img.height * ratio)))
            # Розмиття
            img = img.filter(ImageFilter.GaussianBlur(radius=2))
            # HSV
            hsv = img.convert('HSV')
            w, h = img.size
            hsv_data = list(hsv.getdata())
            # Маски
            mask_green = [self._is_green(p) for p in hsv_data]
            mask_white = [self._is_white(p) for p in hsv_data]
            # Пошук паперу (найбільший білий об'єкт)
            paper = self._find_largest_object_2d(mask_white, w, h)
            if not paper:
                self._toast("❌ Білий папір не знайдено!")
                return
            # Підрахунок пікселів
            P_green = sum(1 for i in range(len(mask_green)) if paper[i] and mask_green[i])
            P_white = sum(1 for i in range(len(mask_white)) if paper[i] and mask_white[i] and not mask_green[i])
            total = P_green + P_white
            if total == 0:
                self._toast("❌ Помилка підрахунку!")
                return
            S_leaf = (P_green / total) * S_ref
            coverage = (P_green / total) * 100
            # Вивід результату
            h_text = self.h_spin.text
            v_text = self.v_spin.text
            r_text = self.r_spin.text
            leaf_text = self.leaf_num.text.strip()
            self.result_label.text = (
                f"✅ Площа: {S_leaf:.2f} см²\n"
                f"📊 Заповнення: {coverage:.1f}%\n"
                f"{h_text} | {v_text} | {r_text} | Листок {leaf_text}"
            )
            # Збереження маски та CSV
            self._save_results(S_leaf, coverage, img, mask_green, mask_white, paper)
            self._toast(f"✅ Площа: {S_leaf:.1f} см²")
        except Exception as e:
            self._toast(f"❌ Помилка обробки: {e}")

    def _is_green(self, pixel):
        """H: 35-85, S: 40-255, V: 40-255 (у шкалі 0-255 для Pillow)."""
        h, s, v = pixel
        return (35 * 255 // 180 <= h <= 85 * 255 // 180) and s >= 40 and v >= 40

    def _is_white(self, pixel):
        """S: 0-40, V: 100-255."""
        h, s, v = pixel
        return s <= 40 and v >= 100

    def _find_largest_object_2d(self, mask_flat, w, h):
        """Шукає найбільшу зв'язану область на бінарній масці (BFS)."""
        grid = [mask_flat[i * w:(i + 1) * w] for i in range(h)]
        visited = [[False] * w for _ in range(h)]
        best = None
        best_size = 0
        for y in range(h):
            for x in range(w):
                if grid[y][x] and not visited[y][x]:
                    q = deque([(y, x)])
                    visited[y][x] = True
                    size = 0
                    comp = set()
                    while q:
                        cy, cx = q.popleft()
                        size += 1
                        comp.add((cy, cx))
                        for ny, nx in [(cy - 1, cx), (cy + 1, cx), (cy, cx - 1), (cy, cx + 1)]:
                            if 0 <= ny < h and 0 <= nx < w and grid[ny][nx] and not visited[ny][nx]:
                                visited[ny][nx] = True
                                q.append((ny, nx))
                    if size > best_size:
                        best_size = size
                        best = comp
        if best is None:
            return None
        # Повертаємо плоску маску для всієї області
        paper_flat = [False] * (w * h)
        for (cy, cx) in best:
            paper_flat[cy * w + cx] = True
        return paper_flat

    def _save_results(self, S_leaf, coverage, img, mask_green, mask_white, paper):
        """Зберігає маску перевірки та CSV."""
        stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        h = self.h_spin.text
        v = self.v_spin.text
        r = self.r_spin.text
        leaf = self.leaf_num.text.strip()
        name = f"{h}_{v}_{r}_Листок{leaf}_{stamp}"
        base = App.get_running_app().user_data_dir
        mask_dir = os.path.join(base, 'Analysis_Masks')
        os.makedirs(mask_dir, exist_ok=True)

        # Побудова зображення маски: фон чорний, папір сірий, листок білий
        mask_img = Image.new('RGB', img.size)
        pixels = [(0, 0, 0)] * (img.width * img.height)
        for i in range(len(pixels)):
            if paper[i]:
                if mask_green[i]:
                    pixels[i] = (255, 255, 255)  # листок
                else:
                    pixels[i] = (128, 128, 128)  # папір
        mask_img.putdata(pixels)
        mask_img.save(os.path.join(mask_dir, f'MASK_{name}.jpg'))

        # CSV
        csv_path = os.path.join(base, 'leaf_surface_reports.csv')
        file_exists = os.path.exists(csv_path) and os.path.getsize(csv_path) > 0
        with open(csv_path, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(["Дата/Час", "Гібрид", "Варіант", "Повторність",
                                 "Номер Листка", "Площа (см²)", "Заповнення (%)"])
            writer.writerow([
                datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                h, v, r, leaf, f"{S_leaf:.2f}", f"{coverage:.1f}"
            ])

    def next_leaf(self, instance):
        cur = self.leaf_num.text.strip()
        if cur.isdigit():
            self.leaf_num.text = str(int(cur) + 1)
        self.photo_path = None
        self.photo_status.text = "Фото не вибрано"
        self.photo_status.color = (0.8, 0, 0, 1)
        self.result_label.text = "Тут з'явиться результат"
        self._toast("🔄 Готово до наступного листка!")

    def _toast(self, msg):
        popup = Popup(
            title='Повідомлення',
            content=Label(text=msg, font_size='16sp'),
            size_hint=(0.7, 0.3)
        )
        popup.open()


# ---------- ГОЛОВНИЙ ДОДАТОК ----------
class LeafApp(App):
    def build(self):
        Window.clearcolor = (0.98, 0.98, 0.98, 1)
        sm = ScreenManager()
        sm.add_widget(MainScreen(name='main'))
        sm.add_widget(CameraScreen(name='camera'))
        return sm


if __name__ == '__main__':
    LeafApp().run()
