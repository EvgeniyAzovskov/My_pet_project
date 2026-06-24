import streamlit as st
from route_calculator import get_route_info
from map_generator import generate_route_map
from streamlit_folium import folium_static
from destinations_data import get_all_destinations, get_destination, get_campings
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
        font-size: 3rem;
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
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }
    .destination-card {
        background: white;
        border-radius: 16px;
        padding: 1.5rem;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08);
        border: 1px solid #e8ecf0;
        transition: all 0.3s;
        height: 100%;
    }
    .destination-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 30px rgba(102, 126, 234, 0.2);
        border-color: #667eea;
    }
    .destination-card .name {
        font-size: 1.4rem;
        font-weight: 700;
        color: #1a1a2e;
    }
    .destination-card .description {
        color: #666;
        font-size: 0.9rem;
        margin: 0.5rem 0;
    }
    .destination-card .stats {
        display: flex;
        gap: 1rem;
        margin-top: 0.5rem;
        font-size: 0.8rem;
        color: #888;
    }
    .camping-card {
        background: #f8f9fa;
        border-radius: 12px;
        padding: 1rem;
        border-left: 4px solid #4caf50;
        margin: 0.5rem 0;
        transition: all 0.3s;
    }
    .camping-card:hover {
        background: #f0f4ff;
    }
    .camping-card .name {
        font-weight: 600;
        color: #1a1a2e;
    }
    .camping-card .price {
        color: #667eea;
        font-weight: 700;
    }
    .camping-card .features {
        display: flex;
        gap: 0.5rem;
        flex-wrap: wrap;
        margin-top: 0.3rem;
    }
    .camping-card .feature {
        background: white;
        padding: 0.2rem 0.6rem;
        border-radius: 12px;
        font-size: 0.7rem;
        color: #666;
        border: 1px solid #ddd;
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
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# ============================================
# ШАПКА
# ============================================
st.markdown('<div class="main-title">🚗 TripPlanner</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">📋 Выберите направление, кемпинг и рассчитайте бюджет</div>', unsafe_allow_html=True)

# ============================================
# СБРОС СОСТОЯНИЯ
# ============================================
if 'reset_clicked' in st.session_state and st.session_state.reset_clicked:
    for key in ['selected_dest', 'selected_camping', 'route_data', 'budget_calculated']:
        if key in st.session_state:
            del st.session_state[key]
    st.session_state.reset_clicked = False
    st.rerun()

# ============================================
# ШАГ 1: ВЫБОР НАПРАВЛЕНИЯ
# ============================================
if 'selected_dest' not in st.session_state:
    st.markdown('<div class="section-title">🌍 Выберите направление</div>', unsafe_allow_html=True)
    
    destinations = get_all_destinations()
    cols = st.columns(3)
    
    for idx, (key, dest) in enumerate(destinations.items()):
        with cols[idx % 3]:
            st.markdown(f"""
            <div class="destination-card">
                <div class="name">{dest['name']}</div>
                <div class="description">{dest['description']}</div>
                <div class="stats">
                    <span>📏 {dest['distance_from_msk']} км от Москвы</span>
                    <span>📅 {dest['recommended_days']} дней</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button(f"📌 Выбрать", key=f"select_{key}", use_container_width=True):
                st.session_state.selected_dest = key
                st.rerun()

# ============================================
# ШАГ 2: ВЫБОР КЕМПИНГА
# ============================================
if 'selected_dest' in st.session_state and 'selected_camping' not in st.session_state:
    dest_key = st.session_state.selected_dest
    dest = get_destination(dest_key)
    
    if dest:
        st.markdown(f'<div class="section-title">🏕️ Кемпинги в {dest["name"]}</div>', unsafe_allow_html=True)
        
        if st.button("⬅️ Выбрать другое направление", use_container_width=True):
            for key in ['selected_dest', 'selected_camping', 'route_data', 'budget_calculated']:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()
        
        campings = get_campings(dest_key)
        
        for camping in campings:
            features_html = " ".join([f'<span class="feature">✅ {f}</span>' for f in camping['features']])
            st.markdown(f"""
            <div class="camping-card">
                <div class="name">{camping['name']}</div>
                <div class="price">💰 {camping['price_per_night']} ₽/ночь</div>
                <div class="description">{camping['description']}</div>
                <div class="features">{features_html}</div>
                <div>⭐ {camping['rating']}/5.0</div>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button(f"🏕️ Выбрать", key=f"camping_{camping['name']}", use_container_width=True):
                st.session_state.selected_camping = camping
                st.session_state.camping_price = camping['price_per_night']
                st.rerun()

# ============================================
# ШАГ 3: РАСЧЕТ БЮДЖЕТА
# ============================================
if 'selected_camping' in st.session_state:
    dest_key = st.session_state.selected_dest
    dest = get_destination(dest_key)
    camping = st.session_state.selected_camping
    
    st.markdown(f'<div class="section-title">📊 Расчет бюджета для {dest["name"]}</div>', unsafe_allow_html=True)
    
    # ===== НАСТРОЙКИ =====
    col1, col2 = st.columns(2)
    with col1:
        start_city = st.text_input("📍 Город старта", value="Москва")
    with col2:
        days = st.number_input("📅 Количество дней", min_value=1, max_value=30, value=dest['recommended_days'], step=1)
    
    # Расчет маршрута
    route_data = None
    if st.button("🚀 Рассчитать маршрут", type="primary", use_container_width=True):
        with st.spinner("🔄 Ищем маршрут..."):
            route_data = get_route_info(start_city, dest['name'])
            if route_data:
                st.session_state.route_data = route_data
                st.session_state.distance = route_data['distance_km']
                st.success(f"✅ Расстояние: {route_data['distance_km']:,} км")
            else:
                st.session_state.distance = dest['distance_from_msk']
                st.warning(f"⚠️ Используем примерное расстояние: {dest['distance_from_msk']:,} км")
    
    # Используем сохраненное расстояние
    if 'distance' in st.session_state:
        distance = st.session_state.distance
    else:
        distance = dest['distance_from_msk']
    
    # ===== ОБРАТНЫЙ ПУТЬ =====
    round_trip = st.checkbox("🔄 Обратный маршрут (туда и обратно)", value=True)
    total_distance = distance * 2 if round_trip else distance
    
    if round_trip:
        st.info(f"📏 Общее расстояние: {total_distance:,} км (включая обратную дорогу)")
    
    # ===== ТОПЛИВО =====
    st.markdown("---")
    st.markdown("### ⛽ Топливо")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        fuel_consumption = st.number_input("Расход (л/100км)", min_value=5.0, max_value=20.0, value=10.0, step=0.5)
    with col2:
        fuel_price = st.number_input("Цена за литр (₽)", min_value=40, max_value=100, value=66, step=1)
    with col3:
        tank_volume = st.number_input("Объем бака (л)", min_value=30, max_value=150, value=60, step=5)
    
    # ===== КЕМПИНГ =====
    st.markdown("---")
    st.markdown("### 🏕️ Проживание")
    
    col1, col2 = st.columns(2)
    with col1:
        camping_price = st.number_input("Цена кемпинга (₽/ночь)", min_value=0, max_value=5000, value=camping['price_per_night'], step=50)
    with col2:
        camping_nights = st.number_input("Ночей в кемпинге", min_value=0, max_value=days, value=days, step=1)
    
    total_camping_cost = camping_price * camping_nights
    
    # ===== РАСЧЕТ БЮДЖЕТА =====
    st.markdown("---")
    
    if st.button("💰 Рассчитать бюджет", type="primary", use_container_width=True):
        st.session_state.budget_calculated = True
    
    if st.session_state.get('budget_calculated', False):
        # Расчет топлива
        total_liters = (total_distance / 100) * fuel_consumption
        total_cost = total_liters * fuel_price
        
        # Количество заправок
        refuels_count = int(total_distance / ((tank_volume / fuel_consumption) * 100)) + 1
        
        # Итог
        grand_total = total_cost + total_camping_cost
        
        st.markdown("---")
        st.markdown("## 💰 Итоговый бюджет")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("⛽ Топливо", f"{total_cost:,.0f} ₽")
            st.caption(f"{total_liters:.1f} л × {fuel_price} ₽")
        with col2:
            st.metric("🏕️ Кемпинг", f"{total_camping_cost:,.0f} ₽")
            st.caption(f"{camping_nights} ночей × {camping_price} ₽")
        with col3:
            st.metric("⛽ Заправок", f"{refuels_count} раз")
            st.caption(f"~{(tank_volume / fuel_consumption) * 100:.0f} км на баке")
        with col4:
            st.metric("💰 ИТОГО", f"{grand_total:,.0f} ₽", delta=f"~{grand_total/days:.0f} ₽/день")
        
        # Детализация
        with st.expander("📋 Детализация бюджета", expanded=True):
            st.markdown("""
            | Статья | Сумма |
            |--------|-------|
            | Топливо | {:.0f} ₽ |
            | Кемпинг | {:.0f} ₽ |
            | ИТОГО | {:.0f} ₽ |
            """.format(total_cost, total_camping_cost, grand_total))
        
        # Карта
        if 'route_data' in st.session_state and st.session_state.route_data:
            st.markdown("---")
            st.markdown("### 🗺️ Карта маршрута")
            
            try:
                route_data = st.session_state.route_data
                folium_map = generate_route_map(route_data)
                folium_static(folium_map, width=1200, height=500)
                
                if route_data.get('has_route'):
                    st.caption("✅ Реальный маршрут по дорогам")
                else:
                    st.caption("⚠️ Приблизительный маршрут")
            except Exception as e:
                st.warning("Карта временно недоступна")
    
    # ===== КНОПКА СБРОСА =====
    st.markdown("---")
    if st.button("🔄 Начать заново", use_container_width=True):
        st.session_state.reset_clicked = True
        st.rerun()

# ============================================
# ФУТЕР
# ============================================
st.markdown('<div class="footer">TripPlanner · Планировщик путешествий · v1.0</div>', unsafe_allow_html=True)