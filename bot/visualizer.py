import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import io
from matplotlib.patches import Circle, Ellipse, Patch
import pandas as pd

# Функция для вычисления нормали к контуру выработки
def get_normal_vector(x, y):
    # Арочная форма: окружность радиусом 1.5 от 0 до 90 градусов (x>0, y>0)
    # и прямоугольник для y < 0
    
    if y >= 0:  # Свод (окружность)
        # Нормаль к окружности направлена от центра (0,0) к точке
        r = np.sqrt(x**2 + y**2)
        if r > 0:
            nx = x / r
            ny = y / r
        else:
            nx, ny = 0, 1
    else:  # Стенки (прямоугольная часть)
        # Для прямоугольной части нормаль направлена горизонтально
        if x > 0 and y != -1.52:
            nx, ny = 1, 0  # правая стенка
        elif x < 0 and y != -1.52:
            nx, ny = -1, 0  # левая стенка
        else:
            nx, ny = 0, -1 
    
    return nx, ny

# Функция для определения длины анкера
def get_anchor_length(zone_data):
    # Пример: чем больше зона, тем длиннее анкер
    width, height = zone_data[1], zone_data[2]
    area = width * height * 3.14
    if area/2 < 0.3*0.3*3.14 and area/2 > 0.15*0.15*3.14:
        return 0.6
    elif area/2 < 0.45*0.45*3.14:
        return 0.9
    elif area/2 >= 0.45*0.45*3.14:
        return 1.2
    else:
        return 0

def plot_zones(num_zones, pred_data, displ, output_size=(800, 600)):

    #словарь для восстановления координат по id
    df = pd.read_csv('dict.csv', 
                 sep='\s+',           # разделитель: пробелы/табуляции
                 skiprows=1,          # пропускаем первую строку (заголовки не в том формате)
                 header=None,         # нет заголовков в данных
                 names=['id', 'x', 'y'])  # задаем имена колонок

    df['id'] = np.where((df['id'] >= 12613) & (df['id'] <= 12635), 25248 - df['id'], df['id'])
    df['id'] = df['id'] - 12611

    res_dict = df.set_index('id').to_dict(orient='index')
    
    fig, ax = plt.subplots(figsize=(output_size[0]/100, output_size[1]/100), dpi=200)

    #область определения
    ax.set_xlim(-3.5, 3.5)
    ax.set_ylim(-3.5, 3.5)
    
    #оси
    ax.axhline(y=0, color='gray', linestyle='--', linewidth=0.5, alpha=0.5)
    ax.axvline(x=0, color='gray', linestyle='--', linewidth=0.5, alpha=0.5)
    
    #выработка
    excavation = Circle((0, 0), 1.5, fill=True, color='black', linewidth=1, zorder = 2)
    ax.add_patch(excavation)
    
    rect = patches.Rectangle((-1.5, -1.5), 3, 1.5, 
                              linewidth=1, color='black', fill=True, zorder = 2)
    ax.add_patch(rect)

    if num_zones == 1:
        zones = [pred_data]
    elif num_zones ==2:
        zones = pred_data.reshape(2,3)
    else:
        return None

    #зоны нарушения
    for i, zone in enumerate(zones):
        if zone[0] >= 55:
            zone[0] = 55
        elips = Ellipse((res_dict[zone[0]]['x'], res_dict[zone[0]]['y']), width=zone[1], height=zone[2], 
                        fill=True, color='red', 
                        linewidth=1, 
                        zorder = 1)
        ax.add_patch(elips)

        elips = Ellipse((-res_dict[zone[0]]['x'], res_dict[zone[0]]['y']), width=zone[1], height=zone[2], 
                        fill=True, color='red', 
                        linewidth=1, 
                        zorder = 1)
        ax.add_patch(elips)

        # Добавляем анкер (зеленая линия)
        # Вычисляем нормаль в центре эллипса
        center_x = res_dict[zone[0]]['x']
        center_y = res_dict[zone[0]]['y']
        
        nx, ny = get_normal_vector(center_x, center_y)
        
        # Определяем длину анкера
        anchor_length = get_anchor_length(zone)

        if anchor_length !=0:
            # Вычисляем конечную точку анкера
            end_x = center_x + nx * anchor_length
            end_y = center_y + ny * anchor_length
        
            # Рисуем анкер
            ax.plot([center_x, end_x], [center_y, end_y], 
                color='green', linewidth=2, zorder=3)

            ax.plot([-center_x, -end_x], [center_y, end_y], 
                color='green', linewidth=2, zorder=3)
        
            # Подписываем длину анкера
            mid_x = (center_x + end_x) / 2
            mid_y = (center_y + end_y) / 2
            ax.text(mid_x, mid_y, f'{anchor_length}м', 
                fontsize=8, color='darkgreen', 
                ha='center', va='bottom',
                bbox=dict(boxstyle='round,pad=0.2', facecolor='white', alpha=0.7))
            ax.text(-mid_x, mid_y, f'{anchor_length}м', 
                fontsize=8, color='darkgreen', 
                ha='center', va='bottom',
                bbox=dict(boxstyle='round,pad=0.2', facecolor='white', alpha=0.7))
    
    legend_elements = [
        Patch(facecolor='black', alpha=0.8, label='Горная выработка'),
        Patch(facecolor='red', alpha=0.8, label='Зоны нарушения сплошности'),
        plt.Line2D([0], [0], color='green', linewidth=2, label='Анкера')
    ]

    ax.text(0, 1.3, f'{np.round(-displ[0].item(), 2)}мм', 
                fontsize=8, color='white', 
                ha='center', va='bottom',
                bbox=dict(boxstyle='round,pad=0.2', facecolor='white', alpha=0.7))

    ax.text(1.1, 0, f'{np.round(-displ[1].item(), 2)}мм', 
                fontsize=8, color='white', 
                ha='center', va='bottom',
                bbox=dict(boxstyle='round,pad=0.2', facecolor='white', alpha=0.7))

    ax.text(-1.1, 0, f'{np.round(-displ[1].item(), 2)}мм', 
                fontsize=8, color='white', 
                ha='center', va='bottom',
                bbox=dict(boxstyle='round,pad=0.2', facecolor='white', alpha=0.7))

    ax.text(0, -1.4, f'{np.round(displ[2].item(), 2)}мм', 
                fontsize=8, color='white', 
                ha='center', va='bottom',
                bbox=dict(boxstyle='round,pad=0.2', facecolor='white', alpha=0.7))
    
    # Настройки графика
    ax.set_xlabel('X (м)', fontsize=12)
    ax.set_ylabel('Y (м)', fontsize=12)
    ax.grid(True, alpha=0.3)
    ax.legend(handles=legend_elements, loc='upper right', fontsize=10)
    
    # Устанавливаем соотношение осей 1:1
    ax.set_aspect('equal')
    
    # Возвращаем изображение в виде байтов
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=200, bbox_inches='tight')
    #plt.show()
    plt.close(fig)
    buf.seek(0)
    
    return [buf, [[res_dict[zone[0]]['x'], res_dict[zone[0]]['y'], get_anchor_length(zone)]  for i, zone in enumerate(zones)]]