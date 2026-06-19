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
    """Расчет количества продукта и стоимости"""
    calc = item.get('calculation')
    if not calc:
        return None, None
    
    calc_type = calc.get('type')
    
    # Расчет для пакетов (крупы)
    if calc_type == 'packets':
        packets_per_day = calc.get('packets_per_person_per_day', 1) * people_count
        total_packets = int(packets_per_day * days)
        price_per_packet = calc.get('price_per_packet', 0)
        total_price = total_packets * price_per_packet
        amount_text = f"{total_packets} пакетов"
        price_text = f"{total_price} руб" if total_price > 0 else None
        return amount_text, price_text
    
    # Расчет для банок (тушенка, консервы)
    elif calc_type == 'cans':
        cans_per_day = calc.get('cans_per_person_per_day', 1) * people_count
        total_cans = int(cans_per_day * days)
        price_per_can = calc.get('price_per_can', 0)
        total_price = total_cans * price_per_can
        amount_text = f"{total_cans} банок"
        price_text = f"{total_price} руб" if total_price > 0 else None
        return amount_text, price_text
    
    # Расчет для штук (чай, сгущенка, хлебцы, вода)
    elif calc_type == 'pieces':
        pieces_per_trip = calc.get('pieces_per_trip', 1)
        total_pieces = pieces_per_trip
        price_per_piece = calc.get('price_per_piece', 0)
        total_price = total_pieces * price_per_piece
        amount_text = f"{total_pieces} шт"
        price_text = f"{total_price} руб" if total_price > 0 else None
        return amount_text, price_text
    
    # Расчет для кг (сахар, орехи, сухофрукты, фрукты)
    elif calc_type == 'kg':
        kg_per_trip = calc.get('kg_per_trip', 1)
        total_kg = kg_per_trip
        price_per_kg = calc.get('price_per_kg', 0)
        total_price = total_kg * price_per_kg
        amount_text = f"{total_kg:.1f} кг"
        price_text = f"{total_price} руб" if total_price > 0 else None
        return amount_text, price_text
    
    # Расчет для набора (специи)
    elif calc_type == 'set':
        price_per_set = calc.get('price_per_set', 0)
        amount_text = "1 набор"
        price_text = f"{price_per_set} руб" if price_per_set > 0 else None
        return amount_text, price_text
    
    return None, None

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