
import os
st.write("Files in directory:", os.listdir())

import streamlit as st
import pandas as pd
import requests
import plotly.express as px
import folium
from streamlit_folium import st_folium
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

st.set_page_config(page_title="SoilSense Dashboard", layout="wide")

st.title("🌱 SoilSense Smart Fertilizer Advisory System")

# -----------------------------
# SAMPLE DATA (replace with your datasets)
# -----------------------------

data = pd.DataFrame({
    "Nitrogen":[100,120,140,160],
    "Phosphorus":[40,50,60,70],
    "Potassium":[20,25,30,35],
    "Temperature":[28,30,32,34],
    "Humidity":[60,65,70,75],
    "Rainfall":[100,120,140,160],
    "Recommended_Chemical":["Urea","DAP","NPK","Potash"],
    "Recommended_Organic":["Compost","Vermicompost","FYM","Biofertilizer"]
})

features = [
    "Nitrogen",
    "Phosphorus",
    "Potassium",
    "Temperature",
    "Humidity",
    "Rainfall"
]

X = data[features]
y = data["Recommended_Chemical"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

model = RandomForestClassifier()
model.fit(X_train, y_train)

accuracy = accuracy_score(y_test, model.predict(X_test))

st.metric("Model Accuracy", f"{round(accuracy*100,2)}%")

# -----------------------------
# WEATHER API
# -----------------------------

API_KEY = "cb81120197f345ae396cd0fa28c1827c"

city = st.sidebar.text_input("City", "Gorakhpur")

def get_weather(city):

    try:

        url = (
            "https://api.openweathermap.org/data/2.5/weather?"
            f"q={city}&appid={API_KEY}&units=metric"
        )

        weather = requests.get(url).json()

        temp = weather["main"]["temp"]
        humidity = weather["main"]["humidity"]
        rainfall = weather.get("rain", {}).get("1h", 0)

        return temp, humidity, rainfall

    except:

        return 30, 60, 0

# -----------------------------
# INPUTS
# -----------------------------

st.sidebar.header("Soil Inputs")

N = st.sidebar.number_input("Nitrogen", 0, 500, 120)
P = st.sidebar.number_input("Phosphorus", 0, 200, 40)
K = st.sidebar.number_input("Potassium", 0, 200, 20)

if st.sidebar.button("Predict"):

    temp, humidity, rainfall = get_weather(city)

    input_data = pd.DataFrame(
        [[N,P,K,temp,humidity,rainfall]],
        columns=features
    )

    chemical = model.predict(input_data)[0]

    organic = data[
        data["Recommended_Chemical"] == chemical
    ]["Recommended_Organic"].iloc[0]

    st.success(f"Chemical Fertilizer: {chemical}")
    st.info(f"Organic Fertilizer: {organic}")

    # -----------------------------
    # BEFORE vs AFTER COMPARISON
    # -----------------------------

    st.header("📊 Before vs After NPK Comparison")

    before_N = N
    before_P = P
    before_K = K

    if chemical == "Urea":
        chemical_ratio = max(0, (140 - N) / 140)
    elif chemical == "DAP":
        chemical_ratio = max(0, (30 - P) / 30)
    elif chemical == "Potash":
        chemical_ratio = max(0, (10 - K) / 10)
    else:
        chemical_ratio = 0.3

    organic_ratio = 1 - chemical_ratio

    after_N = round(before_N * chemical_ratio, 2)
    after_P = round(before_P * chemical_ratio, 2)
    after_K = round(before_K * chemical_ratio, 2)

    comparison_data = pd.DataFrame({

        "Nutrient": ["Nitrogen", "Phosphorus", "Potassium"],

        "Before (Chemical)": [
            before_N,
            before_P,
            before_K
        ],

        "After (Reduced Chemical)": [
            after_N,
            after_P,
            after_K
        ]

    })

    st.dataframe(comparison_data)

    fig = px.bar(
        comparison_data,
        x="Nutrient",
        y=[
            "Before (Chemical)",
            "After (Reduced Chemical)"
        ],
        barmode="group",
        title="Before vs After NPK Levels"
    )

    st.plotly_chart(fig)

# -----------------------------
# MAP
# -----------------------------

st.header("🗺 Farm Location Map")

m = folium.Map(
    location=[26.7606,83.3732],
    zoom_start=6
)

folium.Marker(
    [26.7606,83.3732],
    popup="Farm Location"
).add_to(m)

st_folium(
    m,
    width=700,
    height=500
)
