# route_calculator.py
import requests
import math

def get_coordinates(city_name):
    """Получить координаты города через OpenStreetMap Nominatim"""
    try:
        url = f"https://nominatim.openstreetmap.org/search?q={city_name}&format=json&limit=1"
        headers = {'User-Agent': 'TripPlanner/1.0'}
        response = requests.get(url, headers=headers, timeout=10)
        data = response.json()
        
        if data:
            lat = float(data[0]['lat'])
            lon = float(data[0]['lon'])
            return lat, lon
        else:
            return None, None
    except Exception as e:
        print(f"Ошибка геокодинга: {e}")
        return None, None

def get_route_osrm(start_lat, start_lon, end_lat, end_lon):
    """Получить реальный маршрут по дорогам через OSRM API"""
    try:
        url = f"http://router.project-osrm.org/route/v1/driving/{start_lon},{start_lat};{end_lon},{end_lat}?overview=full&geometries=geojson"
        response = requests.get(url, timeout=30)
        data = response.json()
        
        if data.get('code') == 'Ok':
            route_coords = data['routes'][0]['geometry']['coordinates']
            route_points = [(coord[1], coord[0]) for coord in route_coords]
            distance_m = data['routes'][0]['distance']
            distance_km = round(distance_m / 1000)
            return route_points, distance_km
        else:
            return None, None
    except Exception as e:
        print(f"Ошибка OSRM: {e}")
        return None, None

def get_route_info(start_city, end_city):
    """Получить информацию о маршруте"""
    start_lat, start_lon = get_coordinates(start_city)
    end_lat, end_lon = get_coordinates(end_city)
    
    if not start_lat or not end_lat:
        return None
    
    # Пытаемся построить маршрут через OSRM
    route_points, distance_km = get_route_osrm(start_lat, start_lon, end_lat, end_lon)
    
    if route_points:
        return {
            'start_lat': start_lat,
            'start_lon': start_lon,
            'end_lat': end_lat,
            'end_lon': end_lon,
            'distance_km': distance_km,
            'route_points': route_points,
            'has_route': True
        }
    else:
        return {
            'start_lat': start_lat,
            'start_lon': start_lon,
            'end_lat': end_lat,
            'end_lon': end_lon,
            'distance_km': int(calculate_distance(start_lat, start_lon, end_lat, end_lon)),
            'route_points': None,
            'has_route': False
        }

def calculate_distance(lat1, lon1, lat2, lon2):
    """Расчет расстояния между двумя точками"""
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c