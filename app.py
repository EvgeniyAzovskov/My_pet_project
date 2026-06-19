import streamlit as st
from route_calculator import get_route_info
from map_generator import generate_route_map
from streamlit_folium import folium_static
from checklist_engine import generate_checklist
import re

st.set_page_config(page_title="Trip Checklist", page_icon="🧳")
st.title("🧳 Планировщик путешествий")

# ============================================
# БОКОВАЯ ПАНЕЛЬ
# ============================================
with st.sidebar:
    st.header("⚙️ Настройки")
    
    # ===== МАРШРУТ =====
    st.subheader("🗺️ Маршрут")
    start_city = st.text_input("Город старта", value="Москва")
    end_city = st.text_input("Город финиша", value="Владивосток")
    
    # Кнопка расчета маршрута
    if st.button("🚀 Рассчитать маршрут", type="primary"):
        with st.spinner("Ищем города..."):
            route = get_route_info(start_city, end_city)
            if route:
                st.session_state['route'] = route
                st.session_state['distance'] = route['distance_km']
                st.success(f"✅ Расстояние: {route['distance_km']} км")
            else:
                st.error("❌ Город не найден!")
    
    # ===== ОСНОВНЫЕ ПАРАМЕТРЫ =====
    st.markdown("---")
    st.subheader("👥 Путешественники")
    people = st.number_input("👥 Человек", min_value=1, max_value=6, value=2, step=1)
    days = st.number_input("📅 Дней", min_value=1, max_value=60, value=14, step=1)
    
    # Расстояние (автоматически или вручную)
    if 'distance' in st.session_state:
        distance = st.session_state['distance']
        st.info(f"📏 Расстояние: {distance} км (из маршрута)")
    else:
        distance = st.number_input("📏 Расстояние (км)", min_value=100, max_value=20000, value=8000, step=100)
    
    # ===== ТОПЛИВО =====
    st.markdown("---")
    st.subheader("⛽ Топливо")
    fuel_consumption = st.number_input("Расход (л/100км)", min_value=1.0, max_value=30.0, value=10.0, step=0.5)
    fuel_price = st.number_input("Цена за литр (руб)", min_value=10, max_value=150, value=55, step=1)
    tank_volume = st.number_input("Объем бака (л)", min_value=20, max_value=200, value=60, step=5)
    reserve_percent = st.slider("Запас топлива (%)", min_value=5, max_value=30, value=10, step=5)
    
    # ===== КЕМПИНГ =====
    st.markdown("---")
    camping = st.checkbox("🏕️ Ночлег в палатке", value=True)
    season = st.selectbox("🌤️ Сезон", ["summer", "winter", "autumn", "spring"])
    template = st.selectbox("🏕️ Тип", ["wild", "standard", "luxury"])

# ============================================
# ОСНОВНОЙ ЭКРАН
# ============================================

# Если маршрут рассчитан - показываем карту
if 'route' in st.session_state:
    route = st.session_state['route']
    
    # ===== КАРТА =====
    st.markdown("## 🗺️ Карта маршрута")
    try:
        route_map = generate_route_map(
            route['start_lat'], route['start_lon'],
            route['end_lat'], route['end_lon'],
            route['distance_km']
        )
        folium_static(route_map, width=1000, height=500)
    except Exception as e:
        st.error(f"Ошибка карты: {e}")

# ===== РАСЧЕТ ТОПЛИВА (автоматически) =====
if distance > 0:
    st.markdown("---")
    st.markdown("## ⛽ Расчет топлива")
    
    total_liters = (distance / 100) * fuel_consumption
    total_cost = total_liters * fuel_price
    reserve_factor = 1 + (reserve_percent / 100)
    total_liters_with_reserve = total_liters * reserve_factor
    total_cost_with_reserve = total_cost * reserve_factor
    effective_range = (tank_volume / fuel_consumption) * 100
    refuels_count = distance / effective_range
    refuels_count = int(refuels_count) + (1 if refuels_count % 1 > 0 else 0)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("📊 Всего литров", f"{total_liters_with_reserve:.1f} л")
        st.metric("💸 Стоимость топлива", f"{total_cost_with_reserve:,.0f} руб")
    with col2:
        st.metric("⛽ Заправок", f"{refuels_count} раз", f"~{effective_range:.0f} км/бак")
        st.metric("📅 Расход в день", f"{total_cost_with_reserve/days:,.0f} руб")
with col3:
        st.metric("🚗 Расход", f"{fuel_consumption:.1f} л/100км")
        st.metric("🛢️ Запас хода", f"~{effective_range:.0f} км")

# ===== КНОПКА ГЕНЕРАЦИИ ЧЕК-ЛИСТА =====
st.markdown("---")
if st.button("✅ Собрать чек-лист", type="primary"):
    user_input = {
        "season": season,
        "template": template,
        "camping": camping,
        "people": people,
        "days": days,
        "distance": distance
    }
    
    checklist = generate_checklist(user_input)
    
    if checklist:
        st.success(f"✅ {len(checklist)} позиций")
        
        # Группировка
        categories = {}
        for item in checklist:
            cat = item['category']
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(item)
        
        # Показываем чек-лист
        for cat, items in categories.items():
            with st.expander(f"📌 {cat} ({len(items)})", expanded=True):
                for item in items:
                    label = item['name']
                    if item.get('amount'):
                        label += f" → **{item['amount']}**"
                    if item.get('price'):
                        label += f" (💰 {item['price']})"
                    if item.get('note'):
                        label += f" *({item['note']})*"
                    st.checkbox(label, key=f"{item['name']}_{hash(label)}")
        
        # ИТОГО
        total_food = 0
        for cat, items in categories.items():
            for item in items:
                if item.get('price'):
                    price_match = re.search(r'(\d+)', item['price'])
                    if price_match:
                        total_food += int(price_match.group(1))
        
        if total_food > 0:
            st.markdown("---")
            st.markdown("## 💰 Общий бюджет")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("🍜 Продукты", f"{total_food:,.0f} руб")
            with col2:
                st.metric("⛽ Топливо", f"{total_cost_with_reserve:,.0f} руб")
            with col3:
                total_all = total_food + total_cost_with_reserve
                st.metric("💰 ИТОГО", f"{total_all:,.0f} руб", delta=f"~{total_all/days:,.0f} руб/день")
    else:
        st.warning("Чек-лист пуст. Проверьте условия.")