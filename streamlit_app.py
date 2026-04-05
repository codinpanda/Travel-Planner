import pandas as pd
import streamlit as st
import plotly.express as px
from typing import List, Dict

# --- Set Page Config ---
st.set_page_config(page_title="Premium Travel Planner", page_icon="✈️", layout="wide", initial_sidebar_state="expanded")

# --- Custom CSS for Premium Look ---
# Removing hardcoded colors to maintain 100% compatibility with Light/Dark mode themes!
st.markdown("""
    <style>
    /* Main Fonts */
    .stApp {
        font-family: 'Inter', sans-serif;
    }
    
    /* Hide Streamlit Branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Metrics Styling */
    div[data-testid="stMetricValue"] {
        font-size: 2.2rem !important;
        font-weight: 700 !important;
    }
    div[data-testid="stMetricLabel"] {
        font-size: 1.1rem !important;
        font-weight: 500 !important;
    }
    
    /* Title Styling */
    h1 {
        font-weight: 800;
        letter-spacing: -1px;
    }
    h2, h3 {
        font-weight: 600;
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
        df['transport'] = df['transport'].astype(str).str.title()
        return df
    except FileNotFoundError:
        st.error(f"Critical Error: Data file '{filepath}' not found.")
        st.stop()


def render_sidebar(df: pd.DataFrame) -> Dict:
    """Renders the comprehensive filtering sidebar."""
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
        step=500
    )

    st.sidebar.markdown("#### 📅 Duration Settings")
    min_days = int(df['days'].min())
    max_days = int(df['days'].max())
    days = st.sidebar.slider(
        "Maximum Travel Days", 
        min_value=min_days, 
        max_value=max_days, 
        value=max_days, 
        step=1
    )

    st.sidebar.markdown("#### 🌴 Experience Type")
    available_types = df['type'].unique().tolist()
    selected_types = st.sidebar.multiselect(
        "Travel Type(s)", 
        options=available_types, 
        default=available_types
    )
    
    st.sidebar.markdown("#### ✈️ Transport Options")
    available_transport = df['transport'].unique().tolist()
    selected_transport = st.sidebar.multiselect(
        "Transport Mode(s)", 
        options=available_transport, 
        default=available_transport
    )

    st.sidebar.markdown("#### ⭐ Quality Standards")
    min_rating = st.sidebar.slider(
        "Minimum Rating Requirements", 
        min_value=float(df['rating'].min()), 
        max_value=5.0, 
        value=4.0, 
        step=0.1
    )

    st.sidebar.markdown("---")
    
    sort_by = st.sidebar.selectbox(
        "🔀 Sort Results By", 
        ("Rating (High to Low)", "Cost (Low to High)", "Cost (High to Low)", "Duration (Short to Long)")
    )
    
    st.sidebar.info("💡 **Pro Tip**: Filters use AND logic (all conditions must be met).")

    return {
        "budget": budget,
        "days": days,
        "types": selected_types,
        "transport": selected_transport,
        "min_rating": min_rating,
        "sort_by": sort_by
    }


def process_data(df: pd.DataFrame, filters: Dict) -> pd.DataFrame:
    """Filters dataframe using multi-metric logic and applies sorting."""
    filtered_df = df[
        (df['cost'] <= filters['budget']) & 
        (df['days'] <= filters['days']) &
        (df['type'].isin(filters['types'])) & 
        (df['transport'].isin(filters['transport'])) &
        (df['rating'] >= filters['min_rating'])
    ]
    
    sort_mapping = {
        "Rating (High to Low)": ("rating", False),
        "Cost (Low to High)": ("cost", True),
        "Cost (High to Low)": ("cost", False),
        "Duration (Short to Long)": ("days", True)
    }
    
    sort_col, ascending = sort_mapping[filters["sort_by"]]
    return filtered_df.sort_values(by=sort_col, ascending=ascending)


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
    
    st.markdown("### 📊 Cost vs Rating Scatter Analysis")
    st.markdown("<p style='color: gray; font-size: 0.95rem; margin-top: -10px;'>Hover over any bubble to see destination details. Bubble size corresponds to trip duration.</p>", unsafe_allow_html=True)
    
    travel_type_colors = {
        'Adventure': '#EF4444', # Red
        'Chill': '#3B82F6',    # Blue
        'Cultural': '#8B5CF6', # Purple
        'Luxury': '#F59E0B'    # Amber
    }
    
    # Expanded full-width chart (removed redundant donut chart)
    fig = px.scatter(
        df.head(100), # Limit to top 100 to keep chart readable
        x="rating",
        y="cost",
        color="type",
        size="days", 
        hover_name="destination",
        hover_data={"location": True, "days": True, "type": False, "rating": True, "cost": True},
        labels={"rating": "Rating ⭐", "cost": "Cost (INR) 💰", "type": "Experience"},
        color_discrete_map=travel_type_colors
    )
    
    fig.update_layout(
        xaxis=dict(showgrid=True, gridcolor='rgba(128,128,128,0.2)'), 
        yaxis=dict(showgrid=True, gridcolor='rgba(128,128,128,0.2)'),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=0, r=0, t=20, b=0),
        height=450  # increased emphasis on the main chart
    )
    st.plotly_chart(fig, use_container_width=True, theme="streamlit")

    st.markdown("---")
    st.markdown("### 🏆 Curated Destination Directory")
    
    # Styled Dataframe utilizing Native Streamlit Column Config handling Formatters
    display_cols = ['destination', 'location', 'type', 'days', 'transport', 'cost', 'rating']
    presentation_df = df[display_cols].copy()
    
    st.dataframe(
        presentation_df,
        use_container_width=True,
        hide_index=True,
        height=500,
        column_config={
            "destination": st.column_config.TextColumn("Destination", width="medium"),
            "location": st.column_config.TextColumn("Country / Region"),
            "type": st.column_config.TextColumn("Experience Style"),
            "days": st.column_config.NumberColumn("Duration", format="%d Days"),
            "transport": st.column_config.TextColumn("Transport Mode"),
            "cost": st.column_config.NumberColumn("Total Cost", format="₹%d"),
            "rating": st.column_config.NumberColumn("Quality Rating", format="%.1f ⭐")
        }
    )


def main():
    st.title("✈️ Premium Global Travel Planner")
    st.markdown("<p style='font-size: 1.1rem;'>Discover algorithmically optimized travel destinations curated by your personalized budget, preference, duration, and global quality ratings.</p>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    df = load_data("travel_500.csv")
    filters = render_sidebar(df)
    
    recommended_df = process_data(df, filters)
    render_visualizations(recommended_df)


if __name__ == "__main__":
    main()
