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
# LOAD & CACHE DATASETS
# --------------------------------

@st.cache_data
def load_data():
    dfs = []

    files = [
        "SoilSense_Output.xlsx",
        "SoilSense_weather_dataset_5000_non_repeating.xlsx",
        "rabi_training_data_punjab.csv.xlsx",
        "rabi_punjabcrop.xlsx",
    ]

    for f in files:
        if os.path.exists(f):
            try:
                dfs.append(pd.read_excel(f))
            except Exception as e:
                st.warning(f"Could not load {f}: {e}")

    if not dfs:
        st.error("No dataset files found. Please place the .xlsx files in the same folder as this script.")
        return pd.DataFrame()

    data = pd.concat(dfs, ignore_index=True)
    return data


@st.cache_resource
def train_models(data: pd.DataFrame):
    """Train and cache models so they don't retrain on every interaction."""

    features = ["Nitrogen", "Phosphorus", "Potassium"]

    X = data[features]
    y = data["Recommended_Chemical"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    clf = RandomForestClassifier(n_estimators=100, random_state=42)
    clf.fit(X_train, y_train)
    accuracy = accuracy_score(y_test, clf.predict(X_test))

    # Synthetic yield target (matches original logic)
    yield_target = (
        0.02 * data["Nitrogen"]
        + 0.015 * data["Phosphorus"]
        + 0.01 * data["Potassium"]
    )

    reg = RandomForestRegressor(n_estimators=100, random_state=42)
    reg.fit(X, yield_target)

    return clf, reg, accuracy


# --------------------------------
# LOAD DATA
# --------------------------------

data = load_data()

if data.empty:
    st.stop()

# --------------------------------
# CLEAN DATA
# --------------------------------

data.columns = data.columns.str.strip()

required_cols = ["Nitrogen", "Phosphorus", "Potassium"]

for col in required_cols:
    if col not in data.columns:
        data[col] = 0

if "Recommended_Chemical" not in data.columns:
    data["Recommended_Chemical"] = "Urea"

if "Recommended_Organic" not in data.columns:
    data["Recommended_Organic"] = "Compost"

for col in required_cols:
    data[col] = pd.to_numeric(data[col], errors="coerce")
    data[col] = data[col].fillna(data[col].median())

data = data.dropna(subset=["Recommended_Chemical"])
data["Recommended_Chemical"] = data["Recommended_Chemical"].astype(str)

unique_classes = data["Recommended_Chemical"].nunique()

if unique_classes < 2:
    st.error(
        f"Dataset must contain at least 2 different fertilizer classes. "
        f"Currently found: {unique_classes}. "
        f"Check your data files."
    )
    st.stop()

# --------------------------------
# TRAIN MODELS (cached — runs once)
# --------------------------------

model, yield_model, accuracy = train_models(data)

# --------------------------------
# SIDEBAR INPUT
# --------------------------------

st.sidebar.header("🧪 Soil Inputs")

N = st.sidebar.number_input("Nitrogen (N)", min_value=0, max_value=500, value=120)
P = st.sidebar.number_input("Phosphorus (P)", min_value=0, max_value=200, value=40)
K = st.sidebar.number_input("Potassium (K)", min_value=0, max_value=200, value=20)

predict_clicked = st.sidebar.button("🔍 Predict Fertilizer", use_container_width=True)

# --------------------------------
# SESSION STATE — persist results
# --------------------------------

if "prediction_done" not in st.session_state:
    st.session_state.prediction_done = False
    st.session_state.chemical = None
    st.session_state.organic = None
    st.session_state.soil_score = None
    st.session_state.yield_pred = None
    st.session_state.N = None
    st.session_state.P = None
    st.session_state.K = None

if predict_clicked:
    features = ["Nitrogen", "Phosphorus", "Potassium"]
    input_df = pd.DataFrame([[N, P, K]], columns=features)

    chemical = model.predict(input_df)[0]

    # Get matching organic fertilizer
    matching = data[data["Recommended_Chemical"] == chemical]["Recommended_Organic"]
    organic = matching.iloc[0] if not matching.empty else "Compost"

    soil_score = round(0.4 * N + 0.3 * P + 0.3 * K, 2)
    yield_pred = round(yield_model.predict(input_df)[0], 2)

    # Store in session state so results persist across rerenders
    st.session_state.prediction_done = True
    st.session_state.chemical = chemical
    st.session_state.organic = organic
    st.session_state.soil_score = soil_score
    st.session_state.yield_pred = yield_pred
    st.session_state.N = N
    st.session_state.P = P
    st.session_state.K = K

# --------------------------------
# MAIN CONTENT AREA
# --------------------------------

col1, col2, col3 = st.columns(3)

col1.metric("📊 Model Accuracy", f"{round(accuracy * 100, 2)}%")
col2.metric("🌾 Fertilizer Classes", unique_classes)
col3.metric("📁 Training Samples", len(data))

st.divider()

# --------------------------------
# PREDICTION RESULTS
# --------------------------------

if st.session_state.prediction_done:
    st.subheader("✅ Prediction Results")

    r1, r2, r3, r4 = st.columns(4)

    r1.metric("Chemical Fertilizer", st.session_state.chemical)
    r2.metric("Organic Fertilizer", st.session_state.organic)
    r3.metric("Soil Health Score", st.session_state.soil_score)
    r4.metric("Predicted Yield", f"{st.session_state.yield_pred} t/ha")

    st.divider()

    # NPK bar chart
    st.subheader("📈 Your NPK Profile")

    npk_df = pd.DataFrame({
        "Nutrient": ["Nitrogen", "Phosphorus", "Potassium"],
        "Value": [st.session_state.N, st.session_state.P, st.session_state.K]
    })

    fig = px.bar(
        npk_df,
        x="Nutrient",
        y="Value",
        color="Nutrient",
        color_discrete_sequence=["#2e7d32", "#558b2f", "#9ccc65"],
        text="Value",
        title="NPK Nutrient Levels"
    )
    fig.update_layout(showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

else:
    st.info("👈 Enter your soil values in the sidebar and click **Predict Fertilizer** to see results.")

# --------------------------------
# DATA DISTRIBUTION CHART
# --------------------------------

st.subheader("📊 Dataset: Fertilizer Distribution")

if "Recommended_Chemical" in data.columns:
    top_fertilizers = data["Recommended_Chemical"].value_counts().head(10).reset_index()
    top_fertilizers.columns = ["Fertilizer", "Count"]

    fig2 = px.bar(
        top_fertilizers,
        x="Fertilizer",
        y="Count",
        color="Count",
        color_continuous_scale="Greens",
        title="Top 10 Recommended Chemical Fertilizers in Dataset"
    )
    st.plotly_chart(fig2, use_container_width=True)

# --------------------------------
# FARM MAP
# --------------------------------

st.subheader("🗺️ Farm Location Map")

m = folium.Map(location=[26.7606, 83.3732], zoom_start=6)

folium.Marker(
    [26.7606, 83.3732],
    popup="Farm Location",
    icon=folium.Icon(color="green", icon="leaf")
).add_to(m)

st_folium(m, width=700, height=400)
