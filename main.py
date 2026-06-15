# -*- coding: utf-8 -*-
"""
Вимірювач площі листка (APK-версія).
Камера: camera4kivy. Обробка: Pillow.
"""

import os, csv, shutil, datetime
import numpy as np
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
from kivy.clock import Clock
from kivy.utils import platform
from camera4kivy import Preview


class CameraScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.preview = None
        self.btn_layout = None

    def on_enter(self):
        if not self.preview:
            # Ініціалізація камери відповідно до стандартів camera4kivy
            self.preview = Preview(aspect_ratio='4:3', size_hint=(1, 0.9), pos_hint={'top': 1})
            self.add_widget(self.preview)
            
            self.btn_layout = BoxLayout(size_hint=(1, 0.1), pos_hint={'center_x': 0.5, 'y': 0.01}, padding=dp(5), spacing=dp(10))
            btn_capture = Button(text='📷 Зняти', size_hint=(0.5, 1), background_color=(0.2, 0.6, 0.2, 1), font_size='20sp', color=(1,1,1,1))
            btn_back = Button(text='↩ Назад', size_hint=(0.5, 1), background_color=(0.6, 0.2, 0.2, 1), font_size='20sp', color=(1,1,1,1))
            
            self.btn_layout.add_widget(btn_back)
            self.btn_layout.add_widget(btn_capture)
            self.add_widget(self.btn_layout)
            
            btn_capture.bind(on_press=self.capture_photo)
            btn_back.bind(on_press=self.go_back)
        
        # Підключаємо камеру з невеликою затримкою для стабільності текстур Android
        Clock.schedule_once(self.connect_cam, 0.2)

    def connect_cam(self, dt):
        if self.preview:
            self.preview.connect_camera(enable_analyze_pixels=False)

    def capture_photo(self, instance):
        # Використовуємо надійний скріншот-захоплювач для camera4kivy
        # Він автоматично збереже файл і викличе коллбек
        self.preview.capture_screenshot(location='private', name='temp_leaf')

    def go_back(self, instance):
        self.manager.current = 'main'

    def on_leave(self):
        if self.preview:
            self.preview.disconnect_camera()


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

        content.add_widget(Label(text="🌻 Вимірювач площі листка", size_hint_y=None, height=dp(50), font_size='22sp', bold=True, color=(0.1, 0.5, 0.1, 1)))

        # Гібрид
        content.add_widget(Label(text="Гібрид / сорт:", size_hint_y=None, height=dp(25), font_size='16sp', color=(0,0,0,1)))
        h_box = BoxLayout(orientation='horizontal', spacing=5, size_hint_y=None, height=dp(45))
        self.h_spin = Spinner(text=self.hybrids[0], values=self.hybrids, size_hint_x=0.7, background_color=(0.9,0.9,0.9,1), color=(0,0,0,1), font_size='16sp')
        h_box.add_widget(self.h_spin)
        h_box.add_widget(Button(text="-", size_hint_x=0.15, background_color=(0.8,0.2,0.2,1), font_size='20sp', on_press=lambda x: self.rem('hybrid')))
        h_box.add_widget(Button(text="+", size_hint_x=0.15, background_color=(0.2,0.6,0.2,1), font_size='20sp', on_press=lambda x: self.add('hybrid')))
        content.add_widget(h_box)

        # Варіант
        content.add_widget(Label(text="Варіант:", size_hint_y=None, height=dp(25), font_size='16sp', color=(0,0,0,1)))
        v_box = BoxLayout(orientation='horizontal', spacing=5, size_hint_y=None, height=dp(45))
        self.v_spin = Spinner(text=self.variants[0], values=self.variants, size_hint_x=0.7, background_color=(0.9,0.9,0.9,1), color=(0,0,0,1), font_size='16sp')
        v_box.add_widget(self.v_spin)
        v_box.add_widget(Button(text="-", size_hint_x=0.15, background_color=(0.8,0.2,0.2,1), font_size='20sp', on_press=lambda x: self.rem('variant')))
        v_box.add_widget(Button(text="+", size_hint_x=0.15, background_color=(0.2,0.6,0.2,1), font_size='20sp', on_press=lambda x: self.add('variant')))
        content.add_widget(v_box)

        # Повторність
        content.add_widget(Label(text="Повторність:", size_hint_y=None, height=dp(25), font_size='16sp', color=(0,0,0,1)))
        r_box = BoxLayout(orientation='horizontal', spacing=5, size_hint_y=None, height=dp(45))
        self.r_spin = Spinner(text=self.reps[0], values=self.reps, size_hint_x=0.7, background_color=(0.9,0.9,0.9,1), color=(0,0,0,1), font_size='16sp')
        r_box.add_widget(self.r_spin)
        r_box.add_widget(Button(text="-", size_hint_x=0.15, background_color=(0.8,0.2,0.2,1), font_size='20sp', on_press=lambda x: self.rem('rep')))
        r_box.add_widget(Button(text="+", size_hint_x=0.15, background_color=(0.2,0.6,0.2,1), font_size='20sp', on_press=lambda x: self.add('rep')))
        content.add_widget(r_box)

        content.add_widget(Label(text="Номер листка:", size_hint_y=None, height=dp(25), font_size='16sp', color=(0,0,0,1)))
        self.leaf_num = TextInput(hint_text="Ціле число", input_filter='int', size_hint_y=None, height=dp(45), multiline=False, background_color=(1,1,1,1), foreground_color=(0,0,0,1), font_size='16sp')
        content.add_widget(self.leaf_num)

        content.add_widget(Label(text="Площа еталона (см²):", size_hint_y=None, height=dp(25), font_size='16sp', color=(0,0,0,1)))
        self.ref_area = TextInput(text="623.7", size_hint_y=None, height=dp(45), multiline=False, background_color=(1,1,1,1), foreground_color=(0,0,0,1), font_size='16sp')
        content.add_widget(self.ref_area)

        content.add_widget(Button(text="📷 Відкрити камеру", size_hint_y=None, height=dp(50), background_color=(0.2,0.6,0.2,1), font_size='18sp', color=(1,1,1,1), on_press=self.open_camera))
        self.photo_status = Label(text="Фото не зроблено", size_hint_y=None, height=dp(30), color=(0.8,0,0,1), font_size='16sp')
        content.add_widget(self.photo_status)
        content.add_widget(Button(text="🔍 Розрахувати площу", size_hint_y=None, height=dp(50), background_color=(0.2,0.4,0.8,1), font_size='18sp', color=(1,1,1,1), on_press=self.calc))
        self.result_label = Label(text="Тут з'явиться результат", size_hint_y=None, height=dp(80), halign='center', valign='middle', color=(0,0,0,1), font_size='16sp')
        content.add_widget(self.result_label)
        content.add_widget(Button(text="🔄 Наступний листок", size_hint_y=None, height=dp(50), background_color=(0.5,0.5,0.5,1), font_size='18sp', color=(1,1,1,1), on_press=self.next_leaf))

        scroll.add_widget(content)
        layout.add_widget(scroll)
        self.add_widget(layout)

    def add(self, cat):
        if cat == 'hybrid':
            n = len(self.hybrids)+1
            it = f"Гібрид/сорт {n}"
            if it not in self.hybrids:
                self.hybrids.append(it)
                self.h_spin.values = self.hybrids
        elif cat == 'variant':
            n = len(self.variants)+1
            it = f"Варіант {n}"
            if it not in self.variants:
                self.variants.append(it)
                self.v_spin.values = self.variants
        elif cat == 'rep':
            n = len(self.reps)+1
            it = f"Повторність {n}"
            if it not in self.reps:
                self.reps.append(it)
                self.r_spin.values = self.reps

    def rem(self, cat):
        if cat == 'hybrid' and len(self.hybrids)>1:
            r = self.hybrids.pop()
            self.h_spin.values = self.hybrids
            if self.h_spin.text == r: self.h_spin.text = self.hybrids[0]
        elif cat == 'variant' and len(self.variants)>1:
            r = self.variants.pop()
            self.v_spin.values = self.variants
            if self.v_spin.text == r: self.v_spin.text = self.variants[0]
        elif cat == 'rep' and len(self.reps)>1:
            r = self.reps.pop()
            self.r_spin.values = self.reps
            if self.r_spin.text == r: self.r_spin.text = self.reps[0]

    def open_camera(self, instance):
        if not self.leaf_num.text.strip().isdigit():
            self._toast("❌ Введіть номер листка!")
            return
        self.manager.current = 'camera'

    def process_captured_photo(self, src_path):
        """Викликається автоматично при успішному знімку камери"""
        if not os.path.exists(src_path):
            return
        h, v, r = self.h_spin.text, self.v_spin.text, self.r_spin.text
        leaf = self.leaf_num.text.strip()
        stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        name = f"{h}_{v}_{r}_Листок{leaf}_{stamp}.jpg"
        
        # Отримуємо шлях до публічної папки документів для зручності користувача
        base_dir = self.get_output_directory()
        dest_dir = os.path.join(base_dir, 'Structured_Photos')
        os.makedirs(dest_dir, exist_ok=True)
        
        dest = os.path.join(dest_dir, name)
        shutil.copy2(src_path, dest)
        self.photo_path = dest
        self.photo_status.text = f"✅ {name[:25]}..."
        self.photo_status.color = (0, 0.6, 0, 1)
        self._toast("Фото успішно збережено")

    def get_output_directory(self):
        """Повертає шлях до папки, звідки користувач зможе забрати файли на Android 11+"""
        if platform == 'android':
            from android.storage import primary_external_storage_path
            # Зберігаємо в загальну папку Documents/LeafAreaMeter
            return os.path.join(primary_external_storage_path(), 'Documents', 'LeafAreaMeter')
        return os.path.join(App.get_running_app().user_data_dir, 'LeafAreaMeter')

    def calc(self, instance):
        if not self.photo_path or not os.path.exists(self.photo_path):
            self._toast("❌ Зробіть фото!")
            return
        try:
            S_ref = float(self.ref_area.text) if self.ref_area.text else 623.7
        except:
            self._toast("❌ Площа має бути числом!")
            return
        try:
            img = Image.open(self.photo_path)
            # Зменшуємо роздільну здатність для уникнення OOM (Out of memory) на телефонах
            if img.width > 1200 or img.height > 1200:
                ratio = min(1200 / img.width, 1200 / img.height)
                img = img.resize((int(img.width * ratio), int(img.height * ratio)), Image.Resampling.LANCZOS)
            
            arr = np.array(img.convert('RGB'))
            blurred = np.array(img.filter(ImageFilter.GaussianBlur(radius=2)))
            hsv = np.array(Image.fromarray(blurred).convert('HSV'))
            
            def create_mask(lower, upper):
                l = np.array([int(lower[0]*255/180), lower[1], lower[2]])
                u = np.array([int(upper[0]*255/180), upper[1], upper[2]])
                return ((hsv[:,:,0]>=l[0]) & (hsv[:,:,0]<=u[0]) &
                        (hsv[:,:,1]>=l[1]) & (hsv[:,:,1]<=u[1]) &
                        (hsv[:,:,2]>=l[2]) & (hsv[:,:,2]<=u[2]))

            mask_green = create_mask([35,40,40], [85,255,255])
            mask_white = create_mask([0,0,100], [180,40,255])
            
            # ВИПРАВЛЕНО: Оптимізований BFS пошук найбільшого білого об'єкта (паперу)
            visited = np.zeros_like(mask_white, dtype=bool)
            best_size, best = 0, None
            h, w = mask_white.shape
            
            # Крок сканування 4 для прискорення мобільних процесорів
            for y in range(0, h, 4):
                for x in range(0, w, 4):
                    if mask_white[y, x] and not visited[y, x]:
                        comp = np.zeros_like(mask_white, dtype=bool)
                        q = deque([(y, x)])
                        visited[y, x] = True  # МИТТЄВО мітимо як відвідане!
                        sz = 0
                        
                        while q:
                            cy, cx = q.popleft()
                            comp[cy, cx] = True
                            sz += 1
                            
                            for ny, nx in [(cy-1, cx), (cy+1, cx), (cy, cx-1), (cy, cx+1)]:
                                if 0 <= ny < h and 0 <= nx < w:
                                    if mask_white[ny, nx] and not visited[ny, nx]:
                                        visited[ny, nx] = True  # Запобігає зацикленню
                                        q.append((ny, nx))
                                        
                        if sz > best_size:
                            best_size, best = sz, comp
                            
            if best is None:
                self._toast("❌ Папір не знайдено!")
                return
                
            green_in = mask_green & best
            white_in = (mask_white & ~mask_green) & best
            Pg = np.count_nonzero(green_in)
            Pw = np.count_nonzero(white_in)
            total = Pg + Pw
            
            if total == 0:
                self._toast("❌ Помилка розпізнавання!")
                return
                
            S_leaf = (Pg / total) * S_ref
            cov = (Pg / total) * 100
            
            h, v, r = self.h_spin.text, self.v_spin.text, self.r_spin.text
            leaf = self.leaf_num.text.strip()
            self.result_label.text = f"✅ Площа: {S_leaf:.2f} см²\n📊 Заповнення: {cov:.1f}%\n{h} | {v}"
            
            # Збереження маски та CSV-звіту у публічну папку Documents
            stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            name = f"{h}_{v}_{r}_Листок{leaf}_{stamp}"
            base_dir = self.get_output_directory()
            
            os.makedirs(os.path.join(base_dir, 'Analysis_Masks'), exist_ok=True)
            mask_vis = np.zeros((arr.shape[0], arr.shape[1], 3), dtype=np.uint8)
            mask_vis[white_in > 0] = [128, 128, 128]
            mask_vis[green_in > 0] = [0, 255, 0] # Зелений колір для листка на масці
            Image.fromarray(mask_vis).save(os.path.join(base_dir, 'Analysis_Masks', f'MASK_{name}.jpg'))
            
            csv_path = os.path.join(base_dir, 'leaf_surface_reports.csv')
            fex = os.path.exists(csv_path) and os.path.getsize(csv_path) > 0
            with open(csv_path, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                if not fex:
                    writer.writerow(["Дата/Час", "Гібрид", "Варіант", "Повторність", "Номер Листка", "Площа (см²)", "Заповнення (%)"])
                writer.writerow([datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), h, v, r, leaf, f"{S_leaf:.2f}", f"{cov:.1f}"])
                
            self._toast(f"✅ Площа розрахована: {S_leaf:.1f} см²")
        except Exception as e:
            self._toast(f"❌ Помилка аналізу: {e}")

    def next_leaf(self, instance):
        cur = self.leaf_num.text.strip()
        if cur.isdigit(): 
            self.leaf_num.text = str(int(cur) + 1)
        self.photo_path = None
        self.photo_status.text = "Фото не зроблено"
        self.photo_status.color = (0.8,0,0,1)
        self.result_label.text = "Тут з'явиться результат"
        self._toast("🔄 Готово до наступного листка!")

    def _toast(self, msg):
        Popup(title='Повідомлення', content=Label(text=msg, font_size='16sp'), size_hint=(0.8, 0.25)).open()


class LeafApp(App):
    def build(self):
        Window.clearcolor = (0.95, 0.95, 0.95, 1)
        sm = ScreenManager()
        sm.add_widget(MainScreen(name='main'))
        sm.add_widget(CameraScreen(name='camera'))
        return sm
        
    def on_start(self):
        # Автоматичний запуск обробника подій камери від camera4kivy для Android
        if platform == 'android':
            from android.permissions import request_permissions, Permission
            def callback(permissions, results):
                if all(results):
                    print("Всі дозволи надано!")
            request_permissions([Permission.CAMERA, Permission.WRITE_EXTERNAL_STORAGE, Permission.READ_EXTERNAL_STORAGE], callback)

    def on_camera_image(self, path):
        """Службовий метод екосистеми camera4kivy, куди прилітає знімок скріншоту"""
        if path:
            main_screen = self.root.get_screen('main')
            main_screen.process_captured_photo(path)
            self.root.current = 'main'


if __name__ == '__main__':
    LeafApp().run()
