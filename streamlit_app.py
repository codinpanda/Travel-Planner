import pandas as pd
import streamlit as st
import plotly.express as px
from typing import List, Tuple

# --- Set Page Config ---
st.set_page_config(page_title="Travel Planner Pro", page_icon="🌍", layout="wide")


@st.cache_data
def load_data(filepath: str) -> pd.DataFrame:
    """
    Loads destination dataset into a Pandas DataFrame.
    
    Args:
        filepath: Path to the CSV file.
    Returns:
        DataFrame containing travel destination records.
    """
    try:
        return pd.read_csv(filepath)
    except FileNotFoundError:
        st.error(f"Critical Error: Data file '{filepath}' not found.")
        st.stop()


def render_sidebar(df: pd.DataFrame) -> Tuple[int, List[str], float]:
    """
    Renders sidebar filters and returns the selected conditions.
    """
    st.sidebar.header("🎯 Filter Preferences")

    # Budget
    min_cost = int(df['cost'].min())
    max_cost = int(df['cost'].max())
    budget = st.sidebar.slider(
        "Maximum Budget (INR)", 
        min_value=min_cost, 
        max_value=max_cost, 
        value=15000, 
        step=500
    )

    # Type
    available_types = df['type'].unique().tolist()
    selected_types = st.sidebar.multiselect(
        "Travel Type(s)", 
        options=available_types, 
        default=available_types
    )

    # Rating
    min_rating = st.sidebar.slider(
        "Minimum Rating", 
        min_value=float(df['rating'].min()), 
        max_value=5.0, 
        value=4.0, 
        step=0.1
    )

    st.sidebar.markdown("---")
    st.sidebar.info("Filters use AND logic (all conditions must be met).")

    return budget, selected_types, min_rating


def process_data(df: pd.DataFrame, budget: int, types: List[str], min_rating: float) -> pd.DataFrame:
    """
    Filters and sorts the dataframe based on user criteria.
    """
    filtered_df = df[
        (df['cost'] <= budget) & 
        (df['type'].isin(types)) & 
        (df['rating'] >= min_rating)
    ]
    return filtered_df.sort_values(by='rating', ascending=False)


def render_visualizations(df: pd.DataFrame):
    """
    Renders the metric overview and highly interactive Plotly graphs.
    """
    st.subheader(f"✅ Top Destinations Found: {len(df)}")

    if df.empty:
        st.warning("No destinations match your exact criteria. Try adjusting the filters.")
        return

    # Data Table
    display_cols = ['destination', 'cost', 'rating', 'type', 'location', 'days']
    st.dataframe(df[display_cols].head(15), use_container_width=True)

    st.markdown("---")
    st.subheader("📊 Price vs. Rating Analytics")

    # Plotly Express Scatter Plot
    top_chart_data = df.head(15)
    
    fig = px.scatter(
        top_chart_data,
        x="rating",
        y="cost",
        color="type",
        size="rating",  # Bubble size related to rating
        hover_name="destination",
        hover_data={"location": True, "days": True, "type": False, "rating": True, "cost": True},
        title="Cost vs Rating Configuration",
        labels={"rating": "Rating ⭐", "cost": "Cost (INR) 💰", "type": "Travel Type"},
        color_discrete_map={'adventure': '#FF7F0E', 'chill': '#1F77B4'},
        template="plotly_white"
    )
    
    # Increase marker aesthetic
    fig.update_traces(marker=dict(line=dict(width=1, color='DarkSlateGrey')))
    fig.update_layout(xaxis=dict(showgrid=True), yaxis=dict(showgrid=True))

    st.plotly_chart(fig, use_container_width=True)


def main():
    """
    Main application runner.
    """
    st.title("🌍 Premium Travel Planner")
    st.markdown("Discover optimized travel destinations curated by budget, preference, and global ratings. Fully interactive.")

    df = load_data("travel_500.csv")
    budget, selected_types, min_rating = render_sidebar(df)
    
    recommended_df = process_data(df, budget, selected_types, min_rating)
    render_visualizations(recommended_df)


if __name__ == "__main__":
    main()
