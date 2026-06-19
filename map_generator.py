# map_generator.py
import folium
from streamlit_folium import folium_static
import random

def generate_route_map(start_lat, start_lon, end_lat, end_lon, distance_km=8000):
    """Генерация карты с маршрутом"""
    
    center_lat = (start_lat + end_lat) / 2
    center_lon = (start_lon + end_lon) / 2
    
    m = folium.Map(location=[center_lat, center_lon], zoom_start=5)
    
    # Маршрут (линия)
    points = [
        (start_lat, start_lon),
        (start_lat + (end_lat - start_lat) * 0.25, start_lon + (end_lon - start_lon) * 0.25),
        (start_lat + (end_lat - start_lat) * 0.5, start_lon + (end_lon - start_lon) * 0.5),
        (start_lat + (end_lat - start_lat) * 0.75, start_lon + (end_lon - start_lon) * 0.75),
        (end_lat, end_lon)
    ]
    
    folium.PolyLine(points, color='blue', weight=5, opacity=0.8, popup=f'Маршрут {distance_km} км').add_to(m)
    
    # Старт
    folium.Marker(
        [start_lat, start_lon],
        popup='<b>🚀 СТАРТ</b>',
        icon=folium.Icon(color='green', icon='play', prefix='fa')
    ).add_to(m)
    
    # Финиш
    folium.Marker(
        [end_lat, end_lon],
        popup='<b>🏁 ФИНИШ</b>',
        icon=folium.Icon(color='red', icon='stop', prefix='fa')
    ).add_to(m)
    
    # Заправки (синие маркеры) - распределены вдоль маршрута
    gas_stations = [
        {"name": "Лукойл", "price": 55},
        {"name": "Газпромнефть", "price": 57},
        {"name": "Роснефть", "price": 54},
        {"name": "Татнефть", "price": 53},
        {"name": "Shell", "price": 58},
        {"name": "BP", "price": 56},
        {"name": "Лукойл", "price": 55},
        {"name": "Газпромнефть", "price": 57},
        {"name": "Роснефть", "price": 54},
        {"name": "Татнефть", "price": 53}
    ]
    
    for i, station in enumerate(gas_stations):
        # Распределяем по маршруту
        t = (i + 0.5) / len(gas_stations)
        lat = start_lat + (end_lat - start_lat) * t + random.uniform(-0.02, 0.02)
        lon = start_lon + (end_lon - start_lon) * t + random.uniform(-0.02, 0.02)
        
        folium.Marker(
            [lat, lon],
            popup=f'<b>⛽ {station["name"]}</b><br>💰 {station["price"]} руб/л',
            icon=folium.Icon(color='blue', icon='gas-pump', prefix='fa')
        ).add_to(m)
    
    # Кемпинги (зеленые маркеры)
    campings = [
        {"name": "Лесное озеро", "price": 500, "facilities": "душ, туалет"},
        {"name": "Тихий берег", "price": 300, "facilities": "туалет, вода"},
        {"name": "У карася", "price": 400, "facilities": "душ, рыбалка"},
        {"name": "Березовая роща", "price": 0, "facilities": "без удобств"},
        {"name": "Зеленая поляна", "price": 350, "facilities": "душ, костровище"}
    ]
    
    for i, camp in enumerate(campings):
        t = (i + 0.3) / len(campings)
        lat = start_lat + (end_lat - start_lat) * t + random.uniform(-0.03, 0.03)
        lon = start_lon + (end_lon - start_lon) * t + random.uniform(-0.03, 0.03)
        
        folium.Marker(
            [lat, lon],
            popup=f'<b>🏕️ {camp["name"]}</b><br>💰 {camp["price"]} руб<br>🛠️ {camp["facilities"]}',
            icon=folium.Icon(color='green', icon='campground', prefix='fa')
        ).add_to(m)
    
    return m