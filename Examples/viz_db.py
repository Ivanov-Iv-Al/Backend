import psycopg2
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
import numpy as np


def connect_to_db():
    return psycopg2.connect(
        dbname="location_tracking",
        user="postgres",
        password="123456",
        host="localhost",
        port="5432"
    )


def get_location_data():
    conn = connect_to_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT timestamp, latitude, longitude, speed, accuracy, network_type
        FROM location_data 
        ORDER BY timestamp
    """)

    data = cursor.fetchall()
    cursor.close()
    conn.close()

    return data

def plot_simple_map(data):
    if not data:
        print("Нет данных")
        return

    latitudes = [row[1] for row in data]
    longitudes = [row[2] for row in data]

    plt.figure(figsize=(10, 8))

    plt.scatter(longitudes, latitudes, c='blue', s=50, alpha=0.7,
                edgecolors='black', linewidth=0.5)

    if len(data) > 1:
        plt.plot(longitudes, latitudes, 'r-', alpha=0.5, linewidth=2)

    if len(data) >= 2:
        plt.scatter(longitudes[0], latitudes[0], c='green', s=200,
                    marker='o', label='Начало', edgecolors='black')
        plt.scatter(longitudes[-1], latitudes[-1], c='red', s=200,
                    marker='s', label='Конец', edgecolors='black')

    plt.xlabel('Долгота')
    plt.ylabel('Широта')
    plt.title(f'Карта местоположения ({len(data)} точек)')
    plt.grid(True, alpha=0.3)
    plt.legend()

    plt.gca().set_aspect('equal', adjustable='box')

    plt.tight_layout()
    plt.show()

def main_menu():
    while True:
        print("1) Нарисовать простую карту")
        print("2) Выйти")

        choice = input("Выберите опцию (1 или 2): ").strip()

        if choice == '1':
            data = get_location_data()
            plot_simple_map(data)
        elif choice == '2':
            print("Выход")
            break
        else:
            print("Неверный выбор")


def export_to_csv():
    conn = connect_to_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM location_data")
    data = cursor.fetchall()

    if not data:
        print("Нет данных для экспорта")
        return

    with open('location_data.csv', 'w', encoding='utf-8') as f:
        # Заголовки
        f.write("timestamp,latitude,longitude,altitude,accuracy,speed,network_type,signal_level\n")

        for row in data:
            timestamp = row[1].strftime("%Y-%m-%d %H:%M:%S") if row[1] else ""
            lat = row[2] or ""
            lon = row[3] or ""
            alt = row[4] or ""
            acc = row[5] or ""
            spd = row[6] or ""
            net = row[7] or ""
            sig = row[8] or ""

            f.write(f"{timestamp},{lat},{lon},{alt},{acc},{spd},{net},{sig}\n")

    cursor.close()
    conn.close()
    print(f"Экспортировано {len(data)} записей в location_data.csv")


def show_statistics():
    conn = connect_to_db()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM location_data")
    total = cursor.fetchone()[0]

    print(f"\nСТАТИСТИКА БАЗЫ ДАННЫХ")
    print("=" * 40)
    print(f"Всего записей: {total}")

    if total > 0:
        cursor.execute("SELECT MIN(timestamp), MAX(timestamp) FROM location_data")
        min_time, max_time = cursor.fetchone()
        print(f"Период: {min_time} — {max_time}")

        cursor.execute("""
            SELECT network_type, COUNT(*) as count
            FROM location_data 
            GROUP BY network_type
            ORDER BY count DESC
        """)

        print("\nТипы сетей:")
        for net_type, count in cursor.fetchall():
            percent = (count / total) * 100
            print(f"  {net_type or 'Unknown'}: {count} ({percent:.1f}%)")

        cursor.execute("""
            SELECT 
                ROUND(MIN(latitude)::numeric, 6) as min_lat,
                ROUND(MAX(latitude)::numeric, 6) as max_lat,
                ROUND(MIN(longitude)::numeric, 6) as min_lon,
                ROUND(MAX(longitude)::numeric, 6) as max_lon
            FROM location_data
        """)

        min_lat, max_lat, min_lon, max_lon = cursor.fetchone()
        print(f"\nДиапазон координат:")
        print(f"  Широта: {min_lat} — {max_lat}")
        print(f"  Долгота: {min_lon} — {max_lon}")

    cursor.close()
    conn.close()

main_menu()
