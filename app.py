import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import datetime

# --- PAGE SETUP ---
st.set_page_config(page_title="Specialist Pulse", layout="wide", initial_sidebar_state="expanded")

# --- FAKE DATA GENERATION (PROFILED FOR SEPARATION) ---
@st.cache_data
def generate_data():
    np.random.seed(42)
    start_date = datetime.date(2026, 1, 1)
    end_date = datetime.date.today()
    dates = pd.date_range(start_date, end_date)
    
    # Giving each specialist a "base skill" so the scatter plot spreads out realistically
    specialist_profiles = {
        "Avery S.": {"speed": 29, "acc": 97},  # High/High
        "Jordan T.": {"speed": 27, "acc": 84}, # High/Low
        "Casey L.": {"speed": 15, "acc": 96},  # Low/High
        "Taylor R.": {"speed": 17, "acc": 81}, # Low/Low
        "Morgan W.": {"speed": 23, "acc": 91}, # Middle (Goal)
        "Riley B.": {"speed": 33, "acc": 94},  # Very Fast / Good Acc
        "Quinn M.": {"speed": 14, "acc": 88},  # Slow / Just under Acc
        "Reese K.": {"speed": 21, "acc": 95},  # Just under Speed / High Acc
        "Drew P.": {"speed": 26, "acc": 89}    # Fast / Just under Acc
    }
    states = ["Arizona", "California", "Colorado"]
    
    records = []
    for d in dates:
        for s, profile in specialist_profiles.items():
            state = np.random.choice(states)
            # Add some daily random variance to their base stats
            touches = int(np.random.normal(profile["speed"], 3))
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

# --- HEADER & HIGH-LEVEL METRICS ---
st.markdown("## ⚡ Specialist Pulse Dashboard")
st.markdown("Multi-dimensional workflow tracking and efficiency matrix.")
st.divider()

if not filtered_df.empty:
    avg_touches = round(agg_df["Touches Per Hour"].mean(), 1)
    avg_accuracy = round(agg_df["Accuracy Rate (%)"].mean(), 1)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="Team Avg Touches / Hour", value=f"{avg_touches}", delta=f"{round(avg_touches - 22, 1)} vs Merit Goal")
    with col2:
        st.metric(label="Team Avg Accuracy Rate", value=f"{avg_accuracy}%", delta=f"{round(avg_accuracy - 90, 1)}% vs Goal")
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
        fig_speed.add_hline(y=22, line_dash="dash", line_color="#FF3366", annotation_text="Merit Goal (22/hr)", annotation_position="top right", annotation_font_color="#FF3366")
        fig_speed.update_layout(xaxis_title="", yaxis_title="", showlegend=False, plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
        fig_speed.update_traces(textposition='outside')
        st.plotly_chart(fig_speed, use_container_width=True)

    with col_charts_2:
        st.markdown("### 🎯 Quality: Accuracy Rate")
        agg_df["Color"] = np.where(agg_df["Accuracy Rate (%)"] >= 90.0, "#00E6A8", "#FF3366")
        fig_acc = px.bar(
            agg_df.sort_values("Accuracy Rate (%)", ascending=True), 
            x="Accuracy Rate (%)", y="Specialist", orientation='h', text=agg_df.sort_values("Accuracy Rate (%)", ascending=True)["Accuracy Rate (%)"].round(1),
            template="plotly_dark", color="Color", color_discrete_map="identity"
        )
        fig_acc.add_vline(x=90.0, line_dash="dash", line_color="#FFFFFF", annotation_text="90% Goal", annotation_position="top left")
        fig_acc.update_layout(xaxis_title="", yaxis_title="", xaxis=dict(range=[75, 100]), showlegend=False, plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
        fig_acc.update_traces(textposition='inside')
        st.plotly_chart(fig_acc, use_container_width=True)

    st.markdown("<br><br>", unsafe_allow_html=True)

    # --- ROW 2: QUADRANT SCATTER PLOT ---
    st.markdown("### 🧭 Efficiency & Accuracy Matrix")

    fig_matrix = px.scatter(
        agg_df, x="Touches Per Hour", y="Accuracy Rate (%)", text="Specialist",
        template="plotly_dark", color_discrete_sequence=["#00E6A8"], size_max=60
    )

    # Quadrant Lines
    fig_matrix.add_vline(x=22, line_dash="dash", line_color="#FFFFFF", opacity=0.5)
    fig_matrix.add_hline(y=90, line_dash="dash", line_color="#FFFFFF", opacity=0.5)

    # Quadrant Labels (Low/Low is now bottom-left naturally)
    fig_matrix.add_annotation(x=32, y=98, text="High Speed / High Quality", showarrow=False, font=dict(color="#00E6A8", size=14))
    fig_matrix.add_annotation(x=32, y=80, text="High Speed / Low Quality", showarrow=False, font=dict(color="#FF3366", size=14))
    fig_matrix.add_annotation(x=14, y=98, text="Low Speed / High Quality", showarrow=False, font=dict(color="#FFC107", size=14))
    fig_matrix.add_annotation(x=14, y=80, text="Low Speed / Low Quality", showarrow=False, font=dict(color="#FF3366", size=14))

    fig_matrix.update_traces(textposition='top center', marker=dict(size=14))
    fig_matrix.update_layout(
        xaxis_title="Touches Per Hour (Speed)", yaxis_title="Accuracy Rate % (Quality)",
        xaxis=dict(range=[10, 38]), yaxis=dict(range=[75, 100]),
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", height=600
    )

    st.plotly_chart(fig_matrix, use_container_width=True)

else:
    st.warning("No data available for the selected dates and states. Please adjust your filters.")
