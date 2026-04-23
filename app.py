import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# --- PAGE SETUP ---
# This forces the page to be wide and gives it a clean title
st.set_page_config(page_title="Specialist Pulse", layout="wide", initial_sidebar_state="collapsed")

# --- FAKE DATA GENERATION ---
# Setting a seed so the random data stays the same on each refresh
np.random.seed(42)

specialists = ["Avery S.", "Jordan T.", "Casey L.", "Taylor R.", "Morgan W.", "Riley B.", "Quinn M.", "Reese K.", "Drew P."]

# Simulating touches per hour (Goal is 22)
touches = np.random.randint(16, 32, size=len(specialists))

# Simulating accuracy rates (Goal is 90%)
# Creating a few high performers and a few who need coaching
accuracy = np.random.uniform(85.0, 98.0, size=len(specialists))

df = pd.DataFrame({
    "Specialist": specialists,
    "Touches Per Hour": touches,
    "Accuracy Rate (%)": np.round(accuracy, 1)
})

# Sorting by Touches for a better looking chart
df = df.sort_values("Touches Per Hour", ascending=False)

# --- HEADER ---
st.markdown("## ⚡ Specialist Pulse Dashboard")
st.markdown("Real-time performance metrics and workflow tracking.")
st.divider()

# --- KPI METRIC CARDS ---
# Calculating team averages for the high-level view
avg_touches = round(df["Touches Per Hour"].mean(), 1)
avg_accuracy = round(df["Accuracy Rate (%)"].mean(), 1)

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(label="Team Avg Touches / Hour", value=f"{avg_touches}", delta=f"{round(avg_touches - 22, 1)} vs Merit Goal")
with col2:
    st.metric(label="Team Avg Accuracy", value=f"{avg_accuracy}%", delta=f"{round(avg_accuracy - 90, 1)}% vs Goal")
with col3:
    st.metric(label="Active Specialists", value=len(specialists), delta="Full Capacity")

st.markdown("<br>", unsafe_allow_html=True) # Adds a little breathing room

# --- VISUALIZATIONS ---
col_charts_1, col_charts_2 = st.columns(2)

with col_charts_1:
    st.markdown("Touches Per Hour")
    
    # Modern Bar Chart using Plotly
    fig_speed = px.bar(
        df, 
        x="Specialist", 
        y="Touches Per Hour",
        text="Touches Per Hour",
        template="plotly_dark", # Forces the sleek dark background
        color_discrete_sequence=["#00E6A8"] # Neon mint green
    )
    
    # Adding the Merit Goal Cutoff Line
    fig_speed.add_hline(
        y=22, 
        line_dash="dash", 
        line_color="#FF3366", # Vibrant pink for the goal line
        annotation_text="Merit Goal (22/hr)", 
        annotation_position="top right",
        annotation_font_color="#FF3366"
    )
    
    # Cleaning up the chart aesthetics
    fig_speed.update_layout(
        xaxis_title="", 
        yaxis_title="",
        showlegend=False,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)"
    )
    fig_speed.update_traces(textposition='outside')
    
    st.plotly_chart(fig_speed, use_container_width=True)

with col_charts_2:
    st.markdown("Accuracy Rate")
    
    # Creating a color condition: Red if below 90%, Blue if above
    df["Color"] = np.where(df["Accuracy Rate (%)"] >= 90.0, "#00E6A8", "#FF3366")
    
    # Horizontal Bar Chart for Accuracy
    fig_acc = px.bar(
        df.sort_values("Accuracy Rate (%)", ascending=True), 
        x="Accuracy Rate (%)", 
        y="Specialist",
        orientation='h',
        text="Accuracy Rate (%)",
        template="plotly_dark",
        color="Color",
        color_discrete_map="identity" # Uses the exact hex codes from the column
    )
    
    # Adding the 90% Goal Line
    fig_acc.add_vline(
        x=90.0, 
        line_dash="dash", 
        line_color="#FFFFFF", 
        annotation_text="90% Goal", 
        annotation_position="top left"
    )
    
    # Cleaning up aesthetics
    fig_acc.update_layout(
        xaxis_title="", 
        yaxis_title="",
        xaxis=dict(range=[80, 100]), # Zooming in so the differences are obvious
        showlegend=False,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)"
    )
    fig_acc.update_traces(textposition='inside')
    
    st.plotly_chart(fig_acc, use_container_width=True)
