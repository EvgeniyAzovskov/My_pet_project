# map_generator.py
import folium
from streamlit_folium import folium_static
import random
from places_data import places

def generate_route_map(start_lat, start_lon, end_lat, end_lon, distance_km=8000):
    """
    Генерация карты с маршрутом, заправками и кемпингами
    """
    
    # Создаем карту с центром между началом и концом
    center_lat = (start_lat + end_lat) / 2
    center_lon = (start_lon + end_lon) / 2
    
    # Если координаты не указаны — используем Москва-Владивосток
    if start_lat == 0:
        start_lat, start_lon = 55.7558, 37.6173  # Москва
        end_lat, end_lon = 43.1154, 131.8854     # Владивосток
        center_lat, center_lon = 55.7558, 37.6173
    
    m = folium.Map(location=[center_lat, center_lon], zoom_start=5)
    
    # Добавляем маршрут (имитация прямой линии)
    points = [
        (start_lat, start_lon),
        (start_lat + (end_lat - start_lat) * 0.25, start_lon + (end_lon - start_lon) * 0.25),
        (start_lat + (end_lat - start_lat) * 0.5, start_lon + (end_lon - start_lon) * 0.5),
        (start_lat + (end_lat - start_lat) * 0.75, start_lon + (end_lon - start_lon) * 0.75),
        (end_lat, end_lon)
    ]
    
    folium.PolyLine(points, color='blue', weight=4, opacity=0.7, popup='Маршрут').add_to(m)
    
    # Маркеры старта и финиша
    folium.Marker(
        [start_lat, start_lon],
        popup='<b>🏁 Старт</b>',
        icon=folium.Icon(color='green', icon='play', prefix='fa')
    ).add_to(m)
    
    folium.Marker(
        [end_lat, end_lon],
        popup='<b>🏁 Финиш</b>',
        icon=folium.Icon(color='red', icon='stop', prefix='fa')
    ).add_to(m)
    
    # Добавляем заправки (ГАЗ)
    for station in places['gas_stations']:
        # Имитация распределения по маршруту
        lat = station['lat'] + random.uniform(-0.5, 0.5)
        lon = station['lon'] + random.uniform(-0.5, 0.5)
        
        popup_text = f"""
        <b>⛽ {station['name']}</b><b
       📍 {station['address']}<br
      💰 {station['price']} руб/л
        """
        
        folium.Marker(
            [lat, lon],
            popup=popup_text,
            icon=folium.Icon(color='blue', icon='gas-pump', prefix='fa')
        ).add_to(m)
    
    # Добавляем кемпинги (ПАЛАТКА)
    for camp in places['campings']:
        lat = camp['lat'] + random.uniform(-0.3, 0.3)
        lon = camp['lon'] + random.uniform(-0.3, 0.3)
        
        popup_text = f"""
        <b>🏕️ {camp['name']}</b>

 
   💰 {camp['price']} руб/ночь

  
  🛠️ {camp['facilities']}
        """
        
        folium.Marker(
            [lat, lon],
            popup=popup_text,
            icon=folium.Icon(color='green', icon='campground', prefix='fa')
        ).add_to(m)
    
    return m