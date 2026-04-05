import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from typing import List, Tuple

# --- Set Page Config ---
st.set_page_config(page_title="Premium Travel Planner", page_icon="✈️", layout="wide", initial_sidebar_state="expanded")

# --- Custom CSS for Premium Look ---
st.markdown("""
    <style>
    /* Main Background & Fonts */
    .stApp {
        background-color: #f8f9fa;
        font-family: 'Inter', sans-serif;
    }
    
    /* Hide Streamlit Branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Metrics Styling */
    div[data-testid="stMetricValue"] {
        font-size: 2rem !important;
        font-weight: 700 !important;
        color: #1E3A8A !important;
    }
    div[data-testid="stMetricLabel"] {
        font-size: 1rem !important;
        font-weight: 500 !important;
        color: #64748B !important;
    }
    
    /* Title Styling */
    h1 {
        color: #0F172A;
        font-weight: 800;
        letter-spacing: -1px;
    }
    h2, h3 {
        color: #334155;
        font-weight: 600;
    }
    
    /* Custom Sidebar styling */
    section[data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #e2e8f0;
    }
    </style>
""", unsafe_allow_html=True)


@st.cache_data
def load_data(filepath: str) -> pd.DataFrame:
    """Loads and formats the destination dataset."""
    try:
        df = pd.read_csv(filepath)
        # Ensure proper casing
        df['destination'] = df['destination'].astype(str).str.title()
        df['type'] = df['type'].astype(str).str.title()
        return df
    except FileNotFoundError:
        st.error(f"Critical Error: Data file '{filepath}' not found.")
        st.stop()


def render_sidebar(df: pd.DataFrame) -> Tuple[int, List[str], float]:
    st.sidebar.markdown("## 🎯 Trip Parameters")
    st.sidebar.markdown("Tailor your perfect getaway by adjusting the parameters below.")
    st.sidebar.markdown("---")

    min_cost = int(df['cost'].min())
    max_cost = int(df['cost'].max())
    
    st.sidebar.markdown("#### 💰 Budget Settings")
    budget = st.sidebar.slider(
        "Maximum Budget (INR)", 
        min_value=min_cost, 
        max_value=max_cost, 
        value=min(15000, max_cost), 
        step=500,
        help="Filter out destinations that exceed your maximum spend."
    )

    st.sidebar.markdown("#### 🌴 Experience Type")
    available_types = df['type'].unique().tolist()
    selected_types = st.sidebar.multiselect(
        "Travel Type(s)", 
        options=available_types, 
        default=available_types,
        help="Select the kind of trip you want to have."
    )

    st.sidebar.markdown("#### ⭐ Quality Standards")
    min_rating = st.sidebar.slider(
        "Minimum Rating Requirements", 
        min_value=float(df['rating'].min()), 
        max_value=5.0, 
        value=4.0, 
        step=0.1,
        help="Only show destinations rated consistently highly by travelers."
    )

    st.sidebar.markdown("---")
    st.sidebar.info("💡 **Pro Tip**: Tweak your budget and rating to see how destination clusters adjust in real-time.")

    return budget, selected_types, min_rating


def process_data(df: pd.DataFrame, budget: int, types: List[str], min_rating: float) -> pd.DataFrame:
    filtered_df = df[
        (df['cost'] <= budget) & 
        (df['type'].isin(types)) & 
        (df['rating'] >= min_rating)
    ]
    return filtered_df.sort_values(by='rating', ascending=False)


def render_metrics(df: pd.DataFrame):
    """Render top-level KPI metrics."""
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Matches", len(df))
    with col2:
        avg_cost = df['cost'].mean() if not df.empty else 0
        st.metric("Avg. Trip Cost", f"₹{avg_cost:,.0f}")
    with col3:
        avg_rating = df['rating'].mean() if not df.empty else 0
        st.metric("Avg. Rating", f"{avg_rating:.2f} ⭐")
    with col4:
        avg_duration = df['days'].mean() if not df.empty else 0
        st.metric("Avg. Duration", f"{avg_duration:.1f} Days")


def render_visualizations(df: pd.DataFrame):
    if df.empty:
        st.warning("⚠️ No destinations match your current criteria. Please consider relaxing your filters in the sidebar.", icon="🔍")
        return

    # Metrics Overview
    render_metrics(df)
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Dual Columns for charts
    col_chart1, col_chart2 = st.columns([3, 2])
    
    with col_chart1:
        st.markdown("### 📊 Cost vs Rating Distribution")
        fig = px.scatter(
            df.head(50), # Limit to top 50 to keep chart readable
            x="rating",
            y="cost",
            color="type",
            size="days", 
            hover_name="destination",
            hover_data={"location": True, "days": True, "type": False, "rating": True, "cost": True},
            labels={"rating": "Rating ⭐", "cost": "Cost (INR) 💰", "type": "Experience"},
            color_discrete_sequence=['#3B82F6', '#10B981', '#F59E0B', '#EF4444'],
            template="plotly_white"
        )
        
        fig.update_traces(marker=dict(line=dict(width=1, color='DarkSlateGrey')))
        fig.update_layout(
            xaxis=dict(showgrid=True, gridcolor='#e2e8f0'), 
            yaxis=dict(showgrid=True, gridcolor='#e2e8f0'),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=0, r=0, t=30, b=0)
        )
        st.plotly_chart(fig, use_container_width=True)

    with col_chart2:
        st.markdown("### 🗺️ Destination Styles")
        type_counts = df['type'].value_counts().reset_index()
        type_counts.columns = ['type', 'count']
        
        # Donut Chart
        fig_pie = px.pie(
            type_counts, 
            values='count', 
            names='type',
            hole=0.5,
            color_discrete_sequence=['#3B82F6', '#10B981', '#F59E0B', '#EF4444'],
            template="plotly_white"
        )
        fig_pie.update_traces(textposition='inside', textinfo='percent+label')
        fig_pie.update_layout(
            showlegend=False,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=0, r=0, t=30, b=0)
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    st.markdown("---")
    st.markdown("### 🏆 Top Recommended Destinations Directory")
    
    # Styled Dataframe presentation
    display_cols = ['destination', 'location', 'type', 'days', 'cost', 'rating', 'transport']
    presentation_df = df[display_cols].head(15).copy()
    
    # Format Currency and Strings for UI
    presentation_df['cost'] = presentation_df['cost'].apply(lambda x: f"₹{x:,.0f}")
    presentation_df['rating'] = presentation_df['rating'].apply(lambda x: f"{x} ⭐")
    presentation_df['days'] = presentation_df['days'].apply(lambda x: f"{x} Days")
    
    # Rename columns for display
    presentation_df.columns = ["Destination", "Country / Region", "Experience Style", "Duration", "Total Cost", "Rating", "Transport Mode"]
    
    st.dataframe(
        presentation_df,
        use_container_width=True,
        hide_index=True,
        height=400
    )


def main():
    st.title("✈️ Premium Global Travel Planner")
    st.markdown("<p style='font-size: 1.1rem; color: #64748B;'>Discover algorithmically optimized travel destinations curated by your personalized budget, preference, and global quality ratings.</p>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    df = load_data("travel_500.csv")
    budget, selected_types, min_rating = render_sidebar(df)
    
    recommended_df = process_data(df, budget, selected_types, min_rating)
    render_visualizations(recommended_df)


if __name__ == "__main__":
    main()
