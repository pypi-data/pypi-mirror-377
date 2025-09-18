# pyserverses/server.py
import socket
import threading
import json

class PyServer:
    def __init__(self, host='localhost', port=8000):
        self.host = host
        self.port = port
        self.routes = {}  # для маршрутов
        self.clients = []
        self.running = False

    def route(self, path, methods=['GET']):
        """Декоратор для добавления маршрутов"""
        def wrapper(handler):
            self.routes[path] = {
                'handler': handler,
                'methods': methods
            }
            return handler
        return wrapper

    def handle_request(self, request):
        """Парсинг HTTP запроса"""
        lines = request.split('\n')
        if not lines:
            return None, None, {}
            
        # Первая строка: метод, путь, версия
        request_line = lines[0].strip()
        parts = request_line.split(' ')
        if len(parts) < 3:
            return None, None, {}
            
        method = parts[0]
        path = parts[1]
        
        # Заголовки
        headers = {}
        for line in lines[1:]:
            if ':' in line:
                key, value = line.split(':', 1)
                headers[key.strip().lower()] = value.strip()
                
        return method, path, headers

    def handle_client(self, client_socket, address):
        """Обработка клиента"""
        try:
            request_data = client_socket.recv(1024).decode('utf-8')
            if not request_data:
                return
                
            method, path, headers = self.handle_request(request_data)
            
            if method and path:
                # Ищем маршрут
                if path in self.routes:
                    route = self.routes[path]
                    if method in route['methods']:
                        # Вызываем обработчик
                        response = route['handler']()
                        client_socket.send(response.encode('utf-8'))
                        return
                
                # Страница не найдена
                response = """HTTP/1.1 404 Not Found
Content-Type: text/html; charset=utf-8

<h1>404 - Not Found</h1>"""
                client_socket.send(response.encode('utf-8'))
            else:
                # Не HTTP запрос - обычный клиент
                print(f"[КЛИЕНТ] {address}")
                
        except Exception as e:
            print(f"[ОШИБКА] {e}")
        finally:
            client_socket.close()

    def start(self):
        """Запуск сервера"""
        self.running = True
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((self.host, self.port))
        server_socket.listen(5)
        
        print(f"[ВЕБ-СЕРВЕР ЗАПУЩЕН] http://{self.host if self.host != '0.0.0.0' else 'localhost'}:{self.port}")
        
        try:
            while self.running:
                client_socket, address = server_socket.accept()
                client_thread = threading.Thread(
                    target=self.handle_client, 
                    args=(client_socket, address)
                )
                client_thread.daemon = True
                client_thread.start()
        except KeyboardInterrupt:
            print("\n[СЕРВЕР ОСТАНОВЛЕН]")
        finally:
            server_socket.close()

# Вспомогательные функции
def html_response(content, status="200 OK"):
    return f"""HTTP/1.1 {status}
Content-Type: text/html; charset=utf-8

{content}"""

def json_response(data, status="200 OK"):
    return f"""HTTP/1.1 {status}
Content-Type: application/json

{json.dumps(data)}"""