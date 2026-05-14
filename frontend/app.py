import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
from dotenv import load_dotenv
import os

load_dotenv()
API_URL = os.getenv("API_URL")

st.set_page_config(
    page_title="AI Food Tracker",
    page_icon="🍱",
    layout="wide"
)


def api_get(path: str):
    try:
        response = requests.get(f"{API_URL}{path}", timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError:
        try:
            st.error(response.json())
        except Exception:
            st.error(response.text)
        return []
    except requests.exceptions.RequestException as e:
        st.error(f"Backend error: {e}")
        return []


def api_post(path: str, payload: dict):
    try:
        response = requests.post(f"{API_URL}{path}", json=payload, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError:
        try:
            st.error(response.json())
        except Exception:
            st.error(response.text)
        return None
    except requests.exceptions.RequestException as e:
        st.error(f"Backend error: {e}")
        return None


def api_delete(path: str):
    try:
        response = requests.delete(f"{API_URL}{path}", timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError:
        try:
            st.error(response.json())
        except Exception:
            st.error(response.text)
        return None
    except requests.exceptions.RequestException as e:
        st.error(f"Backend error: {e}")
        return None


if "calorie_goal" not in st.session_state:
    st.session_state.calorie_goal = 2200

if "protein_goal" not in st.session_state:
    st.session_state.protein_goal = 120

if "analyzed_result" not in st.session_state:
    st.session_state.analyzed_result = None


st.sidebar.title("⚙️ Setting")

st.session_state.calorie_goal = st.sidebar.slider(
    "Daily calorie goal",
    min_value=1200,
    max_value=4000,
    value=st.session_state.calorie_goal,
    step=50
)

st.session_state.protein_goal = st.sidebar.slider(
    "Daily protein goal (g)",
    min_value=40,
    max_value=250,
    value=st.session_state.protein_goal,
    step=5
)

st.sidebar.divider()
st.sidebar.subheader("🍽️ Add food")

food_text = st.sidebar.text_area(
    "What did you eat?",
    placeholder="Example: 2 eggs 1 chicken breast",
    height=120
)

if st.sidebar.button("Analyze with AI", use_container_width=True):
    if food_text.strip() == "":
        st.sidebar.warning("Please enter food text first.")
    else:
        result = api_post("/analyze-food", {"text": food_text})
        if result:
            st.session_state.analyzed_result = result
            st.sidebar.success("AI analyzed your food.")


if st.sidebar.button("Analyze and Save directly", use_container_width=True):
    if food_text.strip() == "":
        st.sidebar.warning("Please enter food text first.")
    else:
        result = api_post("/food-logs/ai", {"text": food_text})
        if result:
            st.sidebar.success("Food saved to database.")
            st.session_state.analyzed_result = None
            st.rerun()


st.title("🍱 AI Food Tracker")
st.caption("Track calories and protein from natural language food input.")


today_logs = api_get("/food-logs/today")
weekly_summary = api_get("/food-logs/weekly")

today_df = pd.DataFrame(today_logs)
weekly_df = pd.DataFrame(weekly_summary)

if today_df.empty:
    total_calories = 0
    total_protein = 0
else:
    total_calories = today_df["calories"].sum()
    total_protein = today_df["protein"].sum()

remaining_calories = st.session_state.calorie_goal - total_calories
remaining_protein = st.session_state.protein_goal - total_protein

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Calories eaten",
        f"{int(total_calories)} kcal",
        f"{int(remaining_calories)} kcal remaining"
    )

with col2:
    st.metric(
        "Protein eaten",
        f"{total_protein:.1f} g",
        f"{remaining_protein:.1f} g remaining"
    )

with col3:
    calorie_percent = min(total_calories / st.session_state.calorie_goal, 1.0)
    st.metric("Calorie goal", f"{st.session_state.calorie_goal} kcal")
    st.progress(calorie_percent)

with col4:
    protein_percent = min(total_protein / st.session_state.protein_goal, 1.0)
    st.metric("Protein goal", f"{st.session_state.protein_goal} g")
    st.progress(protein_percent)


st.divider()
st.subheader("🤖 AI Food Result Preview")

if st.session_state.analyzed_result is None:
    st.info("Enter food text in the sidebar and click Analyze with AI.")
else:
    result = st.session_state.analyzed_result
    final_items = result.get("final_items", [])

    if len(final_items) == 0:
        st.warning("AI could not detect food items.")
    else:
        edited_items = []
        meal_options = ["breakfast", "lunch", "dinner", "snack"]

        for i, item in enumerate(final_items):
            with st.expander(
                f"{item.get('food_name', 'Food item')} - {item.get('quantity', '')}",
                expanded=True
            ):
                food_name = st.text_input(
                    "Food name",
                    value=item.get("food_name", ""),
                    key=f"food_name_{i}"
                )

                quantity = st.text_input(
                    "Quantity",
                    value=item.get("quantity", "1 serving"),
                    key=f"quantity_{i}"
                )

                meal_type_value = item.get("meal_type", "snack")

                meal_type = st.selectbox(
                    "Meal type",
                    meal_options,
                    index=meal_options.index(meal_type_value)
                    if meal_type_value in meal_options
                    else 3,
                    key=f"meal_type_{i}"
                )

                calories = st.number_input(
                    "Calories",
                    min_value=0,
                    value=int(item.get("calories", 0)),
                    step=10,
                    key=f"calories_{i}"
                )

                protein = st.number_input(
                    "Protein (g)",
                    min_value=0.0,
                    value=float(item.get("protein", 0)),
                    step=1.0,
                    key=f"protein_{i}"
                )

                source = st.text_input(
                    "Source",
                    value=item.get("source", "ai_estimate"),
                    key=f"source_{i}"
                )

                edited_items.append({
                    "food_name": food_name,
                    "quantity": quantity,
                    "meal_type": meal_type,
                    "calories": calories,
                    "protein": protein,
                    "source": source
                })

        if st.button("Confirm and Save food", use_container_width=True):
            saved_count = 0

            for item in edited_items:
                save_result = api_post("/food-logs", item)

                if save_result:
                    saved_count += 1

            if saved_count > 0:
                st.success(f"Saved {saved_count} food item(s) to database.")
                st.session_state.analyzed_result = None
                st.rerun()


st.divider()
st.subheader("📋 Today's Food Log")

if today_df.empty:
    st.warning("No food logged today.")
else:
    st.dataframe(
        today_df,
        use_container_width=True,
        hide_index=True
    )

    if "id" in today_df.columns:
        delete_id = st.number_input(
            "Food log ID to delete",
            min_value=1,
            step=1
        )

        if st.button("Delete food log"):
            delete_result = api_delete(f"/food-logs/{delete_id}")

            if delete_result:
                st.success("Food log deleted.")
                st.rerun()


st.divider()
st.subheader("📊 Weekly Summary")

if weekly_df.empty:
    st.info("No weekly data yet.")
else:
    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=weekly_df["day"],
            y=weekly_df["total_protein"],
            name="Protein (g)",
            mode="lines+markers",
            yaxis="y1"
        )
    )

    fig.add_trace(
        go.Scatter(
            x=weekly_df["day"],
            y=weekly_df["total_calories"],
            name="Calories (kcal)",
            mode="lines+markers",
            yaxis="y2"
        )
    )

    fig.update_layout(
        xaxis=dict(title="Day"),
        yaxis=dict(
            title="Protein (g)",
            side="left"
        ),
        yaxis2=dict(
            title="Calories (kcal)",
            side="right",
            overlaying="y"
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        height=450
    )

    st.plotly_chart(fig, use_container_width=True)