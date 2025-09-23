import socket


def start_server():
    # Создаем сокет
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # Привязываем сокет к IP-адресу и порту
    server_socket.bind(('localhost', 12345))

    # Слушаем входящие соединения
    server_socket.listen(1)
    print("Сервер запущен и ожидает подключений...")

    try:
        while True:
            # Принимаем входящее соединение
            client_socket, client_address = server_socket.accept()
            print(f"Подключение установлено с {client_address}")

            try:
                while True:
                    # Получаем данные от клиента
                    data = client_socket.recv(1024)
                    if not data:
                        break

                    message = data.decode().strip()
                    print(f"Получено сообщение: {message}")

                    # Отправляем ответ
                    response = f"Сервер получил: {message}"
                    client_socket.send(f"{response}\n".encode())

            except Exception as e:
                print(f"Ошибка: {e}")
            finally:
                client_socket.close()
                print("Соединение закрыто")

    except KeyboardInterrupt:
        print("Сервер остановлен")
    finally:
        server_socket.close()


if __name__ == "__main__":
    start_server()