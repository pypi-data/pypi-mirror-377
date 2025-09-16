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


def POST(url, body):
    """на вход ждем url и body"""
        
    requset = '''
    // Получаем CSRF-токен из куки
    function getCsrfToken() {
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            const [name, value] = cookie.trim().split('=');
            if (name === 'csrfToken') {
                return value;
            }
        }
        return '';
    }
    
    // Альтернативно: ищем токен в meta-тегах
    function getCsrfTokenFromMeta() {
        const metaTag = document.querySelector('meta[name="csrf-token"]');
        return metaTag ? metaTag.content : '';
    }
    
    // Основная функция запроса
    async function fetchGoodsList() {
        const csrfToken = getCsrfToken() || getCsrfTokenFromMeta();
        
        if (!csrfToken) {
            console.error('CSRF token not found');
            return;
        }
    
        try {
            const response = await fetch(\'''' + url + '''\', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRF-Token': csrfToken
                },
                body: JSON.stringify(''' + body + ''')
            });
    
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
    
            const data = await copy(response.json());
            console.log('Успешный ответ:', data);
            return data;
        } catch (error) {
            console.error('Ошибка:', error);
        }
    }
    
    // Запускаем запрос
    fetchGoodsList();'''
    paste(requset)