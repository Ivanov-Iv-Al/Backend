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


def plot_locations(data):
    if not data:
        print("❌ Нет данных для отображения")
        return

    timestamps = [row[0] for row in data]
    latitudes = [row[1] for row in data]
    longitudes = [row[2] for row in data]
    speeds = [row[3] for row in data]
    accuracies = [row[4] for row in data]
    networks = [row[5] for row in data]

    # Создаем большой график
    fig = plt.figure(figsize=(16, 10))

    # 1. Основной график: траектория движения
    ax1 = plt.subplot(2, 3, 1)
    scatter1 = ax1.scatter(longitudes, latitudes, c=mdates.date2num(timestamps),
                           cmap='viridis', s=30, alpha=0.7)
    ax1.plot(longitudes, latitudes, 'r-', alpha=0.3, linewidth=1)
    ax1.set_xlabel('Долгота')
    ax1.set_ylabel('Широта')
    ax1.set_title('Траектория движения')
    ax1.grid(True, alpha=0.3)
    plt.colorbar(scatter1, ax=ax1, label='Время')

    # 2. График скорости
    ax2 = plt.subplot(2, 3, 2)
    ax2.plot(timestamps, speeds, 'g-', linewidth=2)
    ax2.fill_between(timestamps, 0, speeds, alpha=0.3, color='green')
    ax2.set_xlabel('Время')
    ax2.set_ylabel('Скорость (м/с)')
    ax2.set_title('Скорость движения')
    ax2.grid(True, alpha=0.3)
    ax2.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))

    # 3. График точности GPS
    ax3 = plt.subplot(2, 3, 3)
    colors = ['red' if acc > 20 else 'green' for acc in accuracies]
    ax3.bar(range(len(accuracies)), accuracies, color=colors, alpha=0.6)
    ax3.axhline(y=20, color='orange', linestyle='--', label='Порог 20м')
    ax3.set_xlabel('Измерение')
    ax3.set_ylabel('Точность (м)')
    ax3.set_title('Точность GPS измерений')
    ax3.legend()
    ax3.grid(True, alpha=0.3)

    # 4. Распределение по типам сети
    ax4 = plt.subplot(2, 3, 4)
    unique_networks = list(set(networks))
    network_counts = [networks.count(net) for net in unique_networks]
    colors = plt.cm.Set3(np.linspace(0, 1, len(unique_networks)))
    ax4.pie(network_counts, labels=unique_networks, autopct='%1.1f%%',
            colors=colors, startangle=90)
    ax4.set_title('Распределение по типам сети')

    # 5. Временная шкала измерений
    ax5 = plt.subplot(2, 3, 5)
    time_diffs = [(timestamps[i + 1] - timestamps[i]).total_seconds()
                  for i in range(len(timestamps) - 1)]
    ax5.plot(range(len(time_diffs)), time_diffs, 'b-')
    ax5.axhline(y=5, color='red', linestyle='--', label='Интервал 5с')
    ax5.set_xlabel('Интервал')
    ax5.set_ylabel('Время (секунды)')
    ax5.set_title('Интервалы между измерениями')
    ax5.legend()
    ax5.grid(True, alpha=0.3)

    # 6. Карта тепла траектории
    ax6 = plt.subplot(2, 3, 6)
    heatmap, xedges, yedges = np.histogram2d(longitudes, latitudes, bins=20)
    extent = [xedges[0], xedges[-1], yedges[0], yedges[-1]]
    im = ax6.imshow(heatmap.T, extent=extent, origin='lower',
                    cmap='hot', aspect='auto')
    ax6.set_xlabel('Долгота')
    ax6.set_ylabel('Широта')
    ax6.set_title('Карта плотности точек')
    plt.colorbar(im, ax=ax6, label='Количество точек')

    plt.suptitle(f'Анализ данных о местоположении ({len(data)} измерений)',
                 fontsize=16, fontweight='bold')
    plt.tight_layout()
    plt.show()


def plot_simple_map(data):
    """Простой график только с координатами"""
    if not data:
        print("❌ Нет данных")
        return

    latitudes = [row[1] for row in data]
    longitudes = [row[2] for row in data]

    plt.figure(figsize=(10, 8))

    # Точки
    plt.scatter(longitudes, latitudes, c='blue', s=50, alpha=0.7,
                edgecolors='black', linewidth=0.5)

    # Линия пути
    if len(data) > 1:
        plt.plot(longitudes, latitudes, 'r-', alpha=0.5, linewidth=2)

    # Начальная и конечная точки
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

    # Добавить сетку координат
    plt.gca().set_aspect('equal', adjustable='box')

    plt.tight_layout()
    plt.show()


def plot_realtime_monitor():
    """Мониторинг в реальном времени"""
    import time

    plt.ion()  # Включить интерактивный режим
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    while True:
        try:
            data = get_location_data()

            if not data:
                print("Ожидание данных...")
                time.sleep(5)
                continue

            latitudes = [row[1] for row in data]
            longitudes = [row[2] for row in data]
            timestamps = [row[0] for row in data]

            # Очистить графики
            ax1.clear()
            ax2.clear()

            # График 1: Траектория
            ax1.scatter(longitudes, latitudes, c='blue', s=30, alpha=0.6)
            ax1.plot(longitudes, latitudes, 'r-', alpha=0.3)
            ax1.set_xlabel('Долгота')
            ax1.set_ylabel('Широта')
            ax1.set_title(f'Траектория ({len(data)} точек)')
            ax1.grid(True, alpha=0.3)

            # График 2: Временная шкала
            time_nums = mdates.date2num(timestamps)
            ax2.plot(timestamps, range(len(timestamps)), 'b-')
            ax2.set_xlabel('Время')
            ax2.set_ylabel('Количество измерений')
            ax2.set_title('Временная шкала измерений')
            ax2.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
            ax2.grid(True, alpha=0.3)

            plt.suptitle(f'Обновлено: {datetime.now().strftime("%H:%M:%S")}',
                         fontsize=10)
            plt.tight_layout()
            plt.draw()
            plt.pause(5)  # Обновлять каждые 5 секунд

        except KeyboardInterrupt:
            print("\nОстановка мониторинга...")
            break
        except Exception as e:
            print(f"Ошибка: {e}")
            time.sleep(5)

    plt.ioff()
    plt.show()


def main_menu():
    while True:
        print("\n" + "=" * 50)
        print("📊 ВИЗУАЛИЗАЦИЯ ДАННЫХ ИЗ POSTGRESQL")
        print("=" * 50)
        print("1. Полный анализ (6 графиков)")
        print("2. Простая карта местоположения")
        print("3. Мониторинг в реальном времени")
        print("4. Экспорт данных в CSV")
        print("5. Статистика базы данных")
        print("6. Выход")
        print("-" * 50)

        choice = input("Выберите опцию (1-6): ").strip()

        if choice == '1':
            data = get_location_data()
            plot_locations(data)
        elif choice == '2':
            data = get_location_data()
            plot_simple_map(data)
        elif choice == '3':
            plot_realtime_monitor()
        elif choice == '4':
            export_to_csv()
        elif choice == '5':
            show_statistics()
        elif choice == '6':
            print("Выход...")
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
    print(f"✅ Экспортировано {len(data)} записей в location_data.csv")


def show_statistics():
    conn = connect_to_db()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM location_data")
    total = cursor.fetchone()[0]

    print(f"\n📊 СТАТИСТИКА БАЗЫ ДАННЫХ")
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

        print("\n📶 Типы сетей:")
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
        print(f"\n📍 Диапазон координат:")
        print(f"  Широта: {min_lat} — {max_lat}")
        print(f"  Долгота: {min_lon} — {max_lon}")

    cursor.close()
    conn.close()


if __name__ == "__main__":
    main_menu()