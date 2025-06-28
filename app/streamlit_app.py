# streamlit_app.py

import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from genetic_algorithm import run_genetic_algorithm, HOTEL_COORDS

st.set_page_config(page_title="Travel Route Optimizer", layout="wide")
st.title("🗺️ Travel Route Optimizer with Genetic Algorithm")

# Load coordinates from CSV
try:
    df = pd.read_csv("data/places_with_coords.csv")
    coords_list = list(zip(df["latitude"], df["longitude"]))
except Exception as e:
    st.error("Error loading coordinates. Make sure places_with_coords.csv exists.")
    st.stop()

# GA parameters
st.sidebar.header("Genetic Algorithm Settings")
generations = st.sidebar.slider("Generations", 10, 500, 100, 10)
pop_size = st.sidebar.slider("Population Size", 10, 200, 50, 10)

# Session state to keep results
if "best_route" not in st.session_state:
    st.session_state.best_route = None
    st.session_state.best_distance = None

if st.button("Run Optimization"):
    with st.spinner("Running Genetic Algorithm..."):
        best_route, best_distance = run_genetic_algorithm(coords_list, generations, pop_size)
        st.session_state.best_route = best_route
        st.session_state.best_distance = best_distance

# Display map and result
if st.session_state.best_route:
    best_route = st.session_state.best_route
    best_distance = st.session_state.best_distance
    full_route = [HOTEL_COORDS] + best_route + [HOTEL_COORDS]

    m = folium.Map(location=HOTEL_COORDS, zoom_start=13)
    for i, coord in enumerate(full_route):
        label = "Hotel" if i == 0 or i == len(full_route) - 1 else f"Stop {i}"
        folium.Marker(
            location=coord,
            tooltip=label,
            icon=folium.Icon(color="blue", icon="fa-map-marker", prefix="fa")
        ).add_to(m)

    folium.PolyLine(locations=full_route, color="blue", weight=3).add_to(m)
    st.success(f"✅ Best route total distance: {best_distance:.2f} km")
    st_folium(m, width=900, height=600)
else:
    st.info("Click the button to run the optimization and view the best route.")
