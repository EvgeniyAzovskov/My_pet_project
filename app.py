import streamlit as st
from route_calculator import get_route_info
from map_generator import generate_route_map
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
    .settings-collapse {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# ============================================
# ШАПКА
# ============================================
st.markdown('<div class="main-title">🚗 TripPlanner</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">📋 Планируйте путешествия с умом — маршрут, топливо, снаряжение</div>', unsafe_allow_html=True)

# ============================================
# БЛОК ПОИСКА МАРШРУТА (как на Aviasales)
# ============================================
st.markdown('<div class="search-box">', unsafe_allow_html=True)

col1, col2, col3 = st.columns([2, 2, 1])
with col1:
    start_city = st.text_input("📍 Откуда", value="Москва", placeholder="Город старта")
with col2:
    end_city = st.text_input("🏁 Куда", value="Владивосток", placeholder="Город финиша")
with col3:
    st.markdown("<br>", unsafe_allow_html=True)  # Отступ для выравнивания
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
            st.success(f"✅ Маршрут построен! {route['distance_km']:,} км")
            st.rerun()
        else:
            st.error("❌ Город не найден! Проверьте название")

# ============================================
# ЕСЛИ МАРШРУТ ПОСТРОЕН
# ============================================
if 'route' in st.session_state:
    route = st.session_state['route']
    distance = st.session_state['distance']
    start_city = st.session_state.get('start_city', 'Москва')
    end_city = st.session_state.get('end_city', 'Владивосток')
    
    # ===== НАСТРОЙКИ ПУТЕШЕСТВИЯ (компактно) =====
    with st.expander("⚙️ Настройки путешествия", expanded=True):
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            people = st.number_input("👥 Человек", min_value=1, max_value=10, value=2, step=1)
        with col2:
            days = st.number_input("📅 Дней", min_value=1, max_value=90, value=14, step=1)
        with col3:
            camping = st.checkbox("🏕️ Палатка", value=True)
        with col4:
            season = st.selectbox("🌤️ Сезон", ["summer", "winter", "autumn", "spring"])
        
        st.markdown("---")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            fuel_consumption = st.number_input("⛽ Расход (л/100км)", min_value=1.0, max_value=30.0, value=10.0, step=0.5)
        with col2:
            fuel_price = st.number_input("💰 Цена (₽/л)", min_value=10, max_value=150, value=55, step=1)
        with col3:
            tank_volume = st.number_input("🛢️ Бак (л)", min_value=20, max_value=200, value=60, step=5)
        with col4:
            reserve_percent = st.slider("Запас (%)", min_value=5, max_value=30, value=10, step=5)
    
    # ===== РАСЧЕТ ТОПЛИВА =====
    total_liters = (distance / 100) * fuel_consumption
    total_cost = total_liters * fuel_price
    reserve_factor = 1 + (reserve_percent / 100)
    total_liters_with_reserve = total_liters * reserve_factor
    total_cost_with_reserve = total_cost * reserve_factor
    effective_range = (tank_volume / fuel_consumption) * 100
    refuels_count = int(distance / effective_range) + 1
    
    # ===== ОБЗОР ПОЕЗДКИ =====
    st.markdown('<div class="section-title">📊 Обзор поездки</div>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="value">{distance:,}</div>
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
    
    # ===== КАРТА =====
    st.markdown('<div class="section-title">🗺️ Карта маршрута</div>', unsafe_allow_html=True)
    
    try:
        deck = generate_route_map(route)
        st.pydeck_chart(deck)
        if route.get('has_route'):
            st.caption("✅ Реальный маршрут по дорогам · ⛽ АЗС · 🏕️ Кемпинги")
        else:
            st.warning("⚠️ Реальный маршрут не доступен, показана прямая линия")
    except Exception as e:
        st.error(f"Ошибка загрузки карты: {e}")
    
    # ===== ДЕТАЛЬНЫЙ РАСЧЕТ =====
    with st.expander("📋 Детальный расчет", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("#### ⛽ Топливо")
            fuel_data = pd.DataFrame({
                "Показатель": ["Расход", "Всего литров", "С запасом", "Цена за литр", "Стоимость", "Стоимость с запасом"],"Значение": [
                    f"{fuel_consumption} л/100км",
                    f"{total_liters:.1f} л",
                    f"{total_liters_with_reserve:.1f} л",
                    f"{fuel_price} ₽/л",
                    f"{total_cost:,.0f} ₽",
                    f"{total_cost_with_reserve:,.0f} ₽"
                ]
            })
            st.dataframe(fuel_data, hide_index=True, use_container_width=True)
        
        with col2:
            st.markdown("#### 🗺️ Маршрут")
            route_data = pd.DataFrame({
                "Показатель": ["Откуда", "Куда", "Расстояние", "Запас хода", "Заправок", "Расход в день"],
                "Значение": [
                    start_city,
                    end_city,
                    f"{distance:,} км",
                    f"{effective_range:.0f} км",
                    f"{refuels_count} раз",
                    f"{total_cost_with_reserve/days:,.0f} ₽"
                ]
            })
            st.dataframe(route_data, hide_index=True, use_container_width=True)
    
    # ===== ЧЕК-ЛИСТ =====
    st.markdown('<div class="section-title">🎒 Чек-лист снаряжения</div>', unsafe_allow_html=True)
    
    if st.button("🔄 Собрать чек-лист", use_container_width=True):
        user_input = {
            "season": season,
            "template": "wild",
            "camping": camping,
            "people": people,
            "days": days,
            "distance": distance
        }
        
        checklist = generate_checklist(user_input)
        
        if checklist:
            st.balloons()
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
                        # Разбиваем на 2 колонки для компактности
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
            
            # Итоговый бюджет
            total_food = 0
            for cat, items in categories.items():
                for item in items:
                    if item.get('price'):
                        price_match = re.search(r'(\d+)', item['price'])
                        if price_match:
                            total_food += int(price_match.group(1))
            
            if total_food > 0:
                st.markdown("---")
                st.markdown("## 💰 Итоговый бюджет")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("🍜 Продукты", f"{total_food:,.0f} ₽")
                with col2:
                    st.metric("⛽ Топливо", f"{total_cost_with_reserve:,.0f} ₽")
                with col3:
                    total_all = total_food + total_cost_with_reserve
                    st.metric("💰 ИТОГО", f"{total_all:,.0f} ₽", delta=f"~{total_all/days:,.0f} ₽/день")
        else:
            st.warning("Чек-лист пуст. Проверьте условия")
    
    # ===== КНОПКА СБРОСА =====
    if st.button("🔄 Новый маршрут", use_container_width=True):for key in ['route', 'distance', 'start_city', 'end_city']:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()

# ============================================
# ФУТЕР
# ============================================
st.markdown('<div class="footer">TripPlanner · Планировщик путешествий · v1.0</div>', unsafe_allow_html=True)