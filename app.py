import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import datetime

# --- PAGE SETUP ---
st.set_page_config(page_title="Specialist Pulse", layout="wide", initial_sidebar_state="expanded")

# --- GLOBAL VARIABLES ---
MERIT_GOAL = 5.0
ACCURACY_GOAL = 90.0

# --- FAKE DATA GENERATION (STATE-BASED SPEED LOGIC) ---
@st.cache_data
def generate_data():
    np.random.seed(42)
    start_date = datetime.date(2026, 1, 1)
    end_date = datetime.date.today()
    dates = pd.date_range(start_date, end_date)
    
    state_speeds = {
        "California": 6.0,  
        "Arizona": 4.2,     
        "Colorado": 3.75    
    }

    specialist_profiles = {
        "Avery S.": {"speed_mod": 1.5, "acc": 97},  
        "Jordan T.": {"speed_mod": 0.8, "acc": 84}, 
        "Casey L.": {"speed_mod": -1.0, "acc": 96}, 
        "Taylor R.": {"speed_mod": -1.5, "acc": 81}, 
        "Morgan W.": {"speed_mod": 0.0, "acc": 91}, 
        "Riley B.": {"speed_mod": 2.0, "acc": 94},  
        "Quinn M.": {"speed_mod": -1.2, "acc": 88}, 
        "Reese K.": {"speed_mod": 0.5, "acc": 95},  
        "Drew P.": {"speed_mod": 0.2, "acc": 89}    
    }
    
    states = list(state_speeds.keys())
    
    records = []
    for d in dates:
        for s, profile in specialist_profiles.items():
            state = np.random.choice(states)
            
            base_speed = state_speeds[state] + profile["speed_mod"]
            touches = np.random.normal(base_speed, 0.8)
            touches = max(1, int(round(touches))) 
            
            accuracy = np.clip(np.random.normal(profile["acc"], 2.5), 0, 100) 
            
            records.append([d, s, state, touches, accuracy])
            
    return pd.DataFrame(records, columns=["Date", "Specialist", "State", "Touches Per Hour", "Accuracy Rate (%)"])

df = generate_data()

# --- SIDEBAR FILTERS ---
st.sidebar.markdown("### Dashboard Controls")

min_date = df["Date"].min().date()
max_date = df["Date"].max().date()
selected_dates = st.sidebar.date_input("Select Date Range", [min_date, max_date], min_value=min_date, max_value=max_date)
selected_states = st.sidebar.multiselect("Select States", options=["Arizona", "California", "Colorado"], default=["Arizona", "California", "Colorado"])

st.sidebar.divider()
st.sidebar.markdown("Data powered by Sigma Connection (Simulated)")

# --- FILTERING LOGIC ---
if len(selected_dates) == 2:
    start_filter, end_filter = selected_dates
    mask = (df['Date'].dt.date >= start_filter) & (df['Date'].dt.date <= end_filter) & (df['State'].isin(selected_states))
    filtered_df = df[mask]
else:
    filtered_df = df

agg_df = filtered_df.groupby("Specialist").agg({"Touches Per Hour": "mean", "Accuracy Rate (%)": "mean"}).reset_index()

# --- QUADRANT COLOR LOGIC ---
def get_quadrant_color(row):
    if row["Touches Per Hour"] >= MERIT_GOAL and row["Accuracy Rate (%)"] >= ACCURACY_GOAL:
        return "#00E6A8" # Green (High Speed, High Quality)
    elif row["Touches Per Hour"] < MERIT_GOAL and row["Accuracy Rate (%)"] < ACCURACY_GOAL:
        return "#FF3366" # Red (Low Speed, Low Quality)
    else:
        return "#FFC107" # Orange (Mixed quadrants: Top-Left or Bottom-Right)

if not filtered_df.empty:
    agg_df["Quadrant Color"] = agg_df.apply(get_quadrant_color, axis=1)

# --- HEADER & HIGH-LEVEL METRICS ---
st.markdown("## ⚡ Specialist Pulse Dashboard")
st.markdown("Multi-dimensional workflow tracking and efficiency matrix.")
st.divider()

if not filtered_df.empty:
    avg_touches = round(agg_df["Touches Per Hour"].mean(), 1)
    avg_accuracy = round(agg_df["Accuracy Rate (%)"].mean(), 1)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="Team Avg Touches / Hour", value=f"{avg_touches}", delta=f"{round(avg_touches - MERIT_GOAL, 1)} vs Merit Goal")
    with col2:
        st.metric(label="Team Avg Accuracy Rate", value=f"{avg_accuracy}%", delta=f"{round(avg_accuracy - ACCURACY_GOAL, 1)}% vs Goal")
    with col3:
        st.metric(label="Total Submissions Analyzed", value=f"{len(filtered_df)}")

    st.markdown("<br>", unsafe_allow_html=True)

    # --- ROW 1: BAR CHARTS ---
    col_charts_1, col_charts_2 = st.columns(2)

    with col_charts_1:
        st.markdown("### 🚀 Speed: Touches Per Hour")
        fig_speed = px.bar(
            agg_df.sort_values("Touches Per Hour", ascending=False), 
            x="Specialist", y="Touches Per Hour", text=agg_df.sort_values("Touches Per Hour", ascending=False)["Touches Per Hour"].round(1),
            template="plotly_dark", color_discrete_sequence=["#00E6A8"]
        )
        fig_speed.add_hline(y=MERIT_GOAL, line_dash="dash", line_color="#FF3366", annotation_text=f"Merit Goal ({MERIT_GOAL}/hr)", annotation_position="top right", annotation_font_color="#FF3366")
        fig_speed.update_layout(xaxis_title="", yaxis_title="", showlegend=False, plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
        fig_speed.update_traces(textposition='outside')
        st.plotly_chart(fig_speed, use_container_width=True)

    with col_charts_2:
        st.markdown("### 🎯 Quality: Accuracy Rate")
        # Color coding for the bar chart
        agg_df["Bar Color"] = np.where(agg_df["Accuracy Rate (%)"] >= ACCURACY_GOAL, "#00E6A8", "#FF3366")
        fig_acc = px.bar(
            agg_df.sort_values("Accuracy Rate (%)", ascending=True), 
            x="Accuracy Rate (%)", y="Specialist", orientation='h', text=agg_df.sort_values("Accuracy Rate (%)", ascending=True)["Accuracy Rate (%)"].round(1),
            template="plotly_dark", color="Bar Color", color_discrete_map="identity"
        )
        fig_acc.add_vline(x=ACCURACY_GOAL, line_dash="dash", line_color="#FFFFFF", annotation_text="90% Goal", annotation_position="top left")
        fig_acc.update_layout(xaxis_title="", yaxis_title="", xaxis=dict(range=[75, 100]), showlegend=False, plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
        fig_acc.update_traces(textposition='inside')
        st.plotly_chart(fig_acc, use_container_width=True)

    st.markdown("<br><br>", unsafe_allow_html=True)

    # --- ROW 2: QUADRANT SCATTER PLOT ---
    st.markdown("### 🧭 Efficiency & Accuracy Matrix")

    # The scatter plot now pulls the "Quadrant Color" column we generated
    fig_matrix = px.scatter(
        agg_df, x="Touches Per Hour", y="Accuracy Rate (%)", text="Specialist",
        template="plotly_dark", color="Quadrant Color", color_discrete_map="identity", size_max=60
    )

    # Quadrant Lines
    fig_matrix.add_vline(x=MERIT_GOAL, line_dash="dash", line_color="#FFFFFF", opacity=0.5)
    fig_matrix.add_hline(y=ACCURACY_GOAL, line_dash="dash", line_color="#FFFFFF", opacity=0.5)

    # (Removed text annotations per your request)

    fig_matrix.update_traces(textposition='top center', marker=dict(size=14))
    fig_matrix.update_layout(
        xaxis_title="Touches Per Hour (Speed)", yaxis_title="Accuracy Rate % (Quality)",
        xaxis=dict(range=[1, 9]), yaxis=dict(range=[75, 100]),
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", height=600,
        showlegend=False
    )

    st.plotly_chart(fig_matrix, use_container_width=True)

else:
    st.warning("No data available for the selected dates and states. Please adjust your filters.")
