import requests
import json

def send_json(api_url, data, headers=None):
    """
    Универсальная функция для отправки данных на API эндпоинт методом POST.
    
    Поддерживает на вход:
    - dict (Python словарь)
    - list (Python список)
    - str (JSON-строка)

    Автоматически сериализует данные в JSON, если нужно.
    
    :param api_url: URL API
    :param data: dict, list или JSON-строка
    :param headers: dict — дополнительные заголовки (опционально)
    :return: dict или list — распарсенный JSON ответ
    """
    if headers is None:
        headers = {}
    
    headers['Content-Type'] = 'application/json'

    # Если data — строка, пытаемся её распарсить в объект, чтобы убедиться, что это валидный JSON
    if isinstance(data, str):
        try:
            parsed_data = json.loads(data)
        except json.JSONDecodeError:
            raise ValueError("Строка не является валидным JSON")
    else:
        parsed_data = data  # dict или list оставляем как есть

    try:
        # Сериализация объекта Python обратно в JSON для отправки
        response = requests.post(api_url, headers=headers, data=json.dumps(parsed_data))
        response.raise_for_status()
        
        # Возвращаем ответ как Python объект
        return response.json()
    
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP ошибка: {http_err}")
    except requests.exceptions.RequestException as err:
        print(f"Ошибка запроса: {err}")
    except json.JSONDecodeError:
        print("Ошибка: ответ не является валидным JSON")
