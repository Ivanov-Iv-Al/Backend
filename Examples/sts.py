import zmq
import json
from datetime import datetime


def start_zeromq_server():
    context = zmq.Context()

    socket = context.socket(zmq.REP)

    socket.bind("tcp://*:12345")

    print("ZeroMQ сервер запущен на порту 12345")

    try:
        while True:
            message = socket.recv_string()
            print(f"Получено сообщение: {message}")

            if message.startswith("LOCATION_DATA:"):
                try:
                    location_json = message.replace("LOCATION_DATA:", "").strip()
                    location_data = json.loads(location_json)

                    print("Данные о локации::")
                    print(f"Широта: {location_data.get('latitude')}")
                    print(f"Долгота: {location_data.get('longitude')}")
                    print(f"Высота: {location_data.get('altitude')} м")
                    print(f"Точность: {location_data.get('accuracy')} м")
                    print(f"Время: {location_data.get('time_formatted')}")

                    save_location_to_file(location_data)

                    response = f"SUCCESS: Локация получена {datetime.now().strftime('%H:%M:%S')}"

                except json.JSONDecodeError as e:
                    response = f"ERROR: Ошибка парсинга JSON - {e}"
                except Exception as e:
                    response = f"ERROR: {e}"
            else:
                response = f"ECHO: {message}"

            socket.send_string(response)

    except KeyboardInterrupt:
        print("\nСервер остановлен")
    finally:
        socket.close()
        context.term()


def save_location_to_file(location_data):
    try:
        filename = f"locations_{datetime.now().strftime('%Y%m%d')}.json"

        try:
            with open(filename, 'r', encoding='utf-8') as f:
                existing_data = json.load(f)
        except FileNotFoundError:
            existing_data = []

        existing_data.append({
            **location_data,
            "received_at": datetime.now().isoformat()
        })

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(existing_data, f, ensure_ascii=False, indent=2)

        print(f"Данные сохранены в {filename}")

    except Exception as e:
        print(f"Ошибка сохранения в файл: {e}")


if __name__ == "__main__":
    start_zeromq_server()