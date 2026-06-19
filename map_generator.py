# map_generator.py
import folium
from streamlit_folium import folium_static
import random

def generate_route_map(route_info):
    """Генерация карты с реальным маршрутом по дорогам"""
    
    start_lat = route_info['start_lat']
    start_lon = route_info['start_lon']
    end_lat = route_info['end_lat']
    end_lon = route_info['end_lon']
    distance_km = route_info['distance_km']
    route_points = route_info.get('route_points')
    has_route = route_info.get('has_route', False)
    
    center_lat = (start_lat + end_lat) / 2
    center_lon = (start_lon + end_lon) / 2
    
    m = folium.Map(location=[center_lat, center_lon], zoom_start=5)
    
    # ===== МАРШРУТ =====
    if has_route and route_points:
        folium.PolyLine(
            route_points,
            color='#667eea',
            weight=5,
            opacity=0.9,
            popup=f'🚗 Маршрут {distance_km} км'
        ).add_to(m)
    else:
        points = [
            (start_lat, start_lon),
            (start_lat + (end_lat - start_lat) * 0.33, start_lon + (end_lon - start_lon) * 0.33),
            (start_lat + (end_lat - start_lat) * 0.66, start_lon + (end_lon - start_lon) * 0.66),
            (end_lat, end_lon)
        ]
        folium.PolyLine(
            points,
            color='orange',
            weight=4,
            opacity=0.7,
            popup=f'⚠️ Приближенный маршрут {distance_km} км'
        ).add_to(m)
    
    # ===== СТАРТ =====
    folium.Marker(
        [start_lat, start_lon],
        popup='<b>🚀 СТАРТ</b>',
        icon=folium.Icon(color='green', icon='play', prefix='fa')
    ).add_to(m)
    
    # ===== ФИНИШ =====
    folium.Marker(
        [end_lat, end_lon],
        popup='<b>🏁 ФИНИШ</b>',
        icon=folium.Icon(color='red', icon='stop', prefix='fa')
    ).add_to(m)
    
    # ===== ЗАПРАВКИ =====
    gas_stations = [
        {"name": "Лукойл", "price": 55},
        {"name": "Газпромнефть", "price": 57},
        {"name": "Роснефть", "price": 54},
        {"name": "Татнефть", "price": 53},
        {"name": "Shell", "price": 58},
        {"name": "BP", "price": 56},
        {"name": "Лукойл", "price": 55},
        {"name": "Газпромнефть", "price": 57}
    ]
    
    if has_route and route_points:
        step = max(1, len(route_points) // (len(gas_stations) + 1))
        for i, station in enumerate(gas_stations):
            idx = min((i + 1) * step, len(route_points) - 1)
            lat, lon = route_points[idx]
            lat += random.uniform(-0.005, 0.005)
            lon += random.uniform(-0.005, 0.005)
            
            folium.Marker(
                [lat, lon],
                popup=f'<b>⛽ {station["name"]}</b><br>💰 {station["price"]} ₽/л',
                icon=folium.Icon(color='blue', icon='gas-pump', prefix='fa')
            ).add_to(m)
    else:
        for i, station in enumerate(gas_stations):
            t = (i + 0.5) / len(gas_stations)
            lat = start_lat + (end_lat - start_lat) * t + random.uniform(-0.01, 0.01)
            lon = start_lon + (end_lon - start_lon) * t + random.uniform(-0.01, 0.01)
            folium.Marker(
                [lat, lon],
                popup=f'<b>⛽ {station["name"]}</b><br>💰 {station["price"]} ₽/л',
                icon=folium.Icon(color='blue', icon='gas-pump', prefix='fa')
            ).add_to(m)
    
    # ===== КЕМПИНГИ =====
    campings = [
        {"name": "Лесное озеро", "price": 500, "facilities": "душ, туалет"},
        {"name": "Тихий берег", "price": 300, "facilities": "туалет, вода"},
        {"name": "У карася", "price": 400, "facilities": "душ, рыбалка"},
        {"name": "Березовая роща", "price": 0, "facilities": "без удобств"},
        {"name": "Зеленая поляна", "price": 350, "facilities": "душ, костровище"}
    ]
    
    if has_route and route_points:
        step = max(1, len(route_points) // (len(campings) + 1))
        for i, camp in enumerate(campings):
            idx = min((i + 1) * step + step//2, len(route_points) - 1)
            lat, lon = route_points[idx]
            lat += random.uniform(-0.01, 0.01)
            lon += random.uniform(-0.01, 0.01)
            
            folium.Marker(
                [lat, lon],
                popup=f'<b>🏕️ {camp["name"]}</b><br>💰 {camp["price"]} ₽<br>🛠️ {camp["facilities"]}',
                icon=folium.Icon(color='green', icon='campground', prefix='fa')
            ).add_to(m)
    else:
        for i, camp in enumerate(campings):
            t = (i + 0.3) / len(campings)
            lat = start_lat + (end_lat - start_lat) * t + random.uniform(-0.02, 0.02)
            lon = start_lon + (end_lon - start_lon) * t + random.uniform(-0.02, 0.02)
            folium.Marker(
                [lat, lon],
                popup=f'<b>🏕️ {camp["name"]}</b><br>💰 {camp["price"]} ₽',
                icon=folium.Icon(color='green', icon='campground', prefix='fa')
            ).add_to(m)
    
    return m