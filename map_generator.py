# map_generator.py
import folium
from streamlit_folium import folium_static
import osmnx as ox
import networkx as nx
from places_data import places
import random

def generate_route_map(start_lat, start_lon, end_lat, end_lon, distance_km=8000):
    """
    Генерация карты с реальным маршрутом по дорогам, заправками и кемпингами
    """
    
    # Если координаты не указаны — используем Москва-Владивосток
    if start_lat == 0:
        start_lat, start_lon = 55.7558, 37.6173  # Москва
        end_lat, end_lon = 43.1154, 131.8854     # Владивосток
    
    # ====== ПОСТРОЕНИЕ РЕАЛЬНОГО МАРШРУТА ======
    try:
        # Загружаем граф дорог для России (или региона)
        # Используем центры городов для оптимизации
        center_lat = (start_lat + end_lat) / 2
        center_lon = (start_lon + end_lon) / 2
        
        # Загружаем граф дорог (ограничиваем область, чтобы не висло)
        # Для длинных маршрутов используем упрощенный подход
        G = ox.graph_from_point(
            (center_lat, center_lon), 
            dist=2000000,  # 2000 км в радиусе
            network_type='drive',
            simplify=True
        )
        
        # Находим ближайшие узлы к старту и финишу
        start_node = ox.distance.nearest_nodes(G, start_lon, start_lat)
        end_node = ox.distance.nearest_nodes(G, end_lon, end_lat)
        
        # Строим кратчайший путь
        route = nx.shortest_path(G, start_node, end_node, weight='length')
        
        # Получаем координаты маршрута
        route_coords = [(G.nodes[node]['y'], G.nodes[node]['x']) for node in route]
        
        print(f"Маршрут построен! {len(route)} точек")
        
    except Exception as e:
        print(f"Ошибка построения маршрута: {e}")
        # Если не удалось построить маршрут — используем приближенный путь через города
        route_coords = get_approximate_route(start_lat, start_lon, end_lat, end_lon)
    
    # ====== СОЗДАЕМ КАРТУ ======
    center_lat = (start_lat + end_lat) / 2
    center_lon = (start_lon + end_lon) / 2
    
    m = folium.Map(location=[center_lat, center_lon], zoom_start=5)
    
    # Добавляем маршрут
    folium.PolyLine(
        route_coords,
        color='blue',
        weight=5,
        opacity=0.8,
        popup=f'Маршрут {distance_km} км'
    ).add_to(m)
    
    # ====== МАРКЕРЫ СТАРТА И ФИНИША ======
    folium.Marker(
        [start_lat, start_lon],
        popup='<b>🏁 СТАРТ</b><br>Москва',
        icon=folium.Icon(color='green', icon='play', prefix='fa')
    ).add_to(m)
    
    folium.Marker(
        [end_lat, end_lon],
        popup='<b>🏁 ФИНИШ</b><br>Владивосток',
        icon=folium.Icon(color='red', icon='stop', prefix='fa')
    ).add_to(m)
    
    # ====== ДОБАВЛЯЕМ ЗАПРАВКИ ======
    for station in places['gas_stations']:
        # Распределяем заправки вдоль маршрута
        idx = random.randint(0, len(route_coords) - 1)
        lat, lon = route_coords[idx]
        
        # Добавляем немного случайности
        lat += random.uniform(-0.01, 0.01)
        lon += random.uniform(-0.01, 0.01)
        
        popup_text = f"""
        <b>⛽ {station['name']}</b><br>
        📍 {station['address']}<br>
        💰 {station['price']} руб/л
        """
        
        folium.Marker(
            [lat, lon],
            popup=popup_text,
            icon=folium.Icon(color='blue', icon='gas-pump', prefix='fa')
        ).add_to(m)
    
    # ====== ДОБАВЛЯЕМ КЕМПИНГИ ======
    for camp in places['campings']:
        idx = random.randint(0, len(route_coords) - 1)
        lat, lon = route_coords[idx]
        
        lat += random.uniform(-0.05, 0.05)
        lon += random.uniform(-0.05, 0.05)
        
        popup_text = f"""
        <b>🏕️ {camp['name']}</b><br>
        💰 {camp['price']} руб/ночь<br>
        🛠️ {camp['facilities']}
        """
        
        folium.Marker(
            [lat, lon],
            popup=popup_text,
            icon=folium.Icon(color='green', icon='campground', prefix='fa')
        ).add_to(m)
    
    return m
def get_approximate_route(start_lat, start_lon, end_lat, end_lon):
    """
    Приближенный маршрут через крупные города (если osmnx не работает)
    """
    # Крупные города на пути Москва-Владивосток
    cities = [
        (55.7558, 37.6173),   # Москва
        (56.3327, 44.0056),   # Нижний Новгород
        (55.7961, 49.1064),   # Казань
        (54.7350, 55.9587),   # Уфа
        (55.0302, 73.3926),   # Омск
        (55.0084, 82.9357),   # Новосибирск
        (56.0106, 92.8526),   # Красноярск
        (52.2833, 104.2833),  # Иркутск
        (51.8333, 107.6000),  # Улан-Удэ
        (48.4802, 135.0719),  # Хабаровск
        (43.1154, 131.8854)   # Владивосток
    ]
    
    # Интерполируем точки
    route_coords = []
    for i in range(len(cities) - 1):
        lat1, lon1 = cities[i]
        lat2, lon2 = cities[i + 1]
        
        # Добавляем 5 точек между городами
        for j in range(5):
            t = j / 5
            lat = lat1 + (lat2 - lat1) * t
            lon = lon1 + (lon2 - lon1) * t
            route_coords.append((lat, lon))
    
    return route_coords