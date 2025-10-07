import socket
import json

def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(('localhost', 12345))
    server_socket.listen(1)
    print("Сервер запущен и ожидает подключений...")

    try:
        while True:
            client_socket, client_address = server_socket.accept()
            print(f"Подключение установлено с {client_address}")

            try:
                while True:
                    data = client_socket.recv(1024)
                    if not data:
                        break

                    message = data.decode().strip()
                    print(f"Получено сообщение: {message}")

                    # Обработка данных локации
                    if message.startswith("LOCATION_DATA:"):
                        try:
                            location_json = message.replace("LOCATION_DATA:", "").strip()
                            location_data = json.loads(location_json)
                            print("Данные локации получены:")
                            print(f"  Широта: {location_data.get('latitude')}")
                            print(f"  Долгота: {location_data.get('longitude')}")
                            print(f"  Высота: {location_data.get('altitude')}")
                            print(f"  Время: {location_data.get('time_formatted')}")
                            
                            response = f"Локация получена: {location_data.get('latitude')}, {location_data.get('longitude')}"
                        except json.JSONDecodeError as e:
                            response = f"Ошибка парсинга локации: {e}"
                    else:
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
