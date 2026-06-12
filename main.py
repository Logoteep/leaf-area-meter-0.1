# -*- coding: utf-8 -*-
"""
Вимірювач площі листка (APK-версія без камери).
Кнопки: "Вибрати фото" та "Останнє фото". Обробка: Pillow.
"""

import os, csv, shutil, datetime
from PIL import Image, ImageFilter
from collections import deque
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.uix.filechooser import FileChooserListView
from kivy.core.window import Window
from kivy.metrics import dp


class LeafApp(App):
    def build(self):
        Window.clearcolor = (0.98, 0.98, 0.98, 1)
        self.photo_path = None
        self.hybrids = ["Гібрид/сорт 1"]
        self.variants = ["Варіант 1 (контроль)"]
        self.reps = ["Повторність 1"]

        root = BoxLayout(orientation='vertical', padding=dp(15), spacing=dp(10))
        scroll = ScrollView()
        content = BoxLayout(orientation='vertical', spacing=dp(10), size_hint_y=None)
        content.bind(minimum_height=content.setter('height'))

        content.add_widget(Label(text="🌻 Вимірювач площі листка", size_hint_y=None, height=dp(50),
                                 font_size='22sp', bold=True, color=(0,0.3,0,1)))

        # Гібрид
        content.add_widget(Label(text="Гібрид / сорт:", size_hint_y=None, height=dp(30), font_size='18sp', color=(0,0,0,1)))
        h_box = BoxLayout(orientation='horizontal', spacing=5, size_hint_y=None, height=dp(50))
        self.h_spin = Spinner(text=self.hybrids[0], values=self.hybrids, size_hint_x=0.7,
                              background_color=(1,1,1,1), color=(0,0,0,1), font_size='16sp')
        h_box.add_widget(self.h_spin)
        h_box.add_widget(Button(text="-", size_hint_x=0.15, background_color=(0.8,0.2,0.2,1),
                                on_press=lambda x: self.rem('hybrid')))
        h_box.add_widget(Button(text="+", size_hint_x=0.15, background_color=(0.2,0.6,0.2,1),
                                on_press=lambda x: self.add('hybrid')))
        content.add_widget(h_box)

        # Варіант
        content.add_widget(Label(text="Варіант:", size_hint_y=None, height=dp(30), font_size='18sp', color=(0,0,0,1)))
        v_box = BoxLayout(orientation='horizontal', spacing=5, size_hint_y=None, height=dp(50))
        self.v_spin = Spinner(text=self.variants[0], values=self.variants, size_hint_x=0.7,
                              background_color=(1,1,1,1), color=(0,0,0,1), font_size='16sp')
        v_box.add_widget(self.v_spin)
        v_box.add_widget(Button(text="-", size_hint_x=0.15, background_color=(0.8,0.2,0.2,1),
                                on_press=lambda x: self.rem('variant')))
        v_box.add_widget(Button(text="+", size_hint_x=0.15, background_color=(0.2,0.6,0.2,1),
                                on_press=lambda x: self.add('variant')))
        content.add_widget(v_box)

        # Повторність
        content.add_widget(Label(text="Повторність:", size_hint_y=None, height=dp(30), font_size='18sp', color=(0,0,0,1)))
        r_box = BoxLayout(orientation='horizontal', spacing=5, size_hint_y=None, height=dp(50))
        self.r_spin = Spinner(text=self.reps[0], values=self.reps, size_hint_x=0.7,
                              background_color=(1,1,1,1), color=(0,0,0,1), font_size='16sp')
        r_box.add_widget(self.r_spin)
        r_box.add_widget(Button(text="-", size_hint_x=0.15, background_color=(0.8,0.2,0.2,1),
                                on_press=lambda x: self.rem('rep')))
        r_box.add_widget(Button(text="+", size_hint_x=0.15, background_color=(0.2,0.6,0.2,1),
                                on_press=lambda x: self.add('rep')))
        content.add_widget(r_box)

        content.add_widget(Label(text="Номер листка:", size_hint_y=None, height=dp(30), font_size='18sp', color=(0,0,0,1)))
        self.leaf_num = TextInput(hint_text="Ціле число", input_filter='int', size_hint_y=None, height=dp(50),
                                  multiline=False, background_color=(1,1,1,1), foreground_color=(0,0,0,1), font_size='16sp')
        content.add_widget(self.leaf_num)

        content.add_widget(Label(text="Площа еталона (см²):", size_hint_y=None, height=dp(30), font_size='18sp', color=(0,0,0,1)))
        self.ref_area = TextInput(text="623.7", size_hint_y=None, height=dp(50), multiline=False,
                                  background_color=(1,1,1,1), foreground_color=(0,0,0,1), font_size='16sp')
        content.add_widget(self.ref_area)

        # Дві кнопки поруч
        btn_box = BoxLayout(orientation='horizontal', spacing=5, size_hint_y=None, height=dp(55))
        btn_choose = Button(text="📁 Вибрати фото", background_color=(0.2,0.6,0.2,1), font_size='18sp', color=(1,1,1,1),
                            on_press=self.choose_photo)
        btn_latest = Button(text="⚡ Останнє фото", background_color=(0.6,0.4,0.2,1), font_size='18sp', color=(1,1,1,1),
                            on_press=self.use_latest_photo)
        btn_box.add_widget(btn_choose)
        btn_box.add_widget(btn_latest)
        content.add_widget(btn_box)

        self.photo_status = Label(text="Фото не вибрано", size_hint_y=None, height=dp(30),
                                  color=(0.8,0,0,1), font_size='16sp')
        content.add_widget(self.photo_status)

        content.add_widget(Button(text="🔍 Розрахувати площу", size_hint_y=None, height=dp(55),
                                  background_color=(0.2,0.4,0.8,1), font_size='18sp', color=(1,1,1,1),
                                  on_press=self.calculate_area))
        self.result_label = Label(text="Тут з'явиться результат", size_hint_y=None, height=dp(100),
                                  halign='center', valign='middle', color=(0,0,0,1), font_size='16sp')
        content.add_widget(self.result_label)

        content.add_widget(Button(text="🔄 Наступний листок", size_hint_y=None, height=dp(55),
                                  background_color=(0.5,0.5,0.5,1), font_size='18sp', color=(1,1,1,1),
                                  on_press=self.next_leaf))

        scroll.add_widget(content)
        root.add_widget(scroll)
        return root

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

    def choose_photo(self, instance):
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)
        fc = FileChooserListView(path='/storage/emulated/0', filters=['*.jpg', '*.jpeg', '*.png'])
        content.add_widget(fc)
        btns = BoxLayout(size_hint_y=None, height=50, spacing=10)
        btn_cancel = Button(text='Скасувати')
        btn_select = Button(text='Вибрати', background_color=(0.2,0.6,0.2,1))
        btns.add_widget(btn_cancel)
        btns.add_widget(btn_select)
        content.add_widget(btns)
        popup = Popup(title='Вибір фото', content=content, size_hint=(0.9,0.9))
        btn_cancel.bind(on_press=popup.dismiss)
        btn_select.bind(on_press=lambda x: self._on_photo_selected(fc, popup))
        popup.open()

    def _on_photo_selected(self, fc, popup):
        if fc.selection:
            src = fc.selection[0]
            popup.dismiss()
            self._copy_and_set_photo(src)

    def use_latest_photo(self, instance):
        """Знаходить останнє фото в DCIM/Camera або Pictures."""
        if not self.leaf_num.text.strip().isdigit():
            self._toast("❌ Введіть номер листка!")
            return
        search_dirs = [
            '/storage/emulated/0/DCIM/Camera',
            '/storage/emulated/0/Pictures'
        ]
        latest_file = None
        latest_time = 0
        for d in search_dirs:
            if os.path.exists(d):
                for f in os.listdir(d):
                    if f.lower().endswith(('.jpg', '.jpeg', '.png')):
                        full = os.path.join(d, f)
                        mtime = os.path.getmtime(full)
                        if mtime > latest_time:
                            latest_time = mtime
                            latest_file = full
        if latest_file:
            self._copy_and_set_photo(latest_file)
        else:
            self._toast("❌ Не знайдено фото. Зробіть знімок камерою.")

    def _copy_and_set_photo(self, src):
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

    def calculate_area(self, instance):
        if not self.photo_path or not os.path.exists(self.photo_path):
            self._toast("❌ Виберіть фото!")
            return
        try:
            S_ref = float(self.ref_area.text) if self.ref_area.text else 623.7
        except:
            self._toast("❌ Площа — число!")
            return
        try:
            img = Image.open(self.photo_path)
            if img.width > 1500 or img.height > 1500:
                ratio = min(1500/img.width, 1500/img.height)
                img = img.resize((int(img.width*ratio), int(img.height*ratio)))
            img = img.filter(ImageFilter.GaussianBlur(radius=2))
            hsv = img.convert('HSV')
            w, h = img.size
            hsv_data = list(hsv.getdata())
            mask_green = [self._is_green(p) for p in hsv_data]
            mask_white = [self._is_white(p) for p in hsv_data]
            paper = self._find_largest_object_2d(mask_white, w, h)
            if not paper:
                self._toast("❌ Папір не знайдено!")
                return
            P_green, P_white = 0, 0
            for i in range(len(mask_green)):
                if paper[i]:
                    if mask_green[i]:
                        P_green += 1
                    elif mask_white[i]:
                        P_white += 1
            total = P_green + P_white
            if total == 0:
                self._toast("❌ Помилка підрахунку!")
                return
            S_leaf = (P_green/total)*S_ref
            cov = (P_green/total)*100
            self.result_label.text = f"✅ Площа: {S_leaf:.2f} см²\n📊 Заповнення: {cov:.1f}%"
            self._save_results(S_leaf, cov, img, mask_green, mask_white, paper)
            self._toast(f"✅ Площа: {S_leaf:.1f} см²")
        except Exception as e:
            self._toast(f"❌ Помилка: {e}")

    def _is_green(self, p):
        return (35*255//180 <= p[0] <= 85*255//180) and p[1] >= 40 and p[2] >= 40

    def _is_white(self, p):
        return p[1] <= 40 and p[2] >= 100

    def _find_largest_object_2d(self, mask_flat, w, h):
        grid = [mask_flat[i*w:(i+1)*w] for i in range(h)]
        visited = [[False]*w for _ in range(h)]
        best, best_size = None, 0
        for y in range(h):
            for x in range(w):
                if grid[y][x] and not visited[y][x]:
                    q = deque([(y,x)])
                    visited[y][x] = True
                    size, comp = 0, set()
                    while q:
                        cy, cx = q.popleft()
                        size += 1
                        comp.add((cy,cx))
                        for ny, nx in [(cy-1,cx),(cy+1,cx),(cy,cx-1),(cy,cx+1)]:
                            if 0 <= ny < h and 0 <= nx < w and grid[ny][nx] and not visited[ny][nx]:
                                visited[ny][nx] = True
                                q.append((ny,nx))
                    if size > best_size:
                        best_size, best = size, comp
        if best is None:
            return None
        return [True if (i//w, i%w) in best else False for i in range(w*h)]

    def _save_results(self, S_leaf, coverage, img, mask_green, mask_white, paper):
        stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        h, v, r, leaf = self.h_spin.text, self.v_spin.text, self.r_spin.text, self.leaf_num.text.strip()
        name = f"{h}_{v}_{r}_Листок{leaf}_{stamp}"
        base = App.get_running_app().user_data_dir
        os.makedirs(os.path.join(base, 'Analysis_Masks'), exist_ok=True)
        mask_img = Image.new('RGB', img.size)
        pixels = [(0,0,0)] * (img.width * img.height)
        for i in range(len(pixels)):
            if paper[i]:
                pixels[i] = (255,255,255) if mask_green[i] else (128,128,128)
        mask_img.putdata(pixels)
        mask_img.save(os.path.join(base, 'Analysis_Masks', f'MASK_{name}.jpg'))
        csv_path = os.path.join(base, 'leaf_surface_reports.csv')
        fex = os.path.exists(csv_path) and os.path.getsize(csv_path) > 0
        with open(csv_path, 'a', newline='', encoding='utf-8') as f:
            w = csv.writer(f)
            if not fex:
                w.writerow(["Дата/Час","Гібрид","Варіант","Повторність","Номер Листка","Площа (см²)","Заповнення (%)"])
            w.writerow([datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), h, v, r, leaf, f"{S_leaf:.2f}", f"{coverage:.1f}"])

    def next_leaf(self, instance):
        cur = self.leaf_num.text.strip()
        if cur.isdigit(): self.leaf_num.text = str(int(cur)+1)
        self.photo_path = None
        self.photo_status.text = "Фото не вибрано"
        self.photo_status.color = (0.8,0,0,1)
        self.result_label.text = "Тут з'явиться результат"
        self._toast("🔄 Готово до наступного листка!")

    def _toast(self, msg):
        popup = Popup(title='Повідомлення', content=Label(text=msg, font_size='16sp'), size_hint=(0.7, 0.3))
        popup.open()


if __name__ == '__main__':
    LeafApp().run()
