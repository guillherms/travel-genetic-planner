import streamlit as st
import logging
import pandas as pd
import folium
from io import StringIO
from pydantic import ValidationError
#from data.model.file import FileSchema
from open_api import OpenAi
from files_schema import FileSchema
from geopy.distance import geodesic
from streamlit_folium import st_folium
from genetic_algorithm import run_genetic_algorithm_for_multiple_days, HOTEL_COORDS
from datetime import date
from streamlit.runtime.uploaded_file_manager import UploadedFile


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def read_csv_file(uploaded_file: UploadedFile) -> pd.DataFrame:
    try:
        tasks_dataframe = pd.read_csv(uploaded_file)
        validate_dataframe(tasks_dataframe)
        tasks_dataframe.set_index("task", inplace=True)
        return tasks_dataframe
    except ValueError as e:
        logging.exception(f"Validation failed!: {e}")
        raise
    except Exception as e:
        logging.exception(f"An unexpected error occurred while reading the CSV file: {e}")
        raise

def validate_dataframe(df: pd.DataFrame) -> None:
    required_columns = {"task", "description", "dependencies", "duration", "priority"}
    print(df.columns)
    missing = required_columns - set(df.columns)
    if missing:
        raise ValueError(f"Colunas faltando: {missing}")
    
    for i, row in df.iterrows():
        try:
            FileSchema(**row.to_dict())
        except ValidationError as e:
            raise ValueError(f"Erro na linha {i}: {e}")
        
def string_to_dataframe(csv_string: str) -> pd.DataFrame:
    df = pd.read_csv(StringIO(csv_string))
    df.columns = df.columns.str.strip()
    return df


st.set_page_config(page_title="Travel Route Optimizer", layout="wide")
st.title("🗺️ Travel Route Optimizer with Genetic Algorithm")

# Sidebar
st.sidebar.header("Trip Settings")


with st.sidebar.expander("🧬 Genetic Algorithm Settings", expanded=True):
    generations = st.slider("Generations Size", 10, 500, 100, 10)
    pop_size = st.slider("Population Size", 10, 200, 50, 10)

with st.sidebar.expander("🗓️ Trip Configuration - Time Limit", expanded=True):
    start_date = st.date_input("Start Date", date.today(), format="DD/MM/YYYY")
    end_date = st.date_input("End Date", start_date, format="DD/MM/YYYY")
    time_limit = st.slider("Time Limit per Day (minutes)", 60, 480, 240, 30)


tipo = st.selectbox("Como deseja ser contatado?", ["Selecione", "Arquivo", "Texto"])
hotel = st.text_input("Hotel Name", placeholder="Name of your hotel (e.g., Hotel XYZ)")

if tipo == "Arquivo":
    uploaded_file = st.file_uploader("📂 Upload CSV file", type=["csv"])
    read_csv_file(uploaded_file)
elif tipo == "Texto":
    destination = st.text_input(placeholder="Enter destination name (e.g., Paris)", label="Destination Name")
    if destination:
        open_ai = OpenAi(place_name=destination, start_date=start_date, end_date=end_date)
        response = open_ai.generate_suggestion_tourist_points()
        string_to_dataframe(response)



if "routes" not in st.session_state:
    st.session_state.routes = []

if st.button("Run Optimization"):
    with st.spinner("Running Genetic Algorithm for each day..."):
        if tipo == "Arquivo":
            df = read_csv_file(uploaded_file)
        elif tipo == "Texto":
            df = string_to_dataframe(response)
        else:
            st.error("Please select a valid input method (File or Text).")
            st.stop()
        #results = run_genetic_algorithm_for_multiple_days(df, start_date, end_date, generations, pop_size)
        #t.session_state.routes = results

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
