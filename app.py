import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import datetime

# --- PAGE SETUP ---
st.set_page_config(page_title="Specialist Pulse", layout="wide", initial_sidebar_state="expanded")

# --- FAKE DATA GENERATION (MULTI-DAY & MULTI-STATE) ---
@st.cache_data
def generate_data():
    np.random.seed(42)
    start_date = datetime.date(2026, 1, 1)
    end_date = datetime.date.today()
    dates = pd.date_range(start_date, end_date)
    
    specialists = ["Avery S.", "Jordan T.", "Casey L.", "Taylor R.", "Morgan W.", "Riley B.", "Quinn M.", "Reese K.", "Drew P."]
    states = ["Arizona", "California", "Colorado"]
    
    records = []
    for d in dates:
        for s in specialists:
            state = np.random.choice(states)
            # Simulating touches per hour
            touches = np.random.randint(15, 32)
            # Simulating rejection rate (Goal is under 10%)
            rejection = np.random.uniform(2.0, 18.0) 
            records.append([d, s, state, touches, rejection])
            
    return pd.DataFrame(records, columns=["Date", "Specialist", "State", "Touches Per Hour", "Rejection Rate (%)"])

df = generate_data()

# --- SIDEBAR FILTERS ---
st.sidebar.markdown("### Dashboard Controls")

# Date Filter
min_date = df["Date"].min().date()
max_date = df["Date"].max().date()
selected_dates = st.sidebar.date_input("Select Date Range", [min_date, max_date], min_value=min_date, max_value=max_date)

# State Filter
selected_states = st.sidebar.multiselect("Select States", options=["Arizona", "California", "Colorado"], default=["Arizona", "California", "Colorado"])

st.sidebar.divider()
st.sidebar.markdown("Data powered by Sigma Connection (Simulated)")

# --- FILTERING LOGIC ---
if len(selected_dates) == 2:
    start_filter, end_filter = selected_dates
    # Filter the dataframe based on sidebar inputs
    mask = (df['Date'].dt.date >= start_filter) & (df['Date'].dt.date <= end_filter) & (df['State'].isin(selected_states))
    filtered_df = df[mask]
else:
    filtered_df = df

# Aggregate data for the scatter plot (Average over the selected time period)
agg_df = filtered_df.groupby("Specialist").agg(
    {"Touches Per Hour": "mean", "Rejection Rate (%)": "mean"}
).reset_index()

# --- HEADER & HIGH-LEVEL METRICS ---
st.markdown("## Specialist Pulse Dashboard")
st.markdown("Multi-dimensional workflow tracking and efficiency matrix.")
st.divider()

if not filtered_df.empty:
    avg_touches = round(agg_df["Touches Per Hour"].mean(), 1)
    avg_rejection = round(agg_df["Rejection Rate (%)"].mean(), 1)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="Avg Touches / Hour (Selected Range)", value=f"{avg_touches}", delta=f"{round(avg_touches - 22, 1)} vs Merit Goal")
    with col2:
        st.metric(label="Avg Rejection Rate (Selected Range)", value=f"{avg_rejection}%", delta=f"{round(10 - avg_rejection, 1)}% vs 10% Goal", delta_color="inverse")
    with col3:
        st.metric(label="Total Submissions Analyzed", value=f"{len(filtered_df)}")

    st.markdown("<br>", unsafe_allow_html=True)

    # --- QUADRANT SCATTER PLOT ---
    st.markdown("### Efficiency & Accuracy Matrix")

    # Creating the scatter plot
    fig_matrix = px.scatter(
        agg_df, 
        x="Touches Per Hour", 
        y="Rejection Rate (%)",
        text="Specialist",
        template="plotly_dark",
        color_discrete_sequence=["#00E6A8"],
        size_max=60
    )

    # Adding the Quadrant Lines (Merit Goal: 22 touches, Rejection Goal: 10%)
    fig_matrix.add_vline(x=22, line_dash="dash", line_color="#FFFFFF", opacity=0.5)
    fig_matrix.add_hline(y=10, line_dash="dash", line_color="#FFFFFF", opacity=0.5)

    # Adding Quadrant Labels
    fig_matrix.add_annotation(x=30, y=5, text="High Speed / High Quality", showarrow=False, font=dict(color="#00E6A8", size=14))
    fig_matrix.add_annotation(x=30, y=16, text="High Speed / Low Quality", showarrow=False, font=dict(color="#FF3366", size=14))
    fig_matrix.add_annotation(x=17, y=5, text="Low Speed / High Quality", showarrow=False, font=dict(color="#FFC107", size=14))
    fig_matrix.add_annotation(x=17, y=16, text="Low Speed / Low Quality", showarrow=False, font=dict(color="#FF3366", size=14))

    # Clean up the chart aesthetics
    fig_matrix.update_traces(textposition='top center', marker=dict(size=12))
    fig_matrix.update_layout(
        xaxis_title="Touches Per Hour (Speed)", 
        yaxis_title="Rejection Rate % (Quality)",
        xaxis=dict(range=[14, 34]),
        yaxis=dict(range=[0, 20]),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        height=600
    )

    st.plotly_chart(fig_matrix, use_container_width=True)

else:
    st.warning("No data available for the selected dates and states. Please adjust your filters.")
