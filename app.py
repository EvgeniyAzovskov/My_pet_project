import streamlit as st
from checklist_engine import generate_checklist

st.set_page_config(page_title="Чек-лист экспедиции", page_icon="🧳")
st.title("🧳 Генератор чек-листа для автоэкспедиции")
st.markdown("### 🚗 8 000 км — это серьезно! Давайте соберем всё правильно.")

col1, col2 = st.columns(2)
with col1:
    season = st.selectbox("🌤️ Сезон", ["summer", "winter", "autumn", "spring"])
    template = st.selectbox("🏕️ Тип поездки", ["wild", "standard", "luxury"])
    camping = st.checkbox("🏕️ Планирую ночевать в палатке (кемпинг)")

with col2:
    people = st.number_input("👥 Количество человек", min_value=1, max_value=6, value=2, step=1)
    days = st.number_input("📅 Количество дней в пути", min_value=1, max_value=60, value=14, step=1)
    distance = st.number_input("📏 Общее расстояние (км)", min_value=100, max_value=20000, value=8000, step=100)

# Кнопка генерации чек-листа
if st.button("✅ Собрать полный чек-лист!"):
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
        st.success(f"✅ Собрано {len(checklist)} позиций!")

        # Группировка по категориям
        categories = {}
        for item in checklist:
            cat = item['category']
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(item)

        # =============================================
        # ГЛАВНОЕ ИЗМЕНЕНИЕ: используем st.form!
        # Теперь чекбоксы НЕ перезагружают страницу
        # =============================================
        with st.form(key="checklist_form"):
            for cat, items in categories.items():
                with st.expander(f"📌 {cat} ({len(items)})", expanded=True):
                    for item in items:
                        label = item['name']
                        if item.get('amount'):
                            label += f" → **{item['amount']}**"
                        if item.get('note'):
                            label += f" *({item['note']})*"

                        # Чекбоксы внутри формы — НЕ вызывают перезагрузку!
                        st.checkbox(label, key=f"{item['name']}_{cat}_{hash(label)}")

            # Кнопка внутри формы (можно оставить для красоты)
            st.form_submit_button("🔄 Обновить состояние")