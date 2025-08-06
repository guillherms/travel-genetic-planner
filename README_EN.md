# 🧬 Travel Genetic Planner

**Travel Genetic Planner** is a project that uses a **Genetic Algorithm (GA)** to optimize a travel itinerary by finding the most efficient order to visit tourist spots, considering geolocation and real-world constraints like schedules and preferences.

---

## 🎯 Objective

Minimize travel time and plan a feasible itinerary, respecting each location’s opening hours and visitor preferences.

---

## 📁 Project Structure

```
travel-genetic-planner/
app/
├── streamlit_app.py                  # VIEW (UI interface)
├── core/
│   ├── api/                          # External APIs (Google, OpenAI)
│   ├── genetic/                      # Genetic Algorithm logic
│   ├── model/
│   │   └── file_input_model.py       # Input validation
│   ├── prompt/
│   │   └── templates.py              # Prompt for place generation
│   ├── services/
│   │   └── planning_service.py       # CONTROLLER
│   └── utils/                        # Helper functions
├── data/                             # Input test files
|README_EN.md                         # This file
|requirements.txt                     # Dependencies
|.gitignore
```

---

## ✅ Requirements

Install the dependencies:

```bash
pip install -r requirements.txt
```

---

## 🚀 How to Run

Start the Streamlit application:

```bash
streamlit run app/streamlit_app.py
```

---

## 📌 Code Walkthrough

```markdown
# Main project flow:

1. The user inputs the hotel name.
2. Then, chooses whether to:
   - Upload a **CSV file** with tourist places, **OR**
   - Get **automatically suggested places** using the OpenAI API.
3. If the user selects suggestions:
   - The app sends a prompt to **OpenAI's API** to generate tourist spots.
4. Regardless of the input method, the app uses **Google Geocoding API** to retrieve the hotel's latitude and longitude.
5. Once the place data is ready, the user runs the **genetic algorithm**.
6. The algorithm returns the optimal route to visit the places, considering distance, time, and preferences.
7. The best result is shown using **interactive maps**, one for each travel day.
```

---

## 🔐 Note: Credentials Setup

To run the project, create a `.env` file at the root with the following variables:

```env
OPENAI_API_KEY=your_openai_api_key_here
GOOGLE_MAPS_API_KEY=your_google_maps_api_key_here
```

### 📘 How to get your API keys:

- 🔑 **OpenAI API Key**:  
  Visit [https://platform.openai.com/account/api-keys](https://platform.openai.com/account/api-keys)  
  Create a key and copy the value.

- 📍 **Google Maps API Key**:  
  1. Go to [https://console.cloud.google.com/](https://console.cloud.google.com/)
  2. Create or select a project.
  3. Enable the "Geocoding API" and "Routes API"
  4. Go to "Credentials" > "Create API Key"
  5. Copy and paste it into your `.env`

---

## 🧠 Genetic Algorithm FAQ

### 💡 What is the fitness function?

The fitness function combines multiple aspects:
- 🕒 Fewer days: `len(itinerary_by_day) * negative_weight`
- 🧭 Shortest total distance: `- total_distance_km`
- ⏰ Respect opening hours: `- penalty_for_outside_opening`
- ⏳ Respect daily time limit: `- penalty_for_time_overload`
- ⭐ Prioritize important locations: `+ bonus_for_priority`
- 🔁 Avoid repeats: `- penalty_for_duplicates`

### 🧬 How is the population initialized?

Initial population is built by randomly shuffling the locations (with possible dependency constraints).

### 🛑 What is the stopping criterion?

- Fixed number of generations  
- OR stagnation (no improvement after X generations)

---
## 📮 Contact

- Developed by Guilherme Santos Oliveira  
- Academic Project – IADevs Postgraduate Phase 2: AI Evolution  
- [LinkedIn](https://www.linkedin.com/in/guilherme-santos-oliveira)