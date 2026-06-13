from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.spinner import Spinner
from kivy.clock import Clock
from kivy.utils import platform
import threading
import sys
import traceback

class SovereignApp(App):
    def build(self):
        try:
            # 1. Muat AI-nya
            sys.path.insert(0, '.')
            from sovereign_ai import SovereignAI
            self.ai = SovereignAI()
            
            # 2. Bangun UI
            layout = BoxLayout(orientation='vertical', padding=10, spacing=8)
            layout.add_widget(Label(text='SOVEREIGN AI', font_size=24, bold=True, size_hint=(1, 0.05), color=(0, 1, 0.2, 1)))
            
            self.mode = Spinner(text='Audit Kode', values=['Audit Kode', 'Review Kode', 'Scan Folder', 'Create Code', 'Kristalisasi'], size_hint=(1, 0.06))
            layout.add_widget(self.mode)
            
            self.input = TextInput(hint_text='Tempel kode atau path folder di sini...', size_hint=(1, 0.4), background_color=(0.05, 0.05, 0.05, 1), foreground_color=(0, 1, 0.2, 1))
            layout.add_widget(self.input)
            
            btn = Button(text='▶ JALANKAN', size_hint=(1, 0.08), background_color=(0, 0.5, 0, 1))
            btn.bind(on_press=self.jalankan_tugas)
            layout.add_widget(btn)
            
            self.output = TextInput(text='Sistem Siap.', readonly=True, size_hint=(1, 0.4), background_color=(0.05, 0.05, 0.05, 1), foreground_color=(0, 1, 0.2, 1))
            layout.add_widget(self.output)
            
            return layout

        except Exception as e:
            error_msg = traceback.format_exc()
            layout = BoxLayout(orientation='vertical', padding=10)
            layout.add_widget(Label(text='CRASH REPORT', color=(1, 0, 0, 1), size_hint=(1, 0.1), bold=True))
            error_box = TextInput(text=error_msg, readonly=True, foreground_color=(1, 0, 0, 1))
            layout.add_widget(error_box)
            return layout

    def on_start(self):
        # Minta izin SETELAH layar muncul agar Android tidak panik
        if platform == 'android':
            try:
                from android.permissions import request_permissions, Permission
                request_permissions([
                    Permission.READ_EXTERNAL_STORAGE, 
                    Permission.WRITE_EXTERNAL_STORAGE,
                    Permission.INTERNET
                ])
            except Exception as e:
                self.output.text = f"Error Izin: {str(e)}"

    def jalankan_tugas(self, instance):
        self.output.text = 'Processing...'
        def task():
            mode = self.mode.text
            data = self.input.text.strip()
            try:
                if mode == 'Audit Kode':
                    hasil = self.ai.audit(data)
                    Clock.schedule_once(lambda dt: setattr(self.output, 'text', f'Ditemukan {len(hasil)} celah'))
                elif mode == 'Review Kode':
                    hasil = self.ai.review(data)
                    Clock.schedule_once(lambda dt: setattr(self.output, 'text', f"Skor: {hasil['skor_keamanan']:.2f} | Anchors: {hasil['anchors_ditemukan']} | Voids: {len(hasil['voids'])}"))
                elif mode == 'Scan Folder':
                    hasil = self.ai.scan_folder(data)
                    Clock.schedule_once(lambda dt: setattr(self.output, 'text', f'Files scanned | Findings: {len(hasil)}'))
                elif mode == 'Create Code':
                    kode, review = self.ai.ciptakan(data)
                    Clock.schedule_once(lambda dt: setattr(self.output, 'text', kode))
                elif mode == 'Kristalisasi':
                    hasil = self.ai.kristalisasi_niat('exploit', data)
                    Clock.schedule_once(lambda dt: setattr(self.output, 'text', f'Payload: {len(hasil)}'))
            except Exception as e:
                error_msg = traceback.format_exc()
                Clock.schedule_once(lambda dt: setattr(self.output, 'text', f'ERROR:\n{error_msg}'))
        threading.Thread(target=task, daemon=True).start()

if __name__ == '__main__':
    SovereignApp().run()
