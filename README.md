# Travel Genetic Planner

The **Travel Genetic Planner** is a project that uses a **Genetic Algorithm (GA)** to optimize a travel itinerary by finding the best order to visit selected tourist spots based on geographic coordinates.

This is a didactic project, ideal for those starting out with genetic algorithms.

---

## 🧠 Objective
Minimize the total distance traveled when visiting a list of tourist attractions, simulating a Traveling Salesman Problem (TSP), with the possibility of adding more realistic constraints in the future (schedules, preferences, costs, etc).

---

## 📁 Project Structure
```
travel-genetic-planner/
│
├── data/
│   ├── pois.csv                  # User-provided tourist spots
│   └── pois_with_coords.csv     # File enriched with lat/long
│
├── src/
│   ├── maps_api.py              # Fetch coordinates via API (Nominatim)
│   ├── genetic_algorithm.py     # Genetic Algorithm (to be implemented)
│   └── planner.py               # Helper functions (distance, etc.)
│
├── app/
│   └── streamlit_app.py         # Streamlit interactive interface (coming soon)
│
├── README.md                    # This file
├── requirements.txt            # Project dependencies
└── .gitignore
```

---

## 🚀 How to Use
1. Add tourist spots in `data/pois.csv` (single column named `place`).
2. Run the script to fetch coordinates:
```bash
python src/maps_api.py
```
3. This will generate `data/pois_with_coords.csv` with latitude and longitude.
4. (Coming soon) Run the optimizer to generate the best route based on distances.

---

## ✅ Requirements
Install the dependencies with:
```bash
pip install -r requirements.txt
```

### requirements.txt (initial)
```
streamlit
requests
pandas
geopy
folium
```

---

## 📌 Project Status
- [x] Coordinate API (OpenStreetMap)
- [ ] Implement basic genetic algorithm
- [ ] Streamlit visualization
- [ ] Support for schedules and preferences

---

## 💡 Author
This project is part of a personal study on Genetic Algorithms with practical application in travel planning.