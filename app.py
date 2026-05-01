# import streamlit as st
# import pandas as pd
# import os
# import plotly.express as px
# import plotly.graph_objects as go
# import folium
# from streamlit_folium import st_folium
# from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
# from sklearn.model_selection import train_test_split
# from sklearn.metrics import accuracy_score

# # ─────────────────────────────────────────────
# # PAGE CONFIG
# # ─────────────────────────────────────────────

# st.set_page_config(
#     page_title="SoilSense Smart Fertilizer Advisory System",
#     page_icon="🌱",
#     layout="wide",
# )

# st.title("🌱 SoilSense Smart Fertilizer Advisory System")
# st.caption("AI-powered soil analysis and fertilizer recommendation for modern agriculture.")

# # ─────────────────────────────────────────────
# # CONSTANTS
# # ─────────────────────────────────────────────

# BASELINE_YIELD = 2.5  # tons/hectare

# REDUCTION_RATIOS = {
#     "Urea":   0.70,
#     "DAP":    0.60,
#     "Potash": 0.65,
# }
# DEFAULT_REDUCTION_RATIO = 0.70

# SOIL_THRESHOLDS = {
#     "Excellent": 150,
#     "Good":      100,
# }

# # ─────────────────────────────────────────────
# # DATA LOADING
# # ─────────────────────────────────────────────

# @st.cache_data
# def load_data():
#     files = [
#         "SoilSense_Output.xlsx",
#         "SoilSense_weather_dataset_5000_non_repeating.xlsx",
#         "rabi_training_data_punjab.csv.xlsx",
#         "rabi_punjabcrop.xlsx",
#     ]

#     dfs = []
#     for f in files:
#         if os.path.exists(f):
#             try:
#                 dfs.append(pd.read_excel(f))
#             except Exception as e:
#                 st.warning(f"⚠️ Could not load **{f}**: {e}")
#         else:
#             st.warning(f"⚠️ File not found: **{f}** — skipping.")

#     if not dfs:
#         st.error("❌ No dataset files found. Place the .xlsx files in the same folder as app.py.")
#         return pd.DataFrame()

#     data = pd.concat(dfs, ignore_index=True)
#     return data


# def clean_data(data: pd.DataFrame) -> pd.DataFrame:
#     data = data.copy()
#     data.columns = data.columns.str.strip()

#     required_cols = ["Nitrogen", "Phosphorus", "Potassium"]

#     for col in required_cols:
#         if col not in data.columns:
#             data[col] = 0
#         data[col] = pd.to_numeric(data[col], errors="coerce")
#         data[col] = data[col].fillna(data[col].median())

#     if "Recommended_Chemical" not in data.columns:
#         data["Recommended_Chemical"] = "Urea"
#     if "Recommended_Organic" not in data.columns:
#         data["Recommended_Organic"] = "Compost"

#     data = data.dropna(subset=["Recommended_Chemical"])
#     data["Recommended_Chemical"] = data["Recommended_Chemical"].astype(str).str.strip()

#     return data


# # ─────────────────────────────────────────────
# # MODEL TRAINING
# # ─────────────────────────────────────────────

# @st.cache_resource
# def train_models(data: pd.DataFrame):
#     features = ["Nitrogen", "Phosphorus", "Potassium"]
#     X = data[features]
#     y = data["Recommended_Chemical"]

#     X_train, X_test, y_train, y_test = train_test_split(
#         X, y, test_size=0.2, random_state=42
#     )

#     clf = RandomForestClassifier(n_estimators=100, random_state=42)
#     clf.fit(X_train, y_train)
#     accuracy = accuracy_score(y_test, clf.predict(X_test))

#     yield_target = (
#         0.02 * data["Nitrogen"]
#         + 0.015 * data["Phosphorus"]
#         + 0.01 * data["Potassium"]
#     )

#     reg = RandomForestRegressor(n_estimators=100, random_state=42)
#     reg.fit(X, yield_target)

#     return clf, reg, round(accuracy * 100, 2)


# # ─────────────────────────────────────────────
# # HELPER FUNCTIONS
# # ─────────────────────────────────────────────

# def get_soil_status(score: float) -> tuple[str, str]:
#     if score >= SOIL_THRESHOLDS["Excellent"]:
#         return "Excellent 🟢", "#2e7d32"
#     elif score >= SOIL_THRESHOLDS["Good"]:
#         return "Good 🟡", "#f9a825"
#     else:
#         return "Poor 🔴", "#c62828"


# def get_reduction_ratio(fertilizer: str) -> float:
#     for key in REDUCTION_RATIOS:
#         if key.lower() in fertilizer.lower():
#             return REDUCTION_RATIOS[key]
#     return DEFAULT_REDUCTION_RATIO


# def compute_before_after(N, P, K, fertilizer: str) -> dict:
#     ratio = get_reduction_ratio(fertilizer)
#     organic_ratio = round((1 - ratio) * 100, 1)
#     chemical_reduction = round((1 - ratio) * 100, 1)

#     return {
#         "Before_N": round(N, 2),
#         "Before_P": round(P, 2),
#         "Before_K": round(K, 2),
#         "After_N":  round(N * ratio, 2),
#         "After_P":  round(P * ratio, 2),
#         "After_K":  round(K * ratio, 2),
#         "Reduction_Ratio":    ratio,
#         "Organic_Ratio_%":    organic_ratio,
#         "Chemical_Reduction_%": chemical_reduction,
#     }


# # ─────────────────────────────────────────────
# # SESSION STATE INIT
# # ─────────────────────────────────────────────

# defaults = {
#     "prediction_done": False,
#     "chemical": None,
#     "organic": None,
#     "soil_score": None,
#     "soil_status": None,
#     "soil_color": None,
#     "yield_pred": None,
#     "yield_improvement_pct": None,
#     "before_after": None,
#     "N": None, "P": None, "K": None,
# }
# for k, v in defaults.items():
#     if k not in st.session_state:
#         st.session_state[k] = v


# # ─────────────────────────────────────────────
# # LOAD + CLEAN + VALIDATE
# # ─────────────────────────────────────────────

# data = load_data()
# if data.empty:
#     st.stop()

# data = clean_data(data)

# unique_classes = data["Recommended_Chemical"].nunique()
# if unique_classes < 2:
#     st.error(
#         f"❌ Dataset must contain at least 2 fertilizer classes. Found: {unique_classes}. "
#         "Check your Excel files."
#     )
#     st.stop()

# model, yield_model, accuracy = train_models(data)

# dataset_size_mb = round(data.memory_usage(deep=True).sum() / 1024 / 1024, 2)

# # ─────────────────────────────────────────────
# # TOP DASHBOARD METRICS
# # ─────────────────────────────────────────────

# st.subheader("📊 Dashboard Overview")
# m1, m2, m3, m4 = st.columns(4)
# m1.metric("🎯 Model Accuracy",       f"{accuracy}%")
# m2.metric("🌾 Fertilizer Classes",   unique_classes)
# m3.metric("📁 Training Samples",     f"{len(data):,}")
# m4.metric("💾 Dataset Size",         f"{dataset_size_mb} MB")

# st.divider()

# # ─────────────────────────────────────────────
# # SIDEBAR
# # ─────────────────────────────────────────────

# st.sidebar.header("🧪 Enter Soil Nutrient Values")
# N = st.sidebar.number_input("Nitrogen (N)",   min_value=0, max_value=500, value=120, step=1)
# P = st.sidebar.number_input("Phosphorus (P)", min_value=0, max_value=200, value=40,  step=1)
# K = st.sidebar.number_input("Potassium (K)",  min_value=0, max_value=200, value=20,  step=1)

# predict_clicked = st.sidebar.button(
#     "🔍 Predict Fertilizer",
#     use_container_width=True,
#     type="primary",
# )

# st.sidebar.divider()
# st.sidebar.markdown("**ℹ️ Soil Score Thresholds**")
# st.sidebar.markdown("- 🟢 Excellent : ≥ 150\n- 🟡 Good : ≥ 100\n- 🔴 Poor : < 100")

# # ─────────────────────────────────────────────
# # RUN PREDICTION
# # ─────────────────────────────────────────────

# if predict_clicked:
#     features = ["Nitrogen", "Phosphorus", "Potassium"]
#     input_df = pd.DataFrame([[N, P, K]], columns=features)

#     chemical = model.predict(input_df)[0]

#     matching_organic = data[data["Recommended_Chemical"] == chemical]["Recommended_Organic"]
#     organic = matching_organic.iloc[0] if not matching_organic.empty else "Compost"

#     soil_score = round(0.4 * N + 0.3 * P + 0.3 * K, 2)
#     soil_status, soil_color = get_soil_status(soil_score)

#     yield_pred = round(yield_model.predict(input_df)[0], 2)
#     yield_improvement = round((yield_pred - BASELINE_YIELD) / BASELINE_YIELD * 100, 2)

#     before_after = compute_before_after(N, P, K, chemical)

#     # Persist all results
#     st.session_state.update({
#         "prediction_done":      True,
#         "chemical":             chemical,
#         "organic":              organic,
#         "soil_score":           soil_score,
#         "soil_status":          soil_status,
#         "soil_color":           soil_color,
#         "yield_pred":           yield_pred,
#         "yield_improvement_pct": yield_improvement,
#         "before_after":         before_after,
#         "N": N, "P": P, "K": K,
#     })

# # ─────────────────────────────────────────────
# # RESULTS SECTION
# # ─────────────────────────────────────────────

# if st.session_state.prediction_done:
#     ba = st.session_state.before_after

#     # ── Section 1: Core Prediction Metrics ──────────────────────────────
#     st.subheader("✅ Fertilizer Recommendation")

#     c1, c2, c3, c4, c5 = st.columns(5)
#     c1.metric("⚗️ Chemical Fertilizer",  st.session_state.chemical)
#     c2.metric("🌿 Organic Fertilizer",   st.session_state.organic)
#     c3.metric("🧮 Soil Health Score",    st.session_state.soil_score)
#     c4.metric("🌾 Predicted Yield",      f"{st.session_state.yield_pred} t/ha")
#     c5.metric(
#         "📈 Yield Improvement",
#         f"{st.session_state.yield_improvement_pct}%",
#         delta=f"vs {BASELINE_YIELD} t/ha baseline",
#     )

#     # Soil Health Status banner
#     st.markdown(
#         f"""
#         <div style="
#             background-color:{st.session_state.soil_color}22;
#             border-left: 6px solid {st.session_state.soil_color};
#             padding: 12px 20px;
#             border-radius: 6px;
#             margin: 12px 0;
#         ">
#             <span style="font-size:18px; font-weight:600; color:{st.session_state.soil_color};">
#                 🌱 Soil Health Status: {st.session_state.soil_status}
#             </span>
#         </div>
#         """,
#         unsafe_allow_html=True,
#     )

#     st.divider()

#     # ── Section 2: Before vs After ───────────────────────────────────────
#     st.subheader("🔄 Before vs After Fertilizer Replacement")

#     col_info1, col_info2 = st.columns(2)
#     col_info1.metric(
#         "♻️ Organic Replacement",
#         f"{ba['Organic_Ratio_%']}%",
#         help="How much of chemical fertilizer is replaced by organic.",
#     )
#     col_info2.metric(
#         "📉 Chemical Reduction",
#         f"{ba['Chemical_Reduction_%']}%",
#         help="Percentage reduction in chemical fertilizer usage.",
#     )

#     # Comparison Table
#     st.markdown("#### 📋 NPK Comparison Table")
#     comparison_df = pd.DataFrame({
#         "Nutrient":    ["Nitrogen (N)", "Phosphorus (P)", "Potassium (K)"],
#         "Before (kg)": [ba["Before_N"],  ba["Before_P"],  ba["Before_K"]],
#         "After (kg)":  [ba["After_N"],   ba["After_P"],   ba["After_K"]],
#         "Reduction (kg)": [
#             round(ba["Before_N"] - ba["After_N"], 2),
#             round(ba["Before_P"] - ba["After_P"], 2),
#             round(ba["Before_K"] - ba["After_K"], 2),
#         ],
#     })
#     st.dataframe(comparison_df, use_container_width=True, hide_index=True)

#     # Before vs After Bar Chart
#     st.markdown("#### 📊 Before vs After NPK Chart")
#     ba_chart_df = pd.DataFrame({
#         "Nutrient": ["N", "P", "K", "N", "P", "K"],
#         "Value":    [
#             ba["Before_N"], ba["Before_P"], ba["Before_K"],
#             ba["After_N"],  ba["After_P"],  ba["After_K"],
#         ],
#         "Phase": ["Before", "Before", "Before", "After", "After", "After"],
#     })

#     fig_ba = px.bar(
#         ba_chart_df,
#         x="Nutrient",
#         y="Value",
#         color="Phase",
#         barmode="group",
#         color_discrete_map={"Before": "#e53935", "After": "#43a047"},
#         text="Value",
#         title=f"NPK Before vs After ({st.session_state.chemical} → Organic blend)",
#         labels={"Value": "Amount (kg/ha)"},
#     )
#     fig_ba.update_traces(textposition="outside")
#     fig_ba.update_layout(legend_title="Phase", height=400)
#     st.plotly_chart(fig_ba, use_container_width=True)

#     st.divider()

#     # ── Section 3: Your NPK Profile ─────────────────────────────────────
#     st.subheader("📈 Your Soil NPK Profile")
#     npk_df = pd.DataFrame({
#         "Nutrient": ["Nitrogen", "Phosphorus", "Potassium"],
#         "Value":    [st.session_state.N, st.session_state.P, st.session_state.K],
#     })
#     fig_npk = px.bar(
#         npk_df,
#         x="Nutrient",
#         y="Value",
#         color="Nutrient",
#         color_discrete_sequence=["#1b5e20", "#388e3c", "#81c784"],
#         text="Value",
#         title="Input Soil Nutrient Levels",
#     )
#     fig_npk.update_traces(textposition="outside")
#     fig_npk.update_layout(showlegend=False, height=380)
#     st.plotly_chart(fig_npk, use_container_width=True)

# else:
#     st.info("👈 Enter your soil nutrient values in the sidebar and click **Predict Fertilizer** to see the full advisory report.")

# # ─────────────────────────────────────────────
# # DATASET DISTRIBUTION (always visible)
# # ─────────────────────────────────────────────

# st.divider()
# st.subheader("📊 Dataset: Top Fertilizer Distribution")

# top_fertilizers = (
#     data["Recommended_Chemical"]
#     .value_counts()
#     .head(10)
#     .reset_index()
# )
# top_fertilizers.columns = ["Fertilizer", "Count"]

# fig_dist = px.bar(
#     top_fertilizers,
#     x="Fertilizer",
#     y="Count",
#     color="Count",
#     color_continuous_scale="Greens",
#     text="Count",
#     title="Top 10 Recommended Chemical Fertilizers in Training Dataset",
# )
# fig_dist.update_traces(textposition="outside")
# fig_dist.update_layout(height=400, coloraxis_showscale=False)
# st.plotly_chart(fig_dist, use_container_width=True)

# # ─────────────────────────────────────────────
# # FARM MAP (always visible)
# # ─────────────────────────────────────────────

# st.divider()
# st.subheader("🗺️ Farm Location Map")

# m = folium.Map(location=[26.7606, 83.3732], zoom_start=6)
# folium.Marker(
#     [26.7606, 83.3732],
#     popup=folium.Popup("<b>Farm Location</b><br>Lat: 26.76 | Lon: 83.37", max_width=200),
#     icon=folium.Icon(color="green", icon="leaf", prefix="fa"),
# ).add_to(m)
# st_folium(m, width=700, height=420)

# st.caption("SoilSense · Powered by RandomForest AI · Built with Streamlit")






import os
import requests
import streamlit as st
import pandas as pd
import plotly.express as px
import folium
from streamlit_folium import st_folium
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

# ─────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="SoilSense: Smart Fertilizer Advisory System",
    page_icon="🌱",
    layout="wide",
)

st.title("🌱 SoilSense: Smart Fertilizer Advisory System")
st.caption("AI-powered soil analysis, fertilizer recommendation, and yield prediction.")

# ─────────────────────────────────────────────────────────────
# CONSTANTS
# ─────────────────────────────────────────────────────────────

CITIES = ["Gorakhpur", "Lucknow", "Varanasi", "Delhi", "Mumbai", "Patna","Mohali"]
BASELINE_YIELD     = 2.5
CHEMICAL_REDUCTION = 0.30
OWM_API_KEY        = os.getenv("OWM_API_KEY", "")
FEATURES           = ["Nitrogen", "Phosphorus", "Potassium"]

# ─────────────────────────────────────────────────────────────
# WEATHER
# ─────────────────────────────────────────────────────────────

def get_weather(city: str) -> tuple:
    """Return (temperature, humidity, rainfall). Falls back to safe defaults."""
    try:
        if not OWM_API_KEY:
            raise ValueError("No API key.")
        url = (
            f"https://api.openweathermap.org/data/2.5/weather"
            f"?q={city}&appid={OWM_API_KEY}&units=metric"
        )
        resp = requests.get(url, timeout=5)
        resp.raise_for_status()
        d = resp.json()
        return (
            round(d["main"]["temp"], 1),
            round(d["main"]["humidity"], 1),
            round(d.get("rain", {}).get("1h", 0.0), 2),
        )
    except Exception:
        return 30.0, 60.0, 0.0

# ─────────────────────────────────────────────────────────────
# DATA LOADING & CLEANING
# ─────────────────────────────────────────────────────────────

@st.cache_data
def load_and_clean_data() -> pd.DataFrame:
    files = [
        "SoilSense_Output.xlsx",
        "SoilSense_weather_dataset_5000_non_repeating.xlsx",
        "rabi_training_data_punjab.csv.xlsx",
        "rabi_punjabcrop.xlsx",
    ]

    dfs = []
    for f in files:
        if os.path.exists(f):
            try:
                dfs.append(pd.read_excel(f))
            except Exception as e:
                st.warning(f"⚠️ Could not read **{f}**: {e}")
        else:
            st.warning(f"⚠️ File not found: **{f}** — skipping.")

    if not dfs:
        return pd.DataFrame()

    data = pd.concat(dfs, ignore_index=True)

    # 1. Strip column names
    data.columns = data.columns.str.strip()

    # 2. Remove duplicates
    data = data.drop_duplicates().reset_index(drop=True)

    # 3 & 4. Numeric conversion + fill NaN with median
    for col in FEATURES:
        if col not in data.columns:
            data[col] = 0
        data[col] = pd.to_numeric(data[col], errors="coerce")
        median_val = data[col].median()
        data[col] = data[col].fillna(median_val if pd.notna(median_val) else 0)

    # Fallback target columns
    if "Recommended_Chemical" not in data.columns:
        data["Recommended_Chemical"] = "Urea"
    if "Recommended_Organic" not in data.columns:
        data["Recommended_Organic"] = "Compost"

    # 5. Drop rows where target is missing
    data = data.dropna(subset=["Recommended_Chemical"])
    data["Recommended_Chemical"] = data["Recommended_Chemical"].astype(str).str.strip()
    data["Recommended_Organic"]  = data["Recommended_Organic"].astype(str).str.strip()

    # Synthetic yield column
    data["Yield"] = (
        0.02  * data["Nitrogen"]
        + 0.015 * data["Phosphorus"]
        + 0.01  * data["Potassium"]
    )

    return data

# ─────────────────────────────────────────────────────────────
# MODEL TRAINING
# ─────────────────────────────────────────────────────────────

@st.cache_resource
def train_models(data: pd.DataFrame):
    X = data[FEATURES]
    y = data["Recommended_Chemical"]

    # Use stratify only when every class has >= 2 samples
    min_count = y.value_counts().min()
    stratify  = y if min_count >= 2 else None

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=stratify
    )

    clf = RandomForestClassifier(
        n_estimators=100,
        max_depth=12,
        min_samples_leaf=5,
        random_state=42,
    )
    clf.fit(X_train, y_train)
    acc = accuracy_score(y_test, clf.predict(X_test))

    reg = RandomForestRegressor(
        n_estimators=100,
        max_depth=12,
        min_samples_leaf=5,
        random_state=42,
    )
    reg.fit(X, data["Yield"])

    return clf, reg, round(acc * 100, 2)

# ─────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────

def soil_health_status(score: float):
    if score >= 150:
        return "Excellent 🟢", "#2e7d32"
    elif score >= 100:
        return "Good 🟡", "#f9a825"
    return "Poor 🔴", "#c62828"


def before_after_df(N, P, K) -> pd.DataFrame:
    ratio = 1 - CHEMICAL_REDUCTION
    return pd.DataFrame({
        "Nutrient":    ["Nitrogen (N)", "Phosphorus (P)", "Potassium (K)"],
        "Before (kg)": [round(N, 2),         round(P, 2),         round(K, 2)],
        "After (kg)":  [round(N * ratio, 2), round(P * ratio, 2), round(K * ratio, 2)],
        "Reduction":   [
            f"{round(N * CHEMICAL_REDUCTION, 2)} kg ({int(CHEMICAL_REDUCTION*100)}%)",
            f"{round(P * CHEMICAL_REDUCTION, 2)} kg ({int(CHEMICAL_REDUCTION*100)}%)",
            f"{round(K * CHEMICAL_REDUCTION, 2)} kg ({int(CHEMICAL_REDUCTION*100)}%)",
        ],
    })

# ─────────────────────────────────────────────────────────────
# LOAD DATA
# ─────────────────────────────────────────────────────────────

data = load_and_clean_data()

if data.empty:
    st.error("❌ No data loaded. Add the required .xlsx files to the app directory.")
    st.stop()

unique_classes = data["Recommended_Chemical"].nunique()

if unique_classes < 2:
    st.error(
        "❌ Dataset must contain at least 2 fertilizer types. "
        f"Currently only **{data['Recommended_Chemical'].unique()[0]}** found. "
        "Please check your Excel files."
    )
    st.stop()

# ─────────────────────────────────────────────────────────────
# TRAIN MODELS
# ─────────────────────────────────────────────────────────────

try:
    clf, reg, accuracy = train_models(data)
except Exception as e:
    st.error(f"❌ Model training failed: {e}")
    st.stop()

# ─────────────────────────────────────────────────────────────
# SESSION STATE INITIALISATION
# ─────────────────────────────────────────────────────────────

_defaults = dict(
    prediction_done=False,
    city=None, temperature=None, humidity=None, rainfall=None,
    chemical=None, organic=None,
    soil_score=None, soil_status=None, soil_color=None,
    yield_pred=None, yield_improvement=None,
    N=None, P=None, K=None,
)
for k, v in _defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ─────────────────────────────────────────────────────────────
# DASHBOARD HEADER METRICS
# ─────────────────────────────────────────────────────────────

st.subheader("📊 System Overview")
h1, h2, h3, h4 = st.columns(4)
h1.metric("🎯 Model Accuracy",     f"{accuracy}%")
h2.metric("🌾 Fertilizer Classes", unique_classes)
h3.metric("📁 Training Samples",   f"{len(data):,}")
h4.metric("🗂 Dataset Columns",    len(data.columns))
st.divider()

# ─────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────

st.sidebar.header("🌾 Soil & Location Inputs")
city = st.sidebar.selectbox("📍 Select City", CITIES)
N    = st.sidebar.number_input("Nitrogen (N)",   min_value=0, max_value=500, value=120, step=1)
P    = st.sidebar.number_input("Phosphorus (P)", min_value=0, max_value=200, value=40,  step=1)
K    = st.sidebar.number_input("Potassium (K)",  min_value=0, max_value=200, value=20,  step=1)

predict_clicked = st.sidebar.button(
    "🔍 Predict", use_container_width=True, type="primary"
)

st.sidebar.divider()
st.sidebar.markdown(
    "**Soil Score Guide**\n"
    "- 🟢 Excellent ≥ 150\n"
    "- 🟡 Good ≥ 100\n"
    "- 🔴 Poor < 100"
)

# ─────────────────────────────────────────────────────────────
# PREDICTION LOGIC
# ─────────────────────────────────────────────────────────────

if predict_clicked:
    try:
        input_df = pd.DataFrame([[N, P, K]], columns=FEATURES)

        chemical       = clf.predict(input_df)[0]
        organic_match  = data[data["Recommended_Chemical"] == chemical]["Recommended_Organic"]
        organic        = organic_match.iloc[0] if not organic_match.empty else "Compost"

        soil_score          = round(0.4 * N + 0.3 * P + 0.3 * K, 2)
        status, color       = soil_health_status(soil_score)
        yield_pred          = round(reg.predict(input_df)[0], 2)
        yield_improvement   = round((yield_pred - BASELINE_YIELD) / BASELINE_YIELD * 100, 2)
        temp, hum, rain     = get_weather(city)

        st.session_state.update(dict(
            prediction_done=True,
            city=city, temperature=temp, humidity=hum, rainfall=rain,
            chemical=chemical, organic=organic,
            soil_score=soil_score, soil_status=status, soil_color=color,
            yield_pred=yield_pred, yield_improvement=yield_improvement,
            N=N, P=P, K=K,
        ))

    except Exception as e:
        st.error(f"❌ Prediction error: {e}")

# ─────────────────────────────────────────────────────────────
# RESULTS  (persistent via session_state)
# ─────────────────────────────────────────────────────────────

if st.session_state.prediction_done:
    ss = st.session_state

    # ── Weather ──────────────────────────────────────────────
    st.subheader(f"🌤 Current Weather — {ss.city}")
    w1, w2, w3 = st.columns(3)
    w1.metric("🌡 Temperature", f"{ss.temperature} °C")
    w2.metric("💧 Humidity",    f"{ss.humidity} %")
    w3.metric("🌧 Rainfall",    f"{ss.rainfall} mm")
    st.divider()

    # ── Core Prediction Metrics ──────────────────────────────
    st.subheader("✅ Fertilizer Recommendation & Yield Forecast")
    r1, r2, r3, r4, r5 = st.columns(5)
    r1.metric("⚗️ Chemical Fertilizer", ss.chemical)
    r2.metric("🌿 Organic Fertilizer",  ss.organic)
    r3.metric("🧮 Soil Score",          ss.soil_score)
    r4.metric("🌾 Predicted Yield",     f"{ss.yield_pred} t/ha")
    r5.metric(
        "📈 Yield Improvement",
        f"{ss.yield_improvement}%",
        delta=f"vs {BASELINE_YIELD} t/ha baseline",
    )

    # Soil health banner
    st.markdown(
        f"""
        <div style="background:{ss.soil_color}22;
                    border-left:6px solid {ss.soil_color};
                    padding:12px 20px;border-radius:6px;margin:12px 0;">
            <span style="font-size:18px;font-weight:600;color:{ss.soil_color};">
                🌱 Soil Health Status: {ss.soil_status}
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.divider()

    # ── Before vs After ──────────────────────────────────────
    st.subheader(f"🔄 Before vs After — 30% Chemical Reduction")

    st.dataframe(before_after_df(ss.N, ss.P, ss.K), use_container_width=True, hide_index=True)

    ratio = 1 - CHEMICAL_REDUCTION
    ba_chart = pd.DataFrame({
        "Nutrient": ["N", "P", "K", "N", "P", "K"],
        "Value":    [
            ss.N, ss.P, ss.K,
            round(ss.N * ratio, 2), round(ss.P * ratio, 2), round(ss.K * ratio, 2),
        ],
        "Phase": ["Before"] * 3 + ["After"] * 3,
    })
    fig_ba = px.bar(
        ba_chart, x="Nutrient", y="Value", color="Phase", barmode="group",
        color_discrete_map={"Before": "#e53935", "After": "#43a047"},
        text="Value",
        title="NPK Before vs After Chemical Fertilizer Replacement",
        labels={"Value": "Amount (kg/ha)"},
    )
    fig_ba.update_traces(textposition="outside")
    fig_ba.update_layout(height=400)
    st.plotly_chart(fig_ba, use_container_width=True)
    st.divider()

    # ── NPK Profile ───────────────────────────────────────────
    st.subheader("📈 Your Soil NPK Profile")
    npk_fig = px.bar(
        pd.DataFrame({"Nutrient": FEATURES, "Value": [ss.N, ss.P, ss.K]}),
        x="Nutrient", y="Value", color="Nutrient",
        color_discrete_sequence=["#1b5e20", "#388e3c", "#81c784"],
        text="Value", title="Input Soil Nutrient Levels (kg/ha)",
    )
    npk_fig.update_traces(textposition="outside")
    npk_fig.update_layout(showlegend=False, height=380)
    st.plotly_chart(npk_fig, use_container_width=True)

else:
    st.info("👈 Enter your soil values in the sidebar and click **Predict** to generate the full advisory report.")

# ─────────────────────────────────────────────────────────────
# FERTILIZER DISTRIBUTION  (always visible)
# ─────────────────────────────────────────────────────────────

st.divider()
st.subheader("📊 Dataset: Fertilizer Distribution")

top10 = data["Recommended_Chemical"].value_counts().head(10).reset_index()
top10.columns = ["Fertilizer", "Count"]
fig_dist = px.bar(
    top10, x="Fertilizer", y="Count", color="Count",
    color_continuous_scale="Greens", text="Count",
    title="Top 10 Recommended Chemical Fertilizers in Training Dataset",
)
fig_dist.update_traces(textposition="outside")
fig_dist.update_layout(height=420, coloraxis_showscale=False)
st.plotly_chart(fig_dist, use_container_width=True)

# ─────────────────────────────────────────────────────────────
# FARM MAP  (always visible)
# ─────────────────────────────────────────────────────────────

st.divider()
st.subheader("🗺️ Farm Location Map")

farm_map = folium.Map(location=[26.7606, 83.3732], zoom_start=7)
folium.Marker(
    [26.7606, 83.3732],
    popup=folium.Popup(
        "<b>Farm Location</b><br>Lat: 26.7606 | Lon: 83.3732", max_width=220
    ),
    icon=folium.Icon(color="green", icon="leaf", prefix="fa"),
).add_to(farm_map)
st_folium(farm_map, width=700, height=500)

st.caption("SoilSense · Powered by RandomForest AI & OpenWeatherMap · Built with Streamlit 🌱")
