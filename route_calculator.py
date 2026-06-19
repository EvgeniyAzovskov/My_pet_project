# route_calculator.py
import requests
import math

def get_coordinates(city_name):
    """Получить координаты города через OpenStreetMap Nominatim"""
    try:
        url = f"https://nominatim.openstreetmap.org/search?q={city_name}&format=json&limit=1"
        headers = {'User-Agent': 'TripChecklist/1.0'}
        response = requests.get(url, headers=headers, timeout=10)
        data = response.json()
        
        if data:
            lat = float(data[0]['lat'])
            lon = float(data[0]['lon'])
            return lat, lon
        else:
            return None, None
    except:
        return None, None

def calculate_distance(lat1, lon1, lat2, lon2):
    """Расчет расстояния между двумя точками (формула гаверсинусов)"""
    R = 6371  # Радиус Земли в км
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c

def get_route_info(start_city, end_city):
    """Получить информацию о маршруте (координаты, расстояние)"""
    start_lat, start_lon = get_coordinates(start_city)
    end_lat, end_lon = get_coordinates(end_city)
    
    if start_lat and end_lat:
        distance = calculate_distance(start_lat, start_lon, end_lat, end_lon)
        return {
            'start_lat': start_lat,
            'start_lon': start_lon,
            'end_lat': end_lat,
            'end_lon': end_lon,
            'distance_km': round(distance)
        }
    else:
        return None