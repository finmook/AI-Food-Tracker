import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime


API_URL="http://127.0.0.1:8000"
#import & config
st.set_page_config(
    page_title="AI Food Tracker",
    page_icon="🍱",
    layout="wide"
)

#session state
if "calorie_goal" not in st.session_state:
    st.session_state.calorie_goal=2200

if "protein_goal" not in st.session_state:
    st.session_state.protein_goal=120

if "analyzed_items" not in st.session_state:
    st.session_state.analyzed_items=[]

#mock data
def get_fake_today_logs():
    return [
        {
            "food_name": "Boiled egg",
            "quantity": "2 pcs",
            "meal_type": "breakfast",
            "calories": 140,
            "protein": 12,
            "source": "manual",
            "eaten_at": "2026-05-13 08:00"
        },
        {
            "food_name":"Rice",
            "quantity":"1 bowl",
            "meal_type":"lunch",
            "calories":220,
            "protein":4,
            "source":"manual",
            "eaten_at":"2026-05-13 12:00"
        }
    ]

def get_fake_weekly_summary():
    return [
        {"day":"2026-05-07","total_calories":1800,"total_protein":90},
        {"day":"2026-05-08","total_calories":2100,"total_protein":105},
        {"day":"2026-05-09","total_calories":1900,"total_protein":95},
        {"day":"2026-05-10","total_calories":2300,"total_protein":120},
        {"day":"2026-05-11","total_calories":17500,"total_protein":85},
        {"day":"2026-05-12","total_calories":2000,"total_protein":100},
        {"day":"2026-05-13","total_calories":360,"total_protein":16},
    ]

st.sidebar.title("⚙️ Setting")
st.session_state.calorie_goal=st.sidebar.slider(
    "Daily calorie goal",
    min_value=1200,
    max_value=4000,
    value=st.session_state.calorie_goal,
    step=50
)
st.session_state.protein_goal=st.sidebar.slider(
    "Daily protein goal (g)",
    min_value=40, 
    max_value=250,
    value=st.session_state.protein_goal,
    step=5,
)

st.sidebar.divider()

st.sidebar.subheader("🍽️ Add food")

food_text=st.sidebar.text_area(
    "What did you eat?",
    placeholder="Example: I ate 2 boiled eggs and 1 bowl of rice",
    height=120,
)

analyze_button=st.sidebar.button(
    "Analyze with AI",
    use_container_width=True
)

if analyze_button:
    if food_text.strip()=="":
        st.sidebar.warning("Please enter food text first.")
    else:
        st.session_state.analyzed_items=[
            {
                "food_name":"Boiled egg",
                "quantity":"2 pcs",
                "calories":140
            },
            {
                "food_name":"Rice",
                "quantity": "1 bowl",
                "calories":220,
                "protein":4,
                "source":"ai_estimate"
            }
        ]
        st.sidebar.success("Fake AI analyzed your food.")

#main title and data
st.title("🍱 AI Food Tracker")
st.caption("Track calories and protein from natural language food input.")

today_logs=get_fake_today_logs()
weekly_summary=get_fake_weekly_summary()

today_df=pd.DataFrame(today_logs)
weekly_df=pd.DataFrame(weekly_summary)

if today_df.empty:
    total_calories=0
    total_protein=0
else:
    total_calories=today_df["calories"].sum()
    total_protein=today_df["protein"].sum()

remaining_calories=st.session_state.calorie_goal-total_calories
remaining_protein=st.session_state.protein_goal-total_protein

col1,col2,col3,col4=st.columns(4)

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
    calorie_percent=min(total_calories/st.session_state.calorie_goal,1)
    st.metric("Calorie_goal",f"{st.session_state.calorie_goal} kcal")
    st.progress(calorie_percent)

with col4:
    protein_percent=min(total_protein/st.session_state.protein_goal,1)
    st.metric("Protein goal",f"{st.session_state.protein_goal} g")
    st.progress(protein_percent)

st.divider()
st.subheader("🤖 AI Food Result Preview")

if len(st.session_state.analyzed_items)==0:
    st.info("Enter food text in the sidebar and click Analyze with AI.")
else:
    edited_items=[]
    for i,item in enumerate(st.session_state.analyzed_items):
        with st.expander(
            f"{item.get('food_name','Food item')}-{item.get('quantity','')}",
            expanded=True
        ):
            food_name=st.text_input(
                "Food name",
                value=item.get("food_name",""),
                key=f"food_name_{i}"
            )

            quantity=st.text_input(
                "Quantity",
                value=item.get("quantity",""),
                key=f"quantity_{i}"
            )
    
            meal_type=st.selectbox(
                "Meal type",
                ["breakfast","lunch","dinner","snack"],
                key=f"meal_type_{i}"
            )

            calories=st.number_input(
                "Calories",
                min_value=0,
                value=int(item.get("calories",0)),
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

            source=st.text_input(
                "Source",
                value=item.get("source","ai_estimate"),
                key=f"source_{i}"
            )

            edited_items.append({
                "food_name":food_name,
                "quantity":quantity,
                "meal_type":meal_type,
                "calories":calories,
                "protein":protein,
                "source":source,
                "eaten_at": datetime.now().isoformat()
            })
    if st.button("Confirm and Save food",use_container_width=True):
        st.success("For now this is fake save. Backend will be added later.")
        st.write(edited_items)


#food log table
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

#charts
st.divider()
st.subheader("📊 Weekly Summary")
if weekly_df.empty:
    st.info("No weekly data yet.")
else:
    fig=go.Figure(

    )
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

    st.plotly_chart(fig,use_container_width=True)
    # st.line_chart(
    #     weekly_df,
    #     x="day",
    #     y="total_calories"
    # )
    # st.barchart(
    #     weekly_df,
    #     x="day",
    #     y=total_protein
    # )