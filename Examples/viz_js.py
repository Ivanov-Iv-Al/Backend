import json
import matplotlib.pyplot as plt
from datetime import datetime
import numpy as np
from matplotlib.colors import Normalize
import os


def load_json_data():
    json_file = "loc.json"

    if not os.path.exists(json_file):
        print(f"Файл {json_file} не найден")
        return []

    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        if isinstance(data, list):
            return data
        else:
            return []
    except:
        return []


def parse_timestamp(timestamp):
    try:
        if isinstance(timestamp, (int, float)):
            if timestamp > 1e12:
                timestamp = timestamp / 1000.0
            return datetime.fromtimestamp(timestamp)
        elif isinstance(timestamp, str):
            try:
                return datetime.fromtimestamp(float(timestamp) / 1000.0)
            except:
                formats = [
                    '%Y-%m-%d %H:%M:%S',
                    '%Y-%m-%dT%H:%M:%S',
                    '%Y-%m-%dT%H:%M:%S.%f'
                ]
                for fmt in formats:
                    try:
                        return datetime.strptime(timestamp, fmt)
                    except:
                        continue
        return datetime.now()
    except:
        return datetime.now()


def calculate_signal_from_accuracy(accuracy):
    try:
        accuracy = float(accuracy)
        if accuracy < 5:
            return -60
        elif accuracy < 15:
            return -75
        elif accuracy < 30:
            return -85
        elif accuracy < 50:
            return -95
        else:
            return -105
    except:
        return -85


def plot_data():
    data = load_json_data()

    if not data:
        print("Нет данных для отображения")
        return

    latitudes = []
    longitudes = []
    signal_levels = []

    for item in data:
        lat = item.get('latitude')
        lon = item.get('longitude')
        accuracy = item.get('accuracy')

        if lat is None or lon is None:
            continue

        latitudes.append(float(lat))
        longitudes.append(float(lon))

        if accuracy is not None:
            signal = calculate_signal_from_accuracy(accuracy)
            signal_levels.append(signal)
        else:
            signal_levels.append(-85)

    if not latitudes:
        print("Нет корректных координат в данных")
        return

    signal_array = np.array(signal_levels)

    if len(np.unique(signal_array)) > 1:
        vmin, vmax = np.nanmin(signal_array), np.nanmax(signal_array)
    else:
        vmin, vmax = -120, -50

    norm = Normalize(vmin=vmin, vmax=vmax)
    cmap = plt.cm.viridis_r

    fig, (ax, cbar_ax) = plt.subplots(2, 1, figsize=(12, 10),
                                      gridspec_kw={'height_ratios': [8, 1]})

    scatter = ax.scatter(longitudes, latitudes,
                         c=signal_array,
                         cmap=cmap,
                         norm=norm,
                         s=80,
                         alpha=0.8,
                         edgecolors='black',
                         linewidth=0.8)

    if len(longitudes) > 1:
        ax.plot(longitudes, latitudes, 'gray', alpha=0.4, linewidth=1.5, linestyle='-')

    if len(longitudes) >= 2:
        ax.scatter(longitudes[0], latitudes[0], c='green', s=200,
                   marker='o', label='Начало', edgecolors='black', zorder=5, linewidth=2)
        ax.scatter(longitudes[-1], latitudes[-1], c='red', s=200,
                   marker='s', label='Конец', edgecolors='black', zorder=5, linewidth=2)

    ax.set_xlabel('Долгота', fontsize=12)
    ax.set_ylabel('Широта', fontsize=12)
    ax.set_title('Траектория движения', fontsize=14, fontweight='bold', pad=15)
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.legend(fontsize=11)

    cbar = plt.colorbar(scatter, cax=cbar_ax, orientation='horizontal')
    cbar.set_label('Уровень сигнала (дБм)', fontsize=12)

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    plot_data()