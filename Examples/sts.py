import zmq
import json
import psycopg2
from datetime import datetime
import sys
import time
import traceback
import os


class Database:
    def __init__(self):
        try:
            self.conn = psycopg2.connect(
                dbname="location_tracking",
                user="postgres",
                password="123456",
                host="localhost",
                port=5432
            )
            self.create_simple_table()
            print("Подключено к PostgreSQL")
        except Exception as e:
            print(f"Ошибка подключения к БД: {e}")
            sys.exit(1)

    def create_simple_table(self):
        cursor = self.conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS location_data_simple (
                id SERIAL PRIMARY KEY,
                timestamp TIMESTAMP,
                latitude DOUBLE PRECISION,
                longitude DOUBLE PRECISION,
                altitude DOUBLE PRECISION,
                accuracy FLOAT,
                speed FLOAT,
                time_ms BIGINT,
                net_type VARCHAR(50),
                signal_lvl VARCHAR(50)
            )
        """)
        self.conn.commit()
        cursor.close()

    def save_simple_location(self, data):
        try:
            if not isinstance(data, dict):
                print(f"Ошибка: данные не являются словарем, тип: {type(data)}")
                return False

            cursor = self.conn.cursor()

            timestamp = data.get('timestamp') or int(time.time() * 1000)
            time_ms = data.get('time', timestamp)

            query = """
            INSERT INTO location_data_simple (
                timestamp, latitude, longitude, altitude, accuracy, speed,
                time_ms, net_type, signal_lvl
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """

            values = (
                datetime.fromtimestamp(timestamp / 1000),
                data.get('latitude', 0.0),
                data.get('longitude', 0.0),
                data.get('altitude', 0.0),
                data.get('accuracy', 0.0),
                data.get('speed', 0.0),
                time_ms,
                data.get('net_type', ''),
                data.get('signal_lvl', '')
            )

            cursor.execute(query, values)
            self.conn.commit()
            cursor.close()
            print(f"Сохранено просто: {data.get('latitude', 0):.6f}, {data.get('longitude', 0):.6f}")
            return True

        except Exception as e:
            print(f"Ошибка сохранения: {e}")
            print(f"Трассировка ошибки:")
            traceback.print_exc()
            print(f"Данные: {data}")
            self.conn.rollback()
            return False


def save_to_json(data):
    try:
        all_data = []
        json_file = "loc.json"

        if os.path.exists(json_file):
            with open(json_file, 'r') as f:
                all_data = json.load(f)

        if isinstance(data, dict):
            data['server_time'] = datetime.now().isoformat()
            all_data.append(data)
        elif isinstance(data, list):
            for item in data:
                if isinstance(item, dict):
                    item['server_time'] = datetime.now().isoformat()
                    all_data.append(item)

        with open(json_file, 'w') as f:
            json.dump(all_data, f, indent=2)

        print(f"Сохранено в JSON: {len(all_data)} записей")
        return True

    except Exception as e:
        print(f"Ошибка сохранения в JSON: {e}")
        return False


def debug_server():
    print("Запуск отладочного сервера...")

    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind("tcp://*:12345")

    print("Отладочный сервер запущен на tcp://*:12345")
    print("Ожидание подключений...")

    try:
        db = Database()
    except:
        print("Не удалось подключиться к БД, работаем без сохранения")
        db = None

    try:
        while True:
            try:
                print("\n" + "=" * 50)
                print("Ожидание сообщения...")
                message = socket.recv()
                print(f"Получено сообщение длиной: {len(message)} байт")

                try:
                    data_str = message.decode('utf-8')
                    print(f"Декодированная строка (первые 500 символов):")
                    print(data_str[:500])

                    with open('raw_debug.txt', 'a', encoding='utf-8') as f:
                        f.write(f"\n{'=' * 100}\n")
                        f.write(f"Время: {datetime.now()}\n")
                        f.write(f"Длина: {len(data_str)} символов\n")
                        f.write(data_str)
                        f.write("\n")

                    if data_str == 'CONNECT_TEST':
                        response = "CONNECTED"
                        print(f"Тестовое подключение: {response}")
                    else:
                        try:
                            data_json = json.loads(data_str)
                            print(f"Успешный парсинг JSON")
                            print(f"Тип данных: {type(data_json)}")

                            save_to_json(data_json)

                            if isinstance(data_json, dict):
                                print(f"Содержимое словаря:")
                                for key, value in data_json.items():
                                    print(f"  {key}: {type(value)} = {value}")

                                if db:
                                    db.save_simple_location(data_json)

                                response = "OK - данные получены и обработаны"
                            elif isinstance(data_json, list):
                                print(f"Получен список из {len(data_json)} элементов")
                                if db and data_json:
                                    for item in data_json:
                                        if isinstance(item, dict):
                                            db.save_simple_location(item)

                                response = f"OK - получен список из {len(data_json)} элементов"
                            else:
                                print(f"Неизвестный тип JSON: {type(data_json)}")
                                response = "ERROR: Unknown JSON type"

                        except json.JSONDecodeError as e:
                            print(f"Ошибка JSON: {e}")
                            print(f"Проблемная часть строки: {data_str[max(0, e.pos - 50):e.pos + 50]}")
                            response = f"ERROR: Invalid JSON - {str(e)}"

                except UnicodeDecodeError as e:
                    print(f"Ошибка декодирования UTF-8: {e}")
                    response = "ERROR: Invalid UTF-8 encoding"

                print(f"Отправляем ответ: {response}")
                socket.send_string(response)

            except KeyboardInterrupt:
                print("\nОстановка сервера...")
                break
            except Exception as e:
                print(f"Ошибка: {e}")
                traceback.print_exc()

    finally:
        socket.close()
        context.term()
        if db:
            db.conn.close()
        print("Сервер остановлен")


if __name__ == "__main__":
    debug_server()
