
import streamlit as st
import pandas as pd
import os
import requests
import plotly.express as px
import folium
from streamlit_folium import st_folium

from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

# -----------------------------------------
# PAGE CONFIG
# -----------------------------------------

st.set_page_config(
    page_title="SoilSense Smart Fertilizer Advisory System",
    layout="wide"
)

st.title("🌱 SoilSense Smart Fertilizer Advisory System")

# -----------------------------------------
# SHOW FILES (DEBUG)
# -----------------------------------------

st.write("Files in directory:", os.listdir())

# -----------------------------------------
# LOAD DATASETS
# -----------------------------------------

@st.cache_data
def load_data():

    try:

        data1 = pd.read_excel("SoilSense_Output.xlsx")
        data2 = pd.read_excel("SoilSense_weather_dataset_5000_non_repeating.xlsx")
        data3 = pd.read_excel("rabi_training_data_punjab.csv.xlsx")
        data4 = pd.read_excel("rabi_punjabcrop.xlsx")

        data = pd.concat(
            [data1, data2, data3, data4],
            ignore_index=True
        )

        return data

    except Exception as e:

        st.error("Dataset loading error")
        st.write(e)
        return pd.DataFrame()


data = load_data()

if data.empty:

    st.stop()

# -----------------------------------------
# CLEAN DATA
# -----------------------------------------

required_cols = [
    "Nitrogen",
    "Phosphorus",
    "Potassium"
]

for col in required_cols:

    if col not in data.columns:

        data[col] = 0

data = data.fillna(data.median(numeric_only=True))

# -----------------------------------------
# CREATE TARGET IF MISSING
# -----------------------------------------

if "Recommended_Chemical" not in data.columns:

    data["Recommended_Chemical"] = "Urea"

if "Recommended_Organic" not in data.columns:

    data["Recommended_Organic"] = "Compost"

# -----------------------------------------
# FEATURES
# -----------------------------------------

features = [
    "Nitrogen",
    "Phosphorus",
    "Potassium"
]

X = data[features]

y = data["Recommended_Chemical"]

# -----------------------------------------
# TRAIN MODEL
# -----------------------------------------

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42
)

model = RandomForestClassifier()

model.fit(
    X_train,
    y_train
)

accuracy = accuracy_score(
    y_test,
    model.predict(X_test)
)

st.metric(
    "Model Accuracy",
    str(round(accuracy * 100, 2)) + "%"
)

# -----------------------------------------
# YIELD MODEL
# -----------------------------------------

data["Yield"] = (
    0.02 * data["Nitrogen"]
    + 0.015 * data["Phosphorus"]
    + 0.01 * data["Potassium"]
)

yield_model = RandomForestRegressor()

yield_model.fit(
    X,
    data["Yield"]
)

# -----------------------------------------
# WEATHER API
# -----------------------------------------

API_KEY = "cb81120197f345ae396cd0fa28c1827c"

city = st.sidebar.text_input(
    "City",
    "Gorakhpur"
)

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

# -----------------------------------------
# SIDEBAR INPUT
# -----------------------------------------

st.sidebar.header("Soil Inputs")

N = st.sidebar.number_input(
    "Nitrogen",
    0,
    500,
    120
)

P = st.sidebar.number_input(
    "Phosphorus",
    0,
    200,
    40
)

K = st.sidebar.number_input(
    "Potassium",
    0,
    200,
    20
)

# -----------------------------------------
# PREDICTION
# -----------------------------------------

if st.sidebar.button("Predict"):

    input_data = pd.DataFrame(
        [[N, P, K]],
        columns=features
    )

    chemical = model.predict(
        input_data
    )[0]

    organic = data[
        data["Recommended_Chemical"] == chemical
    ]["Recommended_Organic"].iloc[0]

    st.success(
        f"Chemical Fertilizer: {chemical}"
    )

    st.info(
        f"Organic Fertilizer: {organic}"
    )

    # -------------------------------------
    # SOIL HEALTH SCORE
    # -------------------------------------

    soil_score = (
        0.4 * N
        + 0.3 * P
        + 0.3 * K
    )

    st.subheader(
        "Soil Health Score"
    )

    st.write(
        round(soil_score, 2)
    )

    # -------------------------------------
    # YIELD PREDICTION
    # -------------------------------------

    yield_pred = yield_model.predict(
        input_data
    )[0]

    st.subheader(
        "Predicted Yield"
    )

    st.write(
        round(yield_pred, 2),
        "tons/hectare"
    )

    # -------------------------------------
    # BEFORE vs AFTER COMPARISON
    # -------------------------------------

    st.header(
        "Before vs After Fertilizer Replacement"
    )

    if chemical == "Urea":

        ratio = 0.7

    elif chemical == "DAP":

        ratio = 0.6

    elif chemical == "Potash":

        ratio = 0.65

    else:

        ratio = 0.7

    after_N = round(N * ratio, 2)
    after_P = round(P * ratio, 2)
    after_K = round(K * ratio, 2)

    comparison = pd.DataFrame({

        "Nutrient": [
            "Nitrogen",
            "Phosphorus",
            "Potassium"
        ],

        "Before": [
            N,
            P,
            K
        ],

        "After": [
            after_N,
            after_P,
            after_K
        ]

    })

    st.dataframe(
        comparison
    )

    fig = px.bar(

        comparison,

        x="Nutrient",

        y=["Before", "After"],

        barmode="group",

        title="Before vs After NPK Levels"

    )

    st.plotly_chart(fig)

# -----------------------------------------
# MAP
# -----------------------------------------

st.header("Farm Location Map")

m = folium.Map(
    location=[26.7606, 83.3732],
    zoom_start=6
)

folium.Marker(
    [26.7606, 83.3732],
    popup="Farm Location"
).add_to(m)

st_folium(
    m,
    width=700,
    height=500
)
