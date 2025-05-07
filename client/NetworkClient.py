import socket
import json
import threading
import logging
logger = logging.getLogger(__name__)

# В критических местах
logger.debug("Starting network request...")


class NetworkClient:
    def __init__(self, host='localhost', port=9000):
        self.host = host
        self.port = port
        self.socket = None
        self.connected = False
        self.lock = threading.Lock()
        self.timeout = 5.0

    def connect(self):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
            self.connected = True
            print("Подключение к серверу установлено")
        except Exception as e:
            print("Ошибка подключения:", e)

    def send_request(self, request):
        try:
            if not self.connected:
                self.connect()

            with self.lock:
                # Отправка
                data = json.dumps(request).encode('utf-8') + b'<END>'
                self.socket.sendall(data)

                # Получение ответа
                response_data = b''
                while True:
                    chunk = self.socket.recv(4096)
                    if not chunk:
                        break
                    response_data += chunk
                    if b'<END>' in chunk:
                        response_data = response_data.split(b'<END>')[0]
                        break

                # Декодирование
                try:
                    return json.loads(response_data.decode('utf-8'))
                except json.JSONDecodeError:
                    return {"status": "error", "message": "Неверный формат ответа"}

        except Exception as e:
            logger.error(f"Сетевой сбой: {str(e)}")
            return {"status": "error", "message": "Ошибка соединения"}


    def receive_data(self):
        # Этот метод можно использовать для получения данных в реальном времени
        self.socket.settimeout(self.timeout)
        try:
            while self.connected:
                data = self.socket.recv(4096)
                if data:
                    response = json.loads(data.decode('utf-8'))
                    print("Получены данные:", response)
                else:
                    break
        except Exception as e:
            print("Ошибка получения данных:", e)
        except socket.timeout:
            return {"status": "error", "message": "Response timeout"}
        finally:
            self.connected = False

    def close(self):
        if self.socket:
            self.socket.close()
            self.connected = False


if __name__ == '__main__':
    client = NetworkClient()
    #client.connect()
    client.close()

