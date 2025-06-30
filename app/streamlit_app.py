import streamlit as st
import pandas as pd
import folium
from geopy.distance import geodesic
from streamlit_folium import st_folium
from genetic_algorithm import run_genetic_algorithm_for_multiple_days, HOTEL_COORDS
from datetime import date

st.set_page_config(page_title="Travel Route Optimizer", layout="wide")
st.title("🗺️ Travel Route Optimizer with Genetic Algorithm")

# Load coordinates from CSV
try:
    df = pd.read_csv("data/places_with_coords_mock.csv")
except Exception as e:
    st.error("Error loading coordinates. Make sure the file exists.")
    st.stop()

# Sidebar inputs
st.sidebar.header("Trip Settings")
start_date, end_date = st.sidebar.date_input(
    "Select trip range:",
    value=(date.today(), date.today()),
    min_value=date.today()
)

st.sidebar.header("Genetic Algorithm Settings")
generations = st.sidebar.slider("Generations", 10, 500, 100, 10)
pop_size = st.sidebar.slider("Population Size", 10, 200, 50, 10)
time_limit = st.sidebar.slider("Daily Time Limit (minutes)", 60, 600, 360, 30)

if "routes" not in st.session_state:
    st.session_state.routes = []

if st.button("Run Optimization"):
    with st.spinner("Running Genetic Algorithm for each day..."):
        results = run_genetic_algorithm_for_multiple_days(df, start_date, end_date, generations, pop_size)
        st.session_state.routes = results

# Helper to classify segments

def estimate_travel_time_km(dist_km):
    if dist_km <= 2:
        return (dist_km / 5) * 60, "walk"
    else:
        return (dist_km / 20) * 60, "bus/metro"

def classify_segments(route, coord_to_name):
    segments = []
    for i in range(len(route) - 1):
        start = route[i]
        end = route[i + 1]
        dist_km = geodesic(start, end).kilometers
        travel_time, mode = estimate_travel_time_km(dist_km)

        key_start = (round(start[0], 5), round(start[1], 5))
        key_end = (round(end[0], 5), round(end[1], 5))

        segments.append({
            "From": coord_to_name.get(key_start, "Unknown"),
            "To": coord_to_name.get(key_end, "Unknown"),
            "Distance (km)": round(dist_km, 2),
            "Mode": mode,
            "Travel time (min)": round(travel_time, 1)
        })
    return segments

def split_route_by_day(route, df, coord_to_name, time_limit):
    days = []
    current_day = []
    total_time = 0.0
    current = HOTEL_COORDS

    for stop in route:
        dist_km = geodesic(current, stop).kilometers
        travel_time, _ = estimate_travel_time_km(dist_km)
        visit_time = df[(df["latitude"] == stop[0]) & (df["longitude"] == stop[1])]["min_visit_time_min"].values
        visit_time = int(visit_time[0]) if len(visit_time) else 60

        if total_time + travel_time + visit_time > time_limit and current_day:
            days.append({"stops": current_day, "total_time": round(total_time, 1)})
            current_day = []
            total_time = 0.0

        key = (round(stop[0], 5), round(stop[1], 5))
        current_day.append({
            "place": coord_to_name.get(key, "Unknown"),
            "visit_time_min": visit_time,
            "travel_time_min": round(travel_time, 1)
        })
        total_time += travel_time + visit_time
        current = stop

    if current_day:
        days.append({"stops": current_day, "total_time": round(total_time, 1)})

    return days

# Display results
if st.session_state.routes:
    for day_result in st.session_state.routes:
        route = day_result["route"]
        date_label = day_result["date"].strftime("%A, %d %b %Y")
        distance = day_result["distance"]

        st.header(f"📅 {date_label} — Total distance: {distance:.2f} km")

        if not route:
            st.warning("No open places for this day.")
            continue

        coords_only = [(lat, lon) for _, lat, lon in route]
        full_route = [HOTEL_COORDS] + coords_only + [HOTEL_COORDS]
        coord_to_name = {(round(lat, 5), round(lon, 5)): name for name, lat, lon in route}

        m = folium.Map(location=HOTEL_COORDS, zoom_start=13)
        for i, coord in enumerate(full_route):
            key = (round(coord[0], 5), round(coord[1], 5))
            label = "Hotel" if coord == HOTEL_COORDS else coord_to_name.get(key, f"Stop {i}")
            folium.Marker(
                location=coord,
                tooltip=label,
                icon=folium.Icon(color="blue", icon="info-sign")
            ).add_to(m)

        folium.PolyLine(locations=full_route, color="blue", weight=3).add_to(m)
        st_folium(m, width=900, height=500)

        segments = classify_segments(full_route, coord_to_name)
        st.subheader("🧭 Route Details by Segment")
        st.dataframe(pd.DataFrame(segments))

        st.subheader("📋 Itinerary (Grouped by Time Limit)")
        itinerary = split_route_by_day(coords_only, df, coord_to_name, time_limit)
        for i, day in enumerate(itinerary, 1):
            st.markdown(f"### Block {i} — Total time: {day['total_time']} min")
            st.dataframe(pd.DataFrame(day["stops"]))
else:
    st.info("Select a date range and click the button to generate your optimized travel plan.")
