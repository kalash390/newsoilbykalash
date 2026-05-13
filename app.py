# .streamlit/secrets.toml  (on Streamlit Cloud: Settings → Secrets)
# OWM_API_KEY = "cb81120197f345ae396cd0fa28c1827c"







# code2.....................................................................................................................



# import os
# import random
# import time
# from datetime import datetime

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

# # ─────────────────────────────────────────────────────────────
# # PAGE CONFIG
# # ─────────────────────────────────────────────────────────────

# st.set_page_config(
#     page_title="SoilSense: Smart Fertilizer Advisory System",
#     page_icon="🌱",
#     layout="wide",
# )

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
#     .status-banner  {
#         padding: 14px 20px; border-radius: 8px;
#         margin: 14px 0; font-size: 18px; font-weight: 600;
#     }
#     .section-title  {
#         font-size: 1.15rem; font-weight: 700; color: #1b5e20;
#         border-bottom: 2px solid #a5d6a7;
#         padding-bottom: 6px; margin: 20px 0 14px;
#     }
#     .weather-card   {
#         background: #e8f5e9; border-radius: 10px;
#         padding: 14px 18px; margin-bottom: 10px;
#         border-left: 5px solid #2e7d32;
#     }
# </style>
# """, unsafe_allow_html=True)

# st.markdown("""
# <div class="main-header">
#     <h1>🌱 SoilSense: Smart Fertilizer Advisory System</h1>
#     <p>AI-powered soil analysis · IoT sensors · Live weather · Fertilizer recommendation · Yield prediction</p>
# </div>
# """, unsafe_allow_html=True)

# # ─────────────────────────────────────────────────────────────
# # CONSTANTS
# # ─────────────────────────────────────────────────────────────

# DATASET_FILE   = "improved_balanced_dataset_5000.xlsx"
# BASELINE_YIELD = 2.5
# CHEM_REDUCTION = 0.30

# # Pricing constants (₹ per kg)
# UREA_PRICE    = 6
# DAP_PRICE     = 25
# POTASH_PRICE  = 20
# ORGANIC_PRICE = 4

# CITIES = [
#     "Gorakhpur", "Lucknow", "Varanasi", "Delhi", "Mumbai",
#     "Patna", "Ludhiana", "Amritsar", "Chandigarh", "Jaipur",
#     "Bhopal", "Nagpur", "Agra", "Meerut", "Kanpur",
#     "Allahabad", "Dehradun", "Ranchi", "Kolkata", "Hyderabad",
# ]

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

# CITY_COORDS = {
#     "Gorakhpur":  [26.7606, 83.3732],
#     "Lucknow":    [26.8467, 80.9462],
#     "Varanasi":   [25.3176, 82.9739],
#     "Delhi":      [28.6139, 77.2090],
#     "Mumbai":     [19.0760, 72.8777],
#     "Patna":      [25.5941, 85.1376],
#     "Ludhiana":   [30.9010, 75.8573],
#     "Amritsar":   [31.6340, 74.8723],
#     "Chandigarh": [30.7333, 76.7794],
#     "Jaipur":     [26.9124, 75.7873],
#     "Bhopal":     [23.2599, 77.4126],
#     "Nagpur":     [21.1458, 79.0882],
#     "Agra":       [27.1767, 78.0081],
#     "Meerut":     [28.9845, 77.7064],
#     "Kanpur":     [26.4499, 80.3319],
#     "Allahabad":  [25.4358, 81.8463],
#     "Dehradun":   [30.3165, 78.0322],
#     "Ranchi":     [23.3441, 85.3096],
#     "Kolkata":    [22.5726, 88.3639],
#     "Hyderabad":  [17.3850, 78.4867],
# }

# # ─────────────────────────────────────────────────────────────
# # API KEY
# # ─────────────────────────────────────────────────────────────

# def get_api_key() -> str:
#     """Read OWM_API_KEY from st.secrets, env, or hardcoded fallback."""
#     try:
#         return st.secrets["OWM_API_KEY"]
#     except Exception:
#         return os.getenv("OWM_API_KEY", "cb81120197f345ae396cd0fa28c1827c")

# # ─────────────────────────────────────────────────────────────
# # WEATHER FETCH
# # ─────────────────────────────────────────────────────────────

# @st.cache_data(ttl=1800)
# def get_weather(city: str, api_key: str) -> dict:
#     if not api_key:
#         return {"error": "No API key configured."}
#     try:
#         url = (
#             f"https://api.openweathermap.org/data/2.5/weather"
#             f"?q={city},IN&appid={api_key}&units=metric"
#         )
#         resp = requests.get(url, timeout=6)
#         resp.raise_for_status()
#         d = resp.json()
#         return {
#             "temperature":   round(d["main"]["temp"], 1),
#             "feels_like":    round(d["main"]["feels_like"], 1),
#             "humidity":      round(d["main"]["humidity"], 1),
#             "rainfall":      round(d.get("rain", {}).get("1h", 0.0), 2),
#             "description":   d["weather"][0]["description"].title(),
#             "icon_url":      f"https://openweathermap.org/img/wn/{d['weather'][0]['icon']}@2x.png",
#             "wind_speed":    round(d["wind"]["speed"], 1),
#             "error":         None,
#         }
#     except Exception as e:
#         return {"error": str(e)}

# # ─────────────────────────────────────────────────────────────
# # IoT SENSOR FETCHER
# # ─────────────────────────────────────────────────────────────

# def fetch_sensor_data(source: str = "Simulated", api_url: str = "") -> dict:
#     """Fetch sensor data from chosen source. Falls back to simulation on error."""
#     try:
#         if source == "REST API" and api_url:
#             r = requests.get(api_url, timeout=5)
#             r.raise_for_status()
#             d = r.json()
#             return {
#                 "Soil_Moisture": float(d.get("soil_moisture", 45)),
#                 "Temperature":   float(d.get("temperature",  28)),
#                 "Humidity":      float(d.get("humidity",     65)),
#                 "Soil_pH":       float(d.get("soil_ph",      6.8)),
#                 "Nitrogen":      float(d.get("nitrogen",     120)),
#                 "Phosphorus":    float(d.get("phosphorus",   50)),
#                 "Potassium":     float(d.get("potassium",    40)),
#                 "timestamp":     datetime.now().strftime("%H:%M:%S"),
#                 "source":        "REST API",
#             }

#         last = st.session_state.iot_history[-1] if st.session_state.get("iot_history") else None

#         def drift(key, low, high, delta):
#             v = (last[key] if last else random.uniform(low, high)) + random.uniform(-delta, delta)
#             return round(max(low, min(high, v)), 2)

#         return {
#             "Soil_Moisture": drift("Soil_Moisture", 15, 85,  3),
#             "Temperature":   drift("Temperature",   18, 45,  1.5),
#             "Humidity":      drift("Humidity",      30, 95,  2.5),
#             "Soil_pH":       drift("Soil_pH",       5.0, 8.5, 0.15),
#             "Nitrogen":      drift("Nitrogen",      40, 250, 5),
#             "Phosphorus":    drift("Phosphorus",    20, 130, 3),
#             "Potassium":     drift("Potassium",     20, 130, 3),
#             "timestamp":     datetime.now().strftime("%H:%M:%S"),
#             "source":        "Simulated",
#         }
#     except Exception as e:
#         st.warning(f"⚠️ Sensor fetch error: {e}. Using fallback.")
#         return {
#             "Soil_Moisture": 45.0, "Temperature": 28.0, "Humidity": 65.0,
#             "Soil_pH": 6.8, "Nitrogen": 120.0, "Phosphorus": 50.0, "Potassium": 40.0,
#             "timestamp": datetime.now().strftime("%H:%M:%S"),
#             "source": "Fallback",
#         }

# # ─────────────────────────────────────────────────────────────
# # DATA LOADING & MODEL
# # ─────────────────────────────────────────────────────────────

# @st.cache_data
# def load_data() -> pd.DataFrame:
#     for path in [DATASET_FILE, f"data/{DATASET_FILE}"]:
#         if os.path.exists(path):
#             df = pd.read_excel(path)
#             df.columns = df.columns.str.strip()
#             return df
#     st.error(
#         f"❌ Dataset **{DATASET_FILE}** not found.\n\n"
#         "Place `improved_balanced_dataset_5000.xlsx` in the same folder as `app.py`."
#     )
#     st.stop()

# @st.cache_resource
# def train_models(data: pd.DataFrame):
#     X = data[FEATURES]
#     y = data["Recommended_Chemical"]

#     X_train, X_test, y_train, y_test = train_test_split(
#         X, y, test_size=0.2, random_state=42, stratify=y
#     )

#     clf = RandomForestClassifier(
#         n_estimators=200, max_depth=15,
#         min_samples_leaf=4, min_samples_split=8,
#         max_features="sqrt", random_state=42,
#         class_weight="balanced",
#     )
#     clf.fit(X_train, y_train)
#     accuracy = accuracy_score(y_test, clf.predict(X_test))
#     report   = classification_report(y_test, clf.predict(X_test), output_dict=True)

#     reg = RandomForestRegressor(
#         n_estimators=200, max_depth=15,
#         min_samples_leaf=4, random_state=42,
#     )
#     reg.fit(X, data["Yield"])

#     importances = pd.Series(
#         clf.feature_importances_, index=FEATURES
#     ).sort_values(ascending=False)

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
#         "Nutrient":        ["Nitrogen (N)", "Phosphorus (P)", "Potassium (K)"],
#         "Before (kg/ha)":  [round(n, 2), round(p, 2), round(k, 2)],
#         "After (kg/ha)":   [round(n*r, 2), round(p*r, 2), round(k*r, 2)],
#         "Saved (kg/ha)":   [round(n*CHEM_REDUCTION, 2),
#                             round(p*CHEM_REDUCTION, 2),
#                             round(k*CHEM_REDUCTION, 2)],
#         "Reduction":       [f"{int(CHEM_REDUCTION*100)}%"] * 3,
#     })

# def get_bot_response(user_query: str) -> str:
#     """
#     Smart AI Farming Assistant — uses live NPK values from session state
#     and calls OpenAI GPT-4o-mini for personalised advice.
#     Falls back gracefully if the API key is missing or the call fails.
#     """
#     if not user_query or not user_query.strip():
#         return "Please provide more details about your farming question."

#     # ── Read live NPK values from session state ──────────────────
#     N = st.session_state.get("N") or "N/A"
#     P = st.session_state.get("P") or "N/A"
#     K = st.session_state.get("K") or "N/A"

#     # ── Build system prompt with live soil context ────────────────
#     system_prompt = f"""You are an agricultural expert helping farmers make decisions based on soil nutrient levels.

# Current Soil Data:
# Nitrogen (N): {N} kg/ha
# Phosphorus (P): {P} kg/ha
# Potassium (K): {K} kg/ha

# Provide practical recommendations about:
# - Fertilizer usage
# - Organic vs chemical switch
# - Soil health improvement
# - Yield optimization
# - Cost savings

# Keep answers short, simple, and farmer-friendly. Always refer to the soil data above when relevant."""

#     # ── Try OpenAI API ────────────────────────────────────────────
#     try:
#         from openai import OpenAI

#         openai_key = st.secrets.get("OPENAI_API_KEY", "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")
#         if not openai_key:
#             raise ValueError("OPENAI_API_KEY not found in st.secrets")

#         client = OpenAI(api_key=openai_key)

#         # Build conversation history for multi-turn context
#         messages = [{"role": "system", "content": system_prompt}]
#         # Include last 6 turns of history for context
#         for turn in st.session_state.chat_history[-6:]:
#             messages.append({"role": "user",      "content": turn["user"]})
#             messages.append({"role": "assistant", "content": turn["bot"]})
#         messages.append({"role": "user", "content": user_query.strip()})

#         response = client.chat.completions.create(
#             model="gpt-4o-mini",
#             messages=messages,
#             max_tokens=400,
#             temperature=0.7,
#         )
#         return response.choices[0].message.content.strip()

#     except Exception:
#         # ── Graceful fallback: rule-based replies ─────────────────
#         q = user_query.lower().strip()
#         n_val = st.session_state.get("N")
#         p_val = st.session_state.get("P")
#         k_val = st.session_state.get("K")

#         # NPK-aware fallback replies
#         if any(kw in q for kw in ["nitrogen", "urea", "n value"]):
#             if n_val is not None and n_val < 80:
#                 return f"⚠️ Nitrogen is low ({n_val} kg/ha). Apply Urea or add compost to boost it."
#             elif n_val is not None and n_val > 180:
#                 return f"✅ Nitrogen is high ({n_val} kg/ha). Avoid adding more nitrogen fertilizer."
#             return "🌿 Nitrogen drives leafy growth. Apply Urea or DAP based on your soil test."

#         if any(kw in q for kw in ["phosphorus", "dap", "p value"]):
#             if p_val is not None and p_val < 40:
#                 return f"⚠️ Phosphorus is low ({p_val} kg/ha). Apply DAP or Single Super Phosphate."
#             elif p_val is not None and p_val > 100:
#                 return f"✅ Phosphorus is sufficient ({p_val} kg/ha). Avoid adding more phosphorus fertilizer."
#             return "🌿 Phosphorus supports root growth and flowering. Apply DAP if levels are low."

#         if any(kw in q for kw in ["potassium", "potash", "k value"]):
#             if k_val is not None and k_val < 40:
#                 return f"⚠️ Potassium is low ({k_val} kg/ha). Apply Muriate of Potash (MOP)."
#             elif k_val is not None and k_val > 100:
#                 return f"✅ Potassium is sufficient ({k_val} kg/ha). No additional potash needed."
#             return "🌿 Potassium improves drought resistance and grain quality. Apply MOP if deficient."

#         if any(kw in q for kw in ["organic", "compost", "manure", "natural"]):
#             return "🌿 Switching to organic fertilizer improves soil structure. Start with 30% replacement and increase gradually."
#         if any(kw in q for kw in ["yield", "production", "harvest", "crop"]):
#             return "🌾 Use balanced NPK nutrients and proper irrigation to maximize yield. Timely sowing and certified seeds also help."
#         if any(kw in q for kw in ["cost", "save", "money", "budget"]):
#             return "💰 Organic fertilizers can cut costs by 20–35% over time while improving long-term soil fertility."
#         if any(kw in q for kw in ["soil", "ph", "health", "fertility"]):
#             return "🌱 Maintain soil pH between 6.0–7.5. Add organic matter regularly and avoid overuse of chemical inputs."

#         return "⚠️ AI service temporarily unavailable. Please check your OpenAI API key in Streamlit secrets and try again."

# # ─────────────────────────────────────────────────────────────
# # LOAD + TRAIN
# # ─────────────────────────────────────────────────────────────

# data = load_data()

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

# API_KEY = get_api_key()

# # ─────────────────────────────────────────────────────────────
# # SESSION STATE
# # ─────────────────────────────────────────────────────────────

# _defaults = dict(
#     done=False,
#     city=None, weather=None,
#     chemical=None, organic=None, crop_input=None,
#     soil_score=None, soil_label=None, soil_color=None,
#     yield_pred=None, yield_impr=None,
#     N=None, P=None, K=None, pH=None, moisture=None,
#     derived=None, proba=None,
#     # IoT
#     iot_history=[], iot_auto_refresh=False, iot_data_source="Simulated",
#     iot_last_update=None, iot_use_for_prediction=False,
#     # NPK switch
#     organic_switch_on=False, organic_npk_data=None,
#     # Cost savings
#     cost_reduction_pct=30, cost_analysis_data=None,
#     # Chatbot
#     chat_history=[], chat_input_counter=0,
# )
# for k, v in _defaults.items():
#     if k not in st.session_state:
#         st.session_state[k] = v

# # ─────────────────────────────────────────────────────────────
# # HEADER METRICS
# # ─────────────────────────────────────────────────────────────

# m1, m2, m3, m4, m5 = st.columns(5)
# m1.metric("🎯 Model Accuracy",     f"{accuracy}%")
# m2.metric("🌾 Fertilizer Classes", data["Recommended_Chemical"].nunique())
# m3.metric("📁 Training Samples",   f"{len(data):,}")
# m4.metric("🧬 ML Features",        len(FEATURES))
# m5.metric("🌿 Crop Types",         data["Crop"].nunique())

# st.divider()

# # ═════════════════════════════════════════════════════════════
# # 📡 LIVE IoT SENSOR MONITORING (TOP OF DASHBOARD)
# # ═════════════════════════════════════════════════════════════

# st.header("📡 Live IoT Sensor Data")
# st.caption(
#     "Real-time soil & weather telemetry from ESP32 field sensors. "
#     "Currently in **simulation mode** — switch to API/Firebase for live hardware."
# )

# ctrl1, ctrl2, ctrl3, ctrl4 = st.columns([2, 2, 1.5, 1.5])

# with ctrl1:
#     data_source = st.selectbox(
#         "📡 Data Source",
#         ["Simulated", "REST API", "Firebase (coming soon)"],
#         index=0,
#     )
#     st.session_state.iot_data_source = data_source

# with ctrl2:
#     api_url = ""
#     if data_source == "REST API":
#         api_url = st.text_input("🔗 API Endpoint", placeholder="http://esp32.local/sensors")
#     else:
#         st.text_input("🔗 API Endpoint", value="N/A", disabled=True)

# with ctrl3:
#     auto_refresh = st.toggle(
#         "🔄 Auto-Refresh (5s)",
#         value=st.session_state.iot_auto_refresh,
#     )
#     st.session_state.iot_auto_refresh = auto_refresh

# with ctrl4:
#     manual_refresh = st.button("🔃 Refresh Now", use_container_width=True, type="primary")

# if manual_refresh or auto_refresh or not st.session_state.iot_history:
#     try:
#         new_reading = fetch_sensor_data(data_source, api_url)
#         st.session_state.iot_history.append(new_reading)
#         st.session_state.iot_last_update = new_reading["timestamp"]
#         if len(st.session_state.iot_history) > 50:
#             st.session_state.iot_history = st.session_state.iot_history[-50:]
#     except Exception as e:
#         st.error(f"❌ Could not fetch sensor data: {e}")

# if st.session_state.iot_history:
#     latest = st.session_state.iot_history[-1]
#     prev   = st.session_state.iot_history[-2] if len(st.session_state.iot_history) >= 2 else latest

#     st.markdown(
#         f"**🕒 Last update:** `{latest['timestamp']}` &nbsp;|&nbsp; "
#         f"**📡 Source:** `{latest['source']}` &nbsp;|&nbsp; "
#         f"**📊 Readings stored:** `{len(st.session_state.iot_history)}`"
#     )

#     s1, s2, s3, s4 = st.columns(4)
#     s1.metric("💧 Soil Moisture", f"{latest['Soil_Moisture']} %",
#               delta=round(latest['Soil_Moisture'] - prev['Soil_Moisture'], 2))
#     s2.metric("🌡 Temperature",   f"{latest['Temperature']} °C",
#               delta=round(latest['Temperature'] - prev['Temperature'], 2))
#     s3.metric("💨 Humidity",       f"{latest['Humidity']} %",
#               delta=round(latest['Humidity'] - prev['Humidity'], 2))
#     s4.metric("🧪 Soil pH",        f"{latest['Soil_pH']}",
#               delta=round(latest['Soil_pH'] - prev['Soil_pH'], 2))

#     s5, s6, s7, s8 = st.columns(4)
#     s5.metric("🟢 Nitrogen (N)",   f"{latest['Nitrogen']} kg/ha",
#               delta=round(latest['Nitrogen'] - prev['Nitrogen'], 2))
#     s6.metric("🟠 Phosphorus (P)", f"{latest['Phosphorus']} kg/ha",
#               delta=round(latest['Phosphorus'] - prev['Phosphorus'], 2))
#     s7.metric("🟣 Potassium (K)",  f"{latest['Potassium']} kg/ha",
#               delta=round(latest['Potassium'] - prev['Potassium'], 2))

#     status_color = "#2e7d32"
#     status_text = "🟢 All Systems Normal"
#     if latest['Soil_Moisture'] < 30 or latest['Temperature'] > 40:
#         status_color = "#c62828"
#         status_text = "🔴 Alerts Active"
#     elif latest['Soil_pH'] < 5.5 or latest['Soil_pH'] > 7.8:
#         status_color = "#f9a825"
#         status_text = "🟡 pH Out of Range"

#     s8.markdown(
#         f'<div style="background:{status_color}18;border-left:5px solid {status_color};'
#         f'padding:14px;border-radius:8px;text-align:center;'
#         f'color:{status_color};font-weight:700;font-size:1rem;margin-top:8px;">'
#         f'{status_text}</div>',
#         unsafe_allow_html=True,
#     )

#     # Alerts
#     alert_col1, alert_col2 = st.columns(2)
#     with alert_col1:
#         if latest['Soil_Moisture'] < 30:
#             st.warning(f"💧 **Low moisture detected — irrigation needed!** Current: {latest['Soil_Moisture']}%")
#         if latest['Soil_pH'] < 5.5:
#             st.warning(f"🧪 **Soil too acidic** — pH {latest['Soil_pH']}. Apply lime.")
#         elif latest['Soil_pH'] > 7.8:
#             st.warning(f"🧪 **Soil too alkaline** — pH {latest['Soil_pH']}. Apply gypsum/sulfur.")

#     with alert_col2:
#         if latest['Temperature'] > 40:
#             st.error(f"🌡 **High temperature risk!** Current: {latest['Temperature']}°C.")
#         if latest['Humidity'] > 90:
#             st.warning(f"💨 **Very high humidity** ({latest['Humidity']}%) — fungal disease risk.")

#     # Trend charts
#     if len(st.session_state.iot_history) >= 2:
#         st.markdown("#### 📈 Sensor Trends Over Time")
#         try:
#             hist_df = pd.DataFrame(st.session_state.iot_history)
#             chart_tab1, chart_tab2 = st.tabs(["🌡 Environmental", "🧪 Soil Nutrients"])

#             with chart_tab1:
#                 fig_env = go.Figure()
#                 fig_env.add_trace(go.Scatter(x=hist_df["timestamp"], y=hist_df["Soil_Moisture"],
#                                               mode="lines+markers", name="Soil Moisture (%)",
#                                               line=dict(color="#1565c0", width=2)))
#                 fig_env.add_trace(go.Scatter(x=hist_df["timestamp"], y=hist_df["Temperature"],
#                                               mode="lines+markers", name="Temperature (°C)",
#                                               line=dict(color="#e53935", width=2)))
#                 fig_env.add_trace(go.Scatter(x=hist_df["timestamp"], y=hist_df["Humidity"],
#                                               mode="lines+markers", name="Humidity (%)",
#                                               line=dict(color="#43a047", width=2)))
#                 fig_env.add_trace(go.Scatter(x=hist_df["timestamp"], y=hist_df["Soil_pH"]*10,
#                                               mode="lines+markers", name="Soil pH (×10)",
#                                               line=dict(color="#6a1b9a", width=2, dash="dot")))
#                 fig_env.update_layout(title="Environmental Sensor Trends", height=380,
#                                        plot_bgcolor="white", hovermode="x unified")
#                 st.plotly_chart(fig_env, use_container_width=True)

#             with chart_tab2:
#                 fig_npk = go.Figure()
#                 fig_npk.add_trace(go.Scatter(x=hist_df["timestamp"], y=hist_df["Nitrogen"],
#                                               mode="lines+markers", name="Nitrogen (N)",
#                                               line=dict(color="#2e7d32", width=2)))
#                 fig_npk.add_trace(go.Scatter(x=hist_df["timestamp"], y=hist_df["Phosphorus"],
#                                               mode="lines+markers", name="Phosphorus (P)",
#                                               line=dict(color="#e65100", width=2)))
#                 fig_npk.add_trace(go.Scatter(x=hist_df["timestamp"], y=hist_df["Potassium"],
#                                               mode="lines+markers", name="Potassium (K)",
#                                               line=dict(color="#6a1b9a", width=2)))
#                 fig_npk.update_layout(title="Soil Nutrient Trends (kg/ha)", height=380,
#                                        plot_bgcolor="white", hovermode="x unified")
#                 st.plotly_chart(fig_npk, use_container_width=True)
#         except Exception as e:
#             st.error(f"⚠️ Could not render trend chart: {e}")

#     st.markdown("---")
#     use_iot = st.checkbox(
#         "🔗 **Use live IoT sensor data for fertilizer prediction**",
#         value=st.session_state.iot_use_for_prediction,
#     )
#     st.session_state.iot_use_for_prediction = use_iot

#     if use_iot:
#         st.session_state["iot_N"]        = latest["Nitrogen"]
#         st.session_state["iot_P"]        = latest["Phosphorus"]
#         st.session_state["iot_K"]        = latest["Potassium"]
#         st.session_state["iot_pH"]       = latest["Soil_pH"]
#         st.session_state["iot_moisture"] = latest["Soil_Moisture"]
#         st.success(
#             f"✅ Live sensor data linked to AI prediction. "
#             f"N={latest['Nitrogen']} | P={latest['Phosphorus']} | K={latest['Potassium']}"
#         )

#     with st.expander("📋 View Raw Sensor History"):
#         st.dataframe(pd.DataFrame(st.session_state.iot_history[::-1]),
#                      use_container_width=True, hide_index=True)
#         if st.button("🗑 Clear Sensor History", key="clear_iot"):
#             st.session_state.iot_history = []
#             st.rerun()
# else:
#     st.info("📡 Waiting for sensor data... Click **Refresh Now** to start.")

# st.divider()

# # ─────────────────────────────────────────────────────────────
# # SIDEBAR
# # ─────────────────────────────────────────────────────────────

# st.sidebar.markdown("## 🌾 Soil & Location Inputs")

# city       = st.sidebar.selectbox("📍 Select City", CITIES)
# crop_input = st.sidebar.selectbox("🌱 Select Crop", sorted(data["Crop"].unique()))

# st.sidebar.markdown("---")
# st.sidebar.markdown("**🧪 Soil Nutrients (kg/ha)**")
# N = st.sidebar.slider("Nitrogen (N)",   0, 300, 120)
# P = st.sidebar.slider("Phosphorus (P)", 0, 150,  50)
# K = st.sidebar.slider("Potassium (K)",  0, 150,  40)

# st.sidebar.markdown("**🌍 Soil Properties**")
# pH       = st.sidebar.slider("pH Level",         4.5, 8.5, 6.8, step=0.1)
# moisture = st.sidebar.slider("Soil Moisture (%)", 10,  80,  45)

# st.sidebar.markdown("---")

# if API_KEY:
#     with st.sidebar:
#         with st.spinner(f"Fetching weather for {city}…"):
#             preview = get_weather(city, API_KEY)
#         if preview.get("error"):
#             st.warning(f"⚠️ Weather: {preview['error']}")
#         else:
#             st.markdown(
#                 f'<div class="weather-card">'
#                 f'<b>🌤 {city} — Live Weather</b><br>'
#                 f'🌡 {preview["temperature"]}°C &nbsp;|&nbsp; '
#                 f'💧 {preview["humidity"]}% &nbsp;|&nbsp; '
#                 f'🌧 {preview["rainfall"]} mm<br>'
#                 f'<small>{preview["description"]} · 💨 {preview["wind_speed"]} m/s</small>'
#                 f'</div>',
#                 unsafe_allow_html=True,
#             )
# else:
#     st.sidebar.info("ℹ️ Add **OWM_API_KEY** to Streamlit Secrets for live weather.")

# predict_btn = st.sidebar.button("🔍 Predict Fertilizer", use_container_width=True, type="primary")

# st.sidebar.markdown(
#     "**Soil Score Guide**\n"
#     "- 🟢 Excellent ≥ 150\n"
#     "- 🟡 Good ≥ 100\n"
#     "- 🔴 Poor < 100"
# )

# # ─────────────────────────────────────────────────────────────
# # PREDICTION
# # ─────────────────────────────────────────────────────────────

# if predict_btn:
#     # IoT override
#     if st.session_state.get("iot_use_for_prediction") and "iot_N" in st.session_state:
#         N        = st.session_state["iot_N"]
#         P        = st.session_state["iot_P"]
#         K        = st.session_state["iot_K"]
#         pH       = st.session_state["iot_pH"]
#         moisture = st.session_state["iot_moisture"]
#         st.info("🛰 Using live IoT sensor data for this prediction.")

#     with st.spinner(f"🌐 Fetching live weather for **{city}**…"):
#         weather = get_weather(city, API_KEY)

#     if weather.get("error"):
#         st.error(f"❌ Could not fetch weather: {weather['error']}")
#         st.stop()

#     try:
#         temp     = weather["temperature"]
#         humidity = weather["humidity"]
#         rainfall = weather["rainfall"]

#         derived = compute_derived(N, P, K, temp, humidity, rainfall)

#         input_df = pd.DataFrame([[
#             N, P, K, temp, humidity, rainfall, pH, moisture,
#             derived["Soil_Quality_Index"],
#             derived["NPK_Ratio"],
#             derived["Weather_Index"],
#         ]], columns=FEATURES)

#         chemical  = clf.predict(input_df)[0]
#         proba_arr = clf.predict_proba(input_df)[0]
#         proba     = dict(zip(clf.classes_, np.round(proba_arr * 100, 1)))

#         org_match = data[data["Recommended_Chemical"] == chemical]["Recommended_Organic"]
#         organic   = org_match.iloc[0] if not org_match.empty else "Compost"

#         soil_score   = round(0.4*N + 0.3*P + 0.3*K, 2)
#         label, color = soil_status(soil_score)
#         yield_pred   = float(np.clip(reg.predict(input_df)[0], 1.0, 8.0))
#         yield_pred   = round(yield_pred, 2)
#         yield_impr   = round((yield_pred - BASELINE_YIELD) / BASELINE_YIELD * 100, 1)

#         st.session_state.update(dict(
#             done=True,
#             city=city, weather=weather,
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
#     w  = ss.weather

#     st.markdown('<div class="section-title">🌤 Live Weather Data</div>', unsafe_allow_html=True)
#     wc1, wc2, wc3, wc4, wc5 = st.columns(5)
#     wc1.metric("🌡 Temperature",   f"{w['temperature']} °C", delta=f"Feels {w['feels_like']} °C")
#     wc2.metric("💧 Humidity",      f"{w['humidity']} %")
#     wc3.metric("🌧 Rainfall",      f"{w['rainfall']} mm")
#     wc4.metric("💨 Wind Speed",    f"{w['wind_speed']} m/s")
#     wc5.metric("🌥 Condition",     w["description"])

#     st.divider()

#     st.markdown('<div class="section-title">✅ AI Fertilizer Recommendation</div>', unsafe_allow_html=True)
#     r1, r2, r3, r4, r5, r6 = st.columns(6)
#     r1.metric("⚗️ Chemical Fertilizer",  ss.chemical)
#     r2.metric("🌿 Organic Fertilizer",   ss.organic)
#     r3.metric("🧮 Soil Health Score",    ss.soil_score)
#     r4.metric("🌾 Predicted Yield",      f"{ss.yield_pred} t/ha")
#     r5.metric("📈 Yield vs Baseline",    f"{ss.yield_impr}%", delta=f"base {BASELINE_YIELD} t/ha")
#     r6.metric("🌱 Crop",                ss.crop_input)

#     st.markdown(
#         f'<div class="status-banner" '
#         f'style="background:{ss.soil_color}18;border-left:6px solid {ss.soil_color};'
#         f'color:{ss.soil_color};">🌱 Soil Health Status: {ss.soil_label}</div>',
#         unsafe_allow_html=True,
#     )

#     d1, d2, d3 = st.columns(3)
#     d = ss.derived
#     d1.metric("⚖️ NPK Ratio",          d["NPK_Ratio"])
#     d2.metric("🧪 Soil Quality Index",  d["Soil_Quality_Index"])
#     d3.metric("🌦 Weather Index",       d["Weather_Index"])

#     st.divider()

#     # Confidence chart
#     st.markdown('<div class="section-title">📊 Prediction Confidence</div>', unsafe_allow_html=True)
#     proba_df = (pd.DataFrame(ss.proba.items(), columns=["Fertilizer", "Confidence (%)"])
#                 .sort_values("Confidence (%)", ascending=False))
#     proba_df["Color"] = proba_df["Fertilizer"].map(FERT_COLORS).fillna("#78909c")

#     fig_conf = go.Figure(go.Bar(
#         x=proba_df["Fertilizer"], y=proba_df["Confidence (%)"],
#         marker_color=proba_df["Color"].tolist(),
#         text=proba_df["Confidence (%)"].apply(lambda x: f"{x}%"),
#         textposition="outside",
#     ))
#     fig_conf.update_layout(
#         title=f"Model Confidence — Recommended: <b>{ss.chemical}</b>",
#         yaxis_title="Confidence (%)", yaxis_range=[0, 115],
#         height=360, plot_bgcolor="white", showlegend=False,
#     )
#     st.plotly_chart(fig_conf, use_container_width=True)

#     st.divider()

#     # Before vs After
#     st.markdown(
#         f'<div class="section-title">🔄 Before vs After — {int(CHEM_REDUCTION*100)}% Chemical Reduction</div>',
#         unsafe_allow_html=True,
#     )
#     st.dataframe(before_after_df(ss.N, ss.P, ss.K), use_container_width=True, hide_index=True)

#     ratio    = 1 - CHEM_REDUCTION
#     ba_chart = pd.DataFrame({
#         "Nutrient": ["N", "P", "K", "N", "P", "K"],
#         "Value":    [ss.N, ss.P, ss.K,
#                      round(ss.N*ratio, 2), round(ss.P*ratio, 2), round(ss.K*ratio, 2)],
#         "Phase":    ["Before"]*3 + ["After"]*3,
#     })
#     fig_ba = px.bar(ba_chart, x="Nutrient", y="Value", color="Phase", barmode="group",
#                     color_discrete_map={"Before": "#e53935", "After": "#43a047"},
#                     text="Value", title="NPK Before vs After Fertilizer Replacement",
#                     labels={"Value": "Amount (kg/ha)"})
#     fig_ba.update_traces(textposition="outside")
#     fig_ba.update_layout(height=400, plot_bgcolor="white")
#     st.plotly_chart(fig_ba, use_container_width=True)

#     st.divider()

#     # NPK Profile
#     st.markdown('<div class="section-title">📈 Soil Nutrient Profile vs Optimal</div>', unsafe_allow_html=True)
#     fig_npk = px.bar(
#         pd.DataFrame({
#             "Nutrient":  ["Nitrogen", "Phosphorus", "Potassium"],
#             "Your Soil": [ss.N, ss.P, ss.K],
#             "Optimal":   [150, 75, 75],
#         }),
#         x="Nutrient", y=["Your Soil", "Optimal"], barmode="group",
#         color_discrete_map={"Your Soil": "#2e7d32", "Optimal": "#a5d6a7"},
#         text_auto=True, title="Your Soil Nutrients vs Optimal Levels (kg/ha)",
#     )
#     fig_npk.update_layout(height=380, plot_bgcolor="white")
#     st.plotly_chart(fig_npk, use_container_width=True)

# else:
#     st.info("👈 Select your city and soil values in the sidebar, then click **Predict Fertilizer**.")

# # ═════════════════════════════════════════════════════════════
# # ♻️ CHEMICAL → ORGANIC FERTILIZER SWITCH IMPACT
# # ═════════════════════════════════════════════════════════════

# st.divider()
# st.markdown(
#     '<div class="section-title">♻️ Chemical to Organic Fertilizer Switch Impact on NPK Levels</div>',
#     unsafe_allow_html=True,
# )

# def _safe_val(v):
#     try:
#         v = float(v)
#         if pd.isna(v) or v < 0: return 0.0
#         return v
#     except Exception:
#         return 0.0

# chem_N = _safe_val(st.session_state.N if st.session_state.get("N") is not None else N)
# chem_P = _safe_val(st.session_state.P if st.session_state.get("P") is not None else P)
# chem_K = _safe_val(st.session_state.K if st.session_state.get("K") is not None else K)

# organic_toggle = st.toggle(
#     "🌿 Switch to Organic Fertilizer",
#     value=st.session_state.organic_switch_on,
#     key="organic_switch_toggle",
# )
# st.session_state.organic_switch_on = organic_toggle

# org_N = round(chem_N * 0.7, 2)
# org_P = round(chem_P * 0.7, 2)
# org_K = round(chem_K * 0.7, 2)

# st.session_state.organic_npk_data = {
#     "chem_N": chem_N, "chem_P": chem_P, "chem_K": chem_K,
#     "org_N": org_N,   "org_P": org_P,   "org_K": org_K,
# }

# if not organic_toggle:
#     st.info("🔌 Toggle is **OFF** — showing only Chemical values.")
#     chem_only_df = pd.DataFrame({
#         "Nutrient":       ["Nitrogen", "Phosphorus", "Potassium"],
#         "Chemical Input": [chem_N, chem_P, chem_K],
#     })
#     st.dataframe(chem_only_df, use_container_width=True, hide_index=True)

#     fig_chem_only = px.bar(
#         chem_only_df, x="Nutrient", y="Chemical Input", text="Chemical Input",
#         color="Nutrient", color_discrete_sequence=["#1565c0", "#e65100", "#6a1b9a"],
#         title="Current Chemical Fertilizer NPK Levels (kg/ha)",
#     )
#     fig_chem_only.update_traces(textposition="outside")
#     fig_chem_only.update_layout(height=400, plot_bgcolor="white", showlegend=False)
#     st.plotly_chart(fig_chem_only, use_container_width=True)
# else:
#     c1, c2, c3 = st.columns(3)
#     c1.metric("🧪 Nitrogen (Chem → Org)",   f"{org_N} kg/ha", delta=f"-{round(chem_N - org_N, 2)} kg")
#     c2.metric("🧪 Phosphorus (Chem → Org)", f"{org_P} kg/ha", delta=f"-{round(chem_P - org_P, 2)} kg")
#     c3.metric("🧪 Potassium (Chem → Org)",  f"{org_K} kg/ha", delta=f"-{round(chem_K - org_K, 2)} kg")

#     comparison_df = pd.DataFrame({
#         "Nutrient":       ["Nitrogen", "Phosphorus", "Potassium"],
#         "Chemical Input": [chem_N, chem_P, chem_K],
#         "Organic Output": [org_N, org_P, org_K],
#         "Reduction (kg)": [round(chem_N - org_N, 2), round(chem_P - org_P, 2), round(chem_K - org_K, 2)],
#         "Reduction (%)":  ["30%", "30%", "30%"],
#     })
#     st.dataframe(comparison_df, use_container_width=True, hide_index=True)

#     graph_df = pd.DataFrame({
#         "Nutrient":   ["Nitrogen", "Phosphorus", "Potassium",
#                        "Nitrogen", "Phosphorus", "Potassium"],
#         "Value":      [chem_N, chem_P, chem_K, org_N, org_P, org_K],
#         "Fertilizer": ["Chemical"]*3 + ["Organic"]*3,
#     })

#     try:
#         fig_switch = px.bar(
#             graph_df, x="Nutrient", y="Value", color="Fertilizer", barmode="group",
#             text="Value",
#             color_discrete_map={"Chemical": "#e53935", "Organic": "#43a047"},
#             title="NPK Level Change After Switching to Organic Fertilizer",
#             labels={"Value": "Value (kg/ha)"},
#         )
#         fig_switch.update_traces(textposition="outside")
#         fig_switch.update_layout(height=420, plot_bgcolor="white",
#                                   legend_title="Fertilizer Type",
#                                   yaxis=dict(rangemode="tozero"))
#         st.plotly_chart(fig_switch, use_container_width=True)
#     except Exception as e:
#         st.error(f"⚠️ Could not render comparison graph: {e}")

#     st.success(
#         "✅ **Insight:** Switching to organic fertilizer reduces NPK chemical load by **30%**, "
#         "improving long-term soil health, microbial activity, and reducing groundwater contamination."
#     )

# # ═════════════════════════════════════════════════════════════
# # 💰 COST SAVINGS COMPARISON
# # ═════════════════════════════════════════════════════════════

# st.divider()
# st.markdown('<div class="section-title">💰 Fertilizer Cost Savings Analysis</div>', unsafe_allow_html=True)

# cost_N = _safe_val(st.session_state.N if st.session_state.get("N") is not None else N)
# cost_P = _safe_val(st.session_state.P if st.session_state.get("P") is not None else P)
# cost_K = _safe_val(st.session_state.K if st.session_state.get("K") is not None else K)

# reduction_pct = st.slider(
#     "🔧 Chemical Reduction %",
#     min_value=10, max_value=50,
#     value=st.session_state.cost_reduction_pct,
#     step=5, key="cost_reduction_slider",
# )
# st.session_state.cost_reduction_pct = reduction_pct
# reduction_ratio = reduction_pct / 100.0

# try:
#     chemical_cost = (cost_N * UREA_PRICE) + (cost_P * DAP_PRICE) + (cost_K * POTASH_PRICE)
#     organic_N = cost_N * (1 - reduction_ratio)
#     organic_P = cost_P * (1 - reduction_ratio)
#     organic_K = cost_K * (1 - reduction_ratio)
#     organic_cost = (organic_N + organic_P + organic_K) * ORGANIC_PRICE
#     savings      = max(0.0, chemical_cost - organic_cost)
#     savings_pct  = round((savings / chemical_cost * 100), 1) if chemical_cost > 0 else 0.0

#     chemical_cost = round(max(0.0, chemical_cost), 2)
#     organic_cost  = round(max(0.0, organic_cost), 2)
#     savings       = round(savings, 2)

#     st.session_state.cost_analysis_data = {
#         "chemical_cost": chemical_cost, "organic_cost": organic_cost,
#         "savings": savings, "savings_pct": savings_pct,
#         "reduction_pct": reduction_pct,
#     }
# except Exception as e:
#     st.error(f"⚠️ Cost calculation error: {e}")
#     chemical_cost, organic_cost, savings, savings_pct = 0.0, 0.0, 0.0, 0.0

# mc1, mc2, mc3 = st.columns(3)
# mc1.metric("🧪 Chemical Fertilizer Cost", f"₹{chemical_cost:,.2f}")
# mc2.metric("🌿 Organic Fertilizer Cost",  f"₹{organic_cost:,.2f}")
# mc3.metric("💵 Total Savings",            f"₹{savings:,.2f}", delta=f"{savings_pct}% saved")

# st.markdown("#### 📋 Cost Breakdown Table")
# cost_table = pd.DataFrame({
#     "Type":     ["Chemical", "Organic", "Savings"],
#     "Cost (₹)": [f"₹{chemical_cost:,.2f}", f"₹{organic_cost:,.2f}", f"₹{savings:,.2f}"],
#     "Details":  [
#         f"Urea: ₹{cost_N*UREA_PRICE:,.0f} | DAP: ₹{cost_P*DAP_PRICE:,.0f} | Potash: ₹{cost_K*POTASH_PRICE:,.0f}",
#         f"{reduction_pct}% reduction → {round(organic_N+organic_P+organic_K, 2)} kg @ ₹{ORGANIC_PRICE}/kg",
#         f"You save {savings_pct}% per hectare",
#     ],
# })
# st.dataframe(cost_table, use_container_width=True, hide_index=True)

# st.markdown("#### 📊 Cost Comparison Chart")
# try:
#     cost_chart_df = pd.DataFrame({
#         "Fertilizer Type": ["Chemical", "Organic"],
#         "Cost (₹)":        [chemical_cost, organic_cost],
#     })
#     fig_cost = px.bar(
#         cost_chart_df, x="Fertilizer Type", y="Cost (₹)",
#         color="Fertilizer Type", text="Cost (₹)",
#         color_discrete_map={"Chemical": "#e53935", "Organic": "#43a047"},
#         title="Cost Comparison: Chemical vs Organic Fertilizer",
#         labels={"Cost (₹)": "Cost (₹ per hectare)"},
#     )
#     fig_cost.update_traces(texttemplate="₹%{text:,.0f}", textposition="outside")
#     fig_cost.update_layout(height=420, plot_bgcolor="white", showlegend=False,
#                             yaxis=dict(rangemode="tozero"))
#     st.plotly_chart(fig_cost, use_container_width=True)
# except Exception as e:
#     st.error(f"⚠️ Could not render cost chart: {e}")

# if savings > 0:
#     st.success(
#         f"✅ **Savings Insight:** By switching to organic fertilizer with **{reduction_pct}% chemical reduction**, "
#         f"you save **₹{savings:,.2f} per hectare** ({savings_pct}%). "
#         f"For a 5-hectare farm: **₹{savings*5:,.2f}** saved per season! 🌾"
#     )

# with st.expander("💡 View Pricing Assumptions"):
#     pricing_df = pd.DataFrame({
#         "Fertilizer":   ["Urea (Nitrogen)", "DAP (Phosphorus)", "Potash (Potassium)", "Organic Blend"],
#         "Price (₹/kg)": [UREA_PRICE, DAP_PRICE, POTASH_PRICE, ORGANIC_PRICE],
#         "Type":         ["Chemical", "Chemical", "Chemical", "Organic"],
#     })
#     st.dataframe(pricing_df, use_container_width=True, hide_index=True)

# # ═════════════════════════════════════════════════════════════
# # 📊 DATASET INSIGHTS
# # ═════════════════════════════════════════════════════════════

# st.divider()
# tab1, tab2, tab3 = st.tabs(["📊 Distributions", "🧬 Feature Importance", "📋 Data Sample"])

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
#         fig_dist.update_layout(title="Fertilizer Class Distribution",
#                                 height=360, plot_bgcolor="white", showlegend=False)
#         st.plotly_chart(fig_dist, use_container_width=True)

#     with col_b:
#         crop_dist = data["Crop"].value_counts().reset_index()
#         crop_dist.columns = ["Crop", "Count"]
#         fig_crop = px.pie(crop_dist, names="Crop", values="Count",
#                           title="Crop Type Distribution",
#                           color_discrete_sequence=px.colors.sequential.Greens_r, hole=0.35)
#         fig_crop.update_layout(height=360)
#         st.plotly_chart(fig_crop, use_container_width=True)

#     fig_yield = px.histogram(
#         data, x="Yield", color="Recommended_Chemical",
#         color_discrete_map=FERT_COLORS, nbins=40,
#         title="Yield Distribution by Fertilizer Type (t/ha)",
#         barmode="overlay", opacity=0.7,
#     )
#     fig_yield.update_layout(height=380, plot_bgcolor="white")
#     st.plotly_chart(fig_yield, use_container_width=True)

# with tab2:
#     imp_df = importances.reset_index()
#     imp_df.columns = ["Feature", "Importance"]
#     fig_imp = px.bar(
#         imp_df, x="Importance", y="Feature", orientation="h",
#         color="Importance", color_continuous_scale="Greens",
#         text=imp_df["Importance"].round(3),
#         title="RandomForest Feature Importances",
#     )
#     fig_imp.update_traces(textposition="outside")
#     fig_imp.update_layout(height=480, plot_bgcolor="white",
#                            yaxis={"categoryorder": "total ascending"},
#                            coloraxis_showscale=False)
#     st.plotly_chart(fig_imp, use_container_width=True)

#     fig_scatter = px.scatter(
#         data.sample(1000, random_state=1),
#         x="Nitrogen", y="Phosphorus",
#         color="Recommended_Chemical", color_discrete_map=FERT_COLORS,
#         opacity=0.6,
#         title="Nitrogen vs Phosphorus by Fertilizer (1000 sample)",
#         hover_data=["Crop", "Yield"],
#     )
#     fig_scatter.update_layout(height=420, plot_bgcolor="white")
#     st.plotly_chart(fig_scatter, use_container_width=True)

# with tab3:
#     st.dataframe(data.sample(20, random_state=7).reset_index(drop=True),
#                  use_container_width=True)
#     st.caption(f"Showing 20 random rows from {len(data):,} samples.")

# # ═════════════════════════════════════════════════════════════
# # 🗺️ FARM MAP
# # ═════════════════════════════════════════════════════════════

# st.divider()
# st.markdown('<div class="section-title">🗺️ Farm Location Map</div>', unsafe_allow_html=True)

# selected_coords = CITY_COORDS.get(
#     st.session_state.city if st.session_state.city else "Gorakhpur",
#     [26.7606, 83.3732],
# )

# farm_map = folium.Map(location=selected_coords, zoom_start=6)

# for city_name, coords in CITY_COORDS.items():
#     is_selected = (city_name == st.session_state.city)
#     folium.CircleMarker(
#         coords,
#         radius=8 if is_selected else 5,
#         color="#e65100" if is_selected else "#1b5e20",
#         fill=True,
#         fill_color="#ff7043" if is_selected else "#4caf50",
#         fill_opacity=0.9,
#         popup=folium.Popup(
#             f"<b>{city_name}</b>" + (" ← Selected" if is_selected else ""),
#             max_width=160,
#         ),
#     ).add_to(farm_map)

# folium.Marker(
#     selected_coords,
#     popup=folium.Popup(
#         f"<b>📍 {st.session_state.city or 'Farm Location'}</b><br>"
#         f"Lat: {selected_coords[0]} | Lon: {selected_coords[1]}",
#         max_width=220,
#     ),
#     icon=folium.Icon(color="green", icon="leaf", prefix="fa"),
# ).add_to(farm_map)

# st_folium(farm_map, width=700, height=500)


# # ═════════════════════════════════════════════════════════════
# # 🩺 SOIL HEALTH DIAGNOSTIC REPORT (Medical-Style PDF)
# # ═════════════════════════════════════════════════════════════

# from io import BytesIO
# from datetime import datetime as _dt

# try:
#     from reportlab.lib.pagesizes import A4
#     from reportlab.lib import colors
#     from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
#     from reportlab.lib.units import cm, mm
#     from reportlab.lib.enums import TA_CENTER, TA_LEFT
#     from reportlab.platypus import (
#         SimpleDocTemplate, Table, TableStyle, Paragraph,
#         Spacer, HRFlowable, PageBreak,
#     )
#     REPORTLAB_AVAILABLE = True
# except ImportError:
#     REPORTLAB_AVAILABLE = False


# # ── Normal range definitions ─────────────────────────────────
# NORMAL_RANGES = {
#     "Nitrogen":      (50, 150, "kg/ha"),
#     "Phosphorus":    (20, 60,  "kg/ha"),
#     "Potassium":     (10, 40,  "kg/ha"),
#     "Soil Moisture": (30, 60,  "%"),
#     "Temperature":   (20, 35,  "°C"),
#     "Soil pH":       (6.0, 7.5, ""),
# }


# def _check_status(value, low, high):
#     """Return ('Normal'|'Low'|'High', color)."""
#     try:
#         v = float(value)
#         if v < low:    return "Low",    colors.HexColor("#1565c0")
#         if v > high:   return "High",   colors.HexColor("#c62828")
#         return            "Normal", colors.HexColor("#2e7d32")
#     except Exception:
#         return "N/A", colors.grey


# def _interpret_health(score):
#     """Return health interpretation based on score."""
#     try:
#         s = float(score)
#         if s >= 80: return "Healthy Soil",  colors.HexColor("#2e7d32")
#         if s >= 60: return "Moderate Soil", colors.HexColor("#f9a825")
#         return         "Poor Soil",     colors.HexColor("#c62828")
#     except Exception:
#         return "N/A", colors.grey


# def generate_pdf_report(report_data: dict) -> bytes:
#     """Generate medical-style soil health PDF and return bytes."""
#     buffer = BytesIO()
#     doc = SimpleDocTemplate(
#         buffer, pagesize=A4,
#         rightMargin=1.5*cm, leftMargin=1.5*cm,
#         topMargin=1.2*cm, bottomMargin=1.2*cm,
#         title="Soil Health Diagnostic Report",
#     )

#     styles = getSampleStyleSheet()
#     title_style = ParagraphStyle(
#         "Title", parent=styles["Heading1"], fontSize=20,
#         textColor=colors.HexColor("#1b5e20"), alignment=TA_CENTER,
#         spaceAfter=4, fontName="Helvetica-Bold",
#     )
#     subtitle_style = ParagraphStyle(
#         "Subtitle", parent=styles["Heading2"], fontSize=13,
#         textColor=colors.HexColor("#388e3c"), alignment=TA_CENTER,
#         spaceAfter=6, fontName="Helvetica-Bold",
#     )
#     section_style = ParagraphStyle(
#         "Section", parent=styles["Heading3"], fontSize=12,
#         textColor=colors.white,
#         backColor=colors.HexColor("#1b5e20"),
#         alignment=TA_LEFT, spaceBefore=8, spaceAfter=6,
#         leftIndent=4, borderPadding=4,
#         fontName="Helvetica-Bold",
#     )
#     normal_style = ParagraphStyle(
#         "Normal2", parent=styles["Normal"], fontSize=10,
#         fontName="Helvetica",
#     )
#     footer_style = ParagraphStyle(
#         "Footer", parent=styles["Normal"], fontSize=8,
#         textColor=colors.grey, alignment=TA_CENTER,
#     )

#     story = []

#     # ── HEADER ──────────────────────────────────────────────
#     story.append(Paragraph("🌱 SoilSense Smart Agriculture Laboratory", title_style))
#     story.append(Paragraph("Soil Health Diagnostic Report", subtitle_style))
#     story.append(HRFlowable(width="100%", thickness=2,
#                             color=colors.HexColor("#1b5e20"), spaceAfter=8))

#     # ── PATIENT-LIKE INFO TABLE ─────────────────────────────
#     info_data = [
#         ["Farmer Name:",   report_data.get("farmer_name", "N/A"),
#          "Date:",          report_data.get("date", "N/A")],
#         ["Farm Location:", report_data.get("location", "N/A"),
#          "Time:",          report_data.get("time", "N/A")],
#         ["Crop:",          report_data.get("crop", "N/A"),
#          "Input Mode:",    report_data.get("input_mode", "Manual")],
#         ["Report ID:",     report_data.get("report_id", "N/A"),
#          "Lab:",           "SoilSense AI Lab"],
#     ]
#     info_table = Table(info_data, colWidths=[3.2*cm, 5.5*cm, 3*cm, 5.5*cm])
#     info_table.setStyle(TableStyle([
#         ("FONTNAME",   (0, 0), (-1, -1), "Helvetica"),
#         ("FONTNAME",   (0, 0), (0, -1),  "Helvetica-Bold"),
#         ("FONTNAME",   (2, 0), (2, -1),  "Helvetica-Bold"),
#         ("FONTSIZE",   (0, 0), (-1, -1), 10),
#         ("TEXTCOLOR",  (0, 0), (0, -1),  colors.HexColor("#1b5e20")),
#         ("TEXTCOLOR",  (2, 0), (2, -1),  colors.HexColor("#1b5e20")),
#         ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f1f8e9")),
#         ("BOX",        (0, 0), (-1, -1), 1, colors.HexColor("#1b5e20")),
#         ("INNERGRID",  (0, 0), (-1, -1), 0.3, colors.HexColor("#a5d6a7")),
#         ("VALIGN",     (0, 0), (-1, -1), "MIDDLE"),
#         ("LEFTPADDING",(0, 0), (-1, -1), 6),
#         ("TOPPADDING", (0, 0), (-1, -1), 5),
#         ("BOTTOMPADDING",(0, 0), (-1, -1), 5),
#     ]))
#     story.append(info_table)
#     story.append(Spacer(1, 10))

#     # ── TEST RESULTS TABLE ──────────────────────────────────
#     story.append(Paragraph("&nbsp;&nbsp;LABORATORY TEST RESULTS", section_style))

#     test_header = ["Parameter", "Observed Value", "Normal Range", "Unit", "Status"]
#     test_rows   = [test_header]

#     parameters = [
#         ("Nitrogen",      report_data.get("N")),
#         ("Phosphorus",    report_data.get("P")),
#         ("Potassium",     report_data.get("K")),
#         ("Soil Moisture", report_data.get("moisture")),
#         ("Temperature",   report_data.get("temperature")),
#         ("Soil pH",       report_data.get("pH")),
#     ]

#     status_colors_for_table = []
#     for idx, (param, val) in enumerate(parameters, start=1):
#         low, high, unit = NORMAL_RANGES[param]
#         status, status_color = _check_status(val, low, high)
#         try:
#             display_val = f"{float(val):.2f}" if val is not None else "N/A"
#         except Exception:
#             display_val = "N/A"
#         test_rows.append([
#             param,
#             display_val,
#             f"{low} - {high}",
#             unit,
#             status,
#         ])
#         status_colors_for_table.append((idx, status_color))

#     test_table = Table(test_rows, colWidths=[4.2*cm, 3.5*cm, 3.5*cm, 2*cm, 3.5*cm])
#     style_cmds = [
#         ("BACKGROUND",  (0, 0), (-1, 0), colors.HexColor("#1b5e50")),
#         ("TEXTCOLOR",   (0, 0), (-1, 0), colors.white),
#         ("FONTNAME",    (0, 0), (-1, 0), "Helvetica-Bold"),
#         ("FONTSIZE",    (0, 0), (-1, 0), 10),
#         ("FONTSIZE",    (0, 1), (-1, -1), 9.5),
#         ("ALIGN",       (0, 0), (-1, -1), "CENTER"),
#         ("ALIGN",       (0, 1), (0, -1),  "LEFT"),
#         ("VALIGN",      (0, 0), (-1, -1), "MIDDLE"),
#         ("FONTNAME",    (0, 1), (0, -1),  "Helvetica-Bold"),
#         ("FONTNAME",    (4, 1), (4, -1),  "Helvetica-Bold"),
#         ("BOX",         (0, 0), (-1, -1), 1.2, colors.HexColor("#1b5e50")),
#         ("INNERGRID",   (0, 0), (-1, -1), 0.4, colors.grey),
#         ("ROWBACKGROUNDS", (0, 1), (-1, -1),
#             [colors.white, colors.HexColor("#f1f8e9")]),
#         ("LEFTPADDING", (0, 0), (-1, -1), 6),
#         ("RIGHTPADDING",(0, 0), (-1, -1), 6),
#         ("TOPPADDING",  (0, 0), (-1, -1), 6),
#         ("BOTTOMPADDING",(0, 0), (-1, -1), 6),
#     ]
#     # Add status color to status column per row
#     for row_idx, color in status_colors_for_table:
#         style_cmds.append(("TEXTCOLOR", (4, row_idx), (4, row_idx), color))
#     test_table.setStyle(TableStyle(style_cmds))
#     story.append(test_table)
#     story.append(Spacer(1, 12))

#     # ── FERTILIZER RECOMMENDATION ───────────────────────────
#     story.append(Paragraph("&nbsp;&nbsp;FERTILIZER RECOMMENDATION", section_style))
#     fert_data = [
#         ["Recommendation Type", "Recommended Product"],
#         ["Chemical Fertilizer", report_data.get("chemical", "N/A")],
#         ["Organic Fertilizer",  report_data.get("organic", "N/A")],
#     ]
#     fert_table = Table(fert_data, colWidths=[7*cm, 9.7*cm])
#     fert_table.setStyle(TableStyle([
#         ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#388e3c")),
#         ("TEXTCOLOR",  (0, 0), (-1, 0), colors.white),
#         ("FONTNAME",   (0, 0), (-1, 0), "Helvetica-Bold"),
#         ("FONTNAME",   (0, 1), (0, -1), "Helvetica-Bold"),
#         ("FONTSIZE",   (0, 0), (-1, -1), 10),
#         ("ALIGN",      (0, 0), (-1, -1), "LEFT"),
#         ("VALIGN",     (0, 0), (-1, -1), "MIDDLE"),
#         ("BOX",        (0, 0), (-1, -1), 1, colors.HexColor("#1b5e20")),
#         ("INNERGRID",  (0, 0), (-1, -1), 0.4, colors.grey),
#         ("LEFTPADDING",(0, 0), (-1, -1), 8),
#         ("TOPPADDING", (0, 0), (-1, -1), 6),
#         ("BOTTOMPADDING",(0, 0), (-1, -1), 6),
#         ("ROWBACKGROUNDS", (0, 1), (-1, -1),
#             [colors.white, colors.HexColor("#f1f8e9")]),
#     ]))
#     story.append(fert_table)
#     story.append(Spacer(1, 12))

#     # ── SOIL HEALTH SCORE ───────────────────────────────────
#     story.append(Paragraph("&nbsp;&nbsp;SOIL HEALTH SCORE", section_style))
#     score = report_data.get("soil_score", 0)
#     interp, interp_color = _interpret_health(score)
#     score_data = [
#         ["Soil Health Score", "Interpretation", "Status"],
#         [f"{score} / 200", interp,
#          "✓ Within Acceptable Range" if interp == "Healthy Soil"
#             else ("⚠ Needs Improvement" if interp == "Moderate Soil"
#                   else "✗ Critical Action Needed")],
#     ]
#     score_table = Table(score_data, colWidths=[5*cm, 5*cm, 6.7*cm])
#     score_table.setStyle(TableStyle([
#         ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#388e3c")),
#         ("TEXTCOLOR",  (0, 0), (-1, 0), colors.white),
#         ("FONTNAME",   (0, 0), (-1, 0), "Helvetica-Bold"),
#         ("FONTSIZE",   (0, 0), (-1, -1), 10),
#         ("ALIGN",      (0, 0), (-1, -1), "CENTER"),
#         ("VALIGN",     (0, 0), (-1, -1), "MIDDLE"),
#         ("FONTNAME",   (0, 1), (-1, 1), "Helvetica-Bold"),
#         ("TEXTCOLOR",  (1, 1), (1, 1), interp_color),
#         ("BOX",        (0, 0), (-1, -1), 1, colors.HexColor("#1b5e20")),
#         ("INNERGRID",  (0, 0), (-1, -1), 0.4, colors.grey),
#         ("BACKGROUND", (0, 1), (-1, 1), colors.HexColor("#f1f8e9")),
#         ("TOPPADDING", (0, 0), (-1, -1), 8),
#         ("BOTTOMPADDING",(0, 0), (-1, -1), 8),
#     ]))
#     story.append(score_table)
#     story.append(Spacer(1, 12))

#     # ── YIELD PREDICTION ────────────────────────────────────
#     story.append(Paragraph("&nbsp;&nbsp;YIELD PREDICTION", section_style))
#     yield_data = [
#         ["Parameter", "Predicted Value", "Baseline", "Improvement"],
#         ["Crop Yield",
#          f"{report_data.get('yield_pred', 'N/A')} tons/hectare",
#          f"{report_data.get('baseline_yield', BASELINE_YIELD)} t/ha",
#          f"{report_data.get('yield_improvement', 'N/A')}%"],
#     ]
#     yield_table = Table(yield_data, colWidths=[4*cm, 5*cm, 3.5*cm, 4.2*cm])
#     yield_table.setStyle(TableStyle([
#         ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#388e3c")),
#         ("TEXTCOLOR",  (0, 0), (-1, 0), colors.white),
#         ("FONTNAME",   (0, 0), (-1, 0), "Helvetica-Bold"),
#         ("FONTSIZE",   (0, 0), (-1, -1), 10),
#         ("ALIGN",      (0, 0), (-1, -1), "CENTER"),
#         ("VALIGN",     (0, 0), (-1, -1), "MIDDLE"),
#         ("FONTNAME",   (0, 1), (-1, 1), "Helvetica-Bold"),
#         ("TEXTCOLOR",  (1, 1), (1, 1), colors.HexColor("#1b5e20")),
#         ("BOX",        (0, 0), (-1, -1), 1, colors.HexColor("#1b5e20")),
#         ("INNERGRID",  (0, 0), (-1, -1), 0.4, colors.grey),
#         ("BACKGROUND", (0, 1), (-1, 1), colors.HexColor("#f1f8e9")),
#         ("TOPPADDING", (0, 0), (-1, -1), 7),
#         ("BOTTOMPADDING",(0, 0), (-1, -1), 7),
#     ]))
#     story.append(yield_table)
#     story.append(Spacer(1, 12))

#     # ── COST ANALYSIS ───────────────────────────────────────
#     story.append(Paragraph("&nbsp;&nbsp;COST ANALYSIS", section_style))
#     cost_data = [
#         ["Cost Type", "Amount (₹/hectare)"],
#         ["Chemical Fertilizer Cost",
#          f"₹{report_data.get('chemical_cost', 0):,.2f}"],
#         ["Organic Fertilizer Cost",
#          f"₹{report_data.get('organic_cost', 0):,.2f}"],
#         ["Estimated Savings",
#          f"₹{report_data.get('savings', 0):,.2f}  ({report_data.get('savings_pct', 0)}%)"],
#     ]
#     cost_table = Table(cost_data, colWidths=[9*cm, 7.7*cm])
#     cost_table.setStyle(TableStyle([
#         ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#388e3c")),
#         ("TEXTCOLOR",  (0, 0), (-1, 0), colors.white),
#         ("FONTNAME",   (0, 0), (-1, 0), "Helvetica-Bold"),
#         ("FONTSIZE",   (0, 0), (-1, -1), 10),
#         ("ALIGN",      (0, 0), (-1, -1), "LEFT"),
#         ("ALIGN",      (1, 1), (1, -1),  "RIGHT"),
#         ("VALIGN",     (0, 0), (-1, -1), "MIDDLE"),
#         ("FONTNAME",   (0, 1), (0, -1), "Helvetica-Bold"),
#         ("FONTNAME",   (0, -1), (-1, -1), "Helvetica-Bold"),
#         ("TEXTCOLOR",  (1, -1), (1, -1), colors.HexColor("#2e7d32")),
#         ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#c8e6c9")),
#         ("BOX",        (0, 0), (-1, -1), 1, colors.HexColor("#1b5e20")),
#         ("INNERGRID",  (0, 0), (-1, -1), 0.4, colors.grey),
#         ("LEFTPADDING",(0, 0), (-1, -1), 8),
#         ("RIGHTPADDING",(0, 0), (-1, -1), 8),
#         ("TOPPADDING", (0, 0), (-1, -1), 6),
#         ("BOTTOMPADDING",(0, 0), (-1, -1), 6),
#         ("ROWBACKGROUNDS", (0, 1), (-1, -2),
#             [colors.white, colors.HexColor("#f1f8e9")]),
#     ]))
#     story.append(cost_table)
#     story.append(Spacer(1, 14))

#     # ── SIGNATURE / DISCLAIMER ──────────────────────────────
#     story.append(HRFlowable(width="100%", thickness=1,
#                             color=colors.HexColor("#1b5e20"), spaceAfter=6))
#     story.append(Paragraph(
#         "<b>Authorized by:</b> SoilSense AI Diagnostic Engine "
#         "(RandomForest Classifier · Accuracy: " +
#         f"{report_data.get('model_accuracy', 'N/A')}%)",
#         normal_style,
#     ))
#     story.append(Spacer(1, 4))
#     story.append(Paragraph(
#         "<i>Disclaimer: This is an AI-generated advisory report. For critical farm "
#         "decisions, please consult your local agricultural extension officer. "
#         "Test results are based on the provided input parameters at the time of analysis.</i>",
#         ParagraphStyle("disc", parent=normal_style, fontSize=8,
#                        textColor=colors.grey, alignment=TA_CENTER),
#     ))
#     story.append(Spacer(1, 6))
#     story.append(Paragraph(
#         f"Generated on {report_data.get('date', '')} at {report_data.get('time', '')} "
#         f"· Report ID: {report_data.get('report_id', 'N/A')} · "
#         "© SoilSense Smart Agriculture Laboratory",
#         footer_style,
#     ))

#     doc.build(story)
#     pdf_bytes = buffer.getvalue()
#     buffer.close()
#     return pdf_bytes


# # ═════════════════════════════════════════════════════════════
# # 🩺 PDF REPORT UI SECTION
# # ═════════════════════════════════════════════════════════════

# st.divider()
# st.markdown(
#     '<div class="section-title">🩺 Soil Health Diagnostic Report (Medical Style)</div>',
#     unsafe_allow_html=True,
# )

# if not REPORTLAB_AVAILABLE:
#     st.error(
#         "⚠️ **ReportLab is not installed.** Add `reportlab` to your `requirements.txt` "
#         "and redeploy your app to enable PDF report generation."
#     )
# elif not st.session_state.get("done"):
#     st.info(
#         "📋 Run a fertilizer prediction first (using the sidebar) to generate "
#         "your personalized **Soil Health Diagnostic Report**."
#     )
# else:
#     st.caption(
#         "Generate a professional medical-style soil health report with all your "
#         "test results, fertilizer recommendations, yield prediction, and cost analysis."
#     )

#     # Optional farmer info input
#     finfo1, finfo2 = st.columns(2)
#     with finfo1:
#         farmer_name = st.text_input(
#             "👨‍🌾 Farmer Name (optional)",
#             value="Farmer",
#             key="pdf_farmer_name",
#         )
#         input_mode = st.selectbox(
#             "📥 Input Mode",
#             ["Manual", "IoT Sensor", "Dataset"],
#             index=1 if st.session_state.get("iot_use_for_prediction") else 0,
#             key="pdf_input_mode",
#         )
#     with finfo2:
#         farm_loc = st.text_input(
#             "📍 Farm Location",
#             value=st.session_state.city or "N/A",
#             key="pdf_farm_loc",
#         )

#     if st.button("🧪 Generate PDF Report", type="primary", use_container_width=False):
#         try:
#             ss = st.session_state
#             now = _dt.now()

#             # Pull cost data if available
#             cost = ss.cost_analysis_data or {}

#             report_data = {
#                 "farmer_name":      farmer_name or "Farmer",
#                 "location":         farm_loc or ss.city or "N/A",
#                 "crop":             ss.crop_input or "N/A",
#                 "date":             now.strftime("%d-%b-%Y"),
#                 "time":             now.strftime("%I:%M %p"),
#                 "input_mode":       input_mode,
#                 "report_id":        f"SS-{now.strftime('%Y%m%d-%H%M%S')}",
#                 "N":                ss.N,
#                 "P":                ss.P,
#                 "K":                ss.K,
#                 "moisture":         ss.moisture,
#                 "temperature":      (ss.weather or {}).get("temperature", "N/A"),
#                 "pH":               ss.pH,
#                 "chemical":         ss.chemical or "N/A",
#                 "organic":          ss.organic  or "N/A",
#                 "soil_score":       ss.soil_score or 0,
#                 "yield_pred":       ss.yield_pred or 0,
#                 "yield_improvement":ss.yield_impr or 0,
#                 "baseline_yield":   BASELINE_YIELD,
#                 "chemical_cost":    cost.get("chemical_cost", 0),
#                 "organic_cost":     cost.get("organic_cost", 0),
#                 "savings":          cost.get("savings", 0),
#                 "savings_pct":      cost.get("savings_pct", 0),
#                 "model_accuracy":   accuracy,
#             }

#             with st.spinner("📄 Generating professional PDF report..."):
#                 pdf_bytes = generate_pdf_report(report_data)

#             st.success("✅ Report generated successfully!")

#             # Preview summary
#             with st.expander("👁 View Report Summary", expanded=False):
#                 preview_col1, preview_col2 = st.columns(2)
#                 with preview_col1:
#                     st.markdown(f"""
#                     **🆔 Report ID:** `{report_data['report_id']}`  
#                     **👨‍🌾 Farmer:** {report_data['farmer_name']}  
#                     **📍 Location:** {report_data['location']}  
#                     **🌱 Crop:** {report_data['crop']}  
#                     **📅 Date:** {report_data['date']} · {report_data['time']}
#                     """)
#                 with preview_col2:
#                     st.markdown(f"""
#                     **⚗️ Chemical Fertilizer:** {report_data['chemical']}  
#                     **🌿 Organic Fertilizer:** {report_data['organic']}  
#                     **🧮 Soil Score:** {report_data['soil_score']}  
#                     **🌾 Yield:** {report_data['yield_pred']} t/ha  
#                     **💰 Savings:** ₹{report_data['savings']:,.2f}
#                     """)

#             # Download button
#             st.download_button(
#                 label="📥 Download Soil Health Report (PDF)",
#                 data=pdf_bytes,
#                 file_name=f"Soil_Health_Report_{report_data['report_id']}.pdf",
#                 mime="application/pdf",
#                 use_container_width=True,
#                 type="primary",
#             )

#         except Exception as e:
#             st.error(f"❌ PDF generation error: {e}")
#             st.info(
#                 "Please ensure ReportLab is installed (`pip install reportlab`) "
#                 "and that you have run a successful prediction."
#             )

# # ═════════════════════════════════════════════════════════════
# # 🤖 SMART AI FARMING ASSISTANT (Uses Live NPK Values)
# # ═════════════════════════════════════════════════════════════
# # TEMPORARY DEBUG — remove after fixing
# with st.expander("🔍 Debug Info"):
#     try:
#         key = st.secrets.get("OPENAI_API_KEY", "")
#         if key:
#             st.success(f"✅ Key found — starts with: {key[:8]}...")
#         else:
#             st.error("❌ Key is empty or not found")
#     except Exception as e:
#         st.error(f"❌ secrets error: {e}")
# st.divider()
# st.header("🤖 Smart AI Farming Assistant (Uses Live NPK Values)")

# # ── Live NPK context banner ───────────────────────────────────
# _N = st.session_state.get("N")
# _P = st.session_state.get("P")
# _K = st.session_state.get("K")

# if _N is not None and _P is not None and _K is not None:
#     st.success(
#         f"📡 **Live soil data loaded into AI context** — "
#         f"N: **{_N} kg/ha** · P: **{_P} kg/ha** · K: **{_K} kg/ha**  \n"
#         "The assistant will automatically use these values in every response."
#     )
# else:
#     st.info(
#         "ℹ️ No soil data detected yet. Run a prediction first (Manual / IoT / Dataset) "
#         "so the assistant can give NPK-specific advice."
#     )

# st.caption(
#     "Ask me anything about fertilizers, organic farming, soil health, crop yield, "
#     "or cost savings. Powered by GPT-4o-mini · Your soil data is used automatically. 🌾"
# )

# # ── Quick-question buttons ────────────────────────────────────
# st.markdown("**💡 Quick Questions:**")
# qcol1, qcol2, qcol3, qcol4 = st.columns(4)
# suggested_q = None
# if qcol1.button("🌿 About Organic",  use_container_width=True):
#     suggested_q = "Should I switch to organic fertilizer based on my current NPK levels?"
# if qcol2.button("🌱 Soil Health",    use_container_width=True):
#     suggested_q = "How can I improve my soil health given the current NPK values?"
# if qcol3.button("🌾 Increase Yield", use_container_width=True):
#     suggested_q = "How can I increase my crop yield with these NPK readings?"
# if qcol4.button("💰 Cost Savings",   use_container_width=True):
#     suggested_q = "How can I save fertilizer costs based on my soil nutrient levels?"

# # ── Render existing conversation ──────────────────────────────
# if st.session_state.chat_history:
#     st.markdown(f"**💬 Conversation** ({len(st.session_state.chat_history)} messages)")
#     for turn in st.session_state.chat_history:
#         with st.chat_message("user", avatar="👨‍🌾"):
#             st.markdown(turn["user"])
#         with st.chat_message("assistant", avatar="🌱"):
#             st.markdown(turn["bot"])
# else:
#     st.info("💬 No conversation yet. Type a question below or click a quick-suggestion button.")

# # ── Handle quick-question buttons ────────────────────────────
# if suggested_q:
#     with st.chat_message("user", avatar="👨‍🌾"):
#         st.markdown(suggested_q)
#     with st.chat_message("assistant", avatar="🌱"):
#         with st.spinner("🌾 Thinking..."):
#             try:
#                 bot_reply = get_bot_response(suggested_q)
#             except Exception:
#                 bot_reply = "⚠️ AI service temporarily unavailable. Please try again."
#         st.markdown(bot_reply)
#     st.session_state.chat_history.append({"user": suggested_q, "bot": bot_reply})
#     st.rerun()

# # ── Chat input (always at bottom) ────────────────────────────
# user_input = st.chat_input("Ask your farming question here…")

# if user_input and user_input.strip():
#     query = user_input.strip()
#     with st.chat_message("user", avatar="👨‍🌾"):
#         st.markdown(query)
#     with st.chat_message("assistant", avatar="🌱"):
#         with st.spinner("🌾 Thinking..."):
#             try:
#                 bot_reply = get_bot_response(query)
#             except Exception:
#                 bot_reply = "⚠️ AI service temporarily unavailable. Please try again."
#         st.markdown(bot_reply)
#     st.session_state.chat_history.append({"user": query, "bot": bot_reply})

# # ── Clear chat ────────────────────────────────────────────────
# if st.session_state.chat_history:
#     if st.button("🗑 Clear Chat", use_container_width=False):
#         st.session_state.chat_history = []
#         st.rerun()

# # ─────────────────────────────────────────────────────────────
# # AUTO-REFRESH TRIGGER (IoT) — must be at the very end
# # ─────────────────────────────────────────────────────────────

# if st.session_state.iot_auto_refresh:
#     time.sleep(5)
#     try:
#         st.rerun()
#     except AttributeError:
#         st.experimental_rerun()

# # ─────────────────────────────────────────────────────────────
# # FOOTER
# # ─────────────────────────────────────────────────────────────

# st.divider()
# st.caption(
#     "🌱 **SoilSense** · RandomForest AI · "
#     "IoT Sensors · Live Weather (OpenWeatherMap) · "
#     "Dataset: improved_balanced_dataset_5000.xlsx · "
#     "Built with Streamlit"
# )




# code33......................




# =========================================================
# 🌱 SOIL SENSE V2 — AI Soil Recovery Intelligence Platform
# Upgraded for Punjab Smart Agri Ecosystem Dataset
# =========================================================

import streamlit as st
import pandas as pd
import numpy as np
import requests
import joblib
import os
import random

import plotly.express as px
import plotly.graph_objects as go

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="SOIL SENSE V2",
    page_icon="🌱",
    layout="wide"
)

# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display&family=DM+Sans:wght@300;400;500;600&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

.main-header {
    background: linear-gradient(135deg, #1b4332, #40916c, #74c69d);
    padding: 32px 36px;
    border-radius: 20px;
    margin-bottom: 24px;
}
.main-header h1 {
    color: white;
    margin: 0 0 6px 0;
    font-family: 'DM Serif Display', serif;
    font-size: 46px;
    letter-spacing: -1px;
}
.main-header p {
    color: #d8f3dc;
    font-size: 17px;
    margin: 0;
}

.section-title {
    font-size: 24px;
    font-weight: 600;
    color: #1b4332;
    margin-top: 28px;
    margin-bottom: 12px;
    border-left: 4px solid #40916c;
    padding-left: 12px;
}

.info-box {
    background: #d8f3dc;
    border-left: 5px solid #40916c;
    padding: 14px 18px;
    border-radius: 10px;
    margin-bottom: 16px;
    font-size: 15px;
}

.alert-safe {
    background: #d8f3dc;
    color: #1b4332;
    padding: 16px 20px;
    border-radius: 12px;
    font-size: 18px;
    font-weight: 600;
    border-left: 6px solid #2d6a4f;
}
.alert-caution {
    background: #fff3cd;
    color: #856404;
    padding: 16px 20px;
    border-radius: 12px;
    font-size: 18px;
    font-weight: 600;
    border-left: 6px solid #f4a261;
}
.alert-delay {
    background: #ffe5d0;
    color: #9c3b00;
    padding: 16px 20px;
    border-radius: 12px;
    font-size: 18px;
    font-weight: 600;
    border-left: 6px solid #e76f51;
}
.alert-stop {
    background: #fde8e8;
    color: #7f1d1d;
    padding: 16px 20px;
    border-radius: 12px;
    font-size: 18px;
    font-weight: 600;
    border-left: 6px solid #e53e3e;
}
</style>
""", unsafe_allow_html=True)

# =========================================================
# CONSTANTS — aligned with actual dataset values
# =========================================================

CROPS = ["Wheat", "Rice", "Cotton", "Mustard", "Gram"]
REGIONS = ["Punjab"]
TRANSITION_PHASES = ["Start", "Early Shift", "Mid Shift", "Balanced Shift", "Organic Dominant"]
FARMER_ARCHETYPES = ["Struggling", "Moderate", "Success", "Weather-Hit"]
ALERT_CLASSES = ["SAFE", "PROCEED WITH CAUTION", "DELAY TRANSITION", "STOP TRANSITION"]

MODEL_DIR = "model"
MODEL_PATH = os.path.join(MODEL_DIR, "soil_model.pkl")
ENCODER_PATH = os.path.join(MODEL_DIR, "encoders.pkl")
TARGET_ENCODER_PATH = os.path.join(MODEL_DIR, "target_encoder.pkl")

FEATURES = [
    "Current_Temp",
    "Current_Rain",
    "Current_Hum",
    "Current_Soil_pH",
    "Current_Soil_Organic_Matter_Percent",
    "Current_Soil_Nitrogen_kg_per_ha",
    "Current_Soil_Phosphorus_kg_per_ha",
    "Current_Soil_Potassium_kg_per_ha",
    "Soil_Recovery_Score",
    "Weekly_Improvement_Percent",
    "Transition_Success_Score",
    "Region",
    "Crop_Name",
]

TARGET = "Alert_Status"

# =========================================================
# WEATHER API
# =========================================================

API_KEY = "cb81120197f345ae396cd0fa28c1827c"


def get_weather(city):
    try:
        url = (
            f"https://api.openweathermap.org/data/2.5/weather"
            f"?q={city}&appid={API_KEY}&units=metric"
        )
        data = requests.get(url, timeout=5).json()
        return {
            "temperature": data["main"]["temp"],
            "humidity": data["main"]["humidity"],
            "condition": data["weather"][0]["main"],
            "rainfall": data.get("rain", {}).get("1h", 0),
        }
    except Exception:
        return {"temperature": 30, "humidity": 60, "condition": "Clear", "rainfall": 10}


# =========================================================
# DATASET LOADER
# =========================================================

@st.cache_data
def load_dataset(file):
    if file.name.endswith(".csv"):
        return pd.read_csv(file)
    return pd.read_excel(file)


# =========================================================
# PREPROCESSING
# =========================================================

CATEGORICAL_FEATURES = ["Region", "Crop_Name"]


def preprocess_data(df):
    df = df.copy()
    df.drop_duplicates(inplace=True)
    df.ffill(inplace=True)
    encoders = {}
    for col in CATEGORICAL_FEATURES:
        if col in df.columns:
            le = LabelEncoder()
            df[col] = le.fit_transform(df[col].astype(str))
            encoders[col] = le
    return df, encoders


# =========================================================
# TRAIN MODEL
# =========================================================

def train_model(df):
    df, encoders = preprocess_data(df)

    missing = [f for f in FEATURES if f not in df.columns]
    if missing:
        st.error(f"Missing columns: {missing}")
        return None, None

    X = df[FEATURES]
    y = df[TARGET]

    target_encoder = LabelEncoder()
    y_enc = target_encoder.fit_transform(y)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y_enc, test_size=0.2, random_state=42, stratify=y_enc
    )

    model = RandomForestClassifier(n_estimators=300, random_state=42, n_jobs=-1)
    model.fit(X_train, y_train)

    preds = model.predict(X_test)
    accuracy = accuracy_score(y_test, preds)
    report = classification_report(
        y_test, preds,
        target_names=target_encoder.classes_,
        output_dict=True
    )

    os.makedirs(MODEL_DIR, exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    joblib.dump(encoders, ENCODER_PATH)
    joblib.dump(target_encoder, TARGET_ENCODER_PATH)

    return accuracy, report


# =========================================================
# LOAD MODEL
# =========================================================

def model_exists():
    return all(os.path.exists(p) for p in [MODEL_PATH, ENCODER_PATH, TARGET_ENCODER_PATH])


def load_model():
    model = joblib.load(MODEL_PATH)
    encoders = joblib.load(ENCODER_PATH)
    target_encoder = joblib.load(TARGET_ENCODER_PATH)
    return model, encoders, target_encoder


# =========================================================
# PREDICTION ENGINE
# =========================================================

def predict_alert(input_df: pd.DataFrame):
    model, encoders, target_encoder = load_model()
    df = input_df.copy()
    for col in CATEGORICAL_FEATURES:
        if col in df.columns:
            le = encoders[col]
            df[col] = df[col].astype(str).apply(
                lambda x: le.transform([x])[0] if x in le.classes_ else -1
            )
    preds = model.predict(df[FEATURES])
    return target_encoder.inverse_transform(preds)


def predict_proba_alert(input_df: pd.DataFrame):
    model, encoders, target_encoder = load_model()
    df = input_df.copy()
    for col in CATEGORICAL_FEATURES:
        if col in df.columns:
            le = encoders[col]
            df[col] = df[col].astype(str).apply(
                lambda x: le.transform([x])[0] if x in le.classes_ else -1
            )
    proba = model.predict_proba(df[FEATURES])
    return proba, target_encoder.classes_


# =========================================================
# ALERT DISPLAY HELPER
# =========================================================

def render_alert(alert: str):
    alert = alert.upper()
    if "SAFE" in alert and "PROCEED" not in alert:
        st.markdown(f'<div class="alert-safe">✅ {alert}</div>', unsafe_allow_html=True)
    elif "PROCEED" in alert or "CAUTION" in alert:
        st.markdown(f'<div class="alert-caution">⚠️ {alert}</div>', unsafe_allow_html=True)
    elif "DELAY" in alert:
        st.markdown(f'<div class="alert-delay">🕐 {alert}</div>', unsafe_allow_html=True)
    elif "STOP" in alert:
        st.markdown(f'<div class="alert-stop">🚫 {alert}</div>', unsafe_allow_html=True)


# =========================================================
# SIDEBAR
# =========================================================

menu = st.sidebar.radio(
    "Navigation",
    [
        "🏠 Dashboard",
        "📊 Train Model",
        "📁 Dataset Prediction",
        "🧠 Manual Prediction",
        "🌦 Weather Monitor",
        "📈 Recovery Analytics",
    ],
)

st.sidebar.markdown("---")
if model_exists():
    st.sidebar.success("✅ Model is trained and ready")
else:
    st.sidebar.warning("⚠️ No trained model. Go to 'Train Model' first.")

# =========================================================
# HEADER (always shown)
# =========================================================

st.markdown("""
<div class="main-header">
    <h1>🌱 SOIL SENSE V2</h1>
    <p>AI-Powered Soil Recovery Intelligence for Punjab Smart Agriculture</p>
</div>
""", unsafe_allow_html=True)

# =========================================================
# DASHBOARD
# =========================================================

if menu == "🏠 Dashboard":

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("🌾 Crop Types", "5", "Wheat, Rice, Cotton, Mustard, Gram")
    c2.metric("📁 Dataset Rows", "5,600", "7 weeks × 800 farmers")
    c3.metric("⚠️ Alert Classes", "4", "SAFE / CAUTION / DELAY / STOP")
    c4.metric("📍 Region", "Punjab", "India")

    st.markdown("---")
    st.markdown('<div class="section-title">📡 Live IoT Sensor Simulation</div>', unsafe_allow_html=True)

    i1, i2, i3, i4 = st.columns(4)
    i1.metric("🌡 Temperature", f"{random.randint(25, 42)} °C")
    i2.metric("💧 Humidity", f"{random.randint(40, 90)} %")
    i3.metric("🌧 Rainfall", f"{random.uniform(0, 40):.1f} mm")
    i4.metric("🧪 Soil pH", round(random.uniform(5.5, 7.5), 2))

    st.markdown("---")
    st.markdown('<div class="section-title">📈 Simulated Weekly Soil Recovery Trend</div>', unsafe_allow_html=True)

    week_df = pd.DataFrame({
        "Week": list(range(1, 8)),
        "Recovery Score": [42, 51, 60, 68, 77, 85, 91],
        "Transition Success": [38, 48, 57, 66, 75, 83, 90],
    })
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=week_df["Week"], y=week_df["Recovery Score"],
                             mode="lines+markers", name="Recovery Score",
                             line=dict(color="#40916c", width=3)))
    fig.add_trace(go.Scatter(x=week_df["Week"], y=week_df["Transition Success"],
                             mode="lines+markers", name="Transition Success",
                             line=dict(color="#74c69d", width=3, dash="dash")))
    fig.update_layout(title="Week 1 → 7 Progression", xaxis_title="Week", yaxis_title="Score")
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.markdown('<div class="section-title">🔄 42-Day Before/After Comparison (Sample)</div>', unsafe_allow_html=True)

    compare_df = pd.DataFrame({
        "Parameter": ["Soil pH", "Nitrogen (kg/ha)", "Phosphorus (kg/ha)", "Potassium (kg/ha)", "Organic Matter %"],
        "Day 1": [5.8, 138, 68, 52, 1.2],
        "Day 42": [6.7, 95, 52, 40, 2.8],
    })
    fig2 = px.bar(compare_df, x="Parameter", y=["Day 1", "Day 42"],
                  barmode="group", title="Soil Parameters: Day 1 vs Day 42",
                  color_discrete_map={"Day 1": "#e76f51", "Day 42": "#40916c"})
    st.plotly_chart(fig2, use_container_width=True)

    st.markdown('<div class="section-title">👩‍🌾 Farmer Archetype Distribution (Sample)</div>', unsafe_allow_html=True)
    arch_df = pd.DataFrame({
        "Archetype": ["Success", "Moderate", "Struggling", "Weather-Hit"],
        "Count": [210, 290, 180, 120],
    })
    fig3 = px.pie(arch_df, values="Count", names="Archetype",
                  color_discrete_sequence=px.colors.sequential.Greens_r,
                  title="Farmer Archetype Breakdown")
    st.plotly_chart(fig3, use_container_width=True)

# =========================================================
# TRAIN MODEL
# =========================================================

elif menu == "📊 Train Model":

    st.header("📊 Train Soil Recovery Model")
    st.markdown('<div class="info-box">Upload the <b>Punjab Smart Agri Ecosystem Dataset</b> (.xlsx or .csv) to train the AI model. Training uses a Random Forest classifier on soil, weather, and transition features to predict Alert Status.</div>', unsafe_allow_html=True)

    uploaded_file = st.file_uploader("Upload Dataset", type=["xlsx", "csv"])

    if uploaded_file:
        df = load_dataset(uploaded_file)
        st.success(f"✅ Dataset Loaded — {df.shape[0]:,} rows × {df.shape[1]} columns")
        st.dataframe(df.head(10), use_container_width=True)

        missing_cols = [f for f in FEATURES + [TARGET] if f not in df.columns]
        if missing_cols:
            st.error(f"❌ Missing required columns: {missing_cols}")
        else:
            st.markdown("**Alert Status Distribution**")
            alert_dist = df[TARGET].value_counts().reset_index()
            alert_dist.columns = ["Alert Status", "Count"]
            fig = px.bar(alert_dist, x="Alert Status", y="Count",
                         color="Alert Status",
                         color_discrete_sequence=["#40916c", "#f4a261", "#e76f51", "#e53e3e"])
            st.plotly_chart(fig, use_container_width=True)

            if st.button("🚀 Train AI Model", type="primary"):
                with st.spinner("Training Random Forest on 5,600 records..."):
                    result = train_model(df)
                if result[0] is None:
                    st.error("Training failed. Check column structure.")
                else:
                    accuracy, report = result
                    st.success("✅ Model Training Complete!")
                    st.metric("Overall Accuracy", f"{accuracy:.1%}")

                    report_df = pd.DataFrame(report).transpose()
                    st.markdown("**Per-Class Classification Report**")
                    st.dataframe(report_df.style.format("{:.2f}"), use_container_width=True)

# =========================================================
# DATASET PREDICTION
# =========================================================

elif menu == "📁 Dataset Prediction":

    st.header("📁 Bulk Dataset Prediction")
    st.markdown('<div class="info-box">Upload a dataset with the required feature columns. The trained model will predict the <b>Alert Status</b> for each row.</div>', unsafe_allow_html=True)

    if not model_exists():
        st.error("❌ No trained model found. Please go to 'Train Model' first.")
        st.stop()

    prediction_file = st.file_uploader("Upload Prediction Dataset", type=["xlsx", "csv"])

    if prediction_file:
        df = load_dataset(prediction_file)
        st.write(f"Loaded {df.shape[0]:,} rows")
        st.dataframe(df.head(), use_container_width=True)

        missing = [f for f in FEATURES if f not in df.columns]
        if missing:
            st.error(f"Missing columns: {missing}")
        else:
            if st.button("🔍 Run Predictions", type="primary"):
                with st.spinner("Predicting..."):
                    df["Predicted_Alert"] = predict_alert(df[FEATURES + [c for c in CATEGORICAL_FEATURES if c in df.columns]])

                st.success("✅ Prediction Complete!")
                st.dataframe(df[["Farmer_ID", "Crop_Name", "Region", "Predicted_Alert"] if "Farmer_ID" in df.columns else ["Predicted_Alert"]].head(20),
                             use_container_width=True)

                alert_counts = df["Predicted_Alert"].value_counts().reset_index()
                alert_counts.columns = ["Alert", "Count"]
                fig = px.pie(alert_counts, values="Count", names="Alert",
                             title="Predicted Alert Distribution",
                             color_discrete_sequence=["#40916c", "#f4a261", "#e76f51", "#e53e3e"])
                st.plotly_chart(fig, use_container_width=True)

                csv = df.to_csv(index=False).encode("utf-8")
                st.download_button("⬇ Download Predictions CSV", csv,
                                   "soil_predictions.csv", "text/csv")

# =========================================================
# MANUAL PREDICTION
# =========================================================

elif menu == "🧠 Manual Prediction":

    st.header("🧠 Manual Soil Transition Prediction")
    st.markdown('<div class="info-box">Enter field conditions manually. The AI model will predict transition safety and alert status for the given inputs.</div>', unsafe_allow_html=True)

    if not model_exists():
        st.error("❌ No trained model found. Please go to 'Train Model' first.")
        st.stop()

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🌾 Crop & Location")
        crop = st.selectbox("Crop Name", CROPS)
        region = st.selectbox("Region", REGIONS)
        city = st.text_input("City (for weather fetch)", "Ludhiana")

        st.subheader("🌦 Weather Parameters")
        manual_temp = st.slider("Temperature (°C)", 5.0, 50.0, 30.0)
        manual_rain = st.slider("Rainfall (mm)", 0.0, 200.0, 10.0)
        manual_hum = st.slider("Humidity (%)", 5.0, 100.0, 60.0)

        use_live_weather = st.checkbox("🌐 Override with Live Weather", value=False)

    with col2:
        st.subheader("🧪 Soil Parameters")
        ph = st.slider("Soil pH", 4.0, 9.0, 6.5, step=0.1)
        nitrogen = st.slider("Nitrogen (kg/ha)", 0, 300, 120,
                             help="Safe range: 80–160 kg/ha")
        phosphorus = st.slider("Phosphorus (kg/ha)", 0, 150, 60,
                               help="Safe range: 40–90 kg/ha")
        potassium = st.slider("Potassium (kg/ha)", 0, 200, 50,
                              help="Safe range: 30–80 kg/ha")
        organic = st.slider("Organic Matter (%)", 0.0, 8.0, 2.5, step=0.1,
                            help="Target: > 2.0%")

        st.subheader("📈 Transition Scores")
        recovery_score = st.slider("Soil Recovery Score", 0, 100, 70)
        weekly_improvement = st.slider("Weekly Improvement (%)", 0.0, 30.0, 8.0, step=0.5)
        transition_score = st.slider("Transition Success Score", 0, 100, 75)

    if st.button("🚀 Predict Transition Safety", type="primary"):

        if use_live_weather:
            weather = get_weather(city)
            temp = weather["temperature"]
            rain = weather["rainfall"]
            hum = weather["humidity"]
            st.info(f"Live weather fetched: {temp}°C | {hum}% humidity | {rain}mm rain | {weather['condition']}")
        else:
            temp, rain, hum = manual_temp, manual_rain, manual_hum

        input_df = pd.DataFrame([{
            "Current_Temp": temp,
            "Current_Rain": rain,
            "Current_Hum": hum,
            "Current_Soil_pH": ph,
            "Current_Soil_Organic_Matter_Percent": organic,
            "Current_Soil_Nitrogen_kg_per_ha": nitrogen,
            "Current_Soil_Phosphorus_kg_per_ha": phosphorus,
            "Current_Soil_Potassium_kg_per_ha": potassium,
            "Soil_Recovery_Score": recovery_score,
            "Weekly_Improvement_Percent": weekly_improvement,
            "Transition_Success_Score": transition_score,
            "Region": region,
            "Crop_Name": crop,
        }])

        prediction = predict_alert(input_df)[0]
        proba, classes = predict_proba_alert(input_df)

        st.markdown("---")
        st.subheader("📊 AI Prediction Result")
        render_alert(prediction)

        # Probability bar chart
        prob_df = pd.DataFrame({"Alert Class": classes, "Probability": proba[0]})
        fig = px.bar(prob_df, x="Alert Class", y="Probability",
                     color="Alert Class",
                     color_discrete_sequence=["#40916c", "#f4a261", "#e76f51", "#e53e3e"],
                     title="Prediction Confidence per Alert Class")
        fig.update_yaxes(range=[0, 1], tickformat=".0%")
        st.plotly_chart(fig, use_container_width=True)

        # Summary metrics
        g1, g2, g3 = st.columns(3)
        g1.metric("🌾 Recovery Score", f"{recovery_score}/100")
        g2.metric("📈 Transition Score", f"{transition_score}/100")
        g3.metric("🌱 Organic Matter", f"{organic}%",
                  delta="Good" if organic >= 2.0 else "Needs Improvement")

        # Soil health warnings
        warnings = []
        if ph < 5.5:
            warnings.append("⚠️ Soil pH too acidic — consider lime application")
        elif ph > 7.5:
            warnings.append("⚠️ Soil pH too alkaline — check irrigation water quality")
        if nitrogen > 200:
            warnings.append("⚠️ Nitrogen excessive — risk of leaching and crop damage")
        if organic < 1.5:
            warnings.append("⚠️ Organic matter critically low — increase compost application")
        if temp > 42:
            warnings.append("⚠️ Extreme heat — delay any chemical applications")
        if rain > 100:
            warnings.append("⚠️ Heavy rain — risk of nutrient runoff")

        if warnings:
            st.markdown("**Soil & Weather Alerts:**")
            for w in warnings:
                st.warning(w)
        else:
            st.success("✅ No critical soil or weather warnings detected.")

# =========================================================
# WEATHER MONITOR
# =========================================================

elif menu == "🌦 Weather Monitor":

    st.header("🌦 Live Weather Monitoring")
    st.markdown('<div class="info-box">Fetch real-time weather for any city. Weather data is used by the prediction engine to assess transition safety. Requires a valid OpenWeather API key.</div>', unsafe_allow_html=True)

    city = st.text_input("Enter City", "Ludhiana")

    if st.button("🌍 Fetch Weather"):
        weather = get_weather(city)

        w1, w2, w3, w4 = st.columns(4)
        w1.metric("🌡 Temperature", f"{weather['temperature']} °C")
        w2.metric("💧 Humidity", f"{weather['humidity']} %")
        w3.metric("🌧 Rainfall", f"{weather['rainfall']} mm")
        w4.metric("☁ Condition", weather["condition"])

        if weather["temperature"] > 42:
            st.error("⚠️ Extreme Heat Warning — Avoid fertilizer applications")
        elif weather["temperature"] > 38:
            st.warning("⚠️ High Temperature — Monitor crop stress")

        if weather["humidity"] < 25:
            st.warning("⚠️ Drought Risk — Increase irrigation frequency")

        if weather["rainfall"] > 80:
            st.warning("⚠️ Heavy Rainfall — Risk of nutrient runoff; delay organic applications")
        elif weather["rainfall"] > 150:
            st.error("⚠️ Flood Risk — Halt all transition activities")

        # Gauge chart for temperature
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=weather["temperature"],
            title={"text": "Temperature (°C)"},
            gauge={
                "axis": {"range": [0, 55]},
                "bar": {"color": "#e76f51"},
                "steps": [
                    {"range": [0, 25], "color": "#d8f3dc"},
                    {"range": [25, 38], "color": "#fff3cd"},
                    {"range": [38, 55], "color": "#fde8e8"},
                ],
                "threshold": {"line": {"color": "red", "width": 4}, "value": 42},
            },
        ))
        st.plotly_chart(fig, use_container_width=True)

# =========================================================
# RECOVERY ANALYTICS
# =========================================================

elif menu == "📈 Recovery Analytics":

    st.header("📈 Soil Recovery Analytics")
    st.markdown('<div class="info-box">Upload the dataset to generate interactive analytics on soil recovery, NPK trends, weather impact, and transition success across crops and weeks.</div>', unsafe_allow_html=True)

    uploaded_file = st.file_uploader("Upload Dataset", type=["xlsx", "csv"])

    if uploaded_file:
        df = load_dataset(uploaded_file)
        st.success(f"✅ Dataset loaded — {df.shape[0]:,} rows")

        # --- Filters ---
        with st.expander("🔍 Filter Data"):
            crops_sel = st.multiselect("Crop", CROPS, default=CROPS)
            weeks_sel = st.multiselect("Week", sorted(df["Week_Number"].unique()),
                                       default=sorted(df["Week_Number"].unique()))
            archetypes_sel = st.multiselect("Farmer Archetype", FARMER_ARCHETYPES,
                                            default=FARMER_ARCHETYPES)

        mask = (
            df["Crop_Name"].isin(crops_sel) &
            df["Week_Number"].isin(weeks_sel) &
            df["Farmer_Archetype"].isin(archetypes_sel)
        )
        dff = df[mask]
        st.write(f"Showing {len(dff):,} records after filters")

        # 1. Recovery Score by Week & Crop
        st.markdown('<div class="section-title">📈 Weekly Soil Recovery by Crop</div>', unsafe_allow_html=True)
        weekly_crop = dff.groupby(["Week_Number", "Crop_Name"])["Soil_Recovery_Score"].mean().reset_index()
        fig1 = px.line(weekly_crop, x="Week_Number", y="Soil_Recovery_Score",
                       color="Crop_Name", markers=True,
                       title="Average Soil Recovery Score per Week per Crop",
                       labels={"Week_Number": "Week", "Soil_Recovery_Score": "Recovery Score"})
        st.plotly_chart(fig1, use_container_width=True)

        # 2. NPK trend over weeks
        st.markdown('<div class="section-title">🧪 NPK Weekly Trends</div>', unsafe_allow_html=True)
        npk_week = dff.groupby("Week_Number")[
            ["Current_Soil_Nitrogen_kg_per_ha",
             "Current_Soil_Phosphorus_kg_per_ha",
             "Current_Soil_Potassium_kg_per_ha"]
        ].mean().reset_index()
        fig2 = go.Figure()
        for col, color, label in [
            ("Current_Soil_Nitrogen_kg_per_ha", "#2d6a4f", "Nitrogen"),
            ("Current_Soil_Phosphorus_kg_per_ha", "#40916c", "Phosphorus"),
            ("Current_Soil_Potassium_kg_per_ha", "#74c69d", "Potassium"),
        ]:
            fig2.add_trace(go.Scatter(x=npk_week["Week_Number"], y=npk_week[col],
                                     mode="lines+markers", name=label,
                                     line=dict(color=color, width=3)))
        fig2.update_layout(title="Average NPK Levels per Week",
                           xaxis_title="Week", yaxis_title="kg/ha")
        st.plotly_chart(fig2, use_container_width=True)

        # 3. Weather impact scatter
        st.markdown('<div class="section-title">🌦 Weather Impact on Transition Success</div>', unsafe_allow_html=True)
        fig3 = px.scatter(dff, x="Current_Temp", y="Transition_Success_Score",
                          color="Weather_Risk_Level", size="Soil_Recovery_Score",
                          hover_data=["Crop_Name", "Farmer_Archetype"],
                          title="Temperature vs Transition Success (size = Recovery Score)",
                          color_discrete_map={
                              "Low": "#40916c", "Medium": "#f4a261",
                              "High": "#e76f51", "Extreme": "#e53e3e"
                          })
        st.plotly_chart(fig3, use_container_width=True)

        # 4. Alert Status distribution
        st.markdown('<div class="section-title">⚠️ Alert Status Distribution</div>', unsafe_allow_html=True)
        fig4 = px.histogram(dff, x="Transition_Success_Score", color="Alert_Status",
                            nbins=30, title="Transition Success Score by Alert Status",
                            color_discrete_map={
                                "SAFE": "#40916c",
                                "PROCEED WITH CAUTION": "#f4a261",
                                "DELAY TRANSITION": "#e76f51",
                                "STOP TRANSITION": "#e53e3e",
                            })
        st.plotly_chart(fig4, use_container_width=True)

        # 5. Farmer Archetype vs Recovery
        st.markdown('<div class="section-title">👩‍🌾 Farmer Archetype Performance</div>', unsafe_allow_html=True)
        arch_perf = dff.groupby("Farmer_Archetype")[
            ["Soil_Recovery_Score", "Transition_Success_Score"]
        ].mean().reset_index()
        fig5 = px.bar(arch_perf, x="Farmer_Archetype",
                      y=["Soil_Recovery_Score", "Transition_Success_Score"],
                      barmode="group", title="Avg Recovery & Transition Score by Farmer Archetype",
                      color_discrete_map={
                          "Soil_Recovery_Score": "#40916c",
                          "Transition_Success_Score": "#74c69d"
                      })
        st.plotly_chart(fig5, use_container_width=True)

        # 6. Soil pH progression
        st.markdown('<div class="section-title">🧫 Soil pH Progression by Transition Phase</div>', unsafe_allow_html=True)
        ph_phase = dff.groupby(["Transition_Phase"])["Current_Soil_pH"].mean().reset_index()
        phase_order = ["Start", "Early Shift", "Mid Shift", "Balanced Shift", "Organic Dominant"]
        ph_phase["Transition_Phase"] = pd.Categorical(ph_phase["Transition_Phase"],
                                                       categories=phase_order, ordered=True)
        ph_phase = ph_phase.sort_values("Transition_Phase")
        fig6 = px.bar(ph_phase, x="Transition_Phase", y="Current_Soil_pH",
                      color="Current_Soil_pH", color_continuous_scale="Greens",
                      title="Average Soil pH across Transition Phases")
        st.plotly_chart(fig6, use_container_width=True)

# =========================================================
# FOOTER
# =========================================================

st.markdown("---")
st.markdown(
    "<center>🌱 <b>SOIL SENSE V2</b> — AI-Powered Soil Recovery Intelligence Platform "
    "| Punjab Smart Agri Ecosystem</center>",
    unsafe_allow_html=True,
)
