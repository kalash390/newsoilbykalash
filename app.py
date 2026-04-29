import streamlit as st
import pandas as pd
import os
import plotly.express as px
import folium
from streamlit_folium import st_folium

from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

# --------------------------------
# PAGE CONFIG
# --------------------------------

st.set_page_config(
    page_title="SoilSense Smart Fertilizer Advisory System",
    layout="wide"
)

st.title("🌱 SoilSense Smart Fertilizer Advisory System")

# --------------------------------
# LOAD DATASETS
# --------------------------------

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

# --------------------------------
# CLEAN DATA
# --------------------------------

data.columns = data.columns.str.strip()

required_cols = [
    "Nitrogen",
    "Phosphorus",
    "Potassium"
]

for col in required_cols:

    if col not in data.columns:
        data[col] = 0

# Ensure target exists

if "Recommended_Chemical" not in data.columns:

    data["Recommended_Chemical"] = "Urea"

if "Recommended_Organic" not in data.columns:

    data["Recommended_Organic"] = "Compost"

# Convert numeric safely

for col in required_cols:

    data[col] = pd.to_numeric(
        data[col],
        errors="coerce"
    )

    data[col] = data[col].fillna(
        data[col].median()
    )

# Remove invalid target rows

data = data.dropna(
    subset=["Recommended_Chemical"]
)

data["Recommended_Chemical"] = data[
    "Recommended_Chemical"
].astype(str)

# IMPORTANT FIX

unique_classes = data["Recommended_Chemical"].nunique()

st.write("Unique fertilizer classes:", unique_classes)

if unique_classes < 2:

    st.error(
        "Dataset must contain at least 2 different fertilizers"
    )

    st.stop()

# --------------------------------
# MODEL TRAINING
# --------------------------------

features = [
    "Nitrogen",
    "Phosphorus",
    "Potassium"
]

X = data[features]

y = data["Recommended_Chemical"]

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

# --------------------------------
# YIELD MODEL
# --------------------------------

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

# --------------------------------
# SIDEBAR INPUT
# --------------------------------

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

# --------------------------------
# PREDICTION
# --------------------------------

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

    soil_score = (
        0.4 * N +
        0.3 * P +
        0.3 * K
    )

    st.subheader("Soil Health Score")

    st.write(round(soil_score, 2))

    yield_pred = yield_model.predict(
        input_data
    )[0]

    st.subheader("Predicted Yield")

    st.write(
        round(yield_pred, 2),
        "tons/hectare"
    )

# --------------------------------
# MAP
# --------------------------------

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
