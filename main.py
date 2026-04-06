# Умная автозамена раскладки — OOP версия
import keyboard
import pystray
from PIL import Image, ImageDraw
import time
import sys
from abc import ABC, abstractmethod

class LayoutConverter(ABC):
    """Абстрактный конвертер раскладки"""
    def __init__(self):
        self.en_to_ru = {
            'q':'й','w':'ц','e':'у','r':'к','t':'е','y':'н','u':'г','i':'ш','o':'щ','p':'з',
            '[':'х',']':'ъ','a':'ф','s':'ы','d':'в','f':'а','g':'п','h':'р','j':'о','k':'л',
            'l':'д',';':'ж',"'":'э','z':'я','x':'ч','c':'с','v':'м','b':'и','n':'т','m':'ь',
            ',':'б','.':'ю',
            'Q':'Й','W':'Ц','E':'У','R':'К','T':'Е','Y':'Н','U':'Г','I':'Ш','O':'Щ','P':'З',
            '{':'Х','}':'Ъ','A':'Ф','S':'Ы','D':'В','F':'А','G':'П','H':'Р','J':'О','K':'Л',
            'L':'Д',':':'Ж','"':'Э','Z':'Я','X':'Ч','C':'С','V':'М','B':'И','N':'Т','M':'Ь',
            '<':'Б','>':'Ю'
        }
        self.current_word = ""

    @abstractmethod
    def fix_word(self, word: str) -> str:
        pass

    def is_russian(self, key: str) -> bool:
        return key in "йцукенгшщзхъфывапролджэячсмитьбюЙЦУКЕНГШЩЗХЪФЫВАПРОЛДЖЭЯЧСМИТЬБЮ"


class RuConverter(LayoutConverter):
    def fix_word(self, word: str) -> str:
        return ''.join(self.en_to_ru.get(c, c) for c in word)


class AutoLayoutApp:
    def __init__(self):
        self.converter = RuConverter()
        self.enabled = True
        self.last_word = ""

    def create_tray_icon(self):
        img = Image.new('RGB', (64, 64), color=(0, 120, 215))
        draw = ImageDraw.Draw(img)
        draw.text((18, 15), "RU", fill=(255, 255, 255))
        return img

    def on_key(self, event):
        if not self.enabled or event.event_type != "down":
            return

        key = event.name

        # Конец слова
        if key in ['space', 'enter', 'tab', '.', ',', '!', '?', ';', ':']:
            self.last_word = ""
            return

        # Backspace
        if key == 'backspace':
            if self.last_word:
                self.last_word = self.last_word[:-1]
            return

        # Игнорируем русские буквы
        if self.converter.is_russian(key):
            return

        # Добавляем только английские символы
        if len(key) == 1 and key.isascii() and not key.isspace():
            self.last_word += key
            print(f"Буфер: {self.last_word}")   # отладка

    def convert_last(self):
        if not self.enabled or not self.last_word:
            return

        fixed = self.converter.fix_word(self.last_word)

        if fixed != self.last_word:
            # Удаляем старое слово
            for _ in range(len(self.last_word)):
                keyboard.send('backspace')
                time.sleep(0.007)
            keyboard.write(fixed)
            print(f"✅ Исправлено: {self.last_word} → {fixed}")
            self.last_word = ""

    def toggle(self, icon=None, item=None):
        self.enabled = not self.enabled
        status = "ВКЛ ✅" if self.enabled else "ВЫКЛ ❌"
        print(f"Автозамена: {status}")
        if icon:
            icon.notify("Автозамена", f"Статус: {status}")
            icon.update_menu()

    def run(self):
        keyboard.hook(self.on_key)
        keyboard.add_hotkey('f8', self.convert_last)

        menu = pystray.Menu(
            pystray.MenuItem(lambda i: f"Автозамена: {'Вкл ✅' if self.enabled else 'Выкл ❌'}",
                            self.toggle, checked=lambda i: self.enabled),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Выход", lambda i, it: (i.stop(), sys.exit(0)))
        )

        icon = pystray.Icon("ru_fix", self.create_tray_icon(), "Автозамена (F8)", menu)

        print("🚀 Автозамена запущена!")
        print("Нажми F8 после набора слова — оно исправится")
        print("Пример: pyfxtybt → F8 → привет")

        icon.run()


if __name__ == "__main__":
    app = AutoLayoutApp()
    app.run()
