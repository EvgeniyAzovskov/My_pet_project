from map_generator import generate_route_map
from streamlit_folium import folium_static
import streamlit as st
from checklist_engine import generate_checklist
import re

st.set_page_config(page_title="Чек-лист экспедиции", page_icon="🧳")
st.title("🧳 Генератор чек-листа для автоэкспедиции")
st.markdown("### 🚗 Планируйте путешествие с умом!")

# ============================================
# БОКОВАЯ ПАНЕЛЬ НАСТРОЕК (слева)
# ============================================
with st.sidebar:
    st.header("⚙️ Настройки")
    
    st.subheader("📋 Основные параметры")
    season = st.selectbox("🌤️ Сезон", ["summer", "winter", "autumn", "spring"])
    template = st.selectbox("🏕️ Тип поездки", ["wild", "standard", "luxury"])
    camping = st.checkbox("🏕️ Планирую ночевать в палатке (кемпинг)")
    
    st.subheader("👥 Количество")
    people = st.number_input("👥 Человек", min_value=1, max_value=6, value=2, step=1)
    days = st.number_input("📅 Дней в пути", min_value=1, max_value=60, value=14, step=1)
    distance = st.number_input("📏 Расстояние (км)", min_value=100, max_value=20000, value=8000, step=100)
    
    st.markdown("---")
    st.markdown("---")
    st.subheader("🗺️ Маршрут")
    
    start_city = st.text_input("Город старта", value="Москва")
    end_city = st.text_input("Город финиша", value="Владивосток")
    
    # Для продвинутого режима
    with st.expander("📍 Точные координаты (опционально)"):
        start_lat = st.number_input("Широта старта", value=55.7558, format="%.4f")
        start_lon = st.number_input("Долгота старта", value=37.6173, format="%.4f")
        end_lat = st.number_input("Широта финиша", value=43.1154, format="%.4f")
        end_lon = st.number_input("Долгота финиша", value=131.8854, format="%.4f")
    st.subheader("⛽ Топливо")
    col_fuel1, col_fuel2 = st.columns(2)
    with col_fuel1:
        fuel_consumption = st.number_input(
            "Расход (л/100км)",
            min_value=1.0,
            max_value=30.0,
            value=10.0,
            step=0.5,
            help="Средний расход вашего автомобиля"
        )
        tank_volume = st.number_input(
            "Объем бака (л)",
            min_value=20,
            max_value=200,
            value=60,
            step=5,
            help="Полный объем топливного бака"
        )
    with col_fuel2:
        fuel_price = st.number_input(
            "Цена за литр (руб)",
            min_value=10,
            max_value=150,
            value=55,
            step=1,
            help="Средняя цена топлива на маршруте"
        )
        reserve_percent = st.slider(
            "Запас топлива (%)",
            min_value=5,
            max_value=30,
            value=10,
            step=5,
            help="Оставляйте запас для непредвиденных ситуаций"
        )

# ============================================
# ОСНОВНАЯ ЧАСТЬ
# ============================================

if st.button("✅ Собрать полный чек-лист!", type="primary"):
    user_input = {
        "season": season,
        "template": template,
        "camping": camping,
        "people": people,
        "days": days,
        "distance": distance
    }

    checklist = generate_checklist(user_input)

    if not checklist:
        st.warning("Ничего не найдено. Проверьте условия.")
    else:
        # ========== РАСЧЕТ БЕНЗИНА ==========
        st.markdown("---")
        st.markdown("## ⛽ Расчет топлива")
        
        # Базовые расчеты
        total_liters = (distance / 100) * fuel_consumption
        total_cost = total_liters * fuel_price
        
        # С учетом запаса
        reserve_factor = 1 + (reserve_percent / 100)
        total_liters_with_reserve = total_liters * reserve_factor
        total_cost_with_reserve = total_cost * reserve_factor
        
        # Количество заправок
        effective_range = (tank_volume / fuel_consumption) * 100  # км на полном баке
        refuels_count = distance / effective_range
        refuels_count = int(refuels_count) + (1 if refuels_count % 1 > 0 else 0)
        
        # Расходы в день
        cost_per_day = total_cost_with_reserve / days
        
        # Отображение результатов
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(
                label="📊 Всего литров",
                value=f"{total_liters_with_reserve:.1f} л",
                delta=f"+{reserve_percent}% запас"
            )
            st.metric(
                label="💸 Общая стоимость",
                value=f"{total_cost_with_reserve:,.0f} руб"
            )
        with col2:
            st.metric(
                label="⛽ Количество заправок",
                value=f"{refuels_count} раз",
                delta=f"~{effective_range:.0f} км на баке"
            )
            st.metric(label="📅 Расход в день",
                value=f"{cost_per_day:,.0f} руб/день"
            )
        with col3:
            st.metric(
                label="🚗 Расход на 100 км",
                value=f"{fuel_consumption:.1f} л"
            )
            st.metric(
                label="🛢️ Запас хода",
                value=f"~{effective_range:.0f} км"
            )
        
        # Детальный расчет
        with st.expander("📋 Детальный расчет топлива", expanded=False):
            st.write(f"**Расстояние:** {distance} км")
            st.write(f"**Расход:** {fuel_consumption} л/100км")
            st.write(f"**Цена топлива:** {fuel_price} руб/л")
            st.write(f"**Объем бака:** {tank_volume} л")
            st.write(f"**Запас:** {reserve_percent}%")
            st.write("---")
            st.write(f"**Чистое топливо:** {total_liters:.1f} л")
            st.write(f"**Топливо с запасом:** {total_liters_with_reserve:.1f} л")
            st.write(f"**Чистая стоимость:** {total_cost:,.0f} руб")
            st.write(f"**Стоимость с запасом:** {total_cost_with_reserve:,.0f} руб")
            st.write(f"**Заправок (с учетом бака):** {refuels_count} раз")
        
        st.markdown("---")
        
        # ========== ЧЕК-ЛИСТ ==========
        st.success(f"✅ Собрано {len(checklist)} позиций!")
        # ========== КАРТА МАРШРУТА ==========
        st.markdown("---")
        st.markdown("## 🗺️ Карта маршрута с заправками и кемпингами")
        
        # Определяем координаты
        # Если пользователь ввел координаты — используем их
        if 'start_lat' in locals():
            start_lat_use = start_lat
            start_lon_use = start_lon
            end_lat_use = end_lat
            end_lon_use = end_lon
        else:
            # Иначе стандартные
            start_lat_use, start_lon_use = 55.7558, 37.6173
            end_lat_use, end_lon_use = 43.1154, 131.8854
        
        # Создаем карту с реальным маршрутом
        with st.spinner('Строим маршрут... Это может занять 10-20 секунд'):
            try:
                route_map = generate_route_map(
                    start_lat_use, 
                    start_lon_use, 
                    end_lat_use, 
                    end_lon_use, 
                    distance
                )
                
                # Отображаем карту
                folium_static(route_map, width=1000, height=600)
                
                st.caption("""
                Легенда:  
                🔵 Синяя линия — реальный маршрут по дорогам  
                ⛽ Синий маркер — АЗС  
                🏕️ Зеленый маркер — кемпинг  
                🏁 Флаги — старт/финиш
                """)
                
            except Exception as e:
                st.error(f"⚠️ Не удалось построить маршрут: {e}")
                st.info("Попробуйте использовать приближенный маршрут через города.")
                
                # Показываем приближенный маршрут
                from map_generator import get_approximate_route
                route_coords = get_approximate_route(
                    start_lat_use, start_lon_use, 
                    end_lat_use, end_lon_use
                )
                
                m = folium.Map(location=[55.7558, 37.6173], zoom_start=4)
                folium.PolyLine(route_coords, color='orange', weight=4, 
                              popup='Приближенный маршрут').add_to(m)
                folium_static(m, width=1000, height=600)
        # ========== ИТОГОВАЯ СТОИМОСТЬ ==========
        # Подсчет общей стоимости продуктов
        total_food_price = 0
        for cat, items in categories.items():
            for item in items:
                if item.get('price'):
                    price_match = re.search(r'(\d+)', item['price'])
                    if price_match:
                        total_food_price += int(price_match.group(1))
        
        if total_food_price > 0:
            st.markdown("---")
            st.markdown("## 💰 Общий бюджет")
            
            col_total1, col_total2, col_total3 = st.columns(3)
            with col_total1:
                st.metric("🍜 Продукты", f"{total_food_price:,.0f} руб")
            with col_total2:
                st.metric("⛽ Топливо", f"{total_cost_with_reserve:,.0f} руб")
            with col_total3:
                total_all = total_food_price + total_cost_with_reserve
                st.metric("💰 ИТОГО", f"{total_all:,.0f} руб", 
                         delta=f"~{total_all/days:,.0f} руб/день")