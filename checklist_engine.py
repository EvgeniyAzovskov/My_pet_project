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
    """Расчет количества продукта на основе нормы на человека"""
    calc = item.get('calculation')
    if not calc:
        return None
    
    # Новый тип: расчет в пакетах с распределением
    if calc.get('type') == 'packets':
        # Сколько всего пакетов можно съесть за поездку (максимум 2 в день на человека)
        total_packets_allowed = people_count * days * 2
        
        # Считаем, сколько всего видов круп выбрано
        # Для этого нам нужно знать, сколько пунктов с типом "packets" в чек-листе
        # Мы передадим это через глобальную переменную или пересчитаем позже
        
        # Пока возвращаем "рассчитается позже"
        return {"type": "packets", "people": people_count, "days": days}
    
    elif 'per_person_per_day' in calc:
        # Старый расчет для других продуктов
        total_kg = calc['per_person_per_day'] * people_count * days
        return f"{round(total_kg * 2) / 2:.1f} кг"
    
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
    
    # Сначала соберем все элементы, чтобы посчитать количество круп
    temp_result = []
    packet_items = []
    
    for item in all_items:
        if check_condition(item, user_input):
            temp_result.append(item)
            if item.get('calculation', {}).get('type') == 'packets':
                packet_items.append(item)
    
    # Теперь рассчитаем количества
    for item in temp_result:
        calc = item.get('calculation')
        if calc and calc.get('type') == 'packets':
            # Передаем количество видов круп
            amount = calculate_amount(item, people, days, len(packet_items))
        else:
            amount = calculate_amount(item, people, days)
        
        result.append({
            "name": item['name'],
            "category": item['category'],
            "priority": item.get('priority', 'medium'),
            "amount": amount,
            "note": item.get('note', '')
        })
    
    return result