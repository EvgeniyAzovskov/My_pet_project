import json

def load_checklist_data():
    with open('checklist_data.json', 'r', encoding='utf-8') as f:
        return json.load(f)['items']

def check_condition(item, user_input):
    conditions = item.get('conditions', [])
    
    if not conditions:
        return True
    
    for cond in conditions:
        cond_type = cond['type']
        cond_value = cond['value']
        
        if cond_type == 'season':
            if user_input.get('season') != cond_value:
                return False
        elif cond_type == 'template':
            if user_input.get('template') != cond_value:
                return False
        elif cond_type == 'camping':
            if user_input.get('camping', False) != cond_value:
                return False
        elif cond_type == 'distance':
            user_dist = user_input.get('distance', 0)
            if cond['operator'] == '>':
                if user_dist <= cond_value:
                    return False
            elif cond['operator'] == '<':
                if user_dist >= cond_value:
                    return False
        elif cond_type == 'children':
            user_children = user_input.get('children', 0)
            if cond_value == '>0' and user_children == 0:
                return False
    
    return True

def calculate_amount(item, people_count, days=14):
    """Расчет количества продукта"""
    calc = item.get('calculation')
    if not calc:
        return None
    
    # Расчет для пакетов (крупы)
    if 'packets_per_person_per_day' in calc:
        packets_per_day = calc['packets_per_person_per_day'] * people_count
        total_packets = packets_per_day * days
        return f"{int(total_packets)} пакетов"
    
    # Расчет для круп в кг
    elif 'per_person_per_day' in calc:
        total_kg = calc['per_person_per_day'] * people_count * days
        return f"{round(total_kg * 2) / 2:.1f} кг"
    
    # Расчет для тушенки и консервов
    elif 'cans_per_day_for_2' in calc:
        cans_per_day = calc['cans_per_day_for_2'] * (people_count / 2)
        total_cans = cans_per_day * days
        import math
        return f"{math.ceil(total_cans)} банок"
    
    return None

def generate_checklist(user_input):
    all_items = load_checklist_data()
    result = []
    people = user_input.get('people', 2)
    days = user_input.get('days', 14)
    
    for item in all_items:
        if check_condition(item, user_input):
            amount = calculate_amount(item, people, days)
            result.append({
                "name": item['name'],
                "category": item['category'],
                "priority": item.get('priority', 'medium'),
                "amount": amount,
                "note": item.get('note', '')
            })
    
    return result