# Premium Travel Planner Assistant 🌍

A production-grade, interactive travel recommendation dashboard built with Streamlit and Plotly. This app filters through curated datasets to match you with top destinations based on multiple dynamic criteria (budget, type, and minimum rating).

## Core Features
*   **Dynamic Data Filtering**: Applies logical constraints against maximum budget, travel style, and quality rating.
*   **Clean UI Architecture**: Scalable left-sidebar property configurations.
*   **Interactive Visualizations**: High-fidelity scatter/bubble plots via Plotly allowing for zoom, pan, hover tooltips, and image exports.
*   **Production Code Standards**: Type hinted, modular Python functions ensuring maintainable architecture.

## Installation & Setup

1. **Clone the repository** (if fetched from remote)
2. **Install core requirements**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Boot the Streamlit App**:
   ```bash
   streamlit run streamlit_app.py
   ```

## Included Data
Operates strictly off `travel_500.csv` containing metrics around destination viability, duration, location, format, and cost algorithms.
