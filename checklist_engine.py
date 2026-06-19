import json

def load_checklist_data():
    with open('checklist_data.json', 'r', encoding='utf-8') as f:
        return json.load(f)['items']

def check_condition(item, user_input):
    conditions = item.get('conditions', [])
    
    # Если условий нет — вещь всегда нужна
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
    
    if 'per_person_per_day' in calc:
        # Крупы: граммы на человека в день
        total_kg = calc['per_person_per_day'] * people_count * days
        # Округляем вверх до 0.5 кг
        return f"{round(total_kg * 2) / 2:.1f} кг"
    
    elif 'cans_per_day_for_2' in calc:
        # Тушенка: из расчета на 2 человек
        cans_per_day = calc['cans_per_day_for_2'] * (people_count / 2)
        total_cans = cans_per_day * days
        # Округляем до целых банок вверх
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