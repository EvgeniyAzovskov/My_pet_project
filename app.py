import streamlit as st
from route_calculator import get_route_info
from map_generator import generate_route_map
from streamlit_folium import folium_static
from checklist_engine import generate_checklist
import re
import pandas as pd

st.set_page_config(
    page_title="TripPlanner",
    page_icon="🚗",
    layout="wide"
)

# ============================================
# CSS
# ============================================
st.markdown("""
<style>
    .main-title {
        font-size: 3.5rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0.2rem;
    }
    .sub-title {
        text-align: center;
        color: #666;
        font-size: 1.2rem;
        margin-bottom: 2rem;
    }
    /* Убираем белую полосу над полями ввода */
    .stTextInput > div > div {
        border-top: none !important;
    }
    .stTextInput > div:before {
        display: none !important;
    }
    /* Убираем шарики */
    .stBalloon {
        display: none !important;
    }
    /* Скрываем лишние рамки */
    .stTextInput > div {
        border: 1px solid #ddd !important;
        border-radius: 8px !important;
    }
    .stTextInput > div:focus-within {
        border-color: #667eea !important;
    }
    .search-box {
        background: white;
        padding: 2rem;
        border-radius: 16px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        border: 1px solid #e8ecf0;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        border: 1px solid #f0f0f0;
        text-align: center;
        transition: all 0.3s;
    }
    .metric-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 6px 20px rgba(0,0,0,0.1);
    }
    .metric-card .value {
        font-size: 2rem;
        font-weight: 700;
        color: #1a1a2e;
    }
    .metric-card .label {
        font-size: 0.9rem;
        color: #888;
        margin-top: 0.3rem;
    }
    .section-title {
        font-size: 1.5rem;
        font-weight: 600;
        color: #1a1a2e;
        margin-top: 2rem;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 3px solid #667eea;
    }
    .footer {
        text-align: center;
        color: #999;
        font-size: 0.8rem;
        margin-top: 3rem;
        padding-top: 1rem;
        border-top: 1px solid #eee;
    }
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 8px;
        font-weight: 600;
        padding: 0.6rem 2rem;
        transition: all 0.3s;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
    }
    .budget-card {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        padding: 1.5rem;
        border-radius: 12px;
        border-left: 4px solid #667eea;
    }
    .food-info {
        background: #f0f4ff;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #667eea;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

# ============================================
# ШАПКА
# ============================================
st.markdown('<div class="main-title">🚗 TripPlanner</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">📋 Планируйте путешествия с умом — маршрут, топливо, снаряжение, питание</div>', unsafe_allow_html=True)

# ============================================
# БЛОК ПОИСКА МАРШРУТА
# ============================================
st.markdown('<div class="search-box">', unsafe_allow_html=True)

col1, col2, col3 = st.columns([2, 2, 1])
with col1:
    start_city = st.text_input("📍 Откуда", value="Москва", placeholder="Город старта", label_visibility="collapsed")
with col2:
    end_city = st.text_input("🏁 Куда", value="Владивосток", placeholder="Город финиша", label_visibility="collapsed")
with col3:
    st.markdown("<br>", unsafe_allow_html=True)
    search_clicked = st.button("🚀 Найти маршрут", use_container_width=True)

st.markdown('</div>', unsafe_allow_html=True)

# ============================================
# РАСЧЕТ МАРШРУТА
# ============================================
if search_clicked:
    with st.spinner("🔄 Ищем города и строим маршрут..."):
        route = get_route_info(start_city, end_city)
        if route:
            st.session_state['route'] = route
            st.session_state['distance'] = route['distance_km']
            st.session_state['start_city'] = start_city
            st.session_state['end_city'] = end_city
            st.session_state['route_calculated'] = True
            st.success(f"✅ Маршрут построен! {route['distance_km']:,} км")
            st.rerun()
        else:
            st.error("❌ Город не найден! Проверьте название")

# ============================================
# ЕСЛИ МАРШРУТ ПОСТРОЕН
# ============================================
if 'route' in st.session_state and st.session_state.get('route_calculated', False):
    route = st.session_state['route']
    distance = st.session_state['distance']
    start_city = st.session_state.get('start_city', 'Москва')
    end_city = st.session_state.get('end_city', 'Владивосток')
    
    # ============================================
    # НАСТРОЙКИ ПУТЕШЕСТВИЯ
    # ============================================
    st.markdown('<div class="section-title">⚙️ Настройки путешествия</div>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        people = st.number_input("👥 Человек", min_value=1, max_value=10, value=2, step=1)
    with col2:
        days = st.number_input("📅 Дней", min_value=1, max_value=90, value=14, step=1)
    with col3:
        camping = st.checkbox("🏕️ Палатка", value=True)
    with col4:
        season = st.selectbox("🌤️ Сезон", ["summer", "winter", "autumn", "spring"])
    
    # ===== ОБРАТНЫЙ МАРШРУТ =====
    st.markdown("---")
    col1, col2 = st.columns([1, 3])
    with col1:
        round_trip = st.checkbox("🔄 Обратный маршрут", value=False, help="Добавить обратную дорогу (туда и обратно)")
    
    if round_trip:
        st.info(f"🔄 Маршрут туда и обратно: {distance * 2:,} км (×2)")
        total_distance = distance * 2
    else:
        total_distance = distance
    
    st.markdown("---")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        fuel_consumption = st.number_input(
            "⛽ Расход (л/100км)",
            min_value=1.0,
            max_value=30.0,
            value=10.0,
            step=0.5
        )
    with col2:
        fuel_price = st.number_input(
            "💰 Цена (₽/л)",
            min_value=10,
            max_value=150,
            value=55,
            step=1
        )
    with col3:
        tank_volume = st.number_input(
            "🛢️ Бак (л)",
            min_value=20,
            max_value=200,
            value=60,
            step=5
        )
    with col4:
        reserve_percent = st.slider(
            "Запас (%)",
            min_value=5,
            max_value=30,
            value=10,
            step=5
        )
    
    # ============================================
    # КНОПКА "РАССЧИТАТЬ БЮДЖЕТ"
    # ============================================
    st.markdown("---")
    if st.button("📊 Рассчитать бюджет путешествия", use_container_width=True, type="primary"):
        st.session_state['budget_calculated'] = True
        st.rerun()
    
    # ============================================
    # РАСЧЕТЫ (только если нажата кнопка)
    # ============================================
    if st.session_state.get('budget_calculated', False):
        
        # ===== РАСЧЕТ ТОПЛИВА =====
        total_liters = (total_distance / 100) * fuel_consumption
        total_cost = total_liters * fuel_price
        reserve_factor = 1 + (reserve_percent / 100)
        total_liters_with_reserve = total_liters * reserve_factor
        total_cost_with_reserve = total_cost * reserve_factor
        effective_range = (tank_volume / fuel_consumption) * 100
        refuels_count = int(total_distance / effective_range) + 1
        
        # ===== РАСЧЕТ ПИТАНИЯ =====
        # Нормы питания на человека в день (в рублях)
        food_rates = {
            "wild": {"breakfast": 100, "lunch": 150, "dinner": 150, "snacks": 80},
            "standard": {"breakfast": 200, "lunch": 300, "dinner": 350, "snacks": 150},
            "luxury": {"breakfast": 400, "lunch": 600, "dinner": 700, "snacks": 300}
        }
        
        template = "wild" if camping else "standard"
        rates = food_rates.get(template, food_rates["standard"])
        
        food_per_day_per_person = sum(rates.values())
        total_food_cost = food_per_day_per_person * people * days
        
        food_details = {
            "Завтрак": rates["breakfast"] * people * days,
            "Обед": rates["lunch"] * people * days,
            "Ужин": rates["dinner"] * people * days,
            "Перекусы": rates["snacks"] * people * days
        }
        
        # ============================================
        # ОБЗОР ПОЕЗДКИ
        # ============================================
        st.markdown('<div class="section-title">📊 Обзор поездки</div>', unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="value">{total_distance:,}</div>
                <div class="label">📏 Расстояние (км)</div>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <div class="value">{days}</div>
                <div class="label">📅 Дней в пути</div>
            </div>
            """, unsafe_allow_html=True)
        with col3:
            st.markdown(f"""
            <div class="metric-card">
                <div class="value">{refuels_count}</div>
                <div class="label">⛽ Заправок</div>
            </div>
            """, unsafe_allow_html=True)
        with col4:
            st.markdown(f"""
            <div class="metric-card">
                <div class="value">{total_cost_with_reserve:,.0f} ₽</div>
                <div class="label">💰 Стоимость топлива</div>
            </div>
            """, unsafe_allow_html=True)
        
        # ============================================
        # КАРТА
        # ============================================
        st.markdown('<div class="section-title">🗺️ Карта маршрута</div>', unsafe_allow_html=True)
        
        try:
            folium_map = generate_route_map(route)
            folium_static(folium_map, width=1200, height=500)
            
            if route.get('has_route'):
                st.caption("✅ Реальный маршрут по дорогам · ⛽ АЗС · 🏕️ Кемпинги")
            else:
                st.warning("⚠️ Реальный маршрут не доступен, показана прямая линия")
        except Exception as e:
            st.error(f"Ошибка загрузки карты: {e}")
        
        # ============================================
        # РАСХОДЫ НА ПИТАНИЕ
        # ============================================
        st.markdown('<div class="section-title">🍽️ Расходы на питание</div>', unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="food-info">
            <b>📌 Как считаем:</b><br>
            • {people} чел. × {days} дней = {people * days} человеко-дней<br>
            • Норма: {food_per_day_per_person:.0f} ₽/чел/день<br>
            • Тип питания: {"🏕️ Походный" if camping else "🏨 Стандартный"}
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("🍳 Завтрак", f"{food_details['Завтрак']:,.0f} ₽")
        with col2:
            st.metric("🍝 Обед", f"{food_details['Обед']:,.0f} ₽")
        with col3:st.metric("🍲 Ужин", f"{food_details['Ужин']:,.0f} ₽")
        with col4:
            st.metric("🥜 Перекусы", f"{food_details['Перекусы']:,.0f} ₽")
        
        st.info(f"💰 Итого на питание: {total_food_cost:,.0f} ₽")
        
        # ============================================
        # ЧЕК-ЛИСТ
        # ============================================
        st.markdown('<div class="section-title">🎒 Чек-лист снаряжения</div>', unsafe_allow_html=True)
        
        if st.button("🔄 Собрать чек-лист", use_container_width=True):
            user_input = {
                "season": season,
                "template": "wild" if camping else "standard",
                "camping": camping,
                "people": people,
                "days": days,
                "distance": total_distance
            }
            
            checklist = generate_checklist(user_input)
            
            if checklist:
                st.success(f"✅ Готово! {len(checklist)} позиций")
                
                categories = {}
                for item in checklist:
                    cat = item['category']
                    if cat not in categories:
                        categories[cat] = []
                    categories[cat].append(item)
                
                with st.form(key="checklist_form"):
                    for cat, items in categories.items():
                        with st.expander(f"📌 {cat} ({len(items)})", expanded=True):
                            cols = st.columns(2)
                            for i, item in enumerate(items):
                                with cols[i % 2]:
                                    label = item['name']
                                    if item.get('amount'):
                                        label += f" → **{item['amount']}**"
                                    if item.get('price'):
                                        label += f" (💰 {item['price']})"
                                    if item.get('note'):
                                        label += f" *({item['note']})*"
                                    st.checkbox(label, key=f"{item['name']}_{hash(label)}")
                    
                    st.form_submit_button("📋 Сохранить состояние", use_container_width=True)
                
                # Подсчет стоимости снаряжения
                total_gear_cost = 0
                for cat, items in categories.items():
                    for item in items:
                        if item.get('price'):
                            price_match = re.search(r'(\d+)', item['price'])
                            if price_match:
                                total_gear_cost += int(price_match.group(1))
                
                # ============================================
                # ИТОГОВЫЙ БЮДЖЕТ (ПОСЛЕ ЧЕК-ЛИСТА)
                # ============================================
                st.markdown("---")
                st.markdown('<div class="section-title">💰 Итоговый бюджет путешествия</div>', unsafe_allow_html=True)
                
                grand_total = total_cost_with_reserve + total_food_cost + total_gear_cost
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("⛽ Топливо", f"{total_cost_with_reserve:,.0f} ₽")
                with col2:
                    st.metric("🍽️ Питание", f"{total_food_cost:,.0f} ₽")
                with col3:
                    st.metric("🎒 Снаряжение", f"{total_gear_cost:,.0f} ₽")
                with col4:
                    st.metric("💰 ИТОГО", f"{grand_total:,.0f} ₽", delta=f"~{grand_total/days:,.0f} ₽/день")
                
                st.caption("📌 Снаряжение рассчитано из чек-листа. Цены примерные.")
            else:
                st.warning("Чек-лист пуст. Проверьте условия")
    
    # ============================================
    # КНОПКА НОВОГО МАРШРУТА
    # ============================================
    if st.button("🔄 Новый маршрут", use_container_width=True):
        for key in ['route', 'distance', 'start_city', 'end_city', 'route_calculated', 'budget_calculated']:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()

# ============================================
# ФУТЕР
# ============================================
st.markdown('<div class="footer">TripPlanner · Планировщик путешествий · v1.0</div>', unsafe_allow_html=True)