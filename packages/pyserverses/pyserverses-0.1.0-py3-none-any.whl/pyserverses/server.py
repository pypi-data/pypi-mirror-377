# pyservers/server.py
import socket
import threading

class PyServer:
    def __init__(self, host='localhost', port=8000):
        self.host = host
        self.port = port
        self.clients = []
        self.running = False

    def handle_client(self, client_socket, address):
        """Обработка подключения клиента"""
        print(f"[НОВОЕ ПОДКЛЮЧЕНИЕ] {address}")
        
        while self.running:
            try:
                message = client_socket.recv(1024)
                if message:
                    print(f"[СООБЩЕНИЕ ОТ {address}] {message.decode('utf-8')}")
                    self.broadcast(message, client_socket)
                else:
                    break
            except:
                break
        
        self.clients.remove(client_socket)
        client_socket.close()
        print(f"[ОТКЛЮЧЕНИЕ] {address}")

    def broadcast(self, message, sender_socket):
        """Отправка сообщения всем клиентам, кроме отправителя"""
        for client in self.clients[:]:  # копия списка для безопасного удаления
            if client != sender_socket:
                try:
                    client.send(message)
                except:
                    client.close()
                    self.clients.remove(client)

    def send_to_all(self, message):
        """Отправка сообщения всем клиентам"""
        for client in self.clients[:]:
            try:
                client.send(message.encode('utf-8'))
            except:
                client.close()
                self.clients.remove(client)

    def start(self):
        """Запуск сервера"""
        self.running = True
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((self.host, self.port))
        server_socket.listen()
        
        print(f"[СЕРВЕР ЗАПУЩЕН] {self.host}:{self.port}")
        
        try:
            while self.running:
                client_socket, address = server_socket.accept()
                self.clients.append(client_socket)
                
                client_thread = threading.Thread(
                    target=self.handle_client, 
                    args=(client_socket, address)
                )
                client_thread.daemon = True
                client_thread.start()
                
        except KeyboardInterrupt:
            print("\n[СЕРВЕР ОСТАНОВЛЕН]")
        finally:
            self.stop()

    def stop(self):
        """Остановка сервера"""
        self.running = False
        for client in self.clients[:]:
            try:
                client.close()
            except:
                pass
        self.clients.clear()