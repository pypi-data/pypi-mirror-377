# pyservers/client.py
import socket
import threading

class PyClient:
    def __init__(self, host='localhost', port=8000):
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connected = False

    def connect(self):
        """Подключение к серверу"""
        try:
            self.socket.connect((self.host, self.port))
            self.connected = True
            print(f"[ПОДКЛЮЧЕН К СЕРВЕРУ] {self.host}:{self.port}")
            return True
        except Exception as e:
            print(f"[ОШИБКА ПОДКЛЮЧЕНИЯ] {e}")
            return False

    def send(self, message):
        """Отправка сообщения серверу"""
        if self.connected:
            try:
                if isinstance(message, str):
                    message = message.encode('utf-8')
                self.socket.send(message)
            except Exception as e:
                print(f"[ОШИБКА ОТПРАВКИ] {e}")
                self.connected = False

    def listen(self, callback=None):
        """Прослушивание сообщений от сервера"""
        def receive():
            while self.connected:
                try:
                    message = self.socket.recv(1024)
                    if message:
                        if callback:
                            callback(message)
                        else:
                            print(f"[СЕРВЕР] {message.decode('utf-8')}")
                    else:
                        break
                except:
                    break
            self.connected = False
            print("[ПОТЕРЯНО СОЕДИНЕНИЕ]")

        listen_thread = threading.Thread(target=receive)
        listen_thread.daemon = True
        listen_thread.start()
        return listen_thread

    def disconnect(self):
        """Отключение от сервера"""
        self.connected = False
        try:
            self.socket.close()
        except:
            pass