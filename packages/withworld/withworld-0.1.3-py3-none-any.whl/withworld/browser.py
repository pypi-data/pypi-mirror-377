import webbrowser
import pyautogui
import time
import re
import pyperclip
import sys
from withworld.autokey import paste, enter, esc, f12, close_tab
from withworld.bufer import get_bufer, load_to_bufer

def open_browser_console(url):
    """
    Открывает браузер с указанным URL. и ждет 5 секунд
    """
    
    webbrowser.open(url)
    time.sleep(5)  # даём время открыть браузер и кликнуть на него
    f12()
    esc()
    esc()

    paste("copy('js_panel')")
    esc()
    esc()
    paste("copy('js_panel')")
    if get_bufer() == 'js_panel':
        return True
    else:
        return False


def get_element(selector):
    """Получает код элемента по селектору"""
    selector = selector.replace("\\", "\\\\")   # удвоение всех слэшей
    selector = re.sub(r"(:)", r"\\\1", selector) # двоеточие -> \:
    selector = re.sub(r"(\[)", r"\\\1", selector) # [ -> \[
    selector = re.sub(r"(\])", r"\\\1", selector) # ] -> \]
    paste(f"copy(document.querySelector('{selector}'))")
    time.sleep(0.5)
    return get_bufer()


def click_element(selector):
    """Кликает по элементу"""
    selector = selector.replace("\\", "\\\\")   # удвоение всех слэшей
    selector = re.sub(r"(:)", r"\\\1", selector) # двоеточие -> \:
    selector = re.sub(r"(\[)", r"\\\1", selector) # [ -> \[
    selector = re.sub(r"(\])", r"\\\1", selector) # ] -> \]
    paste(f"document.querySelector('{selector}').click()")
    time.sleep(0.5)


def check_element(selector):
    """Возвращает True или False в зависимости от существования элемента на странице"""
    selector = selector.replace("\\", "\\\\")   # удвоение всех слэшей
    selector = re.sub(r"(:)", r"\\\1", selector) # двоеточие -> \:
    selector = re.sub(r"(\[)", r"\\\1", selector) # [ -> \[
    selector = re.sub(r"(\])", r"\\\1", selector) # ] -> \]
    paste(f"copy(document.querySelector('{selector}'))")
    return get_bufer() != 'null'



