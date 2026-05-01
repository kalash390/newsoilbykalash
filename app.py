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






# import os
# import requests
# import streamlit as st
# import pandas as pd
# import plotly.express as px
# import folium
# from streamlit_folium import st_folium
# from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
# from sklearn.model_selection import train_test_split
# from sklearn.metrics import accuracy_score

# # ─────────────────────────────────────────────────────────────
# # PAGE CONFIG
# # ─────────────────────────────────────────────────────────────

# st.set_page_config(
#     page_title="SoilSense: Smart Fertilizer Advisory System",
#     page_icon="🌱",
#     layout="wide",
# )

# st.title("🌱 SoilSense: Smart Fertilizer Advisory System")
# st.caption("AI-powered soil analysis, fertilizer recommendation, and yield prediction.")

# # ─────────────────────────────────────────────────────────────
# # CONSTANTS
# # ─────────────────────────────────────────────────────────────

# CITIES = ["Gorakhpur", "Lucknow", "Varanasi", "Delhi", "Mumbai", "Patna","Mohali"]
# BASELINE_YIELD     = 2.5
# CHEMICAL_REDUCTION = 0.30
# OWM_API_KEY        = os.getenv("OWM_API_KEY", "cb81120197f345ae396cd0fa28c1827c")
# FEATURES           = ["Nitrogen", "Phosphorus", "Potassium"]

# # ─────────────────────────────────────────────────────────────
# # WEATHER
# # ─────────────────────────────────────────────────────────────

# def get_weather(city: str) -> tuple:
#     """Return (temperature, humidity, rainfall). Falls back to safe defaults."""
#     try:
#         if not OWM_API_KEY:
#             raise ValueError("No API key.")
#         url = (
#             f"https://api.openweathermap.org/data/2.5/weather"
#             f"?q={city}&appid={OWM_API_KEY}&units=metric"
#         )
#         resp = requests.get(url, timeout=5)
#         resp.raise_for_status()
#         d = resp.json()
#         return (
#             round(d["main"]["temp"], 1),
#             round(d["main"]["humidity"], 1),
#             round(d.get("rain", {}).get("1h", 0.0), 2),
#         )
#     except Exception:
#         return 30.0, 60.0, 0.0

# # ─────────────────────────────────────────────────────────────
# # DATA LOADING & CLEANING
# # ─────────────────────────────────────────────────────────────

# @st.cache_data
# def load_and_clean_data() -> pd.DataFrame:
#     files = [
#         # "SoilSense_Output.xlsx",
#         # "SoilSense_weather_dataset_5000_non_repeating.xlsx",
#         # "rabi_training_data_punjab.csv.xlsx",
#         # "rabi_punjabcrop.xlsx",
#         "improved_balanced_dataset_5000.xlsv",
#     ]

#     dfs = []
#     for f in files:
#         if os.path.exists(f):
#             try:
#                 dfs.append(pd.read_excel(f))
#             except Exception as e:
#                 st.warning(f"⚠️ Could not read **{f}**: {e}")
#         else:
#             st.warning(f"⚠️ File not found: **{f}** — skipping.")

#     if not dfs:
#         return pd.DataFrame()

#     data = pd.concat(dfs, ignore_index=True)

#     # 1. Strip column names
#     data.columns = data.columns.str.strip()

#     # 2. Remove duplicates
#     data = data.drop_duplicates().reset_index(drop=True)

#     # 3 & 4. Numeric conversion + fill NaN with median
#     for col in FEATURES:
#         if col not in data.columns:
#             data[col] = 0
#         data[col] = pd.to_numeric(data[col], errors="coerce")
#         median_val = data[col].median()
#         data[col] = data[col].fillna(median_val if pd.notna(median_val) else 0)

#     # Fallback target columns
#     if "Recommended_Chemical" not in data.columns:
#         data["Recommended_Chemical"] = "Urea"
#     if "Recommended_Organic" not in data.columns:
#         data["Recommended_Organic"] = "Compost"

#     # 5. Drop rows where target is missing
#     data = data.dropna(subset=["Recommended_Chemical"])
#     data["Recommended_Chemical"] = data["Recommended_Chemical"].astype(str).str.strip()
#     data["Recommended_Organic"]  = data["Recommended_Organic"].astype(str).str.strip()

#     # Synthetic yield column
#     data["Yield"] = (
#         0.02  * data["Nitrogen"]
#         + 0.015 * data["Phosphorus"]
#         + 0.01  * data["Potassium"]
#     )

#     return data

# # ─────────────────────────────────────────────────────────────
# # MODEL TRAINING
# # ─────────────────────────────────────────────────────────────

# @st.cache_resource
# def train_models(data: pd.DataFrame):
#     X = data[FEATURES]
#     y = data["Recommended_Chemical"]

#     # Use stratify only when every class has >= 2 samples
#     min_count = y.value_counts().min()
#     stratify  = y if min_count >= 2 else None

#     X_train, X_test, y_train, y_test = train_test_split(
#         X, y, test_size=0.2, random_state=42, stratify=stratify
#     )

#     clf = RandomForestClassifier(
#         n_estimators=100,
#         max_depth=12,
#         min_samples_leaf=5,
#         random_state=42,
#     )
#     clf.fit(X_train, y_train)
#     acc = accuracy_score(y_test, clf.predict(X_test))

#     reg = RandomForestRegressor(
#         n_estimators=100,
#         max_depth=12,
#         min_samples_leaf=5,
#         random_state=42,
#     )
#     reg.fit(X, data["Yield"])

#     return clf, reg, round(acc * 100, 2)

# # ─────────────────────────────────────────────────────────────
# # HELPERS
# # ─────────────────────────────────────────────────────────────

# def soil_health_status(score: float):
#     if score >= 150:
#         return "Excellent 🟢", "#2e7d32"
#     elif score >= 100:
#         return "Good 🟡", "#f9a825"
#     return "Poor 🔴", "#c62828"


# def before_after_df(N, P, K) -> pd.DataFrame:
#     ratio = 1 - CHEMICAL_REDUCTION
#     return pd.DataFrame({
#         "Nutrient":    ["Nitrogen (N)", "Phosphorus (P)", "Potassium (K)"],
#         "Before (kg)": [round(N, 2),         round(P, 2),         round(K, 2)],
#         "After (kg)":  [round(N * ratio, 2), round(P * ratio, 2), round(K * ratio, 2)],
#         "Reduction":   [
#             f"{round(N * CHEMICAL_REDUCTION, 2)} kg ({int(CHEMICAL_REDUCTION*100)}%)",
#             f"{round(P * CHEMICAL_REDUCTION, 2)} kg ({int(CHEMICAL_REDUCTION*100)}%)",
#             f"{round(K * CHEMICAL_REDUCTION, 2)} kg ({int(CHEMICAL_REDUCTION*100)}%)",
#         ],
#     })

# # ─────────────────────────────────────────────────────────────
# # LOAD DATA
# # ─────────────────────────────────────────────────────────────

# data = load_and_clean_data()

# if data.empty:
#     st.error("❌ No data loaded. Add the required .xlsx files to the app directory.")
#     st.stop()

# unique_classes = data["Recommended_Chemical"].nunique()

# if unique_classes < 2:
#     st.error(
#         "❌ Dataset must contain at least 2 fertilizer types. "
#         f"Currently only **{data['Recommended_Chemical'].unique()[0]}** found. "
#         "Please check your Excel files."
#     )
#     st.stop()

# # ─────────────────────────────────────────────────────────────
# # TRAIN MODELS
# # ─────────────────────────────────────────────────────────────

# try:
#     clf, reg, accuracy = train_models(data)
# except Exception as e:
#     st.error(f"❌ Model training failed: {e}")
#     st.stop()

# # ─────────────────────────────────────────────────────────────
# # SESSION STATE INITIALISATION
# # ─────────────────────────────────────────────────────────────

# _defaults = dict(
#     prediction_done=False,
#     city=None, temperature=None, humidity=None, rainfall=None,
#     chemical=None, organic=None,
#     soil_score=None, soil_status=None, soil_color=None,
#     yield_pred=None, yield_improvement=None,
#     N=None, P=None, K=None,
# )
# for k, v in _defaults.items():
#     if k not in st.session_state:
#         st.session_state[k] = v

# # ─────────────────────────────────────────────────────────────
# # DASHBOARD HEADER METRICS
# # ─────────────────────────────────────────────────────────────

# st.subheader("📊 System Overview")
# h1, h2, h3, h4 = st.columns(4)
# h1.metric("🎯 Model Accuracy",     f"{accuracy}%")
# h2.metric("🌾 Fertilizer Classes", unique_classes)
# h3.metric("📁 Training Samples",   f"{len(data):,}")
# h4.metric("🗂 Dataset Columns",    len(data.columns))
# st.divider()

# # ─────────────────────────────────────────────────────────────
# # SIDEBAR
# # ─────────────────────────────────────────────────────────────

# st.sidebar.header("🌾 Soil & Location Inputs")
# city = st.sidebar.selectbox("📍 Select City", CITIES)
# N    = st.sidebar.number_input("Nitrogen (N)",   min_value=0, max_value=500, value=120, step=1)
# P    = st.sidebar.number_input("Phosphorus (P)", min_value=0, max_value=200, value=40,  step=1)
# K    = st.sidebar.number_input("Potassium (K)",  min_value=0, max_value=200, value=20,  step=1)

# predict_clicked = st.sidebar.button(
#     "🔍 Predict", use_container_width=True, type="primary"
# )

# st.sidebar.divider()
# st.sidebar.markdown(
#     "**Soil Score Guide**\n"
#     "- 🟢 Excellent ≥ 150\n"
#     "- 🟡 Good ≥ 100\n"
#     "- 🔴 Poor < 100"
# )

# # ─────────────────────────────────────────────────────────────
# # PREDICTION LOGIC
# # ─────────────────────────────────────────────────────────────

# if predict_clicked:
#     try:
#         input_df = pd.DataFrame([[N, P, K]], columns=FEATURES)

#         chemical       = clf.predict(input_df)[0]
#         organic_match  = data[data["Recommended_Chemical"] == chemical]["Recommended_Organic"]
#         organic        = organic_match.iloc[0] if not organic_match.empty else "Compost"

#         soil_score          = round(0.4 * N + 0.3 * P + 0.3 * K, 2)
#         status, color       = soil_health_status(soil_score)
#         yield_pred          = round(reg.predict(input_df)[0], 2)
#         yield_improvement   = round((yield_pred - BASELINE_YIELD) / BASELINE_YIELD * 100, 2)
#         temp, hum, rain     = get_weather(city)

#         st.session_state.update(dict(
#             prediction_done=True,
#             city=city, temperature=temp, humidity=hum, rainfall=rain,
#             chemical=chemical, organic=organic,
#             soil_score=soil_score, soil_status=status, soil_color=color,
#             yield_pred=yield_pred, yield_improvement=yield_improvement,
#             N=N, P=P, K=K,
#         ))

#     except Exception as e:
#         st.error(f"❌ Prediction error: {e}")

# # ─────────────────────────────────────────────────────────────
# # RESULTS  (persistent via session_state)
# # ─────────────────────────────────────────────────────────────

# if st.session_state.prediction_done:
#     ss = st.session_state

#     # ── Weather ──────────────────────────────────────────────
#     st.subheader(f"🌤 Current Weather — {ss.city}")
#     w1, w2, w3 = st.columns(3)
#     w1.metric("🌡 Temperature", f"{ss.temperature} °C")
#     w2.metric("💧 Humidity",    f"{ss.humidity} %")
#     w3.metric("🌧 Rainfall",    f"{ss.rainfall} mm")
#     st.divider()

#     # ── Core Prediction Metrics ──────────────────────────────
#     st.subheader("✅ Fertilizer Recommendation & Yield Forecast")
#     r1, r2, r3, r4, r5 = st.columns(5)
#     r1.metric("⚗️ Chemical Fertilizer", ss.chemical)
#     r2.metric("🌿 Organic Fertilizer",  ss.organic)
#     r3.metric("🧮 Soil Score",          ss.soil_score)
#     r4.metric("🌾 Predicted Yield",     f"{ss.yield_pred} t/ha")
#     r5.metric(
#         "📈 Yield Improvement",
#         f"{ss.yield_improvement}%",
#         delta=f"vs {BASELINE_YIELD} t/ha baseline",
#     )

#     # Soil health banner
#     st.markdown(
#         f"""
#         <div style="background:{ss.soil_color}22;
#                     border-left:6px solid {ss.soil_color};
#                     padding:12px 20px;border-radius:6px;margin:12px 0;">
#             <span style="font-size:18px;font-weight:600;color:{ss.soil_color};">
#                 🌱 Soil Health Status: {ss.soil_status}
#             </span>
#         </div>
#         """,
#         unsafe_allow_html=True,
#     )
#     st.divider()

#     # ── Before vs After ──────────────────────────────────────
#     st.subheader(f"🔄 Before vs After — 30% Chemical Reduction")

#     st.dataframe(before_after_df(ss.N, ss.P, ss.K), use_container_width=True, hide_index=True)

#     ratio = 1 - CHEMICAL_REDUCTION
#     ba_chart = pd.DataFrame({
#         "Nutrient": ["N", "P", "K", "N", "P", "K"],
#         "Value":    [
#             ss.N, ss.P, ss.K,
#             round(ss.N * ratio, 2), round(ss.P * ratio, 2), round(ss.K * ratio, 2),
#         ],
#         "Phase": ["Before"] * 3 + ["After"] * 3,
#     })
#     fig_ba = px.bar(
#         ba_chart, x="Nutrient", y="Value", color="Phase", barmode="group",
#         color_discrete_map={"Before": "#e53935", "After": "#43a047"},
#         text="Value",
#         title="NPK Before vs After Chemical Fertilizer Replacement",
#         labels={"Value": "Amount (kg/ha)"},
#     )
#     fig_ba.update_traces(textposition="outside")
#     fig_ba.update_layout(height=400)
#     st.plotly_chart(fig_ba, use_container_width=True)
#     st.divider()

#     # ── NPK Profile ───────────────────────────────────────────
#     st.subheader("📈 Your Soil NPK Profile")
#     npk_fig = px.bar(
#         pd.DataFrame({"Nutrient": FEATURES, "Value": [ss.N, ss.P, ss.K]}),
#         x="Nutrient", y="Value", color="Nutrient",
#         color_discrete_sequence=["#1b5e20", "#388e3c", "#81c784"],
#         text="Value", title="Input Soil Nutrient Levels (kg/ha)",
#     )
#     npk_fig.update_traces(textposition="outside")
#     npk_fig.update_layout(showlegend=False, height=380)
#     st.plotly_chart(npk_fig, use_container_width=True)

# else:
#     st.info("👈 Enter your soil values in the sidebar and click **Predict** to generate the full advisory report.")

# # ─────────────────────────────────────────────────────────────
# # FERTILIZER DISTRIBUTION  (always visible)
# # ─────────────────────────────────────────────────────────────

# st.divider()
# st.subheader("📊 Dataset: Fertilizer Distribution")

# top10 = data["Recommended_Chemical"].value_counts().head(10).reset_index()
# top10.columns = ["Fertilizer", "Count"]
# fig_dist = px.bar(
#     top10, x="Fertilizer", y="Count", color="Count",
#     color_continuous_scale="Greens", text="Count",
#     title="Top 10 Recommended Chemical Fertilizers in Training Dataset",
# )
# fig_dist.update_traces(textposition="outside")
# fig_dist.update_layout(height=420, coloraxis_showscale=False)
# st.plotly_chart(fig_dist, use_container_width=True)

# # ─────────────────────────────────────────────────────────────
# # FARM MAP  (always visible)
# # ─────────────────────────────────────────────────────────────

# st.divider()
# st.subheader("🗺️ Farm Location Map")

# farm_map = folium.Map(location=[26.7606, 83.3732], zoom_start=7)
# folium.Marker(
#     [26.7606, 83.3732],
#     popup=folium.Popup(
#         "<b>Farm Location</b><br>Lat: 26.7606 | Lon: 83.3732", max_width=220
#     ),
#     icon=folium.Icon(color="green", icon="leaf", prefix="fa"),
# ).add_to(farm_map)
# st_folium(farm_map, width=700, height=500)

# st.caption("SoilSense · Powered by RandomForest AI & OpenWeatherMap · Built with Streamlit 🌱")



# import os
# import requests
# import streamlit as st
# import pandas as pd
# import numpy as np
# import plotly.express as px
# import plotly.graph_objects as go
# import folium
# from streamlit_folium import st_folium
# from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
# from sklearn.model_selection import train_test_split
# from sklearn.metrics import accuracy_score, classification_report
# from sklearn.preprocessing import LabelEncoder

# # ─────────────────────────────────────────────────────────────
# # PAGE CONFIG
# # ─────────────────────────────────────────────────────────────

# st.set_page_config(
#     page_title="SoilSense: Smart Fertilizer Advisory System",
#     page_icon="🌱",
#     layout="wide",
# )

# # Custom CSS
# st.markdown("""
# <style>
#     .main-header {
#         background: linear-gradient(135deg, #1b5e20, #388e3c);
#         padding: 20px 28px;
#         border-radius: 12px;
#         margin-bottom: 24px;
#     }
#     .main-header h1 { color: white; margin: 0; font-size: 2rem; }
#     .main-header p  { color: #c8e6c9; margin: 4px 0 0; font-size: 1rem; }
#     .status-banner {
#         padding: 14px 20px;
#         border-radius: 8px;
#         margin: 14px 0;
#         font-size: 18px;
#         font-weight: 600;
#     }
#     .section-title {
#         font-size: 1.2rem;
#         font-weight: 700;
#         color: #1b5e20;
#         border-bottom: 2px solid #a5d6a7;
#         padding-bottom: 6px;
#         margin: 20px 0 14px;
#     }
# </style>
# """, unsafe_allow_html=True)

# st.markdown("""
# <div class="main-header">
#     <h1>🌱 SoilSense: Smart Fertilizer Advisory System</h1>
#     <p>AI-powered soil analysis · Fertilizer recommendation · Yield prediction for Indian agriculture</p>
# </div>
# """, unsafe_allow_html=True)

# # ─────────────────────────────────────────────────────────────
# # CONSTANTS
# # ─────────────────────────────────────────────────────────────

# DATASET_FILE   = "improved_balanced_dataset_5000.xlsx"
# CITIES         = ["Gorakhpur", "Lucknow", "Varanasi", "Delhi", "Mumbai", "Patna",
#                    "Ludhiana", "Amritsar", "Chandigarh", "Jaipur", "Bhopal", "Nagpur"]
# BASELINE_YIELD = 2.5      # tons/hectare
# CHEM_REDUCTION = 0.30     # 30% chemical reduction
# OWM_API_KEY    = os.getenv("OWM_API_KEY", "")

# FEATURES = [
#     "Nitrogen", "Phosphorus", "Potassium",
#     "Temperature", "Humidity", "Rainfall",
#     "pH", "Soil_Moisture",
#     "Soil_Quality_Index", "NPK_Ratio", "Weather_Index",
# ]

# FERT_COLORS = {
#     "Urea":   "#1565c0",
#     "DAP":    "#e65100",
#     "NPK":    "#2e7d32",
#     "Potash": "#6a1b9a",
# }

# # ─────────────────────────────────────────────────────────────
# # WEATHER
# # ─────────────────────────────────────────────────────────────

# def get_weather(city: str) -> tuple:
#     try:
#         if not OWM_API_KEY:
#             raise ValueError("No API key")
#         url = (f"https://api.openweathermap.org/data/2.5/weather"
#                f"?q={city},IN&appid={OWM_API_KEY}&units=metric")
#         r = requests.get(url, timeout=5)
#         r.raise_for_status()
#         d = r.json()
#         return (
#             round(d["main"]["temp"], 1),
#             round(d["main"]["humidity"], 1),
#             round(d.get("rain", {}).get("1h", 0.0), 2),
#         )
#     except Exception:
#         return 28.0, 65.0, 0.0

# # ─────────────────────────────────────────────────────────────
# # DATA LOADING
# # ─────────────────────────────────────────────────────────────

# @st.cache_data
# def load_data() -> pd.DataFrame:
#     paths = [DATASET_FILE, f"data/{DATASET_FILE}", f"/app/{DATASET_FILE}"]
#     for p in paths:
#         if os.path.exists(p):
#             df = pd.read_excel(p)
#             df.columns = df.columns.str.strip()
#             return df
#     st.error(
#         f"❌ Dataset not found: **{DATASET_FILE}**\n\n"
#         "Place `improved_balanced_dataset_5000.xlsx` in the same folder as `app.py`."
#     )
#     st.stop()

# # ─────────────────────────────────────────────────────────────
# # MODEL TRAINING
# # ─────────────────────────────────────────────────────────────

# @st.cache_resource
# def train_models(data: pd.DataFrame):
#     X = data[FEATURES]
#     y = data["Recommended_Chemical"]

#     # Stratified split — balanced dataset guarantees ≥2 samples per class
#     X_train, X_test, y_train, y_test = train_test_split(
#         X, y, test_size=0.2, random_state=42, stratify=y
#     )

#     # Classifier
#     clf = RandomForestClassifier(
#         n_estimators=200,
#         max_depth=15,
#         min_samples_leaf=4,
#         min_samples_split=8,
#         max_features="sqrt",
#         random_state=42,
#         class_weight="balanced",
#     )
#     clf.fit(X_train, y_train)
#     y_pred   = clf.predict(X_test)
#     accuracy = accuracy_score(y_test, y_pred)
#     report   = classification_report(y_test, y_pred, output_dict=True)

#     # Yield regressor
#     reg = RandomForestRegressor(
#         n_estimators=200,
#         max_depth=15,
#         min_samples_leaf=4,
#         random_state=42,
#     )
#     reg.fit(X, data["Yield"])

#     # Feature importances
#     importances = pd.Series(clf.feature_importances_, index=FEATURES).sort_values(ascending=False)

#     return clf, reg, round(accuracy * 100, 2), report, importances

# # ─────────────────────────────────────────────────────────────
# # HELPERS
# # ─────────────────────────────────────────────────────────────

# def soil_status(score: float):
#     if score >= 150: return "Excellent 🟢", "#2e7d32"
#     if score >= 100: return "Good 🟡",      "#f9a825"
#     return              "Poor 🔴",          "#c62828"


# def compute_derived(n, p, k, temp, humidity, rainfall):
#     denom = (p + k) if (p + k) > 0 else 0.001
#     return {
#         "Soil_Quality_Index": round((n + p + k) / 3, 2),
#         "NPK_Ratio":          round(n / denom, 4),
#         "Weather_Index":      round((temp + humidity + rainfall) / 3, 2),
#     }


# def before_after_df(n, p, k):
#     r = 1 - CHEM_REDUCTION
#     return pd.DataFrame({
#         "Nutrient":    ["Nitrogen (N)", "Phosphorus (P)", "Potassium (K)"],
#         "Before (kg/ha)": [round(n,2), round(p,2), round(k,2)],
#         "After (kg/ha)":  [round(n*r,2), round(p*r,2), round(k*r,2)],
#         "Saved (kg/ha)":  [round(n*CHEM_REDUCTION,2),
#                            round(p*CHEM_REDUCTION,2),
#                            round(k*CHEM_REDUCTION,2)],
#         "Reduction":   [f"{int(CHEM_REDUCTION*100)}%"] * 3,
#     })

# # ─────────────────────────────────────────────────────────────
# # LOAD + TRAIN
# # ─────────────────────────────────────────────────────────────

# data = load_data()

# # Final safety clean
# for col in FEATURES + ["Yield"]:
#     if col in data.columns:
#         data[col] = pd.to_numeric(data[col], errors="coerce")
#         data[col] = data[col].fillna(data[col].median())

# data = data.dropna(subset=["Recommended_Chemical"]).reset_index(drop=True)
# data["Recommended_Chemical"] = data["Recommended_Chemical"].astype(str).str.strip()

# try:
#     clf, reg, accuracy, report, importances = train_models(data)
# except Exception as e:
#     st.error(f"❌ Model training failed: {e}")
#     st.stop()

# # ─────────────────────────────────────────────────────────────
# # SESSION STATE
# # ─────────────────────────────────────────────────────────────

# _defaults = dict(
#     done=False,
#     city=None, temp=None, hum=None, rain=None,
#     chemical=None, organic=None, crop_input=None,
#     soil_score=None, soil_label=None, soil_color=None,
#     yield_pred=None, yield_impr=None,
#     N=None, P=None, K=None,
#     pH=None, moisture=None,
#     derived=None, proba=None,
# )
# for k, v in _defaults.items():
#     if k not in st.session_state:
#         st.session_state[k] = v

# # ─────────────────────────────────────────────────────────────
# # HEADER METRICS  (always visible)
# # ─────────────────────────────────────────────────────────────

# m1, m2, m3, m4, m5 = st.columns(5)
# m1.metric("🎯 Model Accuracy",     f"{accuracy}%")
# m2.metric("🌾 Fertilizer Classes", data["Recommended_Chemical"].nunique())
# m3.metric("📁 Training Samples",   f"{len(data):,}")
# m4.metric("🧬 Feature Count",      len(FEATURES))
# m5.metric("🌿 Crop Types",         data["Crop"].nunique())

# st.divider()

# # ─────────────────────────────────────────────────────────────
# # SIDEBAR
# # ─────────────────────────────────────────────────────────────

# st.sidebar.markdown("## 🌾 Soil & Location Inputs")

# city       = st.sidebar.selectbox("📍 City", CITIES)
# crop_input = st.sidebar.selectbox("🌱 Crop", sorted(data["Crop"].unique()))

# st.sidebar.markdown("**Soil Nutrients (kg/ha)**")
# N = st.sidebar.slider("Nitrogen (N)",   0, 300, 120)
# P = st.sidebar.slider("Phosphorus (P)", 0, 150, 50)
# K = st.sidebar.slider("Potassium (K)",  0, 150, 40)

# st.sidebar.markdown("**Soil Properties**")
# pH       = st.sidebar.slider("pH",           4.5, 8.5, 6.8, step=0.1)
# moisture = st.sidebar.slider("Soil Moisture (%)", 10, 80, 45)

# st.sidebar.markdown("**Weather (manual override)**")
# temp_in = st.sidebar.number_input("Temperature (°C)", 10, 45, 28)
# hum_in  = st.sidebar.number_input("Humidity (%)",     20, 100, 65)
# rain_in = st.sidebar.number_input("Rainfall (mm)",    0,  500, 50)

# predict_btn = st.sidebar.button("🔍 Predict", use_container_width=True, type="primary")

# st.sidebar.divider()
# st.sidebar.markdown(
#     "**Soil Score Guide**\n"
#     "- 🟢 Excellent ≥ 150\n"
#     "- 🟡 Good ≥ 100\n"
#     "- 🔴 Poor < 100\n\n"
#     "**Yield baseline:** 2.5 t/ha"
# )

# # ─────────────────────────────────────────────────────────────
# # PREDICTION
# # ─────────────────────────────────────────────────────────────

# if predict_btn:
#     try:
#         # Fetch live weather (fallback to manual inputs)
#         live_temp, live_hum, live_rain = get_weather(city)
#         use_temp = live_temp if OWM_API_KEY else temp_in
#         use_hum  = live_hum  if OWM_API_KEY else hum_in
#         use_rain = live_rain if OWM_API_KEY else rain_in

#         derived = compute_derived(N, P, K, use_temp, use_hum, use_rain)

#         input_df = pd.DataFrame([[
#             N, P, K, use_temp, use_hum, use_rain,
#             pH, moisture,
#             derived["Soil_Quality_Index"],
#             derived["NPK_Ratio"],
#             derived["Weather_Index"],
#         ]], columns=FEATURES)

#         chemical = clf.predict(input_df)[0]
#         proba_arr = clf.predict_proba(input_df)[0]
#         proba = dict(zip(clf.classes_, np.round(proba_arr * 100, 1)))

#         org_match = data[data["Recommended_Chemical"] == chemical]["Recommended_Organic"]
#         organic   = org_match.iloc[0] if not org_match.empty else "Compost"

#         soil_score        = round(0.4*N + 0.3*P + 0.3*K, 2)
#         label, color      = soil_status(soil_score)
#         yield_pred        = round(reg.predict(input_df)[0], 2)
#         yield_pred        = float(np.clip(yield_pred, 1.0, 8.0))
#         yield_impr        = round((yield_pred - BASELINE_YIELD) / BASELINE_YIELD * 100, 1)

#         st.session_state.update(dict(
#             done=True,
#             city=city, temp=use_temp, hum=use_hum, rain=use_rain,
#             chemical=chemical, organic=organic, crop_input=crop_input,
#             soil_score=soil_score, soil_label=label, soil_color=color,
#             yield_pred=yield_pred, yield_impr=yield_impr,
#             N=N, P=P, K=K, pH=pH, moisture=moisture,
#             derived=derived, proba=proba,
#         ))

#     except Exception as e:
#         st.error(f"❌ Prediction error: {e}")

# # ─────────────────────────────────────────────────────────────
# # RESULTS
# # ─────────────────────────────────────────────────────────────

# if st.session_state.done:
#     ss = st.session_state

#     # ── WEATHER ──────────────────────────────────────────────
#     st.markdown('<div class="section-title">🌤 Current Weather Conditions</div>',
#                 unsafe_allow_html=True)
#     w1, w2, w3 = st.columns(3)
#     w1.metric("🌡 Temperature", f"{ss.temp} °C")
#     w2.metric("💧 Humidity",    f"{ss.hum} %")
#     w3.metric("🌧 Rainfall",    f"{ss.rain} mm")

#     st.divider()

#     # ── CORE PREDICTIONS ─────────────────────────────────────
#     st.markdown('<div class="section-title">✅ AI Fertilizer Recommendation</div>',
#                 unsafe_allow_html=True)
#     r1, r2, r3, r4, r5, r6 = st.columns(6)
#     r1.metric("⚗️ Chemical",       ss.chemical)
#     r2.metric("🌿 Organic",        ss.organic)
#     r3.metric("🧮 Soil Score",     ss.soil_score)
#     r4.metric("🌾 Predicted Yield",f"{ss.yield_pred} t/ha")
#     r5.metric("📈 Yield vs Base",  f"{ss.yield_impr}%",
#               delta=f"baseline {BASELINE_YIELD} t/ha")
#     r6.metric("🌱 Crop",          ss.crop_input)

#     # Soil health banner
#     st.markdown(
#         f'<div class="status-banner" '
#         f'style="background:{ss.soil_color}18;border-left:6px solid {ss.soil_color};'
#         f'color:{ss.soil_color};">'
#         f'🌱 Soil Health Status: {ss.soil_label}'
#         f'</div>',
#         unsafe_allow_html=True,
#     )

#     # Derived features callout
#     d = ss.derived
#     d1, d2, d3 = st.columns(3)
#     d1.metric("⚖️ NPK Ratio",          d["NPK_Ratio"])
#     d2.metric("🧪 Soil Quality Index",  d["Soil_Quality_Index"])
#     d3.metric("🌦 Weather Index",       d["Weather_Index"])

#     st.divider()

#     # ── CONFIDENCE CHART ─────────────────────────────────────
#     st.markdown('<div class="section-title">📊 Prediction Confidence</div>',
#                 unsafe_allow_html=True)

#     proba_df = (
#         pd.DataFrame(ss.proba.items(), columns=["Fertilizer", "Confidence (%)"])
#         .sort_values("Confidence (%)", ascending=False)
#     )
#     proba_df["Color"] = proba_df["Fertilizer"].map(FERT_COLORS).fillna("#78909c")

#     fig_conf = go.Figure(go.Bar(
#         x=proba_df["Fertilizer"],
#         y=proba_df["Confidence (%)"],
#         marker_color=proba_df["Color"].tolist(),
#         text=proba_df["Confidence (%)"].apply(lambda x: f"{x}%"),
#         textposition="outside",
#     ))
#     fig_conf.update_layout(
#         title="Model Confidence per Fertilizer Class",
#         yaxis_title="Confidence (%)",
#         yaxis_range=[0, 110],
#         height=360,
#         plot_bgcolor="white",
#         showlegend=False,
#     )
#     st.plotly_chart(fig_conf, use_container_width=True)

#     st.divider()

#     # ── BEFORE vs AFTER ──────────────────────────────────────
#     st.markdown(
#         f'<div class="section-title">🔄 Before vs After — {int(CHEM_REDUCTION*100)}% Chemical Reduction</div>',
#         unsafe_allow_html=True,
#     )

#     ba_df = before_after_df(ss.N, ss.P, ss.K)
#     st.dataframe(ba_df, use_container_width=True, hide_index=True)

#     ratio = 1 - CHEM_REDUCTION
#     ba_chart = pd.DataFrame({
#         "Nutrient": ["N", "P", "K", "N", "P", "K"],
#         "Value":    [ss.N, ss.P, ss.K,
#                      round(ss.N*ratio,2), round(ss.P*ratio,2), round(ss.K*ratio,2)],
#         "Phase":    ["Before"]*3 + ["After"]*3,
#     })
#     fig_ba = px.bar(
#         ba_chart, x="Nutrient", y="Value", color="Phase", barmode="group",
#         color_discrete_map={"Before": "#e53935", "After": "#43a047"},
#         text="Value",
#         title="NPK Before vs After Chemical Fertilizer Replacement",
#         labels={"Value": "Amount (kg/ha)"},
#     )
#     fig_ba.update_traces(textposition="outside")
#     fig_ba.update_layout(height=400, plot_bgcolor="white")
#     st.plotly_chart(fig_ba, use_container_width=True)

#     st.divider()

#     # ── NPK PROFILE ───────────────────────────────────────────
#     st.markdown('<div class="section-title">📈 Soil Nutrient Profile</div>',
#                 unsafe_allow_html=True)

#     fig_npk = px.bar(
#         pd.DataFrame({
#             "Nutrient": ["Nitrogen", "Phosphorus", "Potassium"],
#             "Value":    [ss.N, ss.P, ss.K],
#             "Optimal":  [150,  75,   75],
#         }),
#         x="Nutrient", y=["Value", "Optimal"],
#         barmode="group",
#         color_discrete_map={"Value": "#2e7d32", "Optimal": "#a5d6a7"},
#         text_auto=True,
#         title="Your Soil Nutrients vs Optimal Levels (kg/ha)",
#     )
#     fig_npk.update_layout(height=380, plot_bgcolor="white")
#     st.plotly_chart(fig_npk, use_container_width=True)

# else:
#     st.info("👈 Enter soil values in the sidebar and click **Predict** to generate your full advisory report.")

# # ─────────────────────────────────────────────────────────────
# # DATASET INSIGHTS  (always visible)
# # ─────────────────────────────────────────────────────────────

# st.divider()
# tab1, tab2, tab3 = st.tabs(["📊 Fertilizer Distribution", "🌾 Feature Importance", "📋 Dataset Sample"])

# with tab1:
#     col_a, col_b = st.columns(2)

#     with col_a:
#         dist_df = data["Recommended_Chemical"].value_counts().reset_index()
#         dist_df.columns = ["Fertilizer", "Count"]
#         dist_df["Color"] = dist_df["Fertilizer"].map(FERT_COLORS).fillna("#78909c")
#         fig_dist = go.Figure(go.Bar(
#             x=dist_df["Fertilizer"], y=dist_df["Count"],
#             marker_color=dist_df["Color"].tolist(),
#             text=dist_df["Count"], textposition="outside",
#         ))
#         fig_dist.update_layout(
#             title="Fertilizer Class Distribution (Balanced)",
#             height=380, plot_bgcolor="white", showlegend=False,
#         )
#         st.plotly_chart(fig_dist, use_container_width=True)

#     with col_b:
#         crop_dist = data["Crop"].value_counts().reset_index()
#         crop_dist.columns = ["Crop", "Count"]
#         fig_crop = px.pie(
#             crop_dist, names="Crop", values="Count",
#             title="Crop Type Distribution",
#             color_discrete_sequence=px.colors.sequential.Greens_r,
#             hole=0.35,
#         )
#         fig_crop.update_layout(height=380)
#         st.plotly_chart(fig_crop, use_container_width=True)

#     # Yield distribution
#     fig_yield = px.histogram(
#         data, x="Yield", color="Recommended_Chemical",
#         color_discrete_map=FERT_COLORS,
#         nbins=40,
#         title="Yield Distribution by Fertilizer Type (t/ha)",
#         labels={"Yield": "Yield (t/ha)", "count": "Frequency"},
#         barmode="overlay",
#         opacity=0.7,
#     )
#     fig_yield.update_layout(height=380, plot_bgcolor="white")
#     st.plotly_chart(fig_yield, use_container_width=True)

# with tab2:
#     imp_df = importances.reset_index()
#     imp_df.columns = ["Feature", "Importance"]
#     fig_imp = px.bar(
#         imp_df, x="Importance", y="Feature",
#         orientation="h",
#         color="Importance",
#         color_continuous_scale="Greens",
#         text=imp_df["Importance"].round(3),
#         title="RandomForest Feature Importances",
#     )
#     fig_imp.update_traces(textposition="outside")
#     fig_imp.update_layout(
#         height=480, plot_bgcolor="white",
#         yaxis={"categoryorder": "total ascending"},
#         coloraxis_showscale=False,
#     )
#     st.plotly_chart(fig_imp, use_container_width=True)

#     # Scatter: N vs P coloured by fertilizer
#     fig_scatter = px.scatter(
#         data.sample(1000, random_state=1),
#         x="Nitrogen", y="Phosphorus",
#         color="Recommended_Chemical",
#         color_discrete_map=FERT_COLORS,
#         opacity=0.6,
#         title="Nitrogen vs Phosphorus (sample 1000 rows)",
#         hover_data=["Crop", "Yield"],
#     )
#     fig_scatter.update_layout(height=420, plot_bgcolor="white")
#     st.plotly_chart(fig_scatter, use_container_width=True)

# with tab3:
#     st.dataframe(
#         data.sample(20, random_state=7).reset_index(drop=True),
#         use_container_width=True,
#     )
#     st.caption(f"Showing 20 random rows from {len(data):,} total training samples.")

# # ─────────────────────────────────────────────────────────────
# # FARM MAP  (always visible)
# # ─────────────────────────────────────────────────────────────

# st.divider()
# st.markdown('<div class="section-title">🗺️ Farm Location Map</div>', unsafe_allow_html=True)

# farm_map = folium.Map(location=[26.7606, 83.3732], zoom_start=6)
# folium.Marker(
#     [26.7606, 83.3732],
#     popup=folium.Popup(
#         "<b>📍 Farm Location</b><br>Lat: 26.7606 | Lon: 83.3732<br>Region: Gorakhpur, UP",
#         max_width=240,
#     ),
#     icon=folium.Icon(color="green", icon="leaf", prefix="fa"),
# ).add_to(farm_map)

# # Add city markers
# city_coords = {
#     "Gorakhpur":  [26.7606, 83.3732],
#     "Lucknow":    [26.8467, 80.9462],
#     "Varanasi":   [25.3176, 82.9739],
#     "Delhi":      [28.6139, 77.2090],
#     "Patna":      [25.5941, 85.1376],
#     "Ludhiana":   [30.9010, 75.8573],
#     "Amritsar":   [31.6340, 74.8723],
# }
# for city_name, coords in city_coords.items():
#     folium.CircleMarker(
#         coords, radius=5, color="#1b5e20", fill=True,
#         fill_color="#4caf50", fill_opacity=0.7,
#         popup=city_name,
#     ).add_to(farm_map)

# st_folium(farm_map, width=700, height=500)

# st.caption("SoilSense · Powered by RandomForest AI · Dataset: improved_balanced_dataset_5000.xlsx · Built with Streamlit 🌱")



import os
import requests
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import folium
from streamlit_folium import st_folium
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report

# ─────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="SoilSense: Smart Fertilizer Advisory System",
    page_icon="🌱",
    layout="wide",
)

st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #1b5e20, #388e3c);
        padding: 20px 28px;
        border-radius: 12px;
        margin-bottom: 24px;
    }
    .main-header h1 { color: white; margin: 0; font-size: 2rem; }
    .main-header p  { color: #c8e6c9; margin: 4px 0 0; font-size: 1rem; }
    .status-banner  {
        padding: 14px 20px; border-radius: 8px;
        margin: 14px 0; font-size: 18px; font-weight: 600;
    }
    .section-title  {
        font-size: 1.15rem; font-weight: 700; color: #1b5e20;
        border-bottom: 2px solid #a5d6a7;
        padding-bottom: 6px; margin: 20px 0 14px;
    }
    .weather-card   {
        background: #e8f5e9; border-radius: 10px;
        padding: 14px 18px; margin-bottom: 10px;
        border-left: 5px solid #2e7d32;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="main-header">
    <h1>🌱 SoilSense: Smart Fertilizer Advisory System</h1>
    <p>AI-powered soil analysis · Live weather integration · Fertilizer recommendation · Yield prediction</p>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# CONSTANTS
# ─────────────────────────────────────────────────────────────

DATASET_FILE   = "improved_balanced_dataset_5000.xlsx"
BASELINE_YIELD = 2.5
CHEM_REDUCTION = 0.30

CITIES = [
    "Gorakhpur", "Lucknow", "Varanasi", "Delhi", "Mumbai",
    "Patna", "Ludhiana", "Amritsar", "Chandigarh", "Jaipur",
    "Bhopal", "Nagpur", "Agra", "Meerut", "Kanpur",
    "Allahabad", "Dehradun", "Ranchi", "Kolkata", "Hyderabad",
]

FEATURES = [
    "Nitrogen", "Phosphorus", "Potassium",
    "Temperature", "Humidity", "Rainfall",
    "pH", "Soil_Moisture",
    "Soil_Quality_Index", "NPK_Ratio", "Weather_Index",
]

FERT_COLORS = {
    "Urea":   "#1565c0",
    "DAP":    "#e65100",
    "NPK":    "#2e7d32",
    "Potash": "#6a1b9a",
}

CITY_COORDS = {
    "Gorakhpur":  [26.7606, 83.3732],
    "Lucknow":    [26.8467, 80.9462],
    "Varanasi":   [25.3176, 82.9739],
    "Delhi":      [28.6139, 77.2090],
    "Mumbai":     [19.0760, 72.8777],
    "Patna":      [25.5941, 85.1376],
    "Ludhiana":   [30.9010, 75.8573],
    "Amritsar":   [31.6340, 74.8723],
    "Chandigarh": [30.7333, 76.7794],
    "Jaipur":     [26.9124, 75.7873],
    "Bhopal":     [23.2599, 77.4126],
    "Nagpur":     [21.1458, 79.0882],
    "Agra":       [27.1767, 78.0081],
    "Meerut":     [28.9845, 77.7064],
    "Kanpur":     [26.4499, 80.3319],
    "Allahabad":  [25.4358, 81.8463],
    "Dehradun":   [30.3165, 78.0322],
    "Ranchi":     [23.3441, 85.3096],
    "Kolkata":    [22.5726, 88.3639],
    "Hyderabad":  [17.3850, 78.4867],
}

# ─────────────────────────────────────────────────────────────
# API KEY — read from Streamlit secrets
# ─────────────────────────────────────────────────────────────

def get_api_key() -> str:
    """Read OWM_API_KEY from st.secrets, then env, then return empty string."""
    OWM_API_KEY = "cb81120197f345ae396cd0fa28c1827c"

    try:
        return st.secrets["OWM_API_KEY"]
    except Exception:
        return os.getenv("OWM_API_KEY", "")

# ─────────────────────────────────────────────────────────────
# WEATHER FETCH
# ─────────────────────────────────────────────────────────────

@st.cache_data(ttl=1800)   # cache 30 min so repeated reruns don't hammer the API
def get_weather(city: str, api_key: str) -> dict:
    """
    Fetch live weather from OpenWeatherMap.
    Returns dict with temperature, humidity, rainfall, description, icon_url.
    Falls back to None values on any error so caller can show a warning.
    """
    if not api_key:
        return {"error": "No API key configured in Streamlit secrets."}

    try:
        url = (
            f"https://api.openweathermap.org/data/2.5/weather"
            f"?q={city},IN&appid={api_key}&units=metric"
        )
        resp = requests.get(url, timeout=6)
        resp.raise_for_status()
        d = resp.json()

        return {
            "temperature":   round(d["main"]["temp"], 1),
            "feels_like":    round(d["main"]["feels_like"], 1),
            "humidity":      round(d["main"]["humidity"], 1),
            "rainfall":      round(d.get("rain", {}).get("1h", 0.0), 2),
            "description":   d["weather"][0]["description"].title(),
            "icon_url":      f"https://openweathermap.org/img/wn/{d['weather'][0]['icon']}@2x.png",
            "wind_speed":    round(d["wind"]["speed"], 1),
            "error":         None,
        }
    except requests.exceptions.HTTPError as e:
        return {"error": f"API error ({resp.status_code}): {e}"}
    except Exception as e:
        return {"error": str(e)}

# ─────────────────────────────────────────────────────────────
# DATA LOADING
# ─────────────────────────────────────────────────────────────

@st.cache_data
def load_data() -> pd.DataFrame:
    for path in [DATASET_FILE, f"data/{DATASET_FILE}"]:
        if os.path.exists(path):
            df = pd.read_excel(path)
            df.columns = df.columns.str.strip()
            return df
    st.error(
        f"❌ Dataset **{DATASET_FILE}** not found.\n\n"
        "Place `improved_balanced_dataset_5000.xlsx` in the same folder as `app.py`."
    )
    st.stop()

# ─────────────────────────────────────────────────────────────
# MODEL TRAINING
# ─────────────────────────────────────────────────────────────

@st.cache_resource
def train_models(data: pd.DataFrame):
    X = data[FEATURES]
    y = data["Recommended_Chemical"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    clf = RandomForestClassifier(
        n_estimators=200, max_depth=15,
        min_samples_leaf=4, min_samples_split=8,
        max_features="sqrt", random_state=42,
        class_weight="balanced",
    )
    clf.fit(X_train, y_train)
    accuracy = accuracy_score(y_test, clf.predict(X_test))
    report   = classification_report(y_test, clf.predict(X_test), output_dict=True)

    reg = RandomForestRegressor(
        n_estimators=200, max_depth=15,
        min_samples_leaf=4, random_state=42,
    )
    reg.fit(X, data["Yield"])

    importances = pd.Series(
        clf.feature_importances_, index=FEATURES
    ).sort_values(ascending=False)

    return clf, reg, round(accuracy * 100, 2), report, importances

# ─────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────

def soil_status(score: float):
    if score >= 150: return "Excellent 🟢", "#2e7d32"
    if score >= 100: return "Good 🟡",      "#f9a825"
    return              "Poor 🔴",          "#c62828"


def compute_derived(n, p, k, temp, humidity, rainfall):
    denom = (p + k) if (p + k) > 0 else 0.001
    return {
        "Soil_Quality_Index": round((n + p + k) / 3, 2),
        "NPK_Ratio":          round(n / denom, 4),
        "Weather_Index":      round((temp + humidity + rainfall) / 3, 2),
    }


def before_after_df(n, p, k):
    r = 1 - CHEM_REDUCTION
    return pd.DataFrame({
        "Nutrient":        ["Nitrogen (N)", "Phosphorus (P)", "Potassium (K)"],
        "Before (kg/ha)":  [round(n, 2), round(p, 2), round(k, 2)],
        "After (kg/ha)":   [round(n*r, 2), round(p*r, 2), round(k*r, 2)],
        "Saved (kg/ha)":   [round(n*CHEM_REDUCTION, 2),
                            round(p*CHEM_REDUCTION, 2),
                            round(k*CHEM_REDUCTION, 2)],
        "Reduction":       [f"{int(CHEM_REDUCTION*100)}%"] * 3,
    })

# ─────────────────────────────────────────────────────────────
# LOAD + TRAIN
# ─────────────────────────────────────────────────────────────

data = load_data()

for col in FEATURES + ["Yield"]:
    if col in data.columns:
        data[col] = pd.to_numeric(data[col], errors="coerce")
        data[col] = data[col].fillna(data[col].median())

data = data.dropna(subset=["Recommended_Chemical"]).reset_index(drop=True)
data["Recommended_Chemical"] = data["Recommended_Chemical"].astype(str).str.strip()

try:
    clf, reg, accuracy, report, importances = train_models(data)
except Exception as e:
    st.error(f"❌ Model training failed: {e}")
    st.stop()

API_KEY = get_api_key()

# ─────────────────────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────────────────────

_defaults = dict(
    done=False,
    city=None, weather=None,
    chemical=None, organic=None, crop_input=None,
    soil_score=None, soil_label=None, soil_color=None,
    yield_pred=None, yield_impr=None,
    N=None, P=None, K=None, pH=None, moisture=None,
    derived=None, proba=None,
)
for k, v in _defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ─────────────────────────────────────────────────────────────
# HEADER METRICS
# ─────────────────────────────────────────────────────────────

m1, m2, m3, m4, m5 = st.columns(5)
m1.metric("🎯 Model Accuracy",     f"{accuracy}%")
m2.metric("🌾 Fertilizer Classes", data["Recommended_Chemical"].nunique())
m3.metric("📁 Training Samples",   f"{len(data):,}")
m4.metric("🧬 ML Features",        len(FEATURES))
m5.metric("🌿 Crop Types",         data["Crop"].nunique())

st.divider()

# ─────────────────────────────────────────────────────────────
# SIDEBAR — no weather inputs, only soil + city
# ─────────────────────────────────────────────────────────────

st.sidebar.markdown("## 🌾 Soil & Location Inputs")

city       = st.sidebar.selectbox("📍 Select City", CITIES)
crop_input = st.sidebar.selectbox("🌱 Select Crop", sorted(data["Crop"].unique()))

st.sidebar.markdown("---")
st.sidebar.markdown("**🧪 Soil Nutrients (kg/ha)**")
N = st.sidebar.slider("Nitrogen (N)",   0, 300, 120)
P = st.sidebar.slider("Phosphorus (P)", 0, 150,  50)
K = st.sidebar.slider("Potassium (K)",  0, 150,  40)

st.sidebar.markdown("**🌍 Soil Properties**")
pH       = st.sidebar.slider("pH Level",         4.5, 8.5, 6.8, step=0.1)
moisture = st.sidebar.slider("Soil Moisture (%)", 10,  80,  45)

st.sidebar.markdown("---")

# Live weather preview in sidebar when city changes
if API_KEY:
    with st.sidebar:
        with st.spinner(f"Fetching weather for {city}…"):
            preview = get_weather(city, API_KEY)
        if preview.get("error"):
            st.warning(f"⚠️ Weather: {preview['error']}")
        else:
            st.markdown(
                f'<div class="weather-card">'
                f'<b>🌤 {city} — Live Weather</b><br>'
                f'🌡 {preview["temperature"]}°C &nbsp;|&nbsp; '
                f'💧 {preview["humidity"]}% &nbsp;|&nbsp; '
                f'🌧 {preview["rainfall"]} mm<br>'
                f'<small>{preview["description"]} · 💨 {preview["wind_speed"]} m/s</small>'
                f'</div>',
                unsafe_allow_html=True,
            )
else:
    st.sidebar.info(
        "ℹ️ Add **OWM_API_KEY** to Streamlit Secrets to enable live weather."
    )

predict_btn = st.sidebar.button(
    "🔍 Predict Fertilizer", use_container_width=True, type="primary"
)

st.sidebar.markdown(
    "**Soil Score Guide**\n"
    "- 🟢 Excellent ≥ 150\n"
    "- 🟡 Good ≥ 100\n"
    "- 🔴 Poor < 100"
)

# ─────────────────────────────────────────────────────────────
# PREDICTION
# ─────────────────────────────────────────────────────────────

if predict_btn:
    with st.spinner(f"🌐 Fetching live weather for **{city}**…"):
        weather = get_weather(city, API_KEY)

    if weather.get("error"):
        st.error(f"❌ Could not fetch weather: {weather['error']}")
        st.info("ℹ️ Check your `OWM_API_KEY` in Streamlit Secrets → Settings → Secrets.")
        st.stop()

    try:
        temp     = weather["temperature"]
        humidity = weather["humidity"]
        rainfall = weather["rainfall"]

        derived = compute_derived(N, P, K, temp, humidity, rainfall)

        input_df = pd.DataFrame([[
            N, P, K, temp, humidity, rainfall,
            pH, moisture,
            derived["Soil_Quality_Index"],
            derived["NPK_Ratio"],
            derived["Weather_Index"],
        ]], columns=FEATURES)

        chemical     = clf.predict(input_df)[0]
        proba_arr    = clf.predict_proba(input_df)[0]
        proba        = dict(zip(clf.classes_, np.round(proba_arr * 100, 1)))

        org_match    = data[data["Recommended_Chemical"] == chemical]["Recommended_Organic"]
        organic      = org_match.iloc[0] if not org_match.empty else "Compost"

        soil_score   = round(0.4*N + 0.3*P + 0.3*K, 2)
        label, color = soil_status(soil_score)
        yield_pred   = float(np.clip(reg.predict(input_df)[0], 1.0, 8.0))
        yield_pred   = round(yield_pred, 2)
        yield_impr   = round((yield_pred - BASELINE_YIELD) / BASELINE_YIELD * 100, 1)

        st.session_state.update(dict(
            done=True,
            city=city, weather=weather,
            chemical=chemical, organic=organic, crop_input=crop_input,
            soil_score=soil_score, soil_label=label, soil_color=color,
            yield_pred=yield_pred, yield_impr=yield_impr,
            N=N, P=P, K=K, pH=pH, moisture=moisture,
            derived=derived, proba=proba,
        ))

    except Exception as e:
        st.error(f"❌ Prediction error: {e}")

# ─────────────────────────────────────────────────────────────
# RESULTS
# ─────────────────────────────────────────────────────────────

if st.session_state.done:
    ss = st.session_state
    w  = ss.weather

    # ── LIVE WEATHER PANEL ────────────────────────────────────
    st.markdown('<div class="section-title">🌤 Live Weather Data</div>',
                unsafe_allow_html=True)

    wc1, wc2, wc3, wc4, wc5 = st.columns(5)
    wc1.metric("🌡 Temperature",   f"{w['temperature']} °C",
               delta=f"Feels {w['feels_like']} °C")
    wc2.metric("💧 Humidity",      f"{w['humidity']} %")
    wc3.metric("🌧 Rainfall",      f"{w['rainfall']} mm")
    wc4.metric("💨 Wind Speed",    f"{w['wind_speed']} m/s")
    wc5.metric("🌥 Condition",     w["description"])

    st.divider()

    # ── CORE PREDICTION METRICS ───────────────────────────────
    st.markdown('<div class="section-title">✅ AI Fertilizer Recommendation</div>',
                unsafe_allow_html=True)

    r1, r2, r3, r4, r5, r6 = st.columns(6)
    r1.metric("⚗️ Chemical Fertilizer",  ss.chemical)
    r2.metric("🌿 Organic Fertilizer",   ss.organic)
    r3.metric("🧮 Soil Health Score",    ss.soil_score)
    r4.metric("🌾 Predicted Yield",      f"{ss.yield_pred} t/ha")
    r5.metric("📈 Yield vs Baseline",    f"{ss.yield_impr}%",
              delta=f"base {BASELINE_YIELD} t/ha")
    r6.metric("🌱 Crop",                ss.crop_input)

    # Soil health banner
    st.markdown(
        f'<div class="status-banner" '
        f'style="background:{ss.soil_color}18; border-left:6px solid {ss.soil_color}; '
        f'color:{ss.soil_color};">'
        f'🌱 Soil Health Status: {ss.soil_label}'
        f'</div>',
        unsafe_allow_html=True,
    )

    # Derived features
    d1, d2, d3 = st.columns(3)
    d = ss.derived
    d1.metric("⚖️ NPK Ratio",           d["NPK_Ratio"])
    d2.metric("🧪 Soil Quality Index",   d["Soil_Quality_Index"])
    d3.metric("🌦 Weather Index",        d["Weather_Index"])

    st.divider()

    # ── CONFIDENCE CHART ──────────────────────────────────────
    st.markdown('<div class="section-title">📊 Prediction Confidence</div>',
                unsafe_allow_html=True)

    proba_df = (
        pd.DataFrame(ss.proba.items(), columns=["Fertilizer", "Confidence (%)"])
        .sort_values("Confidence (%)", ascending=False)
    )
    proba_df["Color"] = proba_df["Fertilizer"].map(FERT_COLORS).fillna("#78909c")

    fig_conf = go.Figure(go.Bar(
        x=proba_df["Fertilizer"],
        y=proba_df["Confidence (%)"],
        marker_color=proba_df["Color"].tolist(),
        text=proba_df["Confidence (%)"].apply(lambda x: f"{x}%"),
        textposition="outside",
    ))
    fig_conf.update_layout(
        title=f"Model Confidence — Recommended: <b>{ss.chemical}</b>",
        yaxis_title="Confidence (%)", yaxis_range=[0, 115],
        height=360, plot_bgcolor="white", showlegend=False,
    )
    st.plotly_chart(fig_conf, use_container_width=True)

    st.divider()

    # ── BEFORE vs AFTER ───────────────────────────────────────
    st.markdown(
        f'<div class="section-title">🔄 Before vs After — {int(CHEM_REDUCTION*100)}% Chemical Reduction</div>',
        unsafe_allow_html=True,
    )

    st.dataframe(before_after_df(ss.N, ss.P, ss.K),
                 use_container_width=True, hide_index=True)

    ratio    = 1 - CHEM_REDUCTION
    ba_chart = pd.DataFrame({
        "Nutrient": ["N", "P", "K", "N", "P", "K"],
        "Value":    [ss.N, ss.P, ss.K,
                     round(ss.N*ratio, 2),
                     round(ss.P*ratio, 2),
                     round(ss.K*ratio, 2)],
        "Phase":    ["Before"]*3 + ["After"]*3,
    })
    fig_ba = px.bar(
        ba_chart, x="Nutrient", y="Value", color="Phase", barmode="group",
        color_discrete_map={"Before": "#e53935", "After": "#43a047"},
        text="Value",
        title="NPK Before vs After Fertilizer Replacement",
        labels={"Value": "Amount (kg/ha)"},
    )
    fig_ba.update_traces(textposition="outside")
    fig_ba.update_layout(height=400, plot_bgcolor="white")
    st.plotly_chart(fig_ba, use_container_width=True)

    st.divider()

    # ── NPK PROFILE ───────────────────────────────────────────
    st.markdown('<div class="section-title">📈 Soil Nutrient Profile vs Optimal</div>',
                unsafe_allow_html=True)

    fig_npk = px.bar(
        pd.DataFrame({
            "Nutrient": ["Nitrogen", "Phosphorus", "Potassium"],
            "Your Soil":  [ss.N, ss.P, ss.K],
            "Optimal":    [150, 75, 75],
        }),
        x="Nutrient", y=["Your Soil", "Optimal"],
        barmode="group",
        color_discrete_map={"Your Soil": "#2e7d32", "Optimal": "#a5d6a7"},
        text_auto=True,
        title="Your Soil Nutrients vs Optimal Levels (kg/ha)",
    )
    fig_npk.update_layout(height=380, plot_bgcolor="white")
    st.plotly_chart(fig_npk, use_container_width=True)

else:
    st.info("👈 Select your city and soil values in the sidebar, then click **Predict Fertilizer**.")
    st.markdown(
        "Live weather (temperature, humidity, rainfall) is fetched automatically "
        "from OpenWeatherMap once you click Predict — no manual entry needed."
    )

# ─────────────────────────────────────────────────────────────
# CHEMICAL → ORGANIC FERTILIZER SWITCH IMPACT
# ─────────────────────────────────────────────────────────────

st.divider()
st.markdown(
    '<div class="section-title">♻️ Chemical to Organic Fertilizer Switch Impact on NPK Levels</div>',
    unsafe_allow_html=True,
)

# Initialize session state for this feature so graph persists across reruns
if "organic_switch_on" not in st.session_state:
    st.session_state.organic_switch_on = False
if "organic_npk_data" not in st.session_state:
    st.session_state.organic_npk_data = None

# Pull NPK values from session_state if prediction has been run,
# otherwise fall back to current sidebar slider values
try:
    chem_N = float(st.session_state.N) if st.session_state.get("N") is not None else float(N)
    chem_P = float(st.session_state.P) if st.session_state.get("P") is not None else float(P)
    chem_K = float(st.session_state.K) if st.session_state.get("K") is not None else float(K)
except Exception:
    chem_N, chem_P, chem_K = 0.0, 0.0, 0.0

# Sanitize: no NaN, no negatives
def _safe_val(v):
    try:
        v = float(v)
        if pd.isna(v) or v < 0:
            return 0.0
        return v
    except Exception:
        return 0.0

chem_N = _safe_val(chem_N)
chem_P = _safe_val(chem_P)
chem_K = _safe_val(chem_K)

# Toggle switch
organic_toggle = st.toggle(
    "🌿 Switch to Organic Fertilizer",
    value=st.session_state.organic_switch_on,
    key="organic_switch_toggle",
    help="Toggle ON to see the impact of replacing chemical fertilizer with organic (assumes 30% nutrient reduction).",
)
st.session_state.organic_switch_on = organic_toggle

# Compute organic equivalents (30% reduction → multiply by 0.7)
org_N = round(chem_N * 0.7, 2)
org_P = round(chem_P * 0.7, 2)
org_K = round(chem_K * 0.7, 2)

# Persist computed values
st.session_state.organic_npk_data = {
    "chem_N": chem_N, "chem_P": chem_P, "chem_K": chem_K,
    "org_N":  org_N,  "org_P":  org_P,  "org_K":  org_K,
}

st.markdown("### Impact of Switching from Chemical to Organic Fertilizer")

if not organic_toggle:
    # OFF → show only chemical values
    st.info("🔌 Toggle is **OFF** — currently showing only Chemical Fertilizer values. Turn it ON to compare with Organic.")

    chem_only_df = pd.DataFrame({
        "Nutrient":         ["Nitrogen", "Phosphorus", "Potassium"],
        "Chemical Input":   [chem_N, chem_P, chem_K],
    })
    st.dataframe(chem_only_df, use_container_width=True, hide_index=True)

    fig_chem_only = px.bar(
        chem_only_df, x="Nutrient", y="Chemical Input",
        text="Chemical Input",
        color="Nutrient",
        color_discrete_sequence=["#1565c0", "#e65100", "#6a1b9a"],
        title="Current Chemical Fertilizer NPK Levels (kg/ha)",
        labels={"Chemical Input": "Value (kg/ha)"},
    )
    fig_chem_only.update_traces(textposition="outside")
    fig_chem_only.update_layout(height=400, plot_bgcolor="white", showlegend=False)
    st.plotly_chart(fig_chem_only, use_container_width=True)

else:
    # ON → show full chemical vs organic comparison
    c1, c2, c3 = st.columns(3)
    c1.metric("🧪 Nitrogen (Chem → Org)",   f"{org_N} kg/ha", delta=f"-{round(chem_N - org_N, 2)} kg")
    c2.metric("🧪 Phosphorus (Chem → Org)", f"{org_P} kg/ha", delta=f"-{round(chem_P - org_P, 2)} kg")
    c3.metric("🧪 Potassium (Chem → Org)",  f"{org_K} kg/ha", delta=f"-{round(chem_K - org_K, 2)} kg")

    # Comparison table
    comparison_df = pd.DataFrame({
        "Nutrient":         ["Nitrogen", "Phosphorus", "Potassium"],
        "Chemical Input":   [chem_N, chem_P, chem_K],
        "Organic Output":   [org_N,  org_P,  org_K],
        "Reduction (kg)":   [round(chem_N - org_N, 2),
                             round(chem_P - org_P, 2),
                             round(chem_K - org_K, 2)],
        "Reduction (%)":    ["30%", "30%", "30%"],
    })
    st.dataframe(comparison_df, use_container_width=True, hide_index=True)

    # Grouped bar chart — Chemical vs Organic
    graph_df = pd.DataFrame({
        "Nutrient":      ["Nitrogen", "Phosphorus", "Potassium",
                          "Nitrogen", "Phosphorus", "Potassium"],
        "Value":         [chem_N, chem_P, chem_K, org_N, org_P, org_K],
        "Fertilizer":    ["Chemical", "Chemical", "Chemical",
                          "Organic",  "Organic",  "Organic"],
    })

    try:
        fig_switch = px.bar(
            graph_df,
            x="Nutrient", y="Value",
            color="Fertilizer", barmode="group",
            text="Value",
            color_discrete_map={"Chemical": "#e53935", "Organic": "#43a047"},
            title="NPK Level Change After Switching to Organic Fertilizer",
            labels={"Value": "Value (kg/ha)", "Nutrient": "Nutrient"},
        )
        fig_switch.update_traces(textposition="outside")
        fig_switch.update_layout(
            height=420,
            plot_bgcolor="white",
            legend_title="Fertilizer Type",
            yaxis=dict(rangemode="tozero"),
        )
        st.plotly_chart(fig_switch, use_container_width=True)
    except Exception as e:
        st.error(f"⚠️ Could not render comparison graph: {e}")

    st.success(
        "✅ **Insight:** Switching to organic fertilizer reduces NPK chemical load by **30%**, "
        "improving long-term soil health, microbial activity, and reducing groundwater contamination — "
        "while still maintaining sustainable yield levels."
    )


# ─────────────────────────────────────────────────────────────
# COST SAVINGS COMPARISON: CHEMICAL vs ORGANIC FERTILIZER
# ─────────────────────────────────────────────────────────────

st.divider()
st.markdown(
    '<div class="section-title">💰 Fertilizer Cost Savings Analysis</div>',
    unsafe_allow_html=True,
)

st.caption(
    "Compare the real-world cost of using chemical fertilizers vs switching to organic alternatives. "
    "Adjust the chemical reduction percentage to see how much you can save."
)

# ── Pricing constants (₹ per kg) ─────────────────────────────
UREA_PRICE     = 6    # Nitrogen
DAP_PRICE      = 25   # Phosphorus
POTASH_PRICE   = 20   # Potassium
ORGANIC_PRICE  = 4    # Average organic fertilizer

# ── Session state init ───────────────────────────────────────
if "cost_reduction_pct" not in st.session_state:
    st.session_state.cost_reduction_pct = 30
if "cost_analysis_data" not in st.session_state:
    st.session_state.cost_analysis_data = None

# ── Pull NPK from session_state (fallback to sidebar) ────────
def _safe_cost_val(v):
    try:
        v = float(v)
        if pd.isna(v) or v < 0:
            return 0.0
        return v
    except Exception:
        return 0.0

cost_N = _safe_cost_val(st.session_state.N if st.session_state.get("N") is not None else N)
cost_P = _safe_cost_val(st.session_state.P if st.session_state.get("P") is not None else P)
cost_K = _safe_cost_val(st.session_state.K if st.session_state.get("K") is not None else K)

# ── Reduction slider ─────────────────────────────────────────
reduction_pct = st.slider(
    "🔧 Chemical Reduction %",
    min_value=10, max_value=50,
    value=st.session_state.cost_reduction_pct,
    step=5,
    key="cost_reduction_slider",
    help="Percentage by which chemical fertilizer use is reduced when switching to organic.",
)
st.session_state.cost_reduction_pct = reduction_pct
reduction_ratio = reduction_pct / 100.0

# ── CALCULATIONS ─────────────────────────────────────────────
try:
    # Chemical cost
    chemical_cost = (cost_N * UREA_PRICE) + (cost_P * DAP_PRICE) + (cost_K * POTASH_PRICE)

    # Organic equivalents (reduction factor applied)
    organic_N = cost_N * (1 - reduction_ratio)
    organic_P = cost_P * (1 - reduction_ratio)
    organic_K = cost_K * (1 - reduction_ratio)

    organic_cost = (organic_N + organic_P + organic_K) * ORGANIC_PRICE

    # Savings (clamp to non-negative)
    savings = max(0.0, chemical_cost - organic_cost)
    savings_pct = round((savings / chemical_cost * 100), 1) if chemical_cost > 0 else 0.0

    # Sanitize all values
    chemical_cost = round(max(0.0, chemical_cost), 2)
    organic_cost  = round(max(0.0, organic_cost), 2)
    savings       = round(savings, 2)

    # Persist
    st.session_state.cost_analysis_data = {
        "chemical_cost": chemical_cost,
        "organic_cost":  organic_cost,
        "savings":       savings,
        "savings_pct":   savings_pct,
        "reduction_pct": reduction_pct,
    }

except Exception as e:
    st.error(f"⚠️ Cost calculation error: {e}")
    chemical_cost, organic_cost, savings, savings_pct = 0.0, 0.0, 0.0, 0.0

# ── METRICS DISPLAY ──────────────────────────────────────────
mc1, mc2, mc3 = st.columns(3)
mc1.metric(
    "🧪 Chemical Fertilizer Cost",
    f"₹{chemical_cost:,.2f}",
    help=f"Urea ₹{UREA_PRICE}/kg · DAP ₹{DAP_PRICE}/kg · Potash ₹{POTASH_PRICE}/kg",
)
mc2.metric(
    "🌿 Organic Fertilizer Cost",
    f"₹{organic_cost:,.2f}",
    help=f"Organic blend ₹{ORGANIC_PRICE}/kg (after {reduction_pct}% reduction)",
)
mc3.metric(
    "💵 Total Savings",
    f"₹{savings:,.2f}",
    delta=f"{savings_pct}% saved",
    help="Chemical Cost − Organic Cost",
)

# ── COMPARISON TABLE ─────────────────────────────────────────
st.markdown("#### 📋 Cost Breakdown Table")

cost_table = pd.DataFrame({
    "Type":     ["Chemical", "Organic", "Savings"],
    "Cost (₹)": [f"₹{chemical_cost:,.2f}",
                 f"₹{organic_cost:,.2f}",
                 f"₹{savings:,.2f}"],
    "Details":  [
        f"Urea: ₹{cost_N * UREA_PRICE:,.0f} | DAP: ₹{cost_P * DAP_PRICE:,.0f} | Potash: ₹{cost_K * POTASH_PRICE:,.0f}",
        f"{reduction_pct}% reduction → {round(organic_N + organic_P + organic_K, 2)} kg @ ₹{ORGANIC_PRICE}/kg",
        f"You save {savings_pct}% per hectare",
    ],
})
st.dataframe(cost_table, use_container_width=True, hide_index=True)

# ── COST COMPARISON BAR CHART ────────────────────────────────
st.markdown("#### 📊 Cost Comparison Chart")

try:
    cost_chart_df = pd.DataFrame({
        "Fertilizer Type": ["Chemical", "Organic"],
        "Cost (₹)":        [chemical_cost, organic_cost],
    })

    fig_cost = px.bar(
        cost_chart_df,
        x="Fertilizer Type",
        y="Cost (₹)",
        color="Fertilizer Type",
        text="Cost (₹)",
        color_discrete_map={"Chemical": "#e53935", "Organic": "#43a047"},
        title="Cost Comparison: Chemical vs Organic Fertilizer",
        labels={"Cost (₹)": "Cost (₹ per hectare)"},
    )
    fig_cost.update_traces(
        texttemplate="₹%{text:,.0f}",
        textposition="outside",
    )
    fig_cost.update_layout(
        height=420,
        plot_bgcolor="white",
        showlegend=False,
        yaxis=dict(rangemode="tozero"),
    )
    st.plotly_chart(fig_cost, use_container_width=True)

except Exception as e:
    st.error(f"⚠️ Could not render cost chart: {e}")

# ── INSIGHT BANNER ───────────────────────────────────────────
if savings > 0:
    st.success(
        f"✅ **Savings Insight:** By switching to organic fertilizer with a **{reduction_pct}% chemical reduction**, "
        f"you save **₹{savings:,.2f} per hectare** ({savings_pct}% reduction in fertilizer expenses). "
        f"For a 5-hectare farm, that's approximately **₹{savings * 5:,.2f}** saved per season! 🌾"
    )
else:
    st.info(
        "ℹ️ Enter your soil NPK values in the sidebar to see your personalized cost savings analysis."
    )

# ── PRICING REFERENCE ────────────────────────────────────────
with st.expander("💡 View Pricing Assumptions"):
    pricing_df = pd.DataFrame({
        "Fertilizer":  ["Urea (Nitrogen)", "DAP (Phosphorus)", "Potash (Potassium)", "Organic Blend"],
        "Price (₹/kg)": [UREA_PRICE, DAP_PRICE, POTASH_PRICE, ORGANIC_PRICE],
        "Type":         ["Chemical", "Chemical", "Chemical", "Organic"],
    })
    st.dataframe(pricing_df, use_container_width=True, hide_index=True)
    st.caption(
        "Prices are approximate Indian market rates and may vary by region, subsidy, and season. "
        "Update constants in code (`UREA_PRICE`, `DAP_PRICE`, `POTASH_PRICE`, `ORGANIC_PRICE`) for accurate local pricing."
    )

# ─────────────────────────────────────────────────────────────
# DATASET INSIGHTS  (always visible)
# ─────────────────────────────────────────────────────────────

st.divider()
tab1, tab2, tab3 = st.tabs(["📊 Distributions", "🧬 Feature Importance", "📋 Data Sample"])

with tab1:
    col_a, col_b = st.columns(2)

    with col_a:
        dist_df = data["Recommended_Chemical"].value_counts().reset_index()
        dist_df.columns = ["Fertilizer", "Count"]
        dist_df["Color"] = dist_df["Fertilizer"].map(FERT_COLORS).fillna("#78909c")
        fig_dist = go.Figure(go.Bar(
            x=dist_df["Fertilizer"], y=dist_df["Count"],
            marker_color=dist_df["Color"].tolist(),
            text=dist_df["Count"], textposition="outside",
        ))
        fig_dist.update_layout(
            title="Fertilizer Class Distribution (Balanced — 1250 each)",
            height=360, plot_bgcolor="white", showlegend=False,
        )
        st.plotly_chart(fig_dist, use_container_width=True)

    with col_b:
        crop_dist = data["Crop"].value_counts().reset_index()
        crop_dist.columns = ["Crop", "Count"]
        fig_crop = px.pie(
            crop_dist, names="Crop", values="Count",
            title="Crop Type Distribution",
            color_discrete_sequence=px.colors.sequential.Greens_r,
            hole=0.35,
        )
        fig_crop.update_layout(height=360)
        st.plotly_chart(fig_crop, use_container_width=True)

    fig_yield = px.histogram(
        data, x="Yield", color="Recommended_Chemical",
        color_discrete_map=FERT_COLORS, nbins=40,
        title="Yield Distribution by Fertilizer Type (t/ha)",
        labels={"Yield": "Yield (t/ha)", "count": "Frequency"},
        barmode="overlay", opacity=0.7,
    )
    fig_yield.update_layout(height=380, plot_bgcolor="white")
    st.plotly_chart(fig_yield, use_container_width=True)

with tab2:
    imp_df = importances.reset_index()
    imp_df.columns = ["Feature", "Importance"]
    fig_imp = px.bar(
        imp_df, x="Importance", y="Feature", orientation="h",
        color="Importance", color_continuous_scale="Greens",
        text=imp_df["Importance"].round(3),
        title="RandomForest Feature Importances",
    )
    fig_imp.update_traces(textposition="outside")
    fig_imp.update_layout(
        height=480, plot_bgcolor="white",
        yaxis={"categoryorder": "total ascending"},
        coloraxis_showscale=False,
    )
    st.plotly_chart(fig_imp, use_container_width=True)

    fig_scatter = px.scatter(
        data.sample(1000, random_state=1),
        x="Nitrogen", y="Phosphorus",
        color="Recommended_Chemical",
        color_discrete_map=FERT_COLORS,
        opacity=0.6,
        title="Nitrogen vs Phosphorus — coloured by Fertilizer (1000 sample)",
        hover_data=["Crop", "Yield"],
    )
    fig_scatter.update_layout(height=420, plot_bgcolor="white")
    st.plotly_chart(fig_scatter, use_container_width=True)

with tab3:
    st.dataframe(
        data.sample(20, random_state=7).reset_index(drop=True),
        use_container_width=True,
    )
    st.caption(f"Showing 20 random rows from {len(data):,} total training samples.")

# ─────────────────────────────────────────────────────────────
# FARM MAP
# ─────────────────────────────────────────────────────────────

st.divider()
st.markdown('<div class="section-title">🗺️ Farm Location Map</div>',
            unsafe_allow_html=True)

selected_coords = CITY_COORDS.get(
    st.session_state.city if st.session_state.city else "Gorakhpur",
    [26.7606, 83.3732],
)

farm_map = folium.Map(location=selected_coords, zoom_start=6)

# All city markers
for city_name, coords in CITY_COORDS.items():
    is_selected = (city_name == st.session_state.city)
    folium.CircleMarker(
        coords,
        radius=8 if is_selected else 5,
        color="#e65100" if is_selected else "#1b5e20",
        fill=True,
        fill_color="#ff7043" if is_selected else "#4caf50",
        fill_opacity=0.9,
        popup=folium.Popup(
            f"<b>{city_name}</b>" + (" ← Selected" if is_selected else ""),
            max_width=160,
        ),
    ).add_to(farm_map)

# Main farm pin
folium.Marker(
    selected_coords,
    popup=folium.Popup(
        f"<b>📍 {st.session_state.city or 'Farm Location'}</b><br>"
        f"Lat: {selected_coords[0]} | Lon: {selected_coords[1]}",
        max_width=220,
    ),
    icon=folium.Icon(color="green", icon="leaf", prefix="fa"),
).add_to(farm_map)

st_folium(farm_map, width=700, height=500)

st.caption(
    "SoilSense · RandomForest AI · "
    "Live Weather: OpenWeatherMap · "
    "Dataset: improved_balanced_dataset_5000.xlsx · "
    "Built with Streamlit 🌱"
)

# ─────────────────────────────────────────────────────────────
# AI CHATBOT FOR FARMER ADVICE
# ─────────────────────────────────────────────────────────────

st.divider()
st.header("🤖 AI Chatbot for Farmer Advice")
st.caption(
    "Ask me anything about fertilizers, organic farming, soil health, crop yield, "
    "weather decisions, or cost savings. I'm here to help! 🌾"
)

# ── Session state init ───────────────────────────────────────
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "chat_input_counter" not in st.session_state:
    st.session_state.chat_input_counter = 0

# ── Rule-based response engine ───────────────────────────────
def get_bot_response(user_query: str) -> str:
    """Return a rule-based AI response based on keywords in the query."""
    if not user_query or not user_query.strip():
        return "Please provide more details about your farming question."

    q = user_query.lower().strip()

    # Keyword → response mapping (order matters: most specific first)
    responses = [
        (["cost", "price", "save", "saving", "cheap", "expensive", "money", "budget"],
         "💰 Switching to organic fertilizer can reduce long-term farming costs. "
         "On average, farmers save 20–35% on fertilizer expenses while improving soil "
         "fertility year over year. Use the Cost Savings Analysis section above to "
         "calculate your personal savings."),

        (["organic", "compost", "manure", "vermicompost", "natural"],
         "🌿 Switching to organic fertilizer improves soil structure and reduces "
         "chemical dependency. Organic options like compost, vermicompost, and "
         "green manure enhance microbial activity, water retention, and long-term "
         "soil productivity. Start with a 30% replacement and gradually increase."),

        (["fertilizer", "urea", "dap", "potash", "npk", "nitrogen", "phosphorus", "potassium"],
         "⚗️ Apply fertilizer based on soil test results and avoid overuse to maintain "
         "soil health. Use the right NPK ratio for your crop, apply in split doses, "
         "and combine with organic matter for best results. Overuse leads to soil "
         "degradation and groundwater pollution."),

        (["soil", "ph", "fertility", "erosion", "microbe", "earthworm"],
         "🌱 Maintain soil health by adding organic matter and monitoring pH levels "
         "regularly. Aim for pH 6.0–7.5 for most crops. Practice crop rotation, "
         "cover cropping, and minimize tillage to preserve soil structure and "
         "beneficial microorganisms."),

        (["weather", "rain", "rainfall", "temperature", "humidity", "climate", "monsoon", "drought"],
         "🌦 Adjust irrigation and fertilizer schedules based on rainfall and "
         "temperature conditions. Avoid fertilizer application before heavy rain "
         "(causes runoff). In dry conditions, increase irrigation frequency but "
         "reduce volume. Check the live weather panel above for current data."),

        (["yield", "production", "productivity", "harvest", "growth", "crop"],
         "🌾 Use balanced nutrients and proper irrigation to increase crop yield. "
         "Key practices: timely sowing, certified seeds, integrated pest management, "
         "balanced NPK fertilization, and adequate water supply during critical "
         "growth stages (flowering & grain filling)."),

        (["irrigation", "water", "watering", "drip", "sprinkler"],
         "💧 Efficient irrigation saves water and boosts yield. Drip irrigation can "
         "reduce water use by 30–50% compared to flood irrigation. Water early "
         "morning or late evening to minimize evaporation losses."),

        (["pest", "disease", "insect", "fungus", "weed"],
         "🐛 Practice Integrated Pest Management (IPM): use resistant varieties, "
         "crop rotation, biological controls (neem, ladybugs), and chemical pesticides "
         "only as a last resort. Regular field scouting helps detect issues early."),

        (["rotation", "intercrop", "mixed", "diversif"],
         "🔄 Crop rotation breaks pest cycles and improves soil fertility. Rotate "
         "cereals (wheat, rice) with legumes (chickpea, soybean) to naturally fix "
         "nitrogen. Intercropping also maximizes land use and reduces risk."),

        (["hello", "hi", "hey", "namaste", "greetings"],
         "👋 Hello farmer! I'm your SoilSense AI assistant. Ask me about fertilizers, "
         "organic farming, soil health, weather, yield improvement, or cost savings. "
         "How can I help you today?"),

        (["thank", "thanks", "thx"],
         "🙏 You're welcome! Happy farming! Feel free to ask anything else about "
         "your soil, crops, or fertilizer choices."),
    ]

    for keywords, reply in responses:
        if any(kw in q for kw in keywords):
            return reply

    return ("🤔 Please provide more details about your farming question. "
            "I can help with topics like: **fertilizer**, **organic farming**, "
            "**soil health**, **weather decisions**, **crop yield**, or **cost savings**.")


# ── Quick-suggestion buttons ─────────────────────────────────
st.markdown("**💡 Quick Questions:**")
qcol1, qcol2, qcol3, qcol4 = st.columns(4)
suggested_q = None
if qcol1.button("🌿 About Organic", use_container_width=True):
    suggested_q = "Tell me about organic farming"
if qcol2.button("🌱 Soil Health", use_container_width=True):
    suggested_q = "How to improve soil health?"
if qcol3.button("🌾 Increase Yield", use_container_width=True):
    suggested_q = "How to increase crop yield?"
if qcol4.button("💰 Cost Savings", use_container_width=True):
    suggested_q = "How can I save costs?"

# ── Chat input form ──────────────────────────────────────────
with st.form(key="chatbot_form", clear_on_submit=True):
    user_question = st.text_input(
        "Ask your farming question:",
        placeholder="e.g., How do I improve soil fertility naturally?",
        key=f"chat_input_{st.session_state.chat_input_counter}",
    )
    send_clicked = st.form_submit_button("📤 Ask", use_container_width=False, type="primary")

# ── Process input ────────────────────────────────────────────
query_to_process = None
if send_clicked and user_question and user_question.strip():
    query_to_process = user_question.strip()
elif suggested_q:
    query_to_process = suggested_q

if query_to_process:
    try:
        bot_reply = get_bot_response(query_to_process)
        st.session_state.chat_history.append({
            "user": query_to_process,
            "bot":  bot_reply,
        })
        st.session_state.chat_input_counter += 1
    except Exception as e:
        st.error(f"⚠️ Chatbot error: {e}")

# ── Action buttons ───────────────────────────────────────────
ac1, ac2 = st.columns([1, 5])
if ac1.button("🗑 Clear Chat", use_container_width=True):
    st.session_state.chat_history = []
    st.rerun()

# ── Display chat history (newest at bottom) ──────────────────
if st.session_state.chat_history:
    st.markdown("---")
    st.markdown(f"**💬 Conversation History** ({len(st.session_state.chat_history)} messages)")

    for chat in st.session_state.chat_history:
        try:
            with st.chat_message("user", avatar="👨‍🌾"):
                st.markdown(chat["user"])
            with st.chat_message("assistant", avatar="🤖"):
                st.markdown(chat["bot"])
        except Exception:
            # Fallback for older Streamlit versions
            st.markdown(f"**👨‍🌾 You:** {chat['user']}")
            st.markdown(f"**🤖 SoilSense AI:** {chat['bot']}")
            st.markdown("---")
else:
    st.info(
        "💬 No conversation yet. Type a question above or click a quick-suggestion "
        "button to start chatting with the SoilSense AI assistant!"
    )

# ── Footer note ──────────────────────────────────────────────
st.caption(
    "🤖 SoilSense AI Chatbot · Rule-based assistant · "
    "For complex agronomy questions, consult your local agricultural extension officer."
)
