# destinations_data.py

destinations = {
    "abkhazia": {
        "name": "🇬🇪 Абхазия",
        "description": "Море, горы, мандарины и древние крепости",
        "image": "https://via.placeholder.com/400x300/667eea/ffffff?text=Абхазия",
        "distance_from_msk": 1500,
        "recommended_days": 7,
        "campings": [
            {
                "name": "🏕️ Кемпинг 'Голубое озеро'",
                "price_per_night": 500,
                "rating": 4.8,
                "features": ["душ", "туалет", "кухня", "WiFi"],
                "description": "Уютный кемпинг у озера с видом на горы"
            },
            {
                "name": "🏕️ Кемпинг 'Бамбуковый рай'",
                "price_per_night": 400,
                "rating": 4.5,
                "features": ["туалет", "вода", "костровище"],
                "description": "Недалеко от моря, окружён бамбуковыми рощами"
            },
            {
                "name": "🏕️ Кемпинг 'Горный ветер'",
                "price_per_night": 700,
                "rating": 4.9,
                "features": ["душ", "туалет", "WiFi", "ресторан"],
                "description": "Кемпинг в горах с панорамным видом"
            }
        ]
    },
    "arkhyz": {
        "name": "🏔️ Архыз",
        "description": "Горные вершины, хрустальные озёра и альпийские луга",
        "image": "https://via.placeholder.com/400x300/4caf50/ffffff?text=Архыз",
        "distance_from_msk": 1300,
        "recommended_days": 5,
        "campings": [
            {
                "name": "🏕️ Кемпинг 'Эльбрус'",
                "price_per_night": 600,
                "rating": 4.7,
                "features": ["душ", "туалет", "трансфер", "экскурсии"],
                "description": "Кемпинг у подножия горы"
            },
            {
                "name": "🏕️ Кемпинг 'София'",
                "price_per_night": 450,
                "rating": 4.4,
                "features": ["туалет", "вода", "кухня"],
                "description": "Уютный кемпинг в долине"
            }
        ]
    },
    "altai": {
        "name": "🏔️ Алтай",
        "description": "Горный Алтай — место силы, Чуйский тракт и Катунь",
        "image": "https://via.placeholder.com/400x300/ff6b35/ffffff?text=Алтай",
        "distance_from_msk": 3000,
        "recommended_days": 10,
        "campings": [
            {
                "name": "🏕️ Кемпинг 'Катунь'",
                "price_per_night": 550,
                "rating": 4.9,
                "features": ["душ", "туалет", "баня", "экскурсии"],
                "description": "На берегу реки Катунь"
            },
            {
                "name": "🏕️ Кемпинг 'Горный орел'",
                "price_per_night": 400,
                "rating": 4.6,
                "features": ["туалет", "вода", "костровище"],
                "description": "В горах, с видом на долину"
            },
            {
                "name": "🏕️ Кемпинг 'Чуйский'",
                "price_per_night": 650,
                "rating": 4.8,
                "features": ["душ", "туалет", "WiFi", "магазин"],
                "description": "На Чуйском тракте"
            }
        ]
    }
}

def get_destination(dest_id):
    """Получить данные направления по ID"""
    return destinations.get(dest_id)

def get_all_destinations():
    """Получить все направления"""
    return destinations

def get_campings(dest_id):
    """Получить кемпинги направления"""
    dest = get_destination(dest_id)
    return dest.get('campings', []) if dest else []