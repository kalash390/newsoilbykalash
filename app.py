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
# 🌱 SOIL SENSE V2 — Punjab Smart Agriculture Dashboard
# Full-featured: IoT · Manual Prediction · Analytics · Chat
# =========================================================

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
# import joblib

# from sklearn.ensemble import RandomForestClassifier
# from sklearn.model_selection import train_test_split
# from sklearn.preprocessing import LabelEncoder
# from sklearn.metrics import accuracy_score, classification_report

# # =========================================================
# # PAGE CONFIG
# # =========================================================

# st.set_page_config(
#     page_title="SoilSense V2 — Punjab Smart Agriculture",
#     page_icon="🌱",
#     layout="wide",
# )

# # =========================================================
# # CUSTOM CSS
# # =========================================================

# st.markdown("""
# <style>
# @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;800&family=DM+Sans:wght@300;400;500;600&display=swap');

# html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }

# .main-header {
#     background: linear-gradient(135deg, #14532d 0%, #166534 40%, #15803d 80%, #22c55e 100%);
#     padding: 28px 36px; border-radius: 20px; margin-bottom: 26px;
#     position: relative; overflow: hidden;
# }
# .main-header::before {
#     content: ''; position: absolute; top: -40px; right: -40px;
#     width: 200px; height: 200px; background: rgba(255,255,255,0.06); border-radius: 50%;
# }
# .main-header h1 {
#     color: white; margin: 0 0 6px;
#     font-family: 'Playfair Display', serif; font-size: 44px; letter-spacing: -1px;
# }
# .main-header p { color: #bbf7d0; font-size: 16px; margin: 0; }

# .section-title {
#     font-size: 22px; font-weight: 700; color: #14532d;
#     border-left: 5px solid #22c55e; padding-left: 14px;
#     margin: 28px 0 14px; font-family: 'Playfair Display', serif;
# }
# .info-box {
#     background: linear-gradient(135deg, #f0fdf4, #dcfce7);
#     border-left: 5px solid #16a34a; padding: 14px 20px;
#     border-radius: 12px; margin-bottom: 16px; font-size: 14.5px; color: #14532d;
# }
# .alert-safe {
#     background: linear-gradient(135deg,#f0fdf4,#dcfce7); color: #14532d;
#     border-left: 7px solid #16a34a; padding: 18px 22px; border-radius: 14px;
#     font-size: 20px; font-weight: 700; font-family: 'Playfair Display', serif;
# }
# .alert-caution {
#     background: linear-gradient(135deg,#fffbeb,#fef3c7); color: #78350f;
#     border-left: 7px solid #d97706; padding: 18px 22px; border-radius: 14px;
#     font-size: 20px; font-weight: 700; font-family: 'Playfair Display', serif;
# }
# .alert-delay {
#     background: linear-gradient(135deg,#fff7ed,#fed7aa); color: #9a3412;
#     border-left: 7px solid #ea580c; padding: 18px 22px; border-radius: 14px;
#     font-size: 20px; font-weight: 700; font-family: 'Playfair Display', serif;
# }
# .alert-stop {
#     background: linear-gradient(135deg,#fef2f2,#fecaca); color: #7f1d1d;
#     border-left: 7px solid #dc2626; padding: 18px 22px; border-radius: 14px;
#     font-size: 20px; font-weight: 700; font-family: 'Playfair Display', serif;
# }
# .weather-card {
#     background: linear-gradient(135deg,#eff6ff,#dbeafe);
#     border-left: 5px solid #3b82f6; padding: 14px 18px; border-radius: 12px; margin-bottom: 10px;
# }
# @keyframes fadeUp {
#     from { opacity:0; transform:translateY(20px); } to { opacity:1; transform:translateY(0); }
# }
# .fade-up { animation: fadeUp 0.5s ease forwards; }
# </style>
# """, unsafe_allow_html=True)

# # =========================================================
# # CONSTANTS
# # =========================================================

# CROPS      = ["Wheat", "Rice", "Cotton", "Mustard", "Gram"]
# REGIONS    = ["Punjab"]
# CITIES     = [
#     "Ludhiana", "Amritsar", "Jalandhar", "Patiala", "Bathinda",
#     "Mohali", "Gurdaspur", "Hoshiarpur", "Firozpur", "Moga",
#     "Sangrur", "Barnala", "Fatehgarh Sahib", "Nawanshahr", "Rupnagar",
# ]
# TRANSITION_PHASES = ["Start", "Early Shift", "Mid Shift", "Balanced Shift", "Organic Dominant"]
# FARMER_ARCHETYPES = ["Struggling", "Moderate", "Success", "Weather-Hit"]
# ALERT_CLASSES     = ["SAFE", "PROCEED WITH CAUTION", "DELAY TRANSITION", "STOP TRANSITION"]

# MODEL_DIR          = "model"
# MODEL_PATH         = os.path.join(MODEL_DIR, "soil_model.pkl")
# ENCODER_PATH       = os.path.join(MODEL_DIR, "encoders.pkl")
# TARGET_ENCODER_PATH= os.path.join(MODEL_DIR, "target_encoder.pkl")

# FEATURES = [
#     "Current_Temp", "Current_Rain", "Current_Hum",
#     "Current_Soil_pH", "Current_Soil_Organic_Matter_Percent",
#     "Current_Soil_Nitrogen_kg_per_ha", "Current_Soil_Phosphorus_kg_per_ha",
#     "Current_Soil_Potassium_kg_per_ha",
#     "Soil_Recovery_Score", "Weekly_Improvement_Percent",
#     "Transition_Success_Score", "Region", "Crop_Name",
# ]
# TARGET      = "Alert_Status"
# CAT_FEATURES= ["Region", "Crop_Name"]

# OWM_API_KEY = os.getenv("OWM_API_KEY", "cb81120197f345ae396cd0fa28c1827c")

# # =========================================================
# # SESSION STATE
# # =========================================================

# _defaults = dict(
#     done=False, city="Ludhiana", region="Punjab", crop="Wheat",
#     weather=None, prediction=None, proba=None,
#     N=None, P=None, K=None, pH=None,
#     recovery_score=None, transition_score=None,
#     iot_history=[], iot_auto_refresh=False,
#     iot_data_source="Simulated", iot_last_update=None,
#     iot_use_for_prediction=False,
#     chat_history=[], model_accuracy=None,
# )
# for k, v in _defaults.items():
#     if k not in st.session_state:
#         st.session_state[k] = v

# # =========================================================
# # HELPERS
# # =========================================================

# @st.cache_data(ttl=1800)
# def get_weather(city: str) -> dict:
#     try:
#         url = (f"https://api.openweathermap.org/data/2.5/weather"
#                f"?q={city},IN&appid={OWM_API_KEY}&units=metric")
#         d = requests.get(url, timeout=6).json()
#         return {
#             "temperature": round(d["main"]["temp"], 1),
#             "feels_like":  round(d["main"]["feels_like"], 1),
#             "humidity":    round(d["main"]["humidity"], 1),
#             "rainfall":    round(d.get("rain", {}).get("1h", 0.0), 2),
#             "description": d["weather"][0]["description"].title(),
#             "wind_speed":  round(d["wind"]["speed"], 1),
#             "error": None,
#         }
#     except Exception as e:
#         return {"temperature": 30, "feels_like": 32, "humidity": 60,
#                 "rainfall": 5, "description": "Clear Sky",
#                 "wind_speed": 3.2, "error": str(e)}


# def fetch_sensor_data(source="Simulated", api_url="") -> dict:
#     try:
#         if source == "REST API" and api_url:
#             r = requests.get(api_url, timeout=5).json()
#             return {
#                 "Soil_Moisture": float(r.get("soil_moisture", 45)),
#                 "Temperature":   float(r.get("temperature", 28)),
#                 "Humidity":      float(r.get("humidity", 65)),
#                 "Soil_pH":       float(r.get("soil_ph", 7.0)),
#                 "Nitrogen":      float(r.get("nitrogen", 200)),
#                 "Phosphorus":    float(r.get("phosphorus", 20)),
#                 "Potassium":     float(r.get("potassium", 200)),
#                 "timestamp": datetime.now().strftime("%H:%M:%S"), "source": "REST API",
#             }
#         last = st.session_state.iot_history[-1] if st.session_state.iot_history else None
#         def drift(key, lo, hi, d):
#             v = (last[key] if last else random.uniform(lo, hi)) + random.uniform(-d, d)
#             return round(max(lo, min(hi, v)), 2)
#         return {
#             "Soil_Moisture": drift("Soil_Moisture", 20, 80, 3),
#             "Temperature":   drift("Temperature",   10, 50, 1.5),
#             "Humidity":      drift("Humidity",      30, 100, 2.5),
#             "Soil_pH":       drift("Soil_pH",       6.5, 8.3, 0.1),
#             "Nitrogen":      drift("Nitrogen",      46, 560, 10),
#             "Phosphorus":    drift("Phosphorus",    5, 40, 1),
#             "Potassium":     drift("Potassium",     107, 384, 8),
#             "timestamp": datetime.now().strftime("%H:%M:%S"), "source": "Simulated",
#         }
#     except Exception:
#         return {"Soil_Moisture": 45, "Temperature": 28, "Humidity": 65,
#                 "Soil_pH": 7.0, "Nitrogen": 200, "Phosphorus": 20, "Potassium": 200,
#                 "timestamp": datetime.now().strftime("%H:%M:%S"), "source": "Fallback"}


# @st.cache_data
# def load_dataset(file):
#     return pd.read_excel(file) if file.name.endswith(".xlsx") else pd.read_csv(file)


# def model_exists():
#     return all(os.path.exists(p) for p in [MODEL_PATH, ENCODER_PATH, TARGET_ENCODER_PATH])


# def train_model(df):
#     df = df.copy(); df.drop_duplicates(inplace=True); df.ffill(inplace=True)
#     encoders = {}
#     for col in CAT_FEATURES:
#         if col in df.columns:
#             le = LabelEncoder(); df[col] = le.fit_transform(df[col].astype(str)); encoders[col] = le
#     missing = [f for f in FEATURES + [TARGET] if f not in df.columns]
#     if missing:
#         return None, None, None
#     X = df[FEATURES]; y = df[TARGET]
#     te = LabelEncoder(); y_enc = te.fit_transform(y)
#     X_train, X_test, y_train, y_test = train_test_split(
#         X, y_enc, test_size=0.2, random_state=42, stratify=y_enc)
#     clf = RandomForestClassifier(n_estimators=300, random_state=42, n_jobs=-1)
#     clf.fit(X_train, y_train)
#     preds  = clf.predict(X_test)
#     acc    = accuracy_score(y_test, preds)
#     report = classification_report(y_test, preds, target_names=te.classes_, output_dict=True)
#     os.makedirs(MODEL_DIR, exist_ok=True)
#     joblib.dump(clf, MODEL_PATH); joblib.dump(encoders, ENCODER_PATH); joblib.dump(te, TARGET_ENCODER_PATH)
#     return acc, report, clf


# def load_model():
#     return joblib.load(MODEL_PATH), joblib.load(ENCODER_PATH), joblib.load(TARGET_ENCODER_PATH)


# def encode_cat(df):
#     _, encoders, _ = load_model()
#     df = df.copy()
#     for col in CAT_FEATURES:
#         if col in df.columns:
#             le = encoders[col]
#             df[col] = df[col].astype(str).apply(
#                 lambda x: le.transform([x])[0] if x in le.classes_ else 0)
#     return df


# def predict_single(row: dict):
#     model, _, te = load_model()
#     df = encode_cat(pd.DataFrame([row]))
#     pred  = te.inverse_transform(model.predict(df[FEATURES]))[0]
#     proba = dict(zip(te.classes_, np.round(model.predict_proba(df[FEATURES])[0]*100, 1)))
#     return pred, proba


# def predict_bulk(df: pd.DataFrame):
#     model, _, te = load_model()
#     return te.inverse_transform(model.predict(encode_cat(df)[FEATURES]))


# def render_alert(alert: str):
#     a = alert.upper()
#     if "SAFE" in a and "PROCEED" not in a:
#         st.markdown(f'<div class="alert-safe">✅ {alert}</div>', unsafe_allow_html=True)
#     elif "PROCEED" in a or "CAUTION" in a:
#         st.markdown(f'<div class="alert-caution">⚠️ {alert}</div>', unsafe_allow_html=True)
#     elif "DELAY" in a:
#         st.markdown(f'<div class="alert-delay">🕐 {alert}</div>', unsafe_allow_html=True)
#     elif "STOP" in a:
#         st.markdown(f'<div class="alert-stop">🚫 {alert}</div>', unsafe_allow_html=True)

# # =========================================================
# # HEADER
# # =========================================================

# st.markdown("""
# <div class="main-header fade-up">
#     <h1>🌱 SoilSense V2</h1>
#     <p>Punjab Smart Agriculture · AI Soil Recovery Intelligence · IoT · Live Weather · Transition Advisory</p>
# </div>""", unsafe_allow_html=True)

# # =========================================================
# # SIDEBAR
# # =========================================================

# st.sidebar.markdown("## 🗺️ Location & Crop")
# region = st.sidebar.selectbox("📍 Region", REGIONS)
# city   = st.sidebar.selectbox("🏙️ City",   CITIES,
#                                index=CITIES.index(st.session_state.city)
#                                if st.session_state.city in CITIES else 0)
# crop   = st.sidebar.selectbox("🌾 Crop",   CROPS)
# st.session_state.city = city; st.session_state.region = region; st.session_state.crop = crop

# st.sidebar.markdown("---")
# st.sidebar.markdown("**🧪 Soil Nutrients (kg/ha)**")
# N  = st.sidebar.slider("Nitrogen (N)",   46,  558, 200, help="Punjab dataset range: 46–558 kg/ha")
# P  = st.sidebar.slider("Phosphorus (P)", 5,   40,  20,  help="Punjab dataset range: 5–40 kg/ha")
# K  = st.sidebar.slider("Potassium (K)",  107, 384, 200, help="Punjab dataset range: 107–384 kg/ha")

# st.sidebar.markdown("**🌿 Soil Properties**")
# ph      = st.sidebar.slider("Soil pH",          6.5, 8.3, 7.0, step=0.05)
# org_mat = st.sidebar.slider("Organic Matter %", 0.0, 5.0, 1.5, step=0.1)

# st.sidebar.markdown("**📈 Scores**")
# rec_score   = st.sidebar.slider("Recovery Score",       0,    100,  55)
# trans_score = st.sidebar.slider("Transition Score",     18,   86,   50)
# weekly_imp  = st.sidebar.slider("Weekly Improvement %", -10.0, 20.0, 2.0, step=0.5)

# st.sidebar.markdown("---")

# # Sidebar weather preview
# if OWM_API_KEY != "YOUR_OPENWEATHER_API_KEY":
#     w_preview = get_weather(city)
#     if not w_preview.get("error"):
#         st.sidebar.markdown(
#             f'<div class="weather-card"><b>🌤 {city}</b><br>'
#             f'🌡 {w_preview["temperature"]}°C &nbsp;|&nbsp; '
#             f'💧 {w_preview["humidity"]}% &nbsp;|&nbsp; '
#             f'🌧 {w_preview["rainfall"]} mm<br>'
#             f'<small>{w_preview["description"]} · 💨 {w_preview["wind_speed"]} m/s</small>'
#             f'</div>', unsafe_allow_html=True)
# else:
#     st.sidebar.info("ℹ️ Set OWM_API_KEY env var for live weather.")

# predict_btn = st.sidebar.button("🔍 Run Prediction", use_container_width=True, type="primary")

# st.sidebar.markdown("---")
# if model_exists():
#     st.sidebar.success("✅ Model ready")
#     if st.session_state.model_accuracy:
#         st.sidebar.metric("Accuracy", f"{st.session_state.model_accuracy:.1%}")
# else:
#     st.sidebar.warning("⚠️ Train model first (Train Model tab)")

# # =========================================================
# # PREDICTION TRIGGER
# # =========================================================

# if predict_btn:
#     if not model_exists():
#         st.error("❌ No trained model found. Open the **Train Model** tab and upload your dataset first.")
#     else:
#         w = get_weather(city)
#         temp = w["temperature"] if not w.get("error") else 30
#         rain = w["rainfall"]    if not w.get("error") else 5
#         hum  = w["humidity"]    if not w.get("error") else 60

#         if st.session_state.iot_use_for_prediction and st.session_state.iot_history:
#             lt = st.session_state.iot_history[-1]
#             N = lt["Nitrogen"]; P = lt["Phosphorus"]; K = lt["Potassium"]
#             ph = lt["Soil_pH"]; temp = lt["Temperature"]; hum = lt["Humidity"]

#         row = {
#             "Current_Temp": temp, "Current_Rain": rain, "Current_Hum": hum,
#             "Current_Soil_pH": ph, "Current_Soil_Organic_Matter_Percent": org_mat,
#             "Current_Soil_Nitrogen_kg_per_ha": N, "Current_Soil_Phosphorus_kg_per_ha": P,
#             "Current_Soil_Potassium_kg_per_ha": K,
#             "Soil_Recovery_Score": rec_score, "Weekly_Improvement_Percent": weekly_imp,
#             "Transition_Success_Score": trans_score, "Region": region, "Crop_Name": crop,
#         }
#         pred, proba = predict_single(row)
#         st.session_state.update(dict(
#             done=True, weather=w, prediction=pred, proba=proba,
#             N=N, P=P, K=K, pH=ph, recovery_score=rec_score, transition_score=trans_score,
#         ))

# # =========================================================
# # TABS
# # =========================================================

# tabs = st.tabs([
#     "🏠 Dashboard", "📊 Train Model", "📁 Bulk Prediction",
#     "🧠 Manual Prediction", "📡 IoT Monitor",
#     "🌦 Weather", "📈 Analytics", "🤖 AI Assistant",
# ])
# tab_dash, tab_train, tab_bulk, tab_manual, tab_iot, tab_weather, tab_analytics, tab_chat = tabs

# # ─────────────────────────────────────────────────────────
# # DASHBOARD
# # ─────────────────────────────────────────────────────────

# with tab_dash:
#     k1, k2, k3, k4, k5 = st.columns(5)
#     k1.metric("📍 Region",       region)
#     k2.metric("🏙️ City",          city)
#     k3.metric("🌾 Crop",          crop)
#     k4.metric("👩‍🌾 Total Farmers", "800")
#     k5.metric("📅 Weeks Tracked", "7")

#     st.markdown("---")

#     if st.session_state.done:
#         st.markdown('<div class="section-title">🎯 Current Prediction</div>', unsafe_allow_html=True)
#         render_alert(st.session_state.prediction)
#         st.markdown("<br>", unsafe_allow_html=True)

#         r1, r2, r3, r4 = st.columns(4)
#         r1.metric("🌾 Crop",             st.session_state.crop)
#         r2.metric("🧮 Recovery Score",   f"{st.session_state.recovery_score}/100")
#         r3.metric("📈 Transition Score", f"{st.session_state.transition_score}/100")
#         r4.metric("🧪 Soil pH",          st.session_state.pH)

#         proba_df = pd.DataFrame(list(st.session_state.proba.items()), columns=["Alert", "Prob"])
#         fig_d = px.pie(proba_df, values="Prob", names="Alert", hole=0.55,
#                        title="Prediction Confidence",
#                        color="Alert",
#                        color_discrete_map={
#                            "SAFE": "#16a34a", "PROCEED WITH CAUTION": "#d97706",
#                            "DELAY TRANSITION": "#ea580c", "STOP TRANSITION": "#dc2626"})
#         fig_d.update_layout(height=340)
#         st.plotly_chart(fig_d, use_container_width=True)

#         if st.session_state.N and st.session_state.N > 400:
#             st.warning("⚠️ Nitrogen very high (>400 kg/ha) — reduce chemical fertilizer input")
#         if st.session_state.pH and st.session_state.pH > 8.0:
#             st.warning("⚠️ Alkaline soil (pH>8.0) — consider gypsum/sulfur treatment")
#         if st.session_state.recovery_score and st.session_state.recovery_score < 35:
#             st.error("🚨 Recovery score critically low — urgent soil remediation required")
#     else:
#         st.info("👈 Select Region, City, Crop and soil values in the sidebar — then click **Run Prediction**.")

#     st.markdown("---")
#     st.markdown('<div class="section-title">📊 Dataset Overview</div>', unsafe_allow_html=True)
#     d1, d2 = st.columns(2)
#     with d1:
#         alert_data = pd.DataFrame({
#             "Alert": ["STOP TRANSITION", "DELAY TRANSITION", "PROCEED WITH CAUTION", "SAFE"],
#             "Count": [2980, 2021, 571, 28],
#         })
#         fig_a = px.bar(alert_data, x="Alert", y="Count", color="Alert",
#                        color_discrete_map={
#                            "SAFE": "#16a34a", "PROCEED WITH CAUTION": "#d97706",
#                            "DELAY TRANSITION": "#ea580c", "STOP TRANSITION": "#dc2626"},
#                        title="Alert Status Distribution (5,600 records)")
#         fig_a.update_layout(showlegend=False, height=320)
#         st.plotly_chart(fig_a, use_container_width=True)
#     with d2:
#         wk = pd.DataFrame({"Week": [1,2,3,4,5,6,7],
#                             "Recovery": [32,38,44,51,59,68,78],
#                             "Transition": [28,34,41,48,56,65,74]})
#         fig_w = go.Figure()
#         fig_w.add_trace(go.Scatter(x=wk["Week"], y=wk["Recovery"],
#                                    mode="lines+markers", name="Recovery",
#                                    line=dict(color="#16a34a", width=3)))
#         fig_w.add_trace(go.Scatter(x=wk["Week"], y=wk["Transition"],
#                                    mode="lines+markers", name="Transition",
#                                    line=dict(color="#15803d", width=3, dash="dash")))
#         fig_w.update_layout(title="Week-by-Week Score Progression", height=320,
#                             xaxis_title="Week", yaxis_title="Score")
#         st.plotly_chart(fig_w, use_container_width=True)

#     st.markdown('<div class="section-title">🔄 42-Day Before / After Comparison</div>', unsafe_allow_html=True)
#     compare = pd.DataFrame({
#         "Parameter": ["Soil pH", "Nitrogen (kg/ha)", "Phosphorus (kg/ha)",
#                       "Potassium (kg/ha)", "Organic Matter %", "Recovery Score"],
#         "Day 1":  [7.8, 380, 16, 280, 0.8, 32],
#         "Day 42": [7.1, 220, 28, 190, 2.1, 74],
#     })
#     fig_ba = px.bar(compare, x="Parameter", y=["Day 1", "Day 42"], barmode="group",
#                     title="Soil Parameters: Day 1 → Day 42",
#                     color_discrete_map={"Day 1": "#dc2626", "Day 42": "#16a34a"})
#     fig_ba.update_layout(height=360)
#     st.plotly_chart(fig_ba, use_container_width=True)

# # ─────────────────────────────────────────────────────────
# # TRAIN MODEL
# # ─────────────────────────────────────────────────────────

# with tab_train:
#     st.header("📊 Train Soil Recovery AI Model")
#     st.markdown('<div class="info-box">Upload the <b>Punjab Smart Agri Ecosystem Dataset</b> (.xlsx or .csv). RandomForest learns to classify <b>Alert Status</b> from soil, weather, and transition features.</div>', unsafe_allow_html=True)
#     uploaded = st.file_uploader("Upload Dataset", type=["xlsx","csv"], key="train_upload")
#     if uploaded:
#         df = load_dataset(uploaded)
#         st.success(f"✅ Loaded {df.shape[0]:,} rows × {df.shape[1]} columns")
#         col_a, col_b = st.columns(2)
#         with col_a:
#             st.dataframe(df.head(8), use_container_width=True)
#         with col_b:
#             if TARGET in df.columns:
#                 ac = df[TARGET].value_counts().reset_index()
#                 ac.columns = ["Alert", "Count"]
#                 fig_ac = px.bar(ac, x="Alert", y="Count", color="Alert",
#                                 color_discrete_map={
#                                     "SAFE": "#16a34a", "PROCEED WITH CAUTION": "#d97706",
#                                     "DELAY TRANSITION": "#ea580c", "STOP TRANSITION": "#dc2626"},
#                                 title="Alert Distribution")
#                 fig_ac.update_layout(showlegend=False, height=300)
#                 st.plotly_chart(fig_ac, use_container_width=True)

#         missing = [f for f in FEATURES + [TARGET] if f not in df.columns]
#         if missing:
#             st.error(f"❌ Missing columns: {missing}")
#         else:
#             if st.button("🚀 Train AI Model", type="primary"):
#                 with st.spinner("Training RandomForest (300 trees) on your dataset..."):
#                     acc, report, clf = train_model(df)
#                 if acc is None:
#                     st.error("Training failed — check dataset columns.")
#                 else:
#                     st.session_state.model_accuracy = acc
#                     st.success("✅ Model trained and saved!")
#                     m1, m2, m3 = st.columns(3)
#                     m1.metric("Overall Accuracy", f"{acc:.1%}")
#                     m2.metric("Total Samples", f"{len(df):,}")
#                     m3.metric("Alert Classes", "4")
#                     st.markdown("**Per-Class Report:**")
#                     st.dataframe(pd.DataFrame(report).transpose().style.format("{:.2f}"),
#                                  use_container_width=True)
#                     imp = pd.Series(clf.feature_importances_, index=FEATURES).sort_values()
#                     fig_imp = px.bar(imp.reset_index(), x=0, y="index", orientation="h",
#                                      color=0, color_continuous_scale="Greens",
#                                      title="Feature Importances",
#                                      labels={"index": "Feature", 0: "Importance"})
#                     fig_imp.update_layout(height=420, coloraxis_showscale=False)
#                     st.plotly_chart(fig_imp, use_container_width=True)

# # ─────────────────────────────────────────────────────────
# # BULK PREDICTION
# # ─────────────────────────────────────────────────────────

# with tab_bulk:
#     st.header("📁 Bulk Dataset Prediction")
#     st.markdown('<div class="info-box">Upload a dataset with the same column structure. The AI predicts <b>Alert Status</b> for every row and provides a downloadable CSV.</div>', unsafe_allow_html=True)
#     if not model_exists():
#         st.error("❌ No trained model. Go to **Train Model** tab first.")
#     else:
#         pred_file = st.file_uploader("Upload Prediction Dataset", type=["xlsx","csv"], key="bulk_upload")
#         if pred_file:
#             df = load_dataset(pred_file)
#             st.write(f"Loaded **{df.shape[0]:,}** rows")
#             st.dataframe(df.head(), use_container_width=True)
#             missing = [f for f in FEATURES if f not in df.columns]
#             if missing:
#                 st.error(f"Missing columns: {missing}")
#             else:
#                 if st.button("🔍 Predict All Rows", type="primary"):
#                     with st.spinner("Running bulk predictions..."):
#                         df["Predicted_Alert"] = predict_bulk(df)
#                     st.success("✅ Prediction complete!")
#                     disp = [c for c in ["Farmer_ID","Crop_Name","Region",
#                                         "Soil_Recovery_Score","Predicted_Alert"] if c in df.columns]
#                     st.dataframe(df[disp].head(30), use_container_width=True)
#                     ac = df["Predicted_Alert"].value_counts().reset_index()
#                     ac.columns = ["Alert","Count"]
#                     fig_r = px.pie(ac, values="Count", names="Alert", hole=0.4,
#                                    color="Alert",
#                                    color_discrete_map={
#                                        "SAFE": "#16a34a", "PROCEED WITH CAUTION": "#d97706",
#                                        "DELAY TRANSITION": "#ea580c", "STOP TRANSITION": "#dc2626"},
#                                    title="Predicted Alert Distribution")
#                     st.plotly_chart(fig_r, use_container_width=True)
#                     st.download_button("⬇ Download Results CSV",
#                                        df.to_csv(index=False).encode("utf-8"),
#                                        "soil_predictions.csv", "text/csv")

# # ─────────────────────────────────────────────────────────
# # MANUAL PREDICTION
# # ─────────────────────────────────────────────────────────

# with tab_manual:
#     st.header("🧠 Manual Prediction")
#     st.markdown('<div class="info-box">Enter all field parameters manually. The AI predicts transition safety and provides confidence scores plus soil health warnings.</div>', unsafe_allow_html=True)
#     if not model_exists():
#         st.error("❌ No trained model. Go to **Train Model** tab first.")
#     else:
#         col1, col2, col3 = st.columns(3)
#         with col1:
#             st.subheader("🌾 Crop & Location")
#             m_region = st.selectbox("Region", REGIONS, key="m_region")
#             m_city   = st.selectbox("City",   CITIES,  key="m_city")
#             m_crop   = st.selectbox("Crop",   CROPS,   key="m_crop")
#             m_phase  = st.selectbox("Transition Phase", TRANSITION_PHASES, key="m_phase")
#             m_arch   = st.selectbox("Farmer Archetype", FARMER_ARCHETYPES, key="m_arch")
#         with col2:
#             st.subheader("🌦 Weather")
#             m_temp = st.slider("Temperature (°C)", 7.0,  51.0, 28.0, key="m_temp")
#             m_rain = st.slider("Rainfall (mm)",    0.0,  342.0, 10.0, key="m_rain")
#             m_hum  = st.slider("Humidity (%)",     30.0, 107.0, 65.0, key="m_hum")
#             st.subheader("🧪 Soil")
#             m_ph  = st.slider("Soil pH",          6.5, 8.3, 7.0, step=0.05, key="m_ph")
#             m_org = st.slider("Organic Matter %", 0.0, 5.0, 1.5, step=0.1,  key="m_org")
#         with col3:
#             st.subheader("🧬 Nutrients (kg/ha)")
#             m_N = st.slider("Nitrogen",   46,  558, 200, key="m_N", help="Safe: 150–300 kg/ha")
#             m_P = st.slider("Phosphorus", 5,   40,  20,  key="m_P", help="Safe: 15–30 kg/ha")
#             m_K = st.slider("Potassium",  107, 384, 200, key="m_K", help="Safe: 150–250 kg/ha")
#             st.subheader("📈 Scores")
#             m_rec  = st.slider("Recovery Score",       0,    100, 55,  key="m_rec")
#             m_ts   = st.slider("Transition Score",     18,   86,  50,  key="m_ts")
#             m_wimp = st.slider("Weekly Improvement %", -10.0, 20.0, 2.0, step=0.5, key="m_wimp")

#         if st.button("🚀 Predict", type="primary", use_container_width=True):
#             row = {
#                 "Current_Temp": m_temp, "Current_Rain": m_rain, "Current_Hum": m_hum,
#                 "Current_Soil_pH": m_ph, "Current_Soil_Organic_Matter_Percent": m_org,
#                 "Current_Soil_Nitrogen_kg_per_ha": m_N, "Current_Soil_Phosphorus_kg_per_ha": m_P,
#                 "Current_Soil_Potassium_kg_per_ha": m_K,
#                 "Soil_Recovery_Score": m_rec, "Weekly_Improvement_Percent": m_wimp,
#                 "Transition_Success_Score": m_ts, "Region": m_region, "Crop_Name": m_crop,
#             }
#             pred, proba = predict_single(row)
#             st.markdown("---")
#             st.subheader("📊 Prediction Result")
#             render_alert(pred)

#             proba_df = pd.DataFrame(list(proba.items()), columns=["Alert", "Probability %"])
#             proba_df = proba_df.sort_values("Probability %", ascending=False)
#             fig_p = px.bar(proba_df, x="Alert", y="Probability %", color="Alert",
#                            color_discrete_map={
#                                "SAFE": "#16a34a", "PROCEED WITH CAUTION": "#d97706",
#                                "DELAY TRANSITION": "#ea580c", "STOP TRANSITION": "#dc2626"},
#                            title="Confidence per Alert Class")
#             fig_p.update_layout(showlegend=False, yaxis_range=[0,110], height=320)
#             st.plotly_chart(fig_p, use_container_width=True)

#             npk_df = pd.DataFrame({
#                 "Nutrient": ["Nitrogen", "Phosphorus", "Potassium"],
#                 "Your Value": [m_N, m_P, m_K],
#                 "Healthy Target": [225, 22, 245],
#             })
#             fig_npk = px.bar(npk_df, x="Nutrient", y=["Your Value","Healthy Target"],
#                              barmode="group", title="NPK vs Healthy Target",
#                              color_discrete_map={"Your Value":"#15803d","Healthy Target":"#86efac"})
#             fig_npk.update_layout(height=320)
#             st.plotly_chart(fig_npk, use_container_width=True)

#             warns = []
#             if m_N > 400:  warns.append("⚠️ Nitrogen dangerously high — leaching risk; reduce chemical fertilizer")
#             if m_P < 10:   warns.append("⚠️ Phosphorus very low — root development stunted; apply DAP")
#             if m_ph > 8.0: warns.append("⚠️ Alkaline soil — apply gypsum or sulfur to reduce pH")
#             if m_org < 1.0:warns.append("⚠️ Organic matter critically low — add compost/FYM urgently")
#             if m_temp > 42:warns.append("⚠️ Extreme heat — halt all fertilizer applications")
#             if m_rain > 150:warns.append("⚠️ Heavy rainfall — nutrient runoff risk; delay applications")
#             for w in warns: st.warning(w)
#             if not warns:   st.success("✅ No critical warnings detected.")

# # ─────────────────────────────────────────────────────────
# # IoT MONITOR
# # ─────────────────────────────────────────────────────────

# with tab_iot:
#     st.header("📡 Live IoT Sensor Monitoring")
#     st.caption("Real-time soil & weather telemetry — simulation by default. Connect an ESP32/REST API for live hardware.")

#     ctrl1, ctrl2, ctrl3, ctrl4 = st.columns([2, 2.5, 1.5, 1.5])
#     with ctrl1:
#         src = st.selectbox("📡 Data Source",
#                            ["Simulated","REST API","Firebase (coming soon)"], key="iot_src")
#     with ctrl2:
#         api_url = ""
#         if src == "REST API":
#             api_url = st.text_input("🔗 Endpoint", placeholder="http://esp32.local/sensors")
#         else:
#             st.text_input("🔗 Endpoint", value="N/A", disabled=True)
#     with ctrl3:
#         auto_ref = st.toggle("🔄 Auto (5s)", value=st.session_state.iot_auto_refresh)
#         st.session_state.iot_auto_refresh = auto_ref
#     with ctrl4:
#         man_ref = st.button("🔃 Refresh Now", type="primary", use_container_width=True)

#     if man_ref or auto_ref or not st.session_state.iot_history:
#         new = fetch_sensor_data(src, api_url)
#         st.session_state.iot_history.append(new)
#         st.session_state.iot_last_update = new["timestamp"]
#         if len(st.session_state.iot_history) > 60:
#             st.session_state.iot_history = st.session_state.iot_history[-60:]

#     if st.session_state.iot_history:
#         latest = st.session_state.iot_history[-1]
#         prev   = st.session_state.iot_history[-2] if len(st.session_state.iot_history) >= 2 else latest

#         st.markdown(f"**🕒 Last update:** `{latest['timestamp']}` | "
#                     f"**Source:** `{latest['source']}` | "
#                     f"**Readings stored:** `{len(st.session_state.iot_history)}`")

#         s1, s2, s3, s4 = st.columns(4)
#         s1.metric("💧 Soil Moisture", f"{latest['Soil_Moisture']} %",
#                   delta=round(latest['Soil_Moisture']-prev['Soil_Moisture'],2))
#         s2.metric("🌡 Temperature",   f"{latest['Temperature']} °C",
#                   delta=round(latest['Temperature']-prev['Temperature'],2))
#         s3.metric("💨 Humidity",      f"{latest['Humidity']} %",
#                   delta=round(latest['Humidity']-prev['Humidity'],2))
#         s4.metric("🧪 Soil pH",       f"{latest['Soil_pH']}",
#                   delta=round(latest['Soil_pH']-prev['Soil_pH'],2))

#         n1, n2, n3, n4 = st.columns(4)
#         n1.metric("🟢 Nitrogen",   f"{latest['Nitrogen']} kg/ha",
#                   delta=round(latest['Nitrogen']-prev['Nitrogen'],2))
#         n2.metric("🟠 Phosphorus", f"{latest['Phosphorus']} kg/ha",
#                   delta=round(latest['Phosphorus']-prev['Phosphorus'],2))
#         n3.metric("🟣 Potassium",  f"{latest['Potassium']} kg/ha",
#                   delta=round(latest['Potassium']-prev['Potassium'],2))

#         ok = (latest['Soil_Moisture'] >= 20 and latest['Temperature'] <= 42
#               and 6.5 <= latest['Soil_pH'] <= 8.3)
#         sc = "#16a34a" if ok else "#dc2626"
#         st_txt = "🟢 All Systems Normal" if ok else "🔴 Alerts Active"
#         n4.markdown(
#             f'<div style="background:{sc}18;border-left:5px solid {sc};'
#             f'padding:12px;border-radius:10px;text-align:center;'
#             f'color:{sc};font-weight:700;margin-top:8px;">{st_txt}</div>',
#             unsafe_allow_html=True)

#         if latest['Temperature'] > 42:
#             st.error(f"🌡 Extreme heat ({latest['Temperature']}°C) — halt fertilizer applications")
#         if latest['Soil_Moisture'] < 25:
#             st.warning(f"💧 Low moisture ({latest['Soil_Moisture']}%) — irrigation needed")
#         if latest['Soil_pH'] > 8.3:
#             st.warning(f"🧪 Alkaline pH ({latest['Soil_pH']}) — apply gypsum")
#         if latest['Humidity'] > 95:
#             st.warning(f"💨 High humidity ({latest['Humidity']}%) — fungal disease risk")

#         if len(st.session_state.iot_history) >= 2:
#             hist_df = pd.DataFrame(st.session_state.iot_history)
#             ct1, ct2 = st.tabs(["🌡 Environmental","🧪 Nutrients"])
#             with ct1:
#                 fig_env = go.Figure()
#                 for col, color, name in [
#                     ("Temperature","#dc2626","Temp (°C)"),
#                     ("Humidity","#2563eb","Humidity (%)"),
#                     ("Soil_Moisture","#0891b2","Moisture (%)"),
#                 ]:
#                     fig_env.add_trace(go.Scatter(x=hist_df["timestamp"], y=hist_df[col],
#                                                   mode="lines+markers", name=name,
#                                                   line=dict(color=color, width=2)))
#                 fig_env.add_trace(go.Scatter(x=hist_df["timestamp"], y=hist_df["Soil_pH"]*10,
#                                               mode="lines+markers", name="pH (×10)",
#                                               line=dict(color="#7c3aed", width=2, dash="dot")))
#                 fig_env.update_layout(title="Environmental Sensor Trends", height=370, hovermode="x unified")
#                 st.plotly_chart(fig_env, use_container_width=True)
#             with ct2:
#                 fig_npk = go.Figure()
#                 for col, color, name in [
#                     ("Nitrogen","#16a34a","Nitrogen"), ("Phosphorus","#ea580c","Phosphorus"),
#                     ("Potassium","#7c3aed","Potassium"),
#                 ]:
#                     fig_npk.add_trace(go.Scatter(x=hist_df["timestamp"], y=hist_df[col],
#                                                   mode="lines+markers", name=name,
#                                                   line=dict(color=color, width=2)))
#                 fig_npk.update_layout(title="Soil Nutrients (kg/ha)", height=370, hovermode="x unified")
#                 st.plotly_chart(fig_npk, use_container_width=True)

#         st.markdown("---")
#         use_iot = st.checkbox("🔗 Use live IoT data for next prediction",
#                               value=st.session_state.iot_use_for_prediction)
#         st.session_state.iot_use_for_prediction = use_iot
#         if use_iot:
#             st.success(f"✅ IoT linked — N={latest['Nitrogen']} | P={latest['Phosphorus']} | K={latest['Potassium']}")

#         with st.expander("📋 Raw Sensor History"):
#             st.dataframe(pd.DataFrame(st.session_state.iot_history[::-1]),
#                          use_container_width=True, hide_index=True)
#             if st.button("🗑 Clear History"):
#                 st.session_state.iot_history = []; st.rerun()

#     if st.session_state.iot_auto_refresh:
#         time.sleep(5); st.rerun()

# # ─────────────────────────────────────────────────────────
# # WEATHER
# # ─────────────────────────────────────────────────────────

# with tab_weather:
#     st.header("🌦 Live Weather Monitor")
#     st.markdown('<div class="info-box">Fetch real-time weather for Punjab cities. Extreme conditions trigger automatic STOP / DELAY advisories for fertilizer transition.</div>', unsafe_allow_html=True)

#     wcol1, wcol2 = st.columns([2,1])
#     with wcol1:
#         w_city = st.selectbox("Select City", CITIES,
#                               index=CITIES.index(city) if city in CITIES else 0, key="w_city")
#     with wcol2:
#         fetch_w = st.button("🌍 Fetch Weather", type="primary", use_container_width=True)

#     if fetch_w:
#         w = get_weather(w_city)
#         if w.get("error"):
#             st.warning("Live weather unavailable — showing simulated values.")
#             w = {"temperature":30,"feels_like":32,"humidity":62,
#                  "rainfall":5,"description":"Clear Sky","wind_speed":3.5,"error":None}

#         wm1,wm2,wm3,wm4,wm5 = st.columns(5)
#         wm1.metric("🌡 Temperature", f"{w['temperature']} °C", delta=f"Feels {w['feels_like']} °C")
#         wm2.metric("💧 Humidity",    f"{w['humidity']} %")
#         wm3.metric("🌧 Rainfall",    f"{w['rainfall']} mm")
#         wm4.metric("💨 Wind",        f"{w['wind_speed']} m/s")
#         wm5.metric("☁ Condition",   w["description"])

#         fig_g = go.Figure(go.Indicator(
#             mode="gauge+number+delta", value=w["temperature"],
#             title={"text":"Temperature (°C)","font":{"size":18}},
#             delta={"reference":35},
#             gauge={"axis":{"range":[0,55]}, "bar":{"color":"#ea580c"},
#                    "steps":[{"range":[0,25],"color":"#dcfce7"},
#                              {"range":[25,38],"color":"#fef3c7"},
#                              {"range":[38,55],"color":"#fee2e2"}],
#                    "threshold":{"line":{"color":"#dc2626","width":4},"value":42}}))
#         fig_g.update_layout(height=320)
#         st.plotly_chart(fig_g, use_container_width=True)

#         if w["temperature"] > 42:
#             st.error("🚨 EXTREME HEAT — STOP all fertilizer applications immediately")
#         elif w["temperature"] > 38:
#             st.warning("⚠️ High temperature — monitor crops for heat stress")
#         if w["rainfall"] > 150:
#             st.error("🚨 HEAVY RAINFALL — halt all transition activities; flood risk")
#         elif w["rainfall"] > 80:
#             st.warning("⚠️ Heavy rain — nutrient runoff risk; delay applications")
#         if w["humidity"] < 30:
#             st.warning("⚠️ Very low humidity — increase irrigation frequency")

#         st.markdown('<div class="section-title">🏙️ Punjab City Risk Overview</div>', unsafe_allow_html=True)
#         random.seed(42)
#         city_risk = pd.DataFrame({
#             "City": CITIES,
#             "Temp (°C)": [round(random.uniform(24,43),1) for _ in CITIES],
#             "Humidity (%)": [round(random.uniform(40,85),1) for _ in CITIES],
#             "Risk Level": random.choices(["Low","Medium","High","Extreme"], k=len(CITIES)),
#         })
#         fig_cr = px.scatter(city_risk, x="Temp (°C)", y="Humidity (%)",
#                             color="Risk Level", size=[20]*len(CITIES), text="City",
#                             color_discrete_map={"Low":"#16a34a","Medium":"#d97706",
#                                                 "High":"#ea580c","Extreme":"#dc2626"},
#                             title="Temperature vs Humidity — City Risk Map")
#         fig_cr.update_traces(textposition="top center")
#         fig_cr.update_layout(height=420)
#         st.plotly_chart(fig_cr, use_container_width=True)

# # ─────────────────────────────────────────────────────────
# # ANALYTICS
# # ─────────────────────────────────────────────────────────

# with tab_analytics:
#     st.header("📈 Soil Recovery Analytics")
#     st.markdown('<div class="info-box">Upload the dataset to generate deep analytics on NPK trends, weather impact, farmer archetypes, transition phases and cost savings.</div>', unsafe_allow_html=True)
#     ana_file = st.file_uploader("Upload Dataset", type=["xlsx","csv"], key="ana_upload")

#     if ana_file:
#         df = load_dataset(ana_file)
#         st.success(f"✅ {df.shape[0]:,} records loaded")

#         with st.expander("🔍 Filters", expanded=True):
#             fc1,fc2,fc3,fc4 = st.columns(4)
#             sel_crops  = fc1.multiselect("Crop",      CROPS,             default=CROPS)
#             sel_weeks  = fc2.multiselect("Week",
#                          sorted(df["Week_Number"].unique()) if "Week_Number" in df.columns else [],
#                          default=sorted(df["Week_Number"].unique()) if "Week_Number" in df.columns else [])
#             sel_arch   = fc3.multiselect("Archetype", FARMER_ARCHETYPES, default=FARMER_ARCHETYPES)
#             sel_alerts = fc4.multiselect("Alert",     ALERT_CLASSES,     default=ALERT_CLASSES)

#         mask = pd.Series([True]*len(df))
#         if "Crop_Name"        in df.columns and sel_crops:  mask &= df["Crop_Name"].isin(sel_crops)
#         if "Week_Number"      in df.columns and sel_weeks:  mask &= df["Week_Number"].isin(sel_weeks)
#         if "Farmer_Archetype" in df.columns and sel_arch:   mask &= df["Farmer_Archetype"].isin(sel_arch)
#         if "Alert_Status"     in df.columns and sel_alerts: mask &= df["Alert_Status"].isin(sel_alerts)
#         dff = df[mask]
#         st.write(f"Showing **{len(dff):,}** records")

#         if "Week_Number" in dff.columns:
#             st.markdown('<div class="section-title">📈 Weekly Recovery by Crop</div>', unsafe_allow_html=True)
#             rc = dff.groupby(["Week_Number","Crop_Name"])["Soil_Recovery_Score"].mean().reset_index()
#             fig1 = px.line(rc, x="Week_Number", y="Soil_Recovery_Score", color="Crop_Name",
#                            markers=True, title="Average Soil Recovery Score per Week")
#             fig1.update_layout(height=380)
#             st.plotly_chart(fig1, use_container_width=True)

#             st.markdown('<div class="section-title">🧪 NPK Weekly Trends</div>', unsafe_allow_html=True)
#             npk = dff.groupby("Week_Number")[
#                 ["Current_Soil_Nitrogen_kg_per_ha","Current_Soil_Phosphorus_kg_per_ha",
#                  "Current_Soil_Potassium_kg_per_ha"]].mean().reset_index()
#             fig2 = go.Figure()
#             for col, color, label in [
#                 ("Current_Soil_Nitrogen_kg_per_ha","#16a34a","Nitrogen"),
#                 ("Current_Soil_Phosphorus_kg_per_ha","#d97706","Phosphorus"),
#                 ("Current_Soil_Potassium_kg_per_ha","#7c3aed","Potassium"),
#             ]:
#                 fig2.add_trace(go.Scatter(x=npk["Week_Number"], y=npk[col],
#                                           mode="lines+markers", name=label,
#                                           line=dict(color=color, width=3)))
#             fig2.update_layout(title="Average NPK per Week (kg/ha)", height=380)
#             st.plotly_chart(fig2, use_container_width=True)

#         st.markdown('<div class="section-title">🌦 Weather Impact on Transition</div>', unsafe_allow_html=True)
#         fig3 = px.scatter(dff, x="Current_Temp", y="Transition_Success_Score",
#                           color="Weather_Risk_Level", size="Soil_Recovery_Score",
#                           hover_data=["Crop_Name","Farmer_Archetype"],
#                           title="Temperature vs Transition Success (size = Recovery Score)",
#                           color_discrete_map={"Low":"#16a34a","Medium":"#d97706",
#                                               "High":"#ea580c","Extreme":"#dc2626"})
#         fig3.update_layout(height=420)
#         st.plotly_chart(fig3, use_container_width=True)

#         st.markdown('<div class="section-title">⚠️ Alert Distribution</div>', unsafe_allow_html=True)
#         c4a, c4b = st.columns(2)
#         with c4a:
#             acnt = dff["Alert_Status"].value_counts().reset_index()
#             acnt.columns = ["Alert","Count"]
#             fig4a = px.pie(acnt, values="Count", names="Alert", hole=0.45,
#                            color="Alert",
#                            color_discrete_map={"SAFE":"#16a34a","PROCEED WITH CAUTION":"#d97706",
#                                                "DELAY TRANSITION":"#ea580c","STOP TRANSITION":"#dc2626"},
#                            title="Alert Distribution")
#             fig4a.update_layout(height=360)
#             st.plotly_chart(fig4a, use_container_width=True)
#         with c4b:
#             fig4b = px.histogram(dff, x="Transition_Success_Score", color="Alert_Status", nbins=30,
#                                  title="Transition Score by Alert",
#                                  color_discrete_map={"SAFE":"#16a34a","PROCEED WITH CAUTION":"#d97706",
#                                                      "DELAY TRANSITION":"#ea580c","STOP TRANSITION":"#dc2626"})
#             fig4b.update_layout(height=360)
#             st.plotly_chart(fig4b, use_container_width=True)

#         st.markdown('<div class="section-title">👩‍🌾 Farmer Archetype Performance</div>', unsafe_allow_html=True)
#         arch = dff.groupby("Farmer_Archetype")[
#             ["Soil_Recovery_Score","Transition_Success_Score"]].mean().reset_index()
#         fig5 = px.bar(arch, x="Farmer_Archetype", y=["Soil_Recovery_Score","Transition_Success_Score"],
#                       barmode="group", title="Recovery & Transition Score by Archetype",
#                       color_discrete_map={"Soil_Recovery_Score":"#16a34a","Transition_Success_Score":"#15803d"})
#         fig5.update_layout(height=360)
#         st.plotly_chart(fig5, use_container_width=True)

#         st.markdown('<div class="section-title">💰 Cost Savings by Crop (₹/Acre)</div>', unsafe_allow_html=True)
#         cost = dff.groupby("Crop_Name")["Cost_Saving_INR_per_Acre"].mean().reset_index()
#         fig6 = px.bar(cost, x="Crop_Name", y="Cost_Saving_INR_per_Acre", color="Crop_Name",
#                       title="Average Cost Saving per Crop",
#                       color_discrete_sequence=px.colors.sequential.Greens_r)
#         fig6.update_layout(height=340, showlegend=False)
#         st.plotly_chart(fig6, use_container_width=True)

#         st.markdown('<div class="section-title">🧫 Soil pH by Transition Phase</div>', unsafe_allow_html=True)
#         phase_order = ["Start","Early Shift","Mid Shift","Balanced Shift","Organic Dominant"]
#         ph_ph = dff.groupby("Transition_Phase")["Current_Soil_pH"].mean().reset_index()
#         ph_ph["Transition_Phase"] = pd.Categorical(ph_ph["Transition_Phase"],
#                                                     categories=phase_order, ordered=True)
#         fig7 = px.bar(ph_ph.sort_values("Transition_Phase"),
#                       x="Transition_Phase", y="Current_Soil_pH",
#                       color="Current_Soil_pH", color_continuous_scale="Greens",
#                       title="Average Soil pH across Transition Phases")
#         fig7.update_layout(height=340)
#         st.plotly_chart(fig7, use_container_width=True)

#         with st.expander("📋 Raw Data Sample"):
#             st.dataframe(dff.sample(min(20,len(dff)), random_state=42).reset_index(drop=True),
#                          use_container_width=True)
#     else:
#         st.info("📁 Upload your dataset to see live analytics.")
#         arch_data = pd.DataFrame({
#             "Archetype": ["Success","Moderate","Struggling","Weather-Hit"],
#             "Recovery":  [72, 55, 38, 44],
#             "Transition":[68, 51, 35, 41],
#         })
#         fig_s = px.bar(arch_data, x="Archetype", y=["Recovery","Transition"],
#                        barmode="group", title="Sample: Score by Archetype (upload dataset for live data)")
#         st.plotly_chart(fig_s, use_container_width=True)

# # ─────────────────────────────────────────────────────────
# # AI ASSISTANT
# # ─────────────────────────────────────────────────────────

# with tab_chat:
#     st.header("🤖 AI Farming Assistant")
#     _N = st.session_state.get("N"); _P = st.session_state.get("P"); _K = st.session_state.get("K")
#     if _N is not None:
#         st.success(f"📡 Soil data active — N: **{_N} kg/ha** · P: **{_P} kg/ha** · K: **{_K} kg/ha**")
#     else:
#         st.info("Run a prediction from the sidebar first so the assistant can give soil-specific advice.")
#     st.caption("Ask about fertilizers, organic farming, soil health, NPK levels, weather, or crop transition for Punjab.")

#     qc1,qc2,qc3,qc4 = st.columns(4)
#     suggested_q = None
#     if qc1.button("🌿 Organic Switch",  use_container_width=True):
#         suggested_q = "Should I switch to organic fertilizer with my current NPK levels?"
#     if qc2.button("🌱 Improve Soil",    use_container_width=True):
#         suggested_q = "How can I improve my soil health given current readings?"
#     if qc3.button("🌾 Boost Yield",     use_container_width=True):
#         suggested_q = "How can I increase my crop yield this season?"
#     if qc4.button("💰 Cut Costs",       use_container_width=True):
#         suggested_q = "How can I reduce fertilizer costs on my Punjab farm?"

#     def get_bot_response(query: str) -> str:
#         q = query.lower()
#         N_val = st.session_state.get("N"); P_val = st.session_state.get("P")
#         K_val = st.session_state.get("K")
#         if any(kw in q for kw in ["nitrogen","urea","n value","n level"]):
#             if N_val and N_val > 400:
#                 return (f"⚠️ Your nitrogen is very high ({N_val} kg/ha). Avoid nitrogen-based fertilizer "
#                         f"for 2–3 weeks. Increase organic matter to buffer excess N and prevent leaching.")
#             elif N_val and N_val < 100:
#                 return (f"🌿 Nitrogen is low ({N_val} kg/ha). Apply urea at 100–120 kg/ha in 2 splits "
#                         f"— half at sowing, half at crown root initiation.")
#             return "🌿 Keep nitrogen between 150–300 kg/ha. Urea (46% N) in 2 splits gives best uptake."
#         if any(kw in q for kw in ["phosphorus","dap","p value","p level"]):
#             if P_val and P_val < 10:
#                 return (f"⚠️ Phosphorus critically low ({P_val} kg/ha). Apply DAP (18-46-0) "
#                         f"at 50–60 kg/ha before sowing. Low P severely stunts root development.")
#             return "🌿 Target 15–30 kg/ha. DAP is the most efficient P source for Punjab wheat and rice."
#         if any(kw in q for kw in ["potassium","potash","k value","k level"]):
#             if K_val and K_val > 350:
#                 return (f"✅ Potassium adequate ({K_val} kg/ha). No additional potash needed. "
#                         f"Focus on balancing N and P instead.")
#             return "🌿 Apply MOP (60% K₂O) at 40–50 kg/ha. Potassium improves drought resistance."
#         if any(kw in q for kw in ["organic","compost","manure","natural","switch"]):
#             return ("🌿 Replace 20–25% of chemical N with well-decomposed FYM at 4–5 tonnes/acre. "
#                     "This improves microbial activity and long-term soil structure. "
#                     "Transition gradually over 2–3 seasons to maintain yield stability.")
#         if any(kw in q for kw in ["yield","production","harvest","increase"]):
#             return ("🌾 Ensure balanced NPK, use certified varieties, and apply irrigation scheduling. "
#                     "Punjab wheat target: 20–22 quintals/acre with proper management.")
#         if any(kw in q for kw in ["cost","save","money","budget","cut"]):
#             return ("💰 Switching 30% of chemical fertilizer to vermicompost + FYM "
#                     "saves ₹2,000–3,500/acre per season while improving soil organic matter.")
#         if any(kw in q for kw in ["soil","ph","health","fertility","alkaline"]):
#             return ("🌱 Punjab soils are often alkaline (pH 7.5–8.5). Apply gypsum at 2–3 bags/acre. "
#                     "Green manuring (dhaincha) and FYM raise organic matter effectively.")
#         if any(kw in q for kw in ["weather","rain","drought","flood","heat"]):
#             return ("🌦 STOP fertilizer during heatwaves (>42°C) or floods. "
#                     "Use potassium-rich fertilizers before predicted extreme events for stress tolerance.")
#         return ("🌾 I can help with NPK management, organic transition, pH correction, "
#                 "weather advisories, cost reduction, and yield improvement for Punjab farms. "
#                 "What specific challenge are you facing?")

#     for turn in st.session_state.chat_history:
#         with st.chat_message("user", avatar="👨‍🌾"): st.markdown(turn["user"])
#         with st.chat_message("assistant", avatar="🌱"): st.markdown(turn["bot"])

#     if suggested_q:
#         with st.chat_message("user", avatar="👨‍🌾"): st.markdown(suggested_q)
#         bot_reply = get_bot_response(suggested_q)
#         with st.chat_message("assistant", avatar="🌱"): st.markdown(bot_reply)
#         st.session_state.chat_history.append({"user": suggested_q, "bot": bot_reply})
#         st.rerun()

#     user_input = st.chat_input("Ask your farming question here…")
#     if user_input and user_input.strip():
#         bot_reply = get_bot_response(user_input.strip())
#         st.session_state.chat_history.append({"user": user_input.strip(), "bot": bot_reply})
#         st.rerun()

#     if st.session_state.chat_history:
#         if st.button("🗑 Clear Chat"):
#             st.session_state.chat_history = []; st.rerun()

# # =========================================================
# # FOOTER
# # =========================================================

# st.markdown("---")
# st.markdown(
#     "<center>🌱 <b>SoilSense V2</b> · Punjab Smart Agriculture · "
#     "AI Soil Recovery Intelligence · RandomForest ML · Streamlit</center>",
#     unsafe_allow_html=True)




























# code 4

# ""
# Punjab Smart Agri Ecosystem — Streamlit Dashboard
# ==================================================
# Tools:
#   Tool 1 — Ideal 42-day NPK transition (chemical ↓, organic ↑)
#   Tool 2 — Real-world 42-day NPK with manual weather input
#   Tool 3 — Crop age / growth stage prediction

# Graphs:
#   Graph 1 — NPK comparison: chemical vs organic transition (ideal)
#   Graph 2 — NPK comparison: initial values vs weather-based prediction
# """

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.ensemble import RandomForestRegressor
from sklearn.multioutput import MultiOutputRegressor
from sklearn.metrics import mean_absolute_error, r2_score
import warnings
warnings.filterwarnings("ignore")

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Punjab Smart Agri Ecosystem",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #1a6b2e, #4caf50);
        padding: 1.5rem 2rem;
        border-radius: 12px;
        color: white;
        margin-bottom: 1.5rem;
    }
    .main-header h1 { margin: 0; font-size: 2rem; }
    .main-header p  { margin: 0.3rem 0 0; opacity: 0.9; font-size: 1rem; }

    .metric-card {
        background: #f0faf3;
        border: 1px solid #b2dfdb;
        border-left: 5px solid #4caf50;
        border-radius: 10px;
        padding: 1rem 1.2rem;
        margin-bottom: 0.5rem;
    }
    .metric-card .label { font-size: 0.8rem; color: #555; font-weight: 600; }
    .metric-card .value { font-size: 1.6rem; font-weight: 700; color: #1a6b2e; }
    .metric-card .unit  { font-size: 0.75rem; color: #777; }

    .alert-box {
        padding: 0.8rem 1.2rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        font-weight: 600;
    }
    .alert-extreme { background:#fde8e8; border-left:5px solid #e53935; color:#b71c1c; }
    .alert-high    { background:#fff3e0; border-left:5px solid #fb8c00; color:#e65100; }
    .alert-medium  { background:#fff8e1; border-left:5px solid #fdd835; color:#827717; }
    .alert-low     { background:#e8f5e9; border-left:5px solid #43a047; color:#1b5e20; }

    .stage-badge {
        display:inline-block; padding:0.3rem 0.8rem;
        border-radius:20px; background:#e3f2fd;
        color:#0d47a1; font-weight:700; font-size:0.95rem;
    }
    .section-title {
        font-size:1.25rem; font-weight:700; color:#1a6b2e;
        border-bottom:2px solid #c8e6c9; padding-bottom:0.4rem; margin-bottom:1rem;
    }
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# DATA & MODEL (cached)
# ═══════════════════════════════════════════════════════════════════════════════

FEATURE_COLS = [
    'Current_Temp', 'Current_Rain', 'Current_Hum',
    'Current_Soil_pH', 'Current_Soil_Organic_Matter_Percent',
    'Current_Soil_Nitrogen_kg_per_ha',
    'Current_Soil_Phosphorus_kg_per_ha',
    'Current_Soil_Potassium_kg_per_ha',
    'Soil_Recovery_Score', 'Week_Number',
    'Crop_Name_Enc', 'Weather_Risk_Level_Enc',
    'Farmer_Action_Compliance_Enc', 'Extreme_Event_Flag_Enc',
]
TARGET_COLS = [
    'Current_Soil_Nitrogen_kg_per_ha_Change',
    'Current_Soil_Phosphorus_kg_per_ha_Change',
    'Current_Soil_Potassium_kg_per_ha_Change',
    'Soil_Recovery_Score_Change',
]

GROWTH_STAGES = {
    'Wheat'  : ['Germination','Tillering','Jointing','Heading','Grain Fill','Maturity','Harvest'],
    'Rice'   : ['Germination','Seedling','Tillering','Panicle','Flowering','Grain Fill','Maturity'],
    'Cotton' : ['Germination','Seedling','Squaring','Flowering','Boll Set','Boll Open','Harvest'],
    'Mustard': ['Germination','Rosette','Bolting','Flowering','Pod Fill','Ripening','Harvest'],
    'Gram'   : ['Germination','Seedling','Branching','Flowering','Pod Fill','Maturity','Harvest'],
}

CROP_ICONS = {
    'Wheat': '🌾', 'Rice': '🌾', 'Cotton': '🌿',
    'Mustard': '🌻', 'Gram': '🫘',
}

@st.cache_data
def load_data():
    df = pd.read_excel("Punjab_Smart_Agri_Ecosystem_Dataset.xlsx")
    return df

@st.cache_resource
def build_model(df):
    df = df.copy().sort_values(['Farmer_ID', 'Week_Number']).reset_index(drop=True)
    df['Extreme_Event_Flag'] = df['Extreme_Event_Flag'].fillna('None')

    encoders = {}
    for col in ['Crop_Name', 'Weather_Risk_Level',
                'Farmer_Action_Compliance', 'Farmer_Archetype', 'Extreme_Event_Flag']:
        le = LabelEncoder()
        df[col + '_Enc'] = le.fit_transform(df[col])
        encoders[col] = le

    for nutrient in ['Current_Soil_Nitrogen_kg_per_ha',
                     'Current_Soil_Phosphorus_kg_per_ha',
                     'Current_Soil_Potassium_kg_per_ha',
                     'Soil_Recovery_Score']:
        df[nutrient + '_Change'] = df.groupby('Farmer_ID')[nutrient].diff()

    df['OrganicMatter_Change'] = df.groupby('Farmer_ID')[
        'Current_Soil_Organic_Matter_Percent'].diff()
    df['Organic_Ratio'] = df.groupby('Farmer_ID')[
        'Current_Soil_Organic_Matter_Percent'].transform(
        lambda x: (x - x.iloc[0]) / (x.iloc[0] + 1e-6) * 100)

    df_model = df.dropna(subset=TARGET_COLS).copy()

    X = df_model[FEATURE_COLS]
    y = df_model[TARGET_COLS]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    scaler = StandardScaler()
    X_tr = scaler.fit_transform(X_train)
    X_te = scaler.transform(X_test)

    model = MultiOutputRegressor(
        RandomForestRegressor(n_estimators=200, max_depth=10, random_state=42, n_jobs=-1)
    )
    model.fit(X_tr, y_train)
    y_pred = model.predict(X_te)

    metrics = {}
    names = ['Nitrogen Δ', 'Phosphorus Δ', 'Potassium Δ', 'Recovery Δ']
    for i, name in enumerate(names):
        metrics[name] = {
            'mae': round(mean_absolute_error(y_test.iloc[:, i], y_pred[:, i]), 3),
            'r2' : round(r2_score(y_test.iloc[:, i], y_pred[:, i]), 3),
        }

    return model, scaler, encoders, df, metrics

# ── Weather helpers ────────────────────────────────────────────────────────────

def classify_weather(temp, rain, humidity):
    extreme_event = 'None'
    if temp >= 45:
        risk = 'Extreme'; extreme_event = 'Heatwave'
    elif temp >= 40 or rain >= 180:
        risk = 'High'
        if rain >= 180: extreme_event = 'Flood'
    elif temp >= 34 or rain < 15 or humidity > 85:
        risk = 'Medium'
        if rain < 15: extreme_event = 'Drought'
    else:
        risk = 'Low'
    return risk, extreme_event

# ─────────────────────────────────────────────────────────────────────────────
# TOOL 1 — Ideal 42-day NPK Transition
# ─────────────────────────────────────────────────────────────────────────────

def tool1_ideal_42day(model, scaler, df, encoders, crop_name,
                      start_N, start_P, start_K,
                      start_pH=7.3, start_organic=0.65, start_recovery=35.0):
    ideal_temp     = df[df['Weather_Risk_Level'] == 'Low']['Current_Temp'].mean()
    ideal_rain     = df[df['Weather_Risk_Level'] == 'Low']['Current_Rain'].mean()
    ideal_humidity = df[df['Weather_Risk_Level'] == 'Low']['Current_Hum'].mean()

    crop_enc   = encoders['Crop_Name'].transform([crop_name])[0]
    risk_enc   = encoders['Weather_Risk_Level'].transform(['Low'])[0]
    comply_enc = encoders['Farmer_Action_Compliance'].transform(['Full'])[0]
    event_enc  = encoders['Extreme_Event_Flag'].transform(['None'])[0]

    N, P, K = start_N, start_P, start_K
    pH, org, rec = start_pH, start_organic, start_recovery
    results = []

    for week in range(1, 8):
        X_row = pd.DataFrame([[
            ideal_temp, ideal_rain, ideal_humidity,
            pH, org, N, P, K, rec, week,
            crop_enc, risk_enc, comply_enc, event_enc
        ]], columns=FEATURE_COLS)

        deltas = model.predict(scaler.transform(X_row))[0]
        dN   = np.clip(deltas[0], -60,  5)
        dP   = np.clip(deltas[1],  -2,  3)
        dK   = np.clip(deltas[2],  -1,  5)
        dRec = np.clip(deltas[3],  -3, 20)

        org_gain    = 0.08
        org         = min(org + org_gain, 3.0)
        organic_pct = min((week / 7) * 40, 40)
        chemical_pct = 100 - organic_pct

        for d in range(6):
            actual_day = (week - 1) * 6 + d + 1
            if actual_day > 42: break
            frac  = (d + 1) / 6.0
            results.append({
                'Day': actual_day, 'Week': week,
                'Nitrogen_kg_ha'    : round(np.clip(N + dN * frac, 50, 600), 2),
                'Phosphorus_kg_ha'  : round(np.clip(P + dP * frac,  5,  60), 2),
                'Potassium_kg_ha'   : round(np.clip(K + dK * frac, 80, 400), 2),
                'Soil_Recovery_Score': round(np.clip(rec + dRec * frac, 25, 100), 2),
                'Organic_Input_Pct' : round(organic_pct, 1),
                'Chemical_Input_Pct': round(chemical_pct, 1),
                'Crop': crop_name,
            })

        N   = np.clip(N + dN,   50, 600)
        P   = np.clip(P + dP,    5,  60)
        K   = np.clip(K + dK,   80, 400)
        rec = np.clip(rec + dRec, 25, 100)

    return pd.DataFrame(results)

# ─────────────────────────────────────────────────────────────────────────────
# TOOL 2 — Real-world 42-day NPK
# ─────────────────────────────────────────────────────────────────────────────

def tool2_realworld_42day(model, scaler, encoders, crop_name,
                          start_N, start_P, start_K,
                          start_pH, start_organic, start_recovery,
                          weekly_weather):
    crop_enc = encoders['Crop_Name'].transform([crop_name])[0]
    N, P, K  = start_N, start_P, start_K
    pH, org, rec = start_pH, start_organic, start_recovery
    results = []

    for week, (temp, rain, humidity) in enumerate(weekly_weather, start=1):
        temp     = np.clip(temp,    10,  50)
        rain     = np.clip(rain,     0, 250)
        humidity = np.clip(humidity, 20,  95)

        risk, event = classify_weather(temp, rain, humidity)
        known_risks  = list(encoders['Weather_Risk_Level'].classes_)
        known_events = list(encoders['Extreme_Event_Flag'].classes_)
        risk_enc   = encoders['Weather_Risk_Level'].transform(
            [risk  if risk  in known_risks  else 'High'])[0]
        event_enc  = encoders['Extreme_Event_Flag'].transform(
            [event if event in known_events else 'None'])[0]
        comply_enc = encoders['Farmer_Action_Compliance'].transform(['Full'])[0]

        X_row = pd.DataFrame([[
            temp, rain, humidity,
            pH, org, N, P, K, rec, week,
            crop_enc, risk_enc, comply_enc, event_enc
        ]], columns=FEATURE_COLS)

        deltas = model.predict(scaler.transform(X_row))[0]

        if temp >= 45:
            dN=np.clip(deltas[0]*1.4,-100,0); dP=np.clip(deltas[1]*1.2,-5,1)
            dK=np.clip(deltas[2]*1.2,-5,2);   dRec=np.clip(deltas[3]*0.3,-15,5)
        elif risk == 'High':
            dN=np.clip(deltas[0]*1.2,-80,2); dP=np.clip(deltas[1],-3,2)
            dK=np.clip(deltas[2],-3,3);      dRec=np.clip(deltas[3]*0.5,-10,8)
        elif risk == 'Medium':
            dN=np.clip(deltas[0],-60,3); dP=np.clip(deltas[1],-2,2)
            dK=np.clip(deltas[2],-2,4); dRec=np.clip(deltas[3],-5,12)
        else:
            dN=np.clip(deltas[0],-60,5); dP=np.clip(deltas[1],-2,3)
            dK=np.clip(deltas[2],-1,5); dRec=np.clip(deltas[3],-3,20)

        org_gain    = 0.04 if risk in ['Extreme','High'] else 0.08
        org         = min(org + org_gain, 3.0)
        base_organic = (week / 7) * 40
        organic_pct  = base_organic * (0.4 if risk=='Extreme' else 0.7 if risk=='High' else 1.0)
        chemical_pct = 100 - organic_pct

        for d in range(6):
            actual_day = (week - 1) * 6 + d + 1
            if actual_day > 42: break
            frac = (d + 1) / 6.0
            results.append({
                'Day': actual_day, 'Week': week,
                'Temperature_C'     : temp,
                'Rainfall_mm'       : rain,
                'Humidity_Pct'      : humidity,
                'Weather_Risk'      : risk,
                'Extreme_Event'     : event,
                'Nitrogen_kg_ha'    : round(np.clip(N + dN * frac, 50, 600), 2),
                'Phosphorus_kg_ha'  : round(np.clip(P + dP * frac,  5,  60), 2),
                'Potassium_kg_ha'   : round(np.clip(K + dK * frac, 80, 400), 2),
                'Soil_Recovery_Score': round(np.clip(rec + dRec * frac, 25, 100), 2),
                'Organic_Input_Pct' : round(organic_pct, 1),
                'Chemical_Input_Pct': round(chemical_pct, 1),
                'Crop': crop_name,
            })

        N   = np.clip(N + dN,   50, 600)
        P   = np.clip(P + dP,    5,  60)
        K   = np.clip(K + dK,   80, 400)
        rec = np.clip(rec + dRec, 25, 100)

    return pd.DataFrame(results)

# ─────────────────────────────────────────────────────────────────────────────
# TOOL 3 — Crop growth stage
# ─────────────────────────────────────────────────────────────────────────────

def tool3_crop_stage(df, crop_name, current_N, current_P, current_K,
                     current_recovery, current_week):
    stages      = GROWTH_STAGES.get(crop_name, GROWTH_STAGES['Wheat'])
    stage_index = min(current_week - 1, len(stages) - 1)
    current_stage = stages[stage_index]
    next_stage    = stages[min(stage_index + 1, len(stages) - 1)]

    crop_df  = df[df['Crop_Name'] == crop_name]
    week_df  = crop_df[crop_df['Week_Number'] == current_week]
    if len(week_df) == 0: week_df = crop_df

    avg_N   = week_df['Current_Soil_Nitrogen_kg_per_ha'].mean()
    avg_P   = week_df['Current_Soil_Phosphorus_kg_per_ha'].mean()
    avg_K   = week_df['Current_Soil_Potassium_kg_per_ha'].mean()
    avg_rec = week_df['Soil_Recovery_Score'].mean()

    n_h = min(current_N / avg_N, 1.0) * 100 if avg_N > 0 else 50
    p_h = min(current_P / avg_P, 1.0) * 100 if avg_P > 0 else 50
    k_h = min(current_K / avg_K, 1.0) * 100 if avg_K > 0 else 50
    r_h = min(current_recovery / avg_rec, 1.0) * 100 if avg_rec > 0 else 50
    overall = round((n_h + p_h + k_h + r_h) / 4, 1)

    if   overall >= 80: advice = "Excellent. Continue organic transition as planned."
    elif overall >= 60: advice = "Good. Monitor NPK closely in next 7 days."
    elif overall >= 40: advice = "Moderate stress. Consider slowing organic transition rate."
    else:               advice = "High stress. Pause organic transition. Focus on soil recovery first."

    return {
        'crop': crop_name, 'week': current_week,
        'growth_stage': current_stage, 'next_stage': next_stage,
        'stages': stages, 'stage_index': stage_index,
        'n_health': round(n_h,1), 'p_health': round(p_h,1),
        'k_health': round(k_h,1), 'recovery_health': round(r_h,1),
        'avg_N': round(avg_N,1), 'avg_P': round(avg_P,1),
        'avg_K': round(avg_K,1), 'avg_rec': round(avg_rec,1),
        'overall_health': overall, 'recommendation': advice,
    }

# ═══════════════════════════════════════════════════════════════════════════════
# PLOT FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def plot_graph1(df, crop_name):
    fig = make_subplots(
        rows=2, cols=1, shared_xaxes=True,
        subplot_titles=("NPK Soil Levels Over 42 Days",
                        "Chemical ↓ Declining  |  Organic ↑ Rising"),
        vertical_spacing=0.12, row_heights=[0.6, 0.4],
    )

    colors = {'N': '#1565C0', 'P': '#E65100', 'K': '#2E7D32'}
    for nutrient, col, sym in [('N','Nitrogen_kg_ha','circle'),
                                ('P','Phosphorus_kg_ha','square'),
                                ('K','Potassium_kg_ha','triangle-up')]:
        fig.add_trace(go.Scatter(
            x=df['Day'], y=df[col], name=f'{nutrient} (kg/ha)',
            mode='lines+markers', line=dict(color=colors[nutrient], width=2.5),
            marker=dict(symbol=sym, size=4),
        ), row=1, col=1)

    fig.add_trace(go.Scatter(
        x=df['Day'], y=df['Chemical_Input_Pct'], name='Chemical %',
        fill='tozeroy', fillcolor='rgba(229,57,53,0.25)',
        line=dict(color='#e53935', width=2),
    ), row=2, col=1)
    fig.add_trace(go.Scatter(
        x=df['Day'], y=df['Organic_Input_Pct'], name='Organic %',
        fill='tozeroy', fillcolor='rgba(67,160,71,0.3)',
        line=dict(color='#43a047', width=2),
    ), row=2, col=1)

    # Week separators
    for w in range(1, 7):
        for row in [1, 2]:
            fig.add_vline(x=w*6+0.5, line_width=1, line_dash='dash',
                          line_color='rgba(150,150,150,0.5)', row=row, col=1)

    fig.update_layout(
        title=dict(text=f"🌾 Graph 1 — NPK Transition: Chemical → Organic  |  {crop_name}  |  Ideal Conditions",
                   font=dict(size=15, color='#1a6b2e')),
        height=600, hovermode='x unified',
        legend=dict(orientation='h', y=-0.15),
        plot_bgcolor='rgba(240,250,240,0.4)',
    )
    fig.update_xaxes(title_text="Day", row=2, col=1)
    fig.update_yaxes(title_text="NPK (kg/ha)", row=1, col=1)
    fig.update_yaxes(title_text="Input %", row=2, col=1, range=[0,110])
    return fig


def plot_graph2(df1, df2, crop_name, start_N, start_P, start_K):
    nutrients = [
        ('Nitrogen_kg_ha',   'Nitrogen (N)',   start_N, '#1565C0'),
        ('Phosphorus_kg_ha', 'Phosphorus (P)', start_P, '#E65100'),
        ('Potassium_kg_ha',  'Potassium (K)',  start_K, '#2E7D32'),
    ]
    fig = make_subplots(rows=3, cols=1, shared_xaxes=True,
                        subplot_titles=[f"{label} — Initial vs Predicted" for _, label, _, _ in nutrients],
                        vertical_spacing=0.08)

    for i, (col, label, start_val, color) in enumerate(nutrients, start=1):
        # Initial baseline
        fig.add_hline(y=start_val, line_dash='dot', line_color='gray',
                      line_width=1.8, row=i, col=1,
                      annotation_text=f"Initial: {start_val} kg/ha",
                      annotation_position="top right")
        # Ideal (Tool 1)
        fig.add_trace(go.Scatter(
            x=df1['Day'], y=df1[col], name='Ideal (no extreme weather)',
            line=dict(color=color, width=2, dash='dash'),
            opacity=0.6, legendgroup='ideal',
            showlegend=(i == 1),
        ), row=i, col=1)
        # Real-world (Tool 2)
        fig.add_trace(go.Scatter(
            x=df2['Day'], y=df2[col], name='Predicted (your weather)',
            mode='lines+markers', line=dict(color=color, width=2.5),
            marker=dict(size=3), legendgroup='real',
            showlegend=(i == 1),
        ), row=i, col=1)

        # Shade between initial and real
        fig.add_trace(go.Scatter(
            x=list(df2['Day']) + list(df2['Day'])[::-1],
            y=list(df2[col]) + [start_val]*len(df2),
            fill='toself', fillcolor=color.replace('#','rgba(') + ',0.08)',
            line=dict(color='rgba(255,255,255,0)'),
            showlegend=False, hoverinfo='skip',
        ), row=i, col=1)

        # Highlight extreme weather
        if 'Weather_Risk' in df2.columns:
            for risk, clr in [('Extreme','rgba(229,57,53,0.18)'),
                               ('High','rgba(251,140,0,0.12)')]:
                extreme_days = df2[df2['Weather_Risk'] == risk]['Day'].unique()
                for d in extreme_days:
                    fig.add_vrect(x0=d-0.5, x1=d+0.5, fillcolor=clr,
                                  line_width=0, row=i, col=1)

        fig.update_yaxes(title_text=f"{label} (kg/ha)", row=i, col=1)

    # Week lines
    for w in range(1, 7):
        for row in [1, 2, 3]:
            fig.add_vline(x=w*6+0.5, line_width=1, line_dash='dot',
                          line_color='rgba(150,150,150,0.4)', row=row, col=1)

    fig.update_layout(
        title=dict(text=f"📊 Graph 2 — NPK Comparison: Initial vs Weather-Based Prediction  |  {crop_name}",
                   font=dict(size=15, color='#1a6b2e')),
        height=800, hovermode='x unified',
        legend=dict(orientation='h', y=-0.06),
        plot_bgcolor='rgba(240,250,240,0.4)',
    )
    fig.update_xaxes(title_text="Day", row=3, col=1)
    return fig


def plot_health_radar(result):
    categories = ['N Health', 'P Health', 'K Health', 'Recovery Health']
    values = [result['n_health'], result['p_health'],
               result['k_health'], result['recovery_health']]
    values_closed = values + [values[0]]
    cats_closed   = categories + [categories[0]]

    fig = go.Figure(go.Scatterpolar(
        r=values_closed, theta=cats_closed,
        fill='toself', fillcolor='rgba(76,175,80,0.25)',
        line=dict(color='#2E7D32', width=2.5),
        marker=dict(size=8, color='#1a6b2e'),
    ))
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 100],
                                    tickfont=dict(size=10))),
        showlegend=False, height=320,
        margin=dict(l=40, r=40, t=40, b=40),
        title=dict(text="Crop Health Radar", font=dict(size=13)),
    )
    return fig


def plot_stage_progress(result):
    stages = result['stages']
    idx    = result['stage_index']
    colors = ['#a5d6a7' if i < idx else '#1a6b2e' if i == idx else '#e0e0e0'
              for i in range(len(stages))]

    fig = go.Figure(go.Bar(
        x=stages, y=[1]*len(stages),
        marker_color=colors,
        text=['✓' if i < idx else '▶' if i == idx else ''
              for i in range(len(stages))],
        textposition='inside', textfont=dict(size=18, color='white'),
        hovertemplate='%{x}<extra></extra>',
    ))
    fig.update_layout(
        height=150, showlegend=False,
        yaxis=dict(visible=False),
        xaxis=dict(tickfont=dict(size=11)),
        margin=dict(l=10, r=10, t=10, b=10),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
    )
    return fig


# ═══════════════════════════════════════════════════════════════════════════════
# DATASET OVERVIEW TAB
# ═══════════════════════════════════════════════════════════════════════════════

def tab_dataset_overview(df):
    st.markdown('<div class="section-title">📂 Dataset Overview</div>', unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Records", f"{len(df):,}")
    c2.metric("Unique Farmers", df['Farmer_ID'].nunique())
    c3.metric("Crops", df['Crop_Name'].nunique())
    c4.metric("Weeks Tracked", f"{df['Week_Number'].max()}")

    st.markdown("---")
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**NPK Distribution by Crop**")
        crop_avg = df.groupby('Crop_Name')[
            ['Current_Soil_Nitrogen_kg_per_ha',
             'Current_Soil_Phosphorus_kg_per_ha',
             'Current_Soil_Potassium_kg_per_ha']].mean().reset_index()
        fig = px.bar(crop_avg.melt(id_vars='Crop_Name',
                                    var_name='Nutrient', value_name='Avg kg/ha'),
                     x='Crop_Name', y='Avg kg/ha', color='Nutrient',
                     barmode='group', height=340,
                     color_discrete_map={
                         'Current_Soil_Nitrogen_kg_per_ha': '#1565C0',
                         'Current_Soil_Phosphorus_kg_per_ha': '#E65100',
                         'Current_Soil_Potassium_kg_per_ha': '#2E7D32',
                     })
        fig.update_layout(margin=dict(t=10), plot_bgcolor='rgba(240,250,240,0.4)')
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("**Weather Risk Distribution**")
        risk_counts = df['Weather_Risk_Level'].value_counts().reset_index()
        risk_counts.columns = ['Risk', 'Count']
        fig2 = px.pie(risk_counts, values='Count', names='Risk', hole=0.4,
                      height=340,
                      color_discrete_map={
                          'Extreme':'#e53935','High':'#fb8c00',
                          'Medium':'#fdd835','Low':'#43a047',
                      })
        fig2.update_layout(margin=dict(t=10))
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("**Soil Recovery Score over Weeks (by Crop)**")
    weekly_rec = df.groupby(['Week_Number','Crop_Name'])['Soil_Recovery_Score'].mean().reset_index()
    fig3 = px.line(weekly_rec, x='Week_Number', y='Soil_Recovery_Score',
                   color='Crop_Name', markers=True, height=320,
                   labels={'Week_Number': 'Week', 'Soil_Recovery_Score': 'Avg Recovery Score'})
    fig3.update_layout(plot_bgcolor='rgba(240,250,240,0.4)')
    st.plotly_chart(fig3, use_container_width=True)

    with st.expander("🔍 View Raw Data"):
        st.dataframe(df.head(100), use_container_width=True)


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN APP
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🌾 Punjab Smart Agri Ecosystem</h1>
        <p>AI-powered NPK soil transition planner — Chemical → Organic | IoT-ready | 42-day forecast</p>
    </div>
    """, unsafe_allow_html=True)

    # Load data & model
    with st.spinner("Loading dataset and training model…"):
        df_raw = load_data()
        model, scaler, encoders, df_full, model_metrics = build_model(df_raw)

    st.success(f"✅ Model ready — {len(df_raw):,} records loaded.")

    # Model metrics expander
    with st.expander("🤖 Model Performance (RandomForest MultiOutput Regressor)"):
        mc = st.columns(4)
        for i, (name, vals) in enumerate(model_metrics.items()):
            mc[i].metric(f"{name}", f"MAE: {vals['mae']}", f"R²: {vals['r2']}")

    st.markdown("---")

    # ── Tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Dataset Overview",
        "🌿 Tool 1 — Ideal 42-Day",
        "🌦️ Tool 2 — Real-World Weather",
        "🌱 Tool 3 — Crop Stage",
    ])

    # ──────────────────────────────────────────────────────────────────────────
    with tab1:
        tab_dataset_overview(df_full)

    # ──────────────────────────────────────────────────────────────────────────
    with tab2:
        st.markdown('<div class="section-title">🌿 Tool 1 — Ideal 42-Day NPK Transition</div>',
                    unsafe_allow_html=True)
        st.info("Best-case scenario — low weather risk, full farmer compliance. "
                "Shows chemical fertilizer declining and organic input rising over 42 days.")

        with st.form("form_tool1"):
            c1, c2, c3 = st.columns(3)
            crop     = c1.selectbox("Crop", ['Wheat','Rice','Cotton','Mustard','Gram'])
            start_N  = c2.number_input("Starting Nitrogen (kg/ha)", 50.0, 600.0, 350.0, 10.0)
            start_P  = c3.number_input("Starting Phosphorus (kg/ha)", 5.0, 60.0, 22.0, 1.0)
            c4, c5, c6 = st.columns(3)
            start_K  = c4.number_input("Starting Potassium (kg/ha)", 80.0, 400.0, 250.0, 10.0)
            start_pH = c5.number_input("Soil pH", 5.5, 9.0, 7.3, 0.1)
            start_org = c6.number_input("Soil Organic Matter (%)", 0.1, 5.0, 0.65, 0.05)
            start_rec = st.slider("Starting Soil Recovery Score", 20, 80, 35)
            run = st.form_submit_button("▶ Run Ideal 42-Day Simulation", use_container_width=True)

        if run:
            with st.spinner("Running simulation…"):
                report1 = tool1_ideal_42day(
                    model, scaler, df_full, encoders, crop,
                    start_N, start_P, start_K,
                    start_pH, start_org, start_rec)

            st.session_state['report1'] = report1
            st.session_state['tool1_crop'] = crop
            st.session_state['tool1_NPK'] = (start_N, start_P, start_K)

            # Summary metrics — Day 1 vs Day 42
            d1  = report1.iloc[0]
            d42 = report1.iloc[-1]
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Nitrogen Day 42", f"{d42['Nitrogen_kg_ha']} kg/ha",
                      f"{d42['Nitrogen_kg_ha']-d1['Nitrogen_kg_ha']:+.1f}")
            m2.metric("Phosphorus Day 42", f"{d42['Phosphorus_kg_ha']} kg/ha",
                      f"{d42['Phosphorus_kg_ha']-d1['Phosphorus_kg_ha']:+.1f}")
            m3.metric("Potassium Day 42", f"{d42['Potassium_kg_ha']} kg/ha",
                      f"{d42['Potassium_kg_ha']-d1['Potassium_kg_ha']:+.1f}")
            m4.metric("Organic Input @ Day 42", f"{d42['Organic_Input_Pct']}%",
                      f"Chemical {d42['Chemical_Input_Pct']}%")

            st.plotly_chart(plot_graph1(report1, crop), use_container_width=True)

            with st.expander("📋 Daily Report Table"):
                st.dataframe(report1, use_container_width=True)

            csv = report1.to_csv(index=False).encode()
            st.download_button("⬇ Download Report CSV", csv,
                               "tool1_ideal_42day_report.csv", "text/csv")

    # ──────────────────────────────────────────────────────────────────────────
    with tab3:
        st.markdown('<div class="section-title">🌦️ Tool 2 — Real-World 42-Day (Manual Weather)</div>',
                    unsafe_allow_html=True)
        st.info("Enter actual or forecast weather for each of the 7 weeks. "
                "The model adjusts NPK predictions based on heat, rainfall, and humidity stress.")

        with st.form("form_tool2"):
            c1, c2, c3 = st.columns(3)
            crop2   = c1.selectbox("Crop", ['Wheat','Rice','Cotton','Mustard','Gram'], key='crop2')
            s_N     = c2.number_input("Starting Nitrogen (kg/ha)", 50.0, 600.0, 350.0, 10.0, key='s_N')
            s_P     = c3.number_input("Starting Phosphorus (kg/ha)", 5.0, 60.0, 22.0, 1.0, key='s_P')
            c4, c5, c6 = st.columns(3)
            s_K     = c4.number_input("Starting Potassium (kg/ha)", 80.0, 400.0, 250.0, 10.0, key='s_K')
            s_pH    = c5.number_input("Soil pH", 5.5, 9.0, 7.3, 0.1, key='s_pH')
            s_org   = c6.number_input("Soil Organic Matter (%)", 0.1, 5.0, 0.65, 0.05, key='s_org')
            s_rec   = st.slider("Starting Soil Recovery Score", 20, 80, 35, key='s_rec')

            st.markdown("---")
            st.markdown("**Weekly Weather Input** *(Punjab ranges: Temp 10–50°C | Rain 0–250mm | Humidity 20–95%)*")
            weekly_weather = []
            for wk in range(1, 8):
                dc1, dc2, dc3, dc4 = st.columns([1, 2, 2, 2])
                dc1.markdown(f"**Week {wk}**<br>Days {(wk-1)*6+1}–{min(wk*6,42)}",
                             unsafe_allow_html=True)
                t = dc2.number_input(f"Temp °C", 10.0, 50.0, 30.0, 1.0, key=f't{wk}')
                r = dc3.number_input(f"Rain mm", 0.0, 250.0, 50.0, 5.0, key=f'r{wk}')
                h = dc4.number_input(f"Humidity %", 20.0, 95.0, 60.0, 1.0, key=f'h{wk}')
                weekly_weather.append((t, r, h))

            run2 = st.form_submit_button("▶ Run Real-World Simulation", use_container_width=True)

        if run2:
            with st.spinner("Running real-world simulation…"):
                report2 = tool2_realworld_42day(
                    model, scaler, encoders, crop2,
                    s_N, s_P, s_K, s_pH, s_org, s_rec,
                    weekly_weather)

            st.session_state['report2'] = report2
            st.session_state['tool2_crop'] = crop2
            st.session_state['tool2_NPK']  = (s_N, s_P, s_K)

            # Weather summary
            st.markdown("**Weekly Weather Summary**")
            wsum = report2.drop_duplicates('Week')[
                ['Week','Temperature_C','Rainfall_mm','Humidity_Pct','Weather_Risk','Extreme_Event']
            ].reset_index(drop=True)
            risk_colors = {'Extreme':'alert-extreme','High':'alert-high',
                           'Medium':'alert-medium','Low':'alert-low'}
            for _, row in wsum.iterrows():
                cls = risk_colors.get(row['Weather_Risk'], 'alert-low')
                evt = f"  |  ⚠ {row['Extreme_Event']}" if row['Extreme_Event'] != 'None' else ''
                st.markdown(
                    f'<div class="alert-box {cls}">Week {int(row["Week"])} — '
                    f'🌡 {row["Temperature_C"]}°C  🌧 {row["Rainfall_mm"]}mm  '
                    f'💧 {row["Humidity_Pct"]}%  |  Risk: <b>{row["Weather_Risk"]}</b>{evt}</div>',
                    unsafe_allow_html=True)

            # If Tool 1 was run for the same crop, show Graph 2
            if 'report1' in st.session_state and st.session_state.get('tool1_crop') == crop2:
                st.markdown("---")
                st.plotly_chart(
                    plot_graph2(st.session_state['report1'], report2, crop2, s_N, s_P, s_K),
                    use_container_width=True)
            else:
                # Show just Tool 2 lines
                fig = make_subplots(rows=3, cols=1,
                    subplot_titles=["Nitrogen (N)","Phosphorus (P)","Potassium (K)"],
                    shared_xaxes=True, vertical_spacing=0.08)
                for i, (col, color) in enumerate([
                        ('Nitrogen_kg_ha','#1565C0'),
                        ('Phosphorus_kg_ha','#E65100'),
                        ('Potassium_kg_ha','#2E7D32')], start=1):
                    fig.add_trace(go.Scatter(x=report2['Day'], y=report2[col],
                        mode='lines+markers', line=dict(color=color, width=2.5),
                        marker=dict(size=4), name=col), row=i, col=1)
                fig.update_layout(height=700, showlegend=False,
                    title="NPK Prediction — Real-World Weather",
                    plot_bgcolor='rgba(240,250,240,0.4)')
                st.plotly_chart(fig, use_container_width=True)
                st.info("💡 Also run **Tool 1** for the same crop to unlock Graph 2 comparison.")

            with st.expander("📋 Daily Report Table"):
                st.dataframe(report2, use_container_width=True)

            csv2 = report2.to_csv(index=False).encode()
            st.download_button("⬇ Download Report CSV", csv2,
                               "tool2_realworld_42day_report.csv", "text/csv")

    # ──────────────────────────────────────────────────────────────────────────
    with tab4:
        st.markdown('<div class="section-title">🌱 Tool 3 — Crop Growth Stage Predictor</div>',
                    unsafe_allow_html=True)
        st.info("Enter your current soil readings to identify the crop's growth stage and health score.")

        with st.form("form_tool3"):
            c1, c2 = st.columns(2)
            crop3 = c1.selectbox("Crop", ['Wheat','Rice','Cotton','Mustard','Gram'], key='crop3')
            week3 = c2.slider("Current Week", 1, 7, 4)
            c3, c4, c5, c6 = st.columns(4)
            cur_N   = c3.number_input("Current N (kg/ha)", 50.0, 600.0, 280.0, 5.0, key='cur_N')
            cur_P   = c4.number_input("Current P (kg/ha)",  5.0,  60.0,  21.0, 1.0, key='cur_P')
            cur_K   = c5.number_input("Current K (kg/ha)", 80.0, 400.0, 240.0, 5.0, key='cur_K')
            cur_rec = c6.number_input("Recovery Score", 25.0, 100.0, 45.0, 1.0, key='cur_rec')
            run3 = st.form_submit_button("▶ Predict Growth Stage & Health", use_container_width=True)

        if run3:
            result = tool3_crop_stage(df_full, crop3, cur_N, cur_P, cur_K, cur_rec, week3)

            # Stage progress bar
            st.markdown("**Growth Stage Progress**")
            st.plotly_chart(plot_stage_progress(result), use_container_width=True)

            c1, c2 = st.columns([1, 1])
            with c1:
                st.markdown(f"""
                <div style='background:#f0faf3;border-radius:12px;padding:1.2rem;'>
                    <div style='font-size:0.85rem;color:#555;'>Current Stage</div>
                    <div class='stage-badge' style='font-size:1.3rem;'>
                        {CROP_ICONS.get(crop3,'🌾')} {result['growth_stage']}
                    </div>
                    <div style='margin-top:0.8rem;font-size:0.85rem;color:#555;'>Next Stage →</div>
                    <div style='font-weight:600;color:#1a6b2e;'>{result['next_stage']}</div>
                    <hr/>
                    <div style='font-size:0.85rem;color:#555;'>Overall Health Score</div>
                    <div style='font-size:2.5rem;font-weight:800;color:
                        {"#2E7D32" if result["overall_health"]>=80 else
                         "#F57F17" if result["overall_health"]>=60 else
                         "#e53935"};'>{result['overall_health']}%</div>
                    <hr/>
                    <div style='background:#e8f5e9;border-left:4px solid #43a047;
                                border-radius:6px;padding:0.7rem;margin-top:0.5rem;
                                font-size:0.9rem;color:#1b5e20;'>
                        💡 {result['recommendation']}
                    </div>
                </div>
                """, unsafe_allow_html=True)
            with c2:
                st.plotly_chart(plot_health_radar(result), use_container_width=True)

            # NPK health breakdown
            st.markdown("**Nutrient Health vs. Average for this Week**")
            health_df = pd.DataFrame({
                'Nutrient' : ['Nitrogen (N)', 'Phosphorus (P)', 'Potassium (K)', 'Recovery'],
                'Your Value': [cur_N, cur_P, cur_K, cur_rec],
                'Week Avg'  : [result['avg_N'], result['avg_P'], result['avg_K'], result['avg_rec']],
                'Health %'  : [result['n_health'], result['p_health'], result['k_health'], result['recovery_health']],
            })
            fig_h = px.bar(health_df, x='Nutrient', y=['Your Value','Week Avg'],
                           barmode='group', height=300,
                           color_discrete_map={'Your Value':'#1a6b2e','Week Avg':'#90caf9'},
                           labels={'value':'kg/ha','variable':''})
            fig_h.update_layout(plot_bgcolor='rgba(240,250,240,0.4)', margin=dict(t=10))
            st.plotly_chart(fig_h, use_container_width=True)


if __name__ == "__main__":
    main()





 
