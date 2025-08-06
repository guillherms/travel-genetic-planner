import logging
import streamlit as st
from datetime import date
from core.utils.file_utils import FileUtils
from core.utils.date_utils import DateUtils
from core.services.travel_planner_controller import TravelPlannerController

class TravelApp:
    def __init__(self):
        self.date_utils = DateUtils()
        self.file_utils = FileUtils()
        self.controller = TravelPlannerController()

        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        st.set_page_config(page_title="Travel Route Optimizer", layout="wide")

    def render_sidebar(self):
        st.sidebar.header("Trip Settings")
        with st.sidebar.expander("🧬 Genetic Algorithm Settings", expanded=True):
            generations = st.slider("Generations Size", 10, 500, 100, 10)
            pop_size = st.slider("Population Size", 10, 200, 50, 10)
            mutation = st.slider("Mutation Rate", 0.0, 1.0, 0.1, 0.01, "%.2f")
            crossover = st.slider("Crossover Rate", 0.0, 1.0, 0.8, 0.5, "%.2f")

        with st.sidebar.expander("🧪 OpenAi Settings", expanded=True):
            temperature = st.slider("Temperature Rate", 0.0, 2.0, 1.0, 0.1)
            top_p = st.slider("Top P Rate", 0.0, 2.0, 1.0, 0.1)

        with st.sidebar.expander("🗓️ Trip Configuration - Time Limit", expanded=True):
            start_date = st.date_input("Start Date", date.today(), format="DD/MM/YYYY")
            end_date = st.date_input("End Date", start_date, format="DD/MM/YYYY")
            time_limit = st.slider("Time Limit per Day (minutes)", 60, 1440, 240, 30)

        return generations, pop_size, mutation, crossover, start_date, end_date, time_limit, temperature, top_p

    def run(self):
        try:
            st.title("🗺️ Travel Route Optimizer with Genetic Algorithm")
            generations, pop_size, mutation, crossover, start_date, end_date, time_limit, temperature, top_p = self.render_sidebar()
            input_type = st.selectbox("How do you want to search??", ["Select", "File", "Text"])

            if input_type == "Text":
                with st.form("text_input_form"):
                    st.write("Enter the name to get the tourist attractions.")    
                    hotel_name = st.text_input("Hotel Name", placeholder="Name of your hotel (e.g., Hotel XYZ)", key="hotel_text")
                    destination = st.text_input("Destination", placeholder="e.g., Paris, France", key="destination_text")
                    submitted = st.form_submit_button("Submit")
                if submitted and destination:
                    st.session_state.df = self.controller.handle_text_input(destination,
                                                                            hotel_name,
                                                                            start_date,
                                                                            end_date,
                                                                            temperature,
                                                                            top_p)
                elif submitted and destination == "":
                    st.warning("Por favor, preencha o campo de destino antes de continuar.")

            elif input_type == "File":
                with st.form("file_input_form"):
                    st.write("Faça upload de um arquivo CSV contendo os pontos turísticos.")
                    hotel_name = st.text_input("Hotel Name", placeholder="Name of your hotel (e.g., Hotel XYZ)", key="hotel_file")
                    st.code(
                        "places ,latitude,longitude,mon,tue,wed,thu,fri,sat,sun,estimated_duration_min,priority\\n"
                        "Eiffel Tower,48.8584,2.2945,09:00-18:00,..."
                    )
                    uploaded_file = st.file_uploader("📂 Upload CSV file", type=["csv"])
                    submitted = st.form_submit_button("Submit")
                    if submitted and uploaded_file:
                        try:
                            st.session_state.df, st.session_state.hotel_coordinates\
                            = self.controller.handle_file_upload(uploaded_file, hotel_name)
                        except Exception as e:
                            st.error(f"Erro ao ler o arquivo: {e}")
                    elif submitted and uploaded_file is None:
                        st.warning("Por favor, selecione um arquivo antes de continuar.")

            if "routes" not in st.session_state:
                st.session_state.routes = []

            if "df" in st.session_state and st.session_state.df is not None and not st.session_state.df.empty:
                st.subheader("✏️ Edit tourist attractions")
                st.session_state.df = st.data_editor(
                    st.session_state.df,
                    num_rows="dynamic",
                    use_container_width=True,
                    key="tourist_editor"
                )
                
            if st.button("Run Optimization"):
                if "df" in st.session_state and st.session_state.df is not None and not st.session_state.df.empty:
                    with st.spinner("Running Genetic Algorithm for each day..."):
                        travel_planner = self.controller.run_genetic_algorithm(
                            st.session_state.df,
                            pop_size,
                            generations,
                            mutation,
                            crossover,
                            time_limit,
                            start_date,
                            end_date,
                        )
                        st.session_state.optimized_route = travel_planner
                else:
                    st.error("No data available for optimization. Please upload a file or enter a valid destination.")
            
            if "optimized_route" in st.session_state:
                self.controller.render_result_summary(st.session_state.optimized_route)
                hotel_row = st.session_state.df[st.session_state.df["places"] == "HOTEL"].iloc[0]
                hotel_coords = (hotel_row["latitude"], hotel_row["longitude"])
                self.controller.render_daily_maps(
                    roteiro_por_dia=st.session_state.optimized_route.get("roteiro_por_dia", {}),
                    hotel_coords=hotel_coords
                )
        except Exception as e:
            logging.exception(f"An error occurred: {e}")
            st.error(f"An error occurred: {e}")

if __name__ == "__main__":
    app = TravelApp()
    app.run()