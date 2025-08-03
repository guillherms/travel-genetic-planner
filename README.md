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
app/
├── streamlit_app.py                  # VIEW
├── core/
│   ├── api/                          # API clients (model side)
│   ├── genetic/                      # Algoritmo Genético (model)
│   ├── model/
│   │   └── file_input_model.py       # Esquema de entrada do usuário
│   ├── prompt/
│   │   └── templates.py              # Prompt templates para OpenAI
│   ├── services/
│   │   └── planning_service.py       # CONTROLLER
│   └── utils/                        # Suporte comum
├── data/                             # Arquivos de teste
|README.md                    # This file
|requirements.txt            # Project dependencies
|.gitignore
```

---

## 🚀 How to Use


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

---

# 🗺️ 1. Roteirização / Planejamento de Rota
| Critério | Forma de usar na fitness |
|---|---|
| 🕒 Menor número de dias | len(roteiro_por_dia) * peso |
| 🧭 Menor distância total |- total_distancia_km|
|⏰ Respeitar horários de funcionamento	|- penalidade_por_visita_fora_do_horario|
|⏳ Tempo total diário respeitado	|- penalidade_por_excesso_de_tempo_por_dia|
|⭐ Visitar lugares prioritários	|+ bonus_por_prioridade|
|🔁 Evitar locais repetidos	|- penalidade_por_repetição|


