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





# ==============================================================================
# SOIL SENSE V2 — AI Soil Recovery Intelligence Platform
# Single-file Streamlit Dashboard — FIXED COMPLETE VERSION
# ==============================================================================

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
import io
import warnings
warnings.filterwarnings('ignore')

# ------------------------------------------------------------------------------
# PAGE CONFIG
# ------------------------------------------------------------------------------
st.set_page_config(
    page_title="SOIL SENSE V2",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ------------------------------------------------------------------------------
# CUSTOM CSS
# ------------------------------------------------------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500&display=swap');

:root {
    --soil-dark:    #0d1a0f;
    --soil-green:   #1a3320;
    --leaf-green:   #2d6a4f;
    --lime-accent:  #52b788;
    --gold-accent:  #d4a017;
    --alert-red:    #c1121f;
    --alert-amber:  #e07b00;
    --alert-safe:   #40916c;
    --text-primary: #e8f5e9;
    --text-muted:   #a5c5a8;
    --card-bg:      rgba(26, 51, 32, 0.7);
    --border:       rgba(82, 183, 136, 0.25);
}

html, body, [data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #0a150c 0%, #0d1a0f 50%, #0c1a10 100%);
    font-family: 'DM Sans', sans-serif;
    color: var(--text-primary);
}

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0d1f10 0%, #0a1a0d 100%);
    border-right: 1px solid var(--border);
}

[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] .stRadio label,
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span {
    color: var(--text-primary) !important;
}

h1, h2, h3, h4 {
    font-family: 'Syne', sans-serif;
    color: var(--text-primary);
}

.metric-card {
    background: var(--card-bg);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.2rem 1.4rem;
    backdrop-filter: blur(10px);
    transition: transform 0.2s, box-shadow 0.2s;
}
.metric-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 24px rgba(82, 183, 136, 0.12);
}
.metric-label {
    font-size: 0.72rem;
    font-weight: 500;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: var(--text-muted);
    margin-bottom: 4px;
}
.metric-value {
    font-family: 'Syne', sans-serif;
    font-size: 2rem;
    font-weight: 700;
    color: var(--lime-accent);
    line-height: 1;
}
.metric-sub {
    font-size: 0.78rem;
    color: var(--text-muted);
    margin-top: 4px;
}

.badge-safe   { background:#1b4332; color:#52b788; border:1px solid #52b788; padding:3px 12px; border-radius:20px; font-size:0.8rem; font-weight:600; }
.badge-delay  { background:#3d2200; color:#f4a261; border:1px solid #e07b00; padding:3px 12px; border-radius:20px; font-size:0.8rem; font-weight:600; }
.badge-stop   { background:#3d0000; color:#ff6b6b; border:1px solid #c1121f; padding:3px 12px; border-radius:20px; font-size:0.8rem; font-weight:600; }

.section-header {
    font-family: 'Syne', sans-serif;
    font-size: 1.5rem;
    font-weight: 700;
    color: var(--lime-accent);
    border-left: 4px solid var(--lime-accent);
    padding-left: 12px;
    margin: 1.5rem 0 1rem 0;
}

.platform-header {
    background: linear-gradient(90deg, rgba(26,51,32,0.9) 0%, rgba(13,26,15,0.95) 100%);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 1.6rem 2rem;
    margin-bottom: 1.5rem;
    display: flex;
    align-items: center;
    gap: 1rem;
}
.platform-title {
    font-family: 'Syne', sans-serif;
    font-size: 2rem;
    font-weight: 800;
    color: var(--lime-accent);
    letter-spacing: -0.02em;
    margin: 0;
}
.platform-subtitle {
    color: var(--text-muted);
    font-size: 0.9rem;
    margin: 0;
}

.info-box {
    background: rgba(45, 106, 79, 0.15);
    border: 1px solid rgba(82, 183, 136, 0.3);
    border-radius: 10px;
    padding: 1rem 1.2rem;
    margin: 0.8rem 0;
    color: var(--text-primary);
    font-size: 0.9rem;
}

.week-summary {
    background: rgba(45, 106, 79, 0.2);
    border-left: 3px solid var(--lime-accent);
    border-radius: 0 8px 8px 0;
    padding: 0.8rem 1rem;
    margin: 0.5rem 0;
    font-size: 0.88rem;
}

[data-testid="stDataFrame"] {
    border: 1px solid var(--border);
    border-radius: 8px;
}

.stButton > button {
    background: linear-gradient(135deg, #2d6a4f, #40916c);
    color: white;
    border: none;
    border-radius: 8px;
    font-family: 'Syne', sans-serif;
    font-weight: 600;
    letter-spacing: 0.05em;
    padding: 0.6rem 1.6rem;
    transition: all 0.2s;
}
.stButton > button:hover {
    background: linear-gradient(135deg, #40916c, #52b788);
    transform: translateY(-1px);
    box-shadow: 0 4px 16px rgba(82,183,136,0.3);
}

.stNumberInput input,
.stTextInput input,
.stSelectbox select {
    background: rgba(26,51,32,0.5) !important;
    border: 1px solid var(--border) !important;
    color: var(--text-primary) !important;
    border-radius: 6px !important;
}

.stTabs [data-baseweb="tab"] {
    font-family: 'Syne', sans-serif;
    font-size: 0.85rem;
    font-weight: 600;
    color: var(--text-muted);
}
.stTabs [aria-selected="true"] {
    color: var(--lime-accent) !important;
    border-bottom-color: var(--lime-accent) !important;
}

.stProgress > div > div {
    background: linear-gradient(90deg, #2d6a4f, #52b788) !important;
}

#MainMenu, footer, header { visibility: hidden; }
</style>
""", unsafe_allow_html=True)


# ==============================================================================
# CONSTANTS & CONFIG
# ==============================================================================

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

SOIL_TYPE_MULTIPLIERS = {
    'Sandy' : {'N': 1.15, 'P': 1.05, 'K': 0.95, 'recovery': 0.90},
    'Clay'  : {'N': 0.90, 'P': 0.95, 'K': 1.10, 'recovery': 1.05},
    'Loamy' : {'N': 1.00, 'P': 1.00, 'K': 1.00, 'recovery': 1.10},
}

COLORS = {
    'N'       : '#52b788',
    'P'       : '#d4a017',
    'K'       : '#74b3ce',
    'chemical': '#c1121f',
    'organic' : '#52b788',
    'recovery': '#9b72cf',
    'bg'      : 'rgba(0,0,0,0)',
    'grid'    : 'rgba(82,183,136,0.1)',
    'text'    : '#e8f5e9',
}

PLOT_LAYOUT = dict(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor ='rgba(0,0,0,0)',
    font=dict(color='#e8f5e9', family='DM Sans'),
    legend=dict(bgcolor='rgba(13,26,15,0.8)', bordercolor='rgba(82,183,136,0.3)', borderwidth=1),
    margin=dict(l=50, r=30, t=50, b=50),
)

# Shared axis grid style — applied via update_xaxes/update_yaxes, not in update_layout
_AXIS_STYLE = dict(gridcolor='rgba(82,183,136,0.1)', zerolinecolor='rgba(82,183,136,0.1)')


# ==============================================================================
# BACKEND FUNCTIONS
# ==============================================================================

def load_data(uploaded_file):
    name = uploaded_file.name.lower()
    if name.endswith('.xlsx') or name.endswith('.xls'):
        return pd.read_excel(uploaded_file)
    return pd.read_csv(uploaded_file)


def preprocess(df):
    df = df.copy()
    df = df.sort_values(['Farmer_ID', 'Week_Number']).reset_index(drop=True)
    df['Extreme_Event_Flag'] = df['Extreme_Event_Flag'].fillna('None')

    encoders = {}
    for col in ['Crop_Name', 'Weather_Risk_Level',
                'Farmer_Action_Compliance', 'Farmer_Archetype', 'Extreme_Event_Flag']:
        le = LabelEncoder()
        df[col + '_Enc'] = le.fit_transform(df[col].astype(str))
        encoders[col] = le

    for nutrient in ['Current_Soil_Nitrogen_kg_per_ha',
                     'Current_Soil_Phosphorus_kg_per_ha',
                     'Current_Soil_Potassium_kg_per_ha',
                     'Soil_Recovery_Score']:
        df[nutrient + '_Change'] = df.groupby('Farmer_ID')[nutrient].diff()

    df['OrganicMatter_Change'] = df.groupby(
        'Farmer_ID')['Current_Soil_Organic_Matter_Percent'].diff()
    df['Organic_Ratio'] = df.groupby('Farmer_ID')[
        'Current_Soil_Organic_Matter_Percent'].transform(
        lambda x: (x - x.iloc[0]) / (x.iloc[0] + 1e-6) * 100)

    df_model = df.dropna(subset=[
        'Current_Soil_Nitrogen_kg_per_ha_Change',
        'Current_Soil_Phosphorus_kg_per_ha_Change',
        'Current_Soil_Potassium_kg_per_ha_Change',
        'Soil_Recovery_Score_Change',
    ]).copy()

    return df, df_model, encoders


def train_model(df_model):
    X = df_model[FEATURE_COLS]
    y = df_model[TARGET_COLS]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42)

    scaler = StandardScaler()
    X_train_sc = scaler.fit_transform(X_train)
    X_test_sc  = scaler.transform(X_test)

    model = MultiOutputRegressor(
        RandomForestRegressor(n_estimators=200, max_depth=10,
                              random_state=42, n_jobs=-1)
    )
    model.fit(X_train_sc, y_train)
    y_pred = model.predict(X_test_sc)

    metrics = {}
    names   = ['Nitrogen Δ', 'Phosphorus Δ', 'Potassium Δ', 'Recovery Δ']
    for i, name in enumerate(names):
        metrics[name] = {
            'MAE': round(mean_absolute_error(y_test.iloc[:, i], y_pred[:, i]), 4),
            'R2' : round(r2_score(y_test.iloc[:, i], y_pred[:, i]), 4),
        }

    avg_r2 = np.mean([v['R2'] for v in metrics.values()])
    return model, scaler, metrics, avg_r2


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


def safe_encode(encoder, value, fallback_index=0):
    if value in encoder.classes_:
        return encoder.transform([value])[0]
    return fallback_index


def get_alert_status(recovery_score, risk):
    if risk == 'Extreme' or recovery_score < 30:
        return 'STOP'
    elif risk == 'High' or recovery_score < 50:
        return 'DELAY'
    else:
        return 'SAFE'


# ------------------------------------------------------------------------------
# TOOL 1: Ideal 42-Day NPK Transition
# ------------------------------------------------------------------------------

def tool1_ideal_42day(model, scaler, df, encoders,
                      crop_name, soil_type,
                      start_N, start_P, start_K,
                      start_pH=7.3, start_organic=0.65, start_recovery=35.0):
    ideal_temp     = df[df['Weather_Risk_Level'] == 'Low']['Current_Temp'].mean()
    ideal_rain     = df[df['Weather_Risk_Level'] == 'Low']['Current_Rain'].mean()
    ideal_humidity = df[df['Weather_Risk_Level'] == 'Low']['Current_Hum'].mean()

    # Fallback if filtered df is empty
    if pd.isna(ideal_temp):   ideal_temp = 25.0
    if pd.isna(ideal_rain):   ideal_rain = 60.0
    if pd.isna(ideal_humidity): ideal_humidity = 60.0

    crop_enc   = safe_encode(encoders['Crop_Name'], crop_name)
    risk_enc   = safe_encode(encoders['Weather_Risk_Level'], 'Low')
    comply_enc = safe_encode(encoders['Farmer_Action_Compliance'], 'Full')
    event_enc  = safe_encode(encoders['Extreme_Event_Flag'], 'None')
    soil_mult  = SOIL_TYPE_MULTIPLIERS.get(soil_type, SOIL_TYPE_MULTIPLIERS['Loamy'])

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

        dN   = np.clip(deltas[0] * soil_mult['N'],        -60,  5)
        dP   = np.clip(deltas[1] * soil_mult['P'],         -2,  3)
        dK   = np.clip(deltas[2] * soil_mult['K'],         -1,  5)
        dRec = np.clip(deltas[3] * soil_mult['recovery'],  -3, 20)

        org_gain     = 0.08
        org          = min(org + org_gain, 3.0)
        organic_pct  = min((week / 7) * 40, 40)
        chemical_pct = 100 - organic_pct
        alert        = get_alert_status(rec, 'Low')

        for d in range(6):
            actual_day = (week - 1) * 6 + d + 1
            if actual_day > 42:
                break
            frac  = (d + 1) / 6.0
            day_N = np.clip(N + dN * frac,   50,  600)
            day_P = np.clip(P + dP * frac,    5,   60)
            day_K = np.clip(K + dK * frac,   80,  400)
            day_r = np.clip(rec + dRec*frac, 25,  100)

            results.append({
                'Day': actual_day, 'Week': week,
                'Nitrogen_kg_ha'    : round(day_N, 2),
                'Phosphorus_kg_ha'  : round(day_P, 2),
                'Potassium_kg_ha'   : round(day_K, 2),
                'Soil_Recovery_Score': round(day_r, 2),
                'Organic_Matter_Pct': round(org, 3),
                'Organic_Input_Pct' : round(organic_pct, 1),
                'Chemical_Input_Pct': round(chemical_pct, 1),
                'Weather_Risk'      : 'Low',
                'Extreme_Event'     : 'None',
                'Alert_Status'      : alert,
                'Crop'              : crop_name,
                'Soil_Type'         : soil_type,
            })

        N   = np.clip(N + dN,   50,  600)
        P   = np.clip(P + dP,    5,   60)
        K   = np.clip(K + dK,   80,  400)
        rec = np.clip(rec+dRec, 25,  100)

    return pd.DataFrame(results)


# ------------------------------------------------------------------------------
# TOOL 2: Real-World 42-Day Simulation
# ------------------------------------------------------------------------------

def tool2_realworld_42day(model, scaler, encoders,
                          crop_name, soil_type,
                          start_N, start_P, start_K,
                          weekly_weather,
                          start_pH=7.3, start_organic=0.65, start_recovery=35.0):
    crop_enc   = safe_encode(encoders['Crop_Name'], crop_name)
    comply_enc = safe_encode(encoders['Farmer_Action_Compliance'], 'Full')
    soil_mult  = SOIL_TYPE_MULTIPLIERS.get(soil_type, SOIL_TYPE_MULTIPLIERS['Loamy'])

    N, P, K = start_N, start_P, start_K
    pH, org, rec = start_pH, start_organic, start_recovery
    results = []

    for week in range(1, 8):
        wdata    = weekly_weather[week - 1]
        temp     = np.clip(wdata['temp'],     10,  50)
        rain     = np.clip(wdata['rain'],      0, 250)
        humidity = np.clip(wdata['humidity'], 20,  95)

        risk, event = classify_weather(temp, rain, humidity)
        risk_enc    = safe_encode(encoders['Weather_Risk_Level'], risk)
        event_enc   = safe_encode(encoders['Extreme_Event_Flag'], event)

        X_row = pd.DataFrame([[
            temp, rain, humidity,
            pH, org, N, P, K, rec, week,
            crop_enc, risk_enc, comply_enc, event_enc
        ]], columns=FEATURE_COLS)

        deltas = model.predict(scaler.transform(X_row))[0]

        if temp >= 45:
            wm = {'N': 1.4, 'P': 1.2, 'K': 1.2, 'rec_pos': 0.3, 'rec_neg': 1.4}
        elif risk == 'High':
            wm = {'N': 1.2, 'P': 1.0, 'K': 1.0, 'rec_pos': 0.5, 'rec_neg': 1.2}
        elif risk == 'Medium':
            wm = {'N': 1.0, 'P': 1.0, 'K': 1.0, 'rec_pos': 0.8, 'rec_neg': 1.0}
        else:
            wm = {'N': 1.0, 'P': 1.0, 'K': 1.0, 'rec_pos': 1.0, 'rec_neg': 1.0}

        dN   = np.clip(deltas[0] * wm['N']  * soil_mult['N'], -100,  5)
        dP   = np.clip(deltas[1] * wm['P']  * soil_mult['P'],   -5,  3)
        dK   = np.clip(deltas[2] * wm['K']  * soil_mult['K'],   -5,  5)
        raw_rec = deltas[3] * soil_mult['recovery']
        if raw_rec >= 0:
            dRec = np.clip(raw_rec * wm['rec_pos'], 0, 15)
        else:
            dRec = np.clip(raw_rec * wm['rec_neg'], -15, 0)

        org_gain     = 0.04 if risk in ['Extreme','High'] else 0.08
        org          = min(org + org_gain, 3.0)
        base_org     = (week / 7) * 40
        reduction    = {'Extreme': 0.4, 'High': 0.7, 'Medium': 0.9}.get(risk, 1.0)
        organic_pct  = base_org * reduction
        chemical_pct = 100 - organic_pct
        alert        = get_alert_status(rec, risk)

        for d in range(6):
            actual_day = (week - 1) * 6 + d + 1
            if actual_day > 42:
                break
            frac  = (d + 1) / 6.0
            day_N = np.clip(N + dN * frac,   50,  600)
            day_P = np.clip(P + dP * frac,    5,   60)
            day_K = np.clip(K + dK * frac,   80,  400)
            day_r = np.clip(rec+dRec*frac,   25,  100)

            results.append({
                'Day': actual_day, 'Week': week,
                'Temperature_C'     : temp,
                'Rainfall_mm'       : rain,
                'Humidity_Pct'      : humidity,
                'Weather_Risk'      : risk,
                'Extreme_Event'     : event,
                'Nitrogen_kg_ha'    : round(day_N, 2),
                'Phosphorus_kg_ha'  : round(day_P, 2),
                'Potassium_kg_ha'   : round(day_K, 2),
                'Soil_Recovery_Score': round(day_r, 2),
                'Organic_Input_Pct' : round(organic_pct, 1),
                'Chemical_Input_Pct': round(chemical_pct, 1),
                'Alert_Status'      : alert,
                'Crop'              : crop_name,
                'Soil_Type'         : soil_type,
            })

        N   = np.clip(N + dN,   50,  600)
        P   = np.clip(P + dP,    5,   60)
        K   = np.clip(K + dK,   80,  400)
        rec = np.clip(rec+dRec, 25,  100)

    return pd.DataFrame(results)


# ------------------------------------------------------------------------------
# TOOL 3: Crop Growth Stage Prediction
# ------------------------------------------------------------------------------

def tool3_crop_age_prediction(df, crop_name, current_N, current_P,
                               current_K, current_recovery, current_week):
    stages      = GROWTH_STAGES.get(crop_name, GROWTH_STAGES['Wheat'])
    stage_idx   = min(current_week - 1, len(stages) - 1)
    curr_stage  = stages[stage_idx]
    next_stage  = stages[min(stage_idx + 1, len(stages) - 1)]

    crop_df = df[df['Crop_Name'] == crop_name]
    week_df = crop_df[crop_df['Week_Number'] == current_week]
    if len(week_df) == 0:
        week_df = crop_df

    avg_N   = week_df['Current_Soil_Nitrogen_kg_per_ha'].mean()
    avg_P   = week_df['Current_Soil_Phosphorus_kg_per_ha'].mean()
    avg_K   = week_df['Current_Soil_Potassium_kg_per_ha'].mean()
    avg_rec = week_df['Soil_Recovery_Score'].mean()

    # Fallback for empty crops
    if pd.isna(avg_N):   avg_N   = current_N
    if pd.isna(avg_P):   avg_P   = current_P
    if pd.isna(avg_K):   avg_K   = current_K
    if pd.isna(avg_rec): avg_rec = current_recovery

    n_h = min(current_N        / avg_N,   1.0) * 100 if avg_N   > 0 else 50
    p_h = min(current_P        / avg_P,   1.0) * 100 if avg_P   > 0 else 50
    k_h = min(current_K        / avg_K,   1.0) * 100 if avg_K   > 0 else 50
    r_h = min(current_recovery / avg_rec, 1.0) * 100 if avg_rec > 0 else 50
    overall = round((n_h + p_h + k_h + r_h) / 4, 1)

    if overall >= 80:
        advice = "Excellent condition. Continue organic transition as planned."
        status = "SAFE"
    elif overall >= 60:
        advice = "Good condition. Monitor NPK closely in the next 7 days."
        status = "SAFE"
    elif overall >= 40:
        advice = "Moderate stress detected. Consider slowing organic transition rate."
        status = "DELAY"
    else:
        advice = "High stress. Pause organic transition. Focus on soil recovery first."
        status = "STOP"

    return {
        'crop': crop_name, 'week': current_week,
        'days_completed': (current_week - 1) * 6,
        'growth_stage': curr_stage, 'next_stage': next_stage,
        'n_health': round(n_h, 1), 'p_health': round(p_h, 1),
        'k_health': round(k_h, 1), 'recovery_health': round(r_h, 1),
        'overall_health': overall, 'recommendation': advice, 'alert': status,
        'avg_N': round(avg_N, 1), 'avg_P': round(avg_P, 1),
        'avg_K': round(avg_K, 1), 'avg_rec': round(avg_rec, 1),
    }


# ==============================================================================
# PLOTLY GRAPH FUNCTIONS
# ==============================================================================

def graph1_chemical_vs_organic(report: pd.DataFrame, crop_name: str) -> go.Figure:
    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=[
            'NPK Soil Levels Over 42 Days — Chemical Declining, Organic Supplementing',
            'Chemical Input ↓  vs  Organic Input ↑  (% share)'
        ],
        vertical_spacing=0.14,
        row_heights=[0.6, 0.4],
    )

    fig.add_trace(go.Scatter(
        x=report['Day'], y=report['Nitrogen_kg_ha'],
        name='Nitrogen (N)', line=dict(color=COLORS['N'], width=2.5),
        mode='lines+markers', marker=dict(size=3),
    ), row=1, col=1)
    fig.add_trace(go.Scatter(
        x=report['Day'], y=report['Phosphorus_kg_ha'],
        name='Phosphorus (P)', line=dict(color=COLORS['P'], width=2.5),
        mode='lines+markers', marker=dict(size=3),
    ), row=1, col=1)
    fig.add_trace(go.Scatter(
        x=report['Day'], y=report['Potassium_kg_ha'],
        name='Potassium (K)', line=dict(color=COLORS['K'], width=2.5),
        mode='lines+markers', marker=dict(size=3),
    ), row=1, col=1)

    for w in range(1, 7):
        fig.add_vline(x=w*6+0.5, line_dash='dot',
                      line_color='rgba(255,255,255,0.15)', row=1, col=1)
        fig.add_annotation(x=w*6+1, y=report['Nitrogen_kg_ha'].max()*1.02,
                           text=f'W{w+1}', showarrow=False,
                           font=dict(size=9, color='rgba(200,200,200,0.5)'))

    fig.add_trace(go.Scatter(
        x=report['Day'], y=report['Chemical_Input_Pct'],
        name='Chemical %', fill='tozeroy',
        line=dict(color=COLORS['chemical'], width=2),
        fillcolor='rgba(193,18,31,0.25)',
    ), row=2, col=1)
    fig.add_trace(go.Scatter(
        x=report['Day'], y=report['Organic_Input_Pct'],
        name='Organic %', fill='tozeroy',
        line=dict(color=COLORS['organic'], width=2),
        fillcolor='rgba(82,183,136,0.25)',
    ), row=2, col=1)

    fig.update_layout(
        title=dict(text=f'<b>GRAPH 1 — Ideal NPK Transition</b>  |  {crop_name}',
                   font=dict(size=15, color=COLORS['N'])),
        height=560,
        **PLOT_LAYOUT,
    )
    fig.update_xaxes(title_text='Day', **_AXIS_STYLE)
    fig.update_yaxes(title_text='kg/ha', row=1, col=1, **_AXIS_STYLE)
    fig.update_yaxes(title_text='%', row=2, col=1, range=[0,110], **_AXIS_STYLE)
    return fig


def graph2_initial_vs_weather(report_t1: pd.DataFrame,
                               report_t2: pd.DataFrame,
                               crop_name: str,
                               start_N: float, start_P: float, start_K: float) -> go.Figure:
    nutrients = [
        ('Nitrogen_kg_ha',   'Nitrogen (N)',   start_N, COLORS['N']),
        ('Phosphorus_kg_ha', 'Phosphorus (P)', start_P, COLORS['P']),
        ('Potassium_kg_ha',  'Potassium (K)',  start_K, COLORS['K']),
    ]

    fig = make_subplots(
        rows=3, cols=1,
        subplot_titles=[f'{lbl} — Initial vs Predicted' for _, lbl, _, _ in nutrients],
        vertical_spacing=0.10,
    )

    for i, (col, lbl, start_val, color) in enumerate(nutrients, 1):
        fig.add_trace(go.Scatter(
            x=[1, 42], y=[start_val, start_val],
            name=f'Initial {lbl}: {start_val}',
            line=dict(color='rgba(200,200,200,0.5)', width=1.5, dash='dash'),
            showlegend=(i == 1),
        ), row=i, col=1)

        fig.add_trace(go.Scatter(
            x=report_t1['Day'], y=report_t1[col],
            name='Ideal (no extreme weather)',
            line=dict(color=color, width=1.8, dash='dot'),
            opacity=0.55,
            showlegend=(i == 1),
        ), row=i, col=1)

        fig.add_trace(go.Scatter(
            x=report_t2['Day'], y=report_t2[col],
            name='Predicted (your weather input)',
            line=dict(color=color, width=2.8),
            mode='lines+markers', marker=dict(size=3),
            showlegend=(i == 1),
        ), row=i, col=1)

        # Shade gap
        fig.add_trace(go.Scatter(
            x=pd.concat([report_t2['Day'], report_t2['Day'][::-1]]),
            y=pd.concat([report_t2[col],
                         pd.Series([start_val]*len(report_t2)).reset_index(drop=True)[::-1]]),
            fill='toself',
            fillcolor=f'rgba(82,183,136,0.08)',
            line=dict(color='rgba(0,0,0,0)'),
            showlegend=False,
        ), row=i, col=1)

        if 'Weather_Risk' in report_t2.columns:
            for _, grp in report_t2.groupby('Week'):
                risk = grp['Weather_Risk'].iloc[0]
                if risk in ['Extreme', 'High']:
                    shade = 'rgba(193,18,31,0.12)' if risk == 'Extreme' \
                            else 'rgba(224,123,0,0.10)'
                    d0, d1 = grp['Day'].min(), grp['Day'].max()
                    fig.add_vrect(x0=d0-0.5, x1=d1+0.5,
                                  fillcolor=shade, line_width=0,
                                  row=i, col=1)

        for w in range(1, 7):
            fig.add_vline(x=w*6+0.5, line_dash='dot',
                          line_color='rgba(255,255,255,0.12)',
                          row=i, col=1)

    fig.update_layout(
        title=dict(
            text=f'<b>GRAPH 2 — NPK Comparison: Initial vs Weather-Based Prediction</b>  |  {crop_name}',
            font=dict(size=15, color=COLORS['N'])),
        height=720,
        **PLOT_LAYOUT,
    )
    fig.update_xaxes(title_text='Day', **_AXIS_STYLE)
    fig.update_yaxes(title_text='kg/ha', **_AXIS_STYLE)
    return fig


def graph_soil_recovery(report: pd.DataFrame, title_suffix: str) -> go.Figure:
    fig = go.Figure()

    fig.add_hrect(y0=0,  y1=30, fillcolor='rgba(193,18,31,0.08)',  line_width=0)
    fig.add_hrect(y0=30, y1=55, fillcolor='rgba(224,123,0,0.08)',  line_width=0)
    fig.add_hrect(y0=55, y1=100,fillcolor='rgba(82,183,136,0.06)', line_width=0)

    fig.add_annotation(x=42, y=15,  text='STOP ZONE',  showarrow=False,
                       font=dict(color='rgba(193,18,31,0.6)',  size=10))
    fig.add_annotation(x=42, y=42,  text='DELAY ZONE', showarrow=False,
                       font=dict(color='rgba(224,123,0,0.6)',  size=10))
    fig.add_annotation(x=42, y=72,  text='SAFE ZONE',  showarrow=False,
                       font=dict(color='rgba(82,183,136,0.6)', size=10))

    fig.add_trace(go.Scatter(
        x=report['Day'], y=report['Soil_Recovery_Score'],
        name='Soil Recovery', fill='tozeroy',
        line=dict(color=COLORS['recovery'], width=2.5),
        fillcolor='rgba(155,114,207,0.15)',
        mode='lines+markers', marker=dict(size=3),
    ))

    fig.update_layout(
        title=f'<b>Soil Recovery Score</b> — {title_suffix}',
        height=320,
        **PLOT_LAYOUT,
    )
    fig.update_xaxes(title='Day', **_AXIS_STYLE)
    fig.update_yaxes(title='Score (0–100)', range=[0, 105], **_AXIS_STYLE)
    return fig


def graph_weather_risk_impact(report_t2: pd.DataFrame) -> go.Figure:
    if 'Weather_Risk' not in report_t2.columns:
        return go.Figure()

    weekly = report_t2.groupby('Week').agg({
        'Nitrogen_kg_ha'   : 'mean',
        'Phosphorus_kg_ha' : 'mean',
        'Potassium_kg_ha'  : 'mean',
        'Weather_Risk'     : 'first',
    }).reset_index()

    fig = go.Figure()
    for nutrient_col, nutrient_label, color in [
        ('Nitrogen_kg_ha',   'N avg (kg/ha)', COLORS['N']),
        ('Phosphorus_kg_ha', 'P avg (kg/ha)', COLORS['P']),
        ('Potassium_kg_ha',  'K avg (kg/ha)', COLORS['K']),
    ]:
        fig.add_trace(go.Bar(
            x=[f"W{w}\n{r}" for w, r in zip(weekly['Week'], weekly['Weather_Risk'])],
            y=weekly[nutrient_col],
            name=nutrient_label,
            marker_color=color,
            opacity=0.8,
        ))

    fig.update_layout(
        title='<b>Weekly Average NPK by Weather Risk Level</b>',
        barmode='group',
        height=350,
        **PLOT_LAYOUT,
    )
    fig.update_xaxes(title='Week (Risk Level)', **_AXIS_STYLE)
    fig.update_yaxes(title='kg/ha', **_AXIS_STYLE)
    return fig


def graph_crop_stage_gauge(overall_health: float, crop_name: str) -> go.Figure:
    fig = go.Figure(go.Indicator(
        mode='gauge+number+delta',
        value=overall_health,
        title={'text': f'Overall Crop Health — {crop_name}',
               'font': {'color': COLORS['text'], 'size': 14}},
        gauge={
            'axis': {'range': [0, 100], 'tickcolor': COLORS['text']},
            'bar' : {'color': COLORS['N']},
            'steps': [
                {'range': [0,  40], 'color': 'rgba(193,18,31,0.3)'},
                {'range': [40, 60], 'color': 'rgba(224,123,0,0.3)'},
                {'range': [60,100], 'color': 'rgba(82,183,136,0.2)'},
            ],
            'threshold': {
                'line': {'color': COLORS['P'], 'width': 3},
                'thickness': 0.75, 'value': 60,
            },
        },
        number={'font': {'color': COLORS['N'], 'size': 36}},
    ))
    fig.update_layout(height=280, **PLOT_LAYOUT)
    return fig


# ==============================================================================
# UTILITY HELPERS
# ==============================================================================

def df_to_csv_bytes(df: pd.DataFrame) -> bytes:
    return df.to_csv(index=False).encode('utf-8')


def render_metric_card(label: str, value: str, sub: str = ''):
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">{label}</div>
        <div class="metric-value">{value}</div>
        {"<div class='metric-sub'>" + sub + "</div>" if sub else ""}
    </div>
    """, unsafe_allow_html=True)


def render_alert_badge(status: str):
    cls  = {'SAFE':'badge-safe','DELAY':'badge-delay','STOP':'badge-stop'}.get(status,'badge-safe')
    icon = {'SAFE':'✅','DELAY':'⚠️','STOP':'🛑'}.get(status,'✅')
    st.markdown(f'<span class="{cls}">{icon} {status}</span>', unsafe_allow_html=True)


def render_week_summary(week: int, row: pd.Series):
    st.markdown(f"""
    <div class="week-summary">
        <strong>Week {week} Summary</strong> &nbsp;|&nbsp;
        N: <b>{row['Nitrogen_kg_ha']}</b> kg/ha &nbsp;
        P: <b>{row['Phosphorus_kg_ha']}</b> kg/ha &nbsp;
        K: <b>{row['Potassium_kg_ha']}</b> kg/ha &nbsp;
        Recovery: <b>{row['Soil_Recovery_Score']}</b> &nbsp;
        Organic: <b>{row['Organic_Input_Pct']}%</b> &nbsp;
        Chemical: <b>{row['Chemical_Input_Pct']}%</b>
    </div>
    """, unsafe_allow_html=True)


# ==============================================================================
# SIDEBAR
# ==============================================================================

def render_sidebar():
    st.sidebar.markdown("""
    <div style="text-align:center; padding: 1rem 0 1.5rem 0;">
        <div style="font-size:2.4rem">🌱</div>
        <div style="font-family:'Syne',sans-serif; font-size:1.1rem;
                    font-weight:800; color:#52b788; letter-spacing:0.05em;">
            SOIL SENSE V2
        </div>
        <div style="font-size:0.7rem; color:#a5c5a8; margin-top:2px;">
            AI Soil Recovery Intelligence
        </div>
    </div>
    <hr style="border-color:rgba(82,183,136,0.2); margin: 0 0 1rem 0;">
    """, unsafe_allow_html=True)

    menu = st.sidebar.radio(
        "Navigation",
        [
            "🏠  Dashboard Overview",
            "🤖  Train AI Model",
            "📊  Dataset Prediction",
            "👨‍🌾  Manual Farmer Prediction",
            "🌿  42-Day Ideal Simulation",
            "🌦️  42-Day Real-World Simulation",
            "🌾  Crop Growth Stage",
            "📡  Weather Monitoring",
            "📈  Analytics & Graphs",
            "📥  Download Reports",
        ],
        label_visibility='collapsed',
    )

    st.sidebar.markdown("<hr style='border-color:rgba(82,183,136,0.2);'>", unsafe_allow_html=True)

    if 'model' in st.session_state:
        st.sidebar.markdown("""
        <div style="background:rgba(45,106,79,0.3); border:1px solid rgba(82,183,136,0.4);
                    border-radius:8px; padding:0.6rem 0.8rem; font-size:0.8rem; color:#52b788;">
            ✅ AI Model Trained & Ready
        </div>""", unsafe_allow_html=True)
    else:
        st.sidebar.markdown("""
        <div style="background:rgba(193,18,31,0.15); border:1px solid rgba(193,18,31,0.35);
                    border-radius:8px; padding:0.6rem 0.8rem; font-size:0.8rem; color:#ff9999;">
            ⚠️ No model trained. Upload dataset first.
        </div>""", unsafe_allow_html=True)

    st.sidebar.markdown("""
    <div style="margin-top:1.5rem; font-size:0.7rem; color:rgba(165,197,168,0.5);
                text-align:center;">
        IoT-Ready Architecture · Punjab Validated<br>
        Temp: 10–50°C · Rain: 0–250mm · RH: 20–95%
    </div>
    """, unsafe_allow_html=True)

    # Strip emoji prefix and return clean page name
    return menu.split("  ", 1)[-1].strip()


# ==============================================================================
# PAGE: DASHBOARD OVERVIEW
# ==============================================================================

def page_overview():
    st.markdown("""
    <div class="platform-header">
        <div style="font-size:2.8rem">🌱</div>
        <div>
            <p class="platform-title">SOIL SENSE V2</p>
            <p class="platform-subtitle">
                AI-Powered Soil Recovery Intelligence Platform &nbsp;·&nbsp;
                Punjab Smart Agri Ecosystem &nbsp;·&nbsp;
                Chemical → Organic Transition Engine
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if 'df_full' not in st.session_state:
        st.markdown("""
        <div class="info-box">
            👋 Welcome to <b>SOIL SENSE V2</b>. To get started, go to
            <b>Train AI Model</b> in the sidebar and upload your dataset.
        </div>
        """, unsafe_allow_html=True)
        return

    df = st.session_state['df_full']

    st.markdown('<div class="section-header">Platform Overview</div>', unsafe_allow_html=True)
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1: render_metric_card("Total Records",   f"{len(df):,}", "dataset rows")
    with c2: render_metric_card("Unique Farmers",  f"{df['Farmer_ID'].nunique()}", "enrolled")
    with c3: render_metric_card("Crops Tracked",   f"{df['Crop_Name'].nunique()}", "varieties")
    with c4: render_metric_card("Weeks of Data",   f"{df['Week_Number'].max()}", "= 42 days")
    with c5:
        acc = st.session_state.get('model_accuracy', 0)
        render_metric_card("Model Accuracy", f"{acc*100:.1f}%", "avg R² score")

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown('<div class="section-header">Alert Status Distribution</div>', unsafe_allow_html=True)
    if 'Alert_Status' in df.columns:
        alert_counts = df['Alert_Status'].value_counts()
        safe_n  = alert_counts.get('SAFE',  0)
        delay_n = alert_counts.get('DELAY', 0)
        stop_n  = alert_counts.get('STOP',  0)
    else:
        safe_n, delay_n, stop_n = 0, 0, 0

    ca, cb, cc = st.columns(3)
    with ca: render_metric_card("✅ SAFE",  f"{safe_n:,}",  "healthy transitions")
    with cb: render_metric_card("⚠️ DELAY", f"{delay_n:,}", "slow down advised")
    with cc: render_metric_card("🛑 STOP",  f"{stop_n:,}",  "unsafe to proceed")

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown('<div class="section-header">Day 1 vs Day 42 — Average NPK Comparison</div>',
                unsafe_allow_html=True)

    w1 = df[df['Week_Number'] == df['Week_Number'].min()]
    w7 = df[df['Week_Number'] == df['Week_Number'].max()]

    fig_compare = go.Figure()
    for nutrient, col in [('Nitrogen','Current_Soil_Nitrogen_kg_per_ha'),
                          ('Phosphorus','Current_Soil_Phosphorus_kg_per_ha'),
                          ('Potassium','Current_Soil_Potassium_kg_per_ha')]:
        fig_compare.add_trace(go.Bar(
            name=f'Day 1', x=[nutrient],
            y=[w1[col].mean()],
            marker_color='rgba(193,18,31,0.7)',
            showlegend=(nutrient == 'Nitrogen'),
            legendgroup='day1',
        ))
        fig_compare.add_trace(go.Bar(
            name=f'Day 42', x=[nutrient],
            y=[w7[col].mean()],
            marker_color='rgba(82,183,136,0.8)',
            showlegend=(nutrient == 'Nitrogen'),
            legendgroup='day42',
        ))

    fig_compare.update_layout(
        barmode='group', height=320,
        title='Average NPK: Week 1 (Day 1) vs Week 7 (Day 42)',
        **PLOT_LAYOUT,
    )
    fig_compare.update_yaxes(title='kg/ha', **_AXIS_STYLE)
    fig_compare.update_xaxes(**_AXIS_STYLE)
    st.plotly_chart(fig_compare, use_container_width=True)

    st.markdown('<div class="section-header">Average Soil Recovery Score by Week</div>',
                unsafe_allow_html=True)
    rec_by_week = df.groupby('Week_Number')['Soil_Recovery_Score'].mean().reset_index()
    fig_rec = go.Figure(go.Scatter(
        x=rec_by_week['Week_Number']*6 - 3,
        y=rec_by_week['Soil_Recovery_Score'],
        mode='lines+markers+text',
        text=[f"{v:.1f}" for v in rec_by_week['Soil_Recovery_Score']],
        textposition='top center',
        line=dict(color=COLORS['recovery'], width=3),
        fill='tozeroy', fillcolor='rgba(155,114,207,0.12)',
        marker=dict(size=8, color=COLORS['recovery']),
    ))
    fig_rec.update_layout(height=280, **PLOT_LAYOUT)
    fig_rec.update_xaxes(title='Day (approx.)', **_AXIS_STYLE)
    fig_rec.update_yaxes(title='Recovery Score', **_AXIS_STYLE)
    st.plotly_chart(fig_rec, use_container_width=True)


# ==============================================================================
# PAGE: TRAIN AI MODEL
# ==============================================================================

def page_train():
    st.markdown('<div class="section-header">🤖 Train AI Model</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="info-box">
        Upload your Punjab Smart Agri Ecosystem dataset (.xlsx or .csv).
        The model trains on the actual data — no dummy values, no shortcuts.<br><br>
        <b>Algorithm:</b> MultiOutputRegressor → RandomForest (200 trees, depth 10)<br>
        <b>Predicts:</b> Weekly changes in N, P, K, and Soil Recovery Score
    </div>
    """, unsafe_allow_html=True)

    uploaded = st.file_uploader("Upload Dataset", type=['xlsx','xls','csv'])
    if uploaded is None:
        return

    with st.spinner("Loading dataset..."):
        try:
            df_raw = load_data(uploaded)
        except Exception as e:
            st.error(f"Failed to load file: {e}")
            return

    st.success(f"Loaded: {len(df_raw):,} rows × {len(df_raw.columns)} columns")

    tab1, tab2 = st.tabs(["📋 Preview", "🔍 Missing Values"])
    with tab1:
        st.dataframe(df_raw.head(20), use_container_width=True)
    with tab2:
        missing = df_raw.isnull().sum()
        missing = missing[missing > 0].reset_index()
        missing.columns = ['Column', 'Missing Count']
        missing['Missing %'] = (missing['Missing Count'] / len(df_raw) * 100).round(2)
        if len(missing):
            st.dataframe(missing, use_container_width=True)
            st.caption("Note: Extreme_Event_Flag nulls are expected (~94%) — filled with 'None'.")
        else:
            st.success("No missing values found.")

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🚀 Train AI Model", use_container_width=True):
        with st.spinner("Preprocessing..."):
            try:
                df_full, df_model, encoders = preprocess(df_raw)
            except Exception as e:
                st.error(f"Preprocessing failed: {e}")
                return

        prog = st.progress(0, text="Training RandomForest model...")
        with st.spinner("Training (200 trees × 4 targets)..."):
            try:
                model, scaler, metrics, avg_r2 = train_model(df_model)
            except Exception as e:
                st.error(f"Model training failed: {e}")
                return
        prog.progress(100, text="Training complete!")

        st.session_state['df_raw']        = df_raw
        st.session_state['df_full']       = df_full
        st.session_state['df_model']      = df_model
        st.session_state['encoders']      = encoders
        st.session_state['model']         = model
        st.session_state['scaler']        = scaler
        st.session_state['model_metrics'] = metrics
        st.session_state['model_accuracy']= avg_r2

        st.success("✅ Model trained and saved to session!")

        st.markdown('<div class="section-header">Model Performance</div>', unsafe_allow_html=True)
        mc1, mc2, mc3, mc4, mc5 = st.columns(5)
        for (name, vals), col in zip(metrics.items(), [mc1, mc2, mc3, mc4]):
            with col:
                render_metric_card(name, f"R²={vals['R2']}", f"MAE={vals['MAE']}")
        with mc5:
            render_metric_card("Avg R² Score", f"{avg_r2*100:.1f}%", "overall accuracy")

        fig_met = go.Figure()
        fig_met.add_trace(go.Bar(
            x=list(metrics.keys()),
            y=[v['R2'] for v in metrics.values()],
            marker_color=[COLORS['N'], COLORS['P'], COLORS['K'], COLORS['recovery']],
            text=[f"R²={v['R2']}" for v in metrics.values()],
            textposition='outside',
        ))
        fig_met.update_layout(title='R² Score per Target Variable', height=300, **PLOT_LAYOUT)
        fig_met.update_yaxes(range=[0, 1.1], title='R² Score', **_AXIS_STYLE)
        fig_met.update_xaxes(**_AXIS_STYLE)
        st.plotly_chart(fig_met, use_container_width=True)


# ==============================================================================
# PAGE: DATASET PREDICTION (BULK)
# ==============================================================================

def page_dataset_prediction():
    st.markdown('<div class="section-header">📊 Dataset Bulk Prediction</div>',
                unsafe_allow_html=True)

    if 'model' not in st.session_state:
        st.warning("Please train the model first from the **Train AI Model** page.")
        return

    st.markdown("""
    <div class="info-box">
        Upload a new dataset. The model will predict NPK transition,
        soil recovery, alert status, and crop stage for every row.
    </div>
    """, unsafe_allow_html=True)

    uploaded = st.file_uploader("Upload New Dataset for Prediction", type=['xlsx','xls','csv'])
    if uploaded is None:
        return

    with st.spinner("Loading..."):
        try:
            df_new = load_data(uploaded)
        except Exception as e:
            st.error(f"Failed to load file: {e}")
            return

    st.success(f"Loaded {len(df_new):,} rows")
    st.dataframe(df_new.head(10), use_container_width=True)

    if st.button("🔮 Run Bulk Prediction", use_container_width=True):
        model    = st.session_state['model']
        scaler   = st.session_state['scaler']
        encoders = st.session_state['encoders']

        with st.spinner("Running predictions..."):
            try:
                df_pred, _, _ = preprocess(df_new)
            except Exception as e:
                st.error(f"Preprocessing failed: {e}")
                return

            missing_f = [c for c in FEATURE_COLS if c not in df_pred.columns]
            if missing_f:
                st.warning(f"Missing feature columns: {missing_f}. Filling with 0.")
                for c in missing_f:
                    df_pred[c] = 0

            try:
                X    = df_pred[FEATURE_COLS].fillna(0)
                X_sc = scaler.transform(X)
                preds = model.predict(X_sc)
            except Exception as e:
                st.error(f"Prediction failed: {e}")
                return

            df_pred['Pred_N_Change']   = preds[:, 0].round(3)
            df_pred['Pred_P_Change']   = preds[:, 1].round(3)
            df_pred['Pred_K_Change']   = preds[:, 2].round(3)
            df_pred['Pred_Rec_Change'] = preds[:, 3].round(3)

            df_pred['Predicted_Recovery'] = (
                df_pred['Soil_Recovery_Score'] + df_pred['Pred_Rec_Change']).clip(25, 100)

            df_pred['Alert_Status'] = df_pred.apply(
                lambda r: get_alert_status(
                    r['Predicted_Recovery'],
                    r.get('Weather_Risk_Level', 'Medium')
                ), axis=1)

            df_pred['Crop_Stage'] = df_pred.apply(
                lambda r: GROWTH_STAGES.get(
                    str(r.get('Crop_Name', 'Wheat')),
                    GROWTH_STAGES['Wheat']
                )[min(int(r.get('Week_Number', 1)) - 1, 6)],
                axis=1)

        st.success(f"Predictions complete for {len(df_pred):,} rows.")

        out_cols = ['Farmer_ID','Crop_Name','Week_Number',
                    'Pred_N_Change','Pred_P_Change','Pred_K_Change',
                    'Pred_Rec_Change','Predicted_Recovery','Alert_Status','Crop_Stage']
        out_cols = [c for c in out_cols if c in df_pred.columns]
        st.dataframe(df_pred[out_cols], use_container_width=True)

        alert_counts = df_pred['Alert_Status'].value_counts().reset_index()
        alert_counts.columns = ['Alert','Count']
        fig_alert = px.pie(
            alert_counts, names='Alert', values='Count',
            color='Alert',
            color_discrete_map={'SAFE':'#52b788','DELAY':'#e07b00','STOP':'#c1121f'},
            title='Predicted Alert Distribution',
        )
        fig_alert.update_layout(height=300, **PLOT_LAYOUT)
        st.plotly_chart(fig_alert, use_container_width=True)

        st.session_state['bulk_prediction'] = df_pred[out_cols]
        csv = df_to_csv_bytes(df_pred[out_cols])
        st.download_button("📥 Download Prediction CSV", csv,
                           "bulk_prediction.csv", "text/csv")


# ==============================================================================
# PAGE: MANUAL FARMER PREDICTION
# ==============================================================================

def page_manual_prediction():
    st.markdown('<div class="section-header">👨‍🌾 Manual Farmer Prediction</div>',
                unsafe_allow_html=True)

    if 'model' not in st.session_state:
        st.warning("Please train the model first.")
        return

    st.markdown("""
    <div class="info-box">
        Enter your soil data manually. The AI will predict SAFE / DELAY / STOP,
        the 42-day transition path, and crop stage recommendation.
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Mandatory Inputs**")
        crop_name = st.selectbox("Crop Name", ['Wheat','Rice','Cotton','Mustard','Gram'])
        soil_type = st.selectbox("Soil Type", ['Loamy','Sandy','Clay'])
        start_N   = st.number_input("Nitrogen (N) kg/ha",   50.0, 600.0, 350.0, 10.0)
        start_P   = st.number_input("Phosphorus (P) kg/ha",  5.0,  60.0,  22.0,  1.0)
        start_K   = st.number_input("Potassium (K) kg/ha",  80.0, 400.0, 250.0, 10.0)

    with col2:
        st.markdown("**Optional Inputs**")
        start_pH       = st.slider("Soil pH",             4.0, 9.0, 7.3, 0.1)
        start_organic  = st.slider("Organic Matter (%)",  0.1, 5.0, 0.65, 0.05)
        start_recovery = st.slider("Soil Recovery Score", 25,  100, 35)
        temp           = st.slider("Temperature (°C)",    10,  50,  28)
        rain           = st.slider("Rainfall (mm/week)",  0,   250, 80)
        humidity       = st.slider("Humidity (%)",        20,  95,  60)

    if st.button("🔮 Run Prediction", use_container_width=True):
        model    = st.session_state['model']
        scaler   = st.session_state['scaler']
        encoders = st.session_state['encoders']
        df_full  = st.session_state['df_full']

        risk, event = classify_weather(temp, rain, humidity)

        X_row = pd.DataFrame([[
            temp, rain, humidity, start_pH, start_organic,
            start_N, start_P, start_K, start_recovery, 1,
            safe_encode(encoders['Crop_Name'], crop_name),
            safe_encode(encoders['Weather_Risk_Level'], risk),
            safe_encode(encoders['Farmer_Action_Compliance'], 'Full'),
            safe_encode(encoders['Extreme_Event_Flag'], event),
        ]], columns=FEATURE_COLS)

        deltas       = model.predict(scaler.transform(X_row))[0]
        pred_rec_end = np.clip(start_recovery + deltas[3] * 6, 25, 100)
        alert        = get_alert_status(pred_rec_end, risk)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("#### Immediate Assessment")
        ac1, ac2, ac3 = st.columns(3)
        with ac1:
            render_metric_card("Weather Risk", risk,
                               f"Event: {event}" if event != 'None' else "No extreme event")
        with ac2:
            render_metric_card("Transition Alert", alert, "Based on soil + weather")
        with ac3:
            render_metric_card("7-Day Recovery Est.", f"{pred_rec_end:.1f}",
                               "Soil Recovery Score")

        stage_info = tool3_crop_age_prediction(
            df_full, crop_name, start_N, start_P, start_K, start_recovery, 1)

        st.markdown("#### Crop Stage & Health")
        sc1, sc2, sc3, sc4 = st.columns(4)
        with sc1: render_metric_card("Growth Stage",   stage_info['growth_stage'], "Current stage")
        with sc2: render_metric_card("Next Stage",     stage_info['next_stage'],   "Coming up")
        with sc3: render_metric_card("Overall Health", f"{stage_info['overall_health']}%", "NPK+Recovery")
        with sc4: render_metric_card("Alert",          stage_info['alert'], "Status")

        st.markdown(f"""
        <div class="info-box">
            🌾 <b>Recommendation:</b> {stage_info['recommendation']}
        </div>
        """, unsafe_allow_html=True)

        st.markdown("#### Fertilizer Reduction Path (Ideal Scenario)")
        report_quick = tool1_ideal_42day(
            model, scaler, df_full, encoders, crop_name, soil_type,
            start_N, start_P, start_K, start_pH, start_organic, start_recovery)

        st.plotly_chart(graph1_chemical_vs_organic(report_quick, crop_name),
                        use_container_width=True)

        st.session_state['manual_report'] = report_quick
        st.session_state['manual_params'] = {
            'crop': crop_name, 'soil': soil_type,
            'N': start_N, 'P': start_P, 'K': start_K,
        }


# ==============================================================================
# PAGE: 42-DAY IDEAL SIMULATION
# ==============================================================================

def page_ideal_simulation():
    st.markdown('<div class="section-header">🌿 42-Day Ideal Simulation</div>',
                unsafe_allow_html=True)

    if 'model' not in st.session_state:
        st.warning("Please train the model first.")
        return

    st.markdown("""
    <div class="info-box">
        <b>Ideal scenario:</b> Low weather risk throughout, full farmer compliance,
        no extreme events. Shows the best-case chemical → organic transition path.
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        crop_name = st.selectbox("Crop", ['Wheat','Rice','Cotton','Mustard','Gram'], key='ideal_crop')
        soil_type = st.selectbox("Soil Type", ['Loamy','Sandy','Clay'], key='ideal_soil')
    with col2:
        start_N = st.number_input("Starting N (kg/ha)", 50.0, 600.0, 350.0, key='ideal_N')
        start_P = st.number_input("Starting P (kg/ha)",  5.0,  60.0,  22.0, key='ideal_P')
    with col3:
        start_K        = st.number_input("Starting K (kg/ha)", 80.0, 400.0, 250.0, key='ideal_K')
        start_recovery = st.slider("Starting Recovery Score", 25, 100, 35, key='ideal_rec')

    if st.button("▶ Run 42-Day Ideal Simulation", use_container_width=True):
        model    = st.session_state['model']
        scaler   = st.session_state['scaler']
        encoders = st.session_state['encoders']
        df_full  = st.session_state['df_full']

        with st.spinner("Simulating 42 days..."):
            report = tool1_ideal_42day(
                model, scaler, df_full, encoders, crop_name, soil_type,
                start_N, start_P, start_K, start_recovery=start_recovery)

        st.session_state['report_tool1'] = report

        last_row = report.iloc[-1]
        st.markdown("#### Final State (Day 42)")
        m1, m2, m3, m4, m5 = st.columns(5)
        with m1: render_metric_card("Final Nitrogen",   f"{last_row['Nitrogen_kg_ha']}", "kg/ha")
        with m2: render_metric_card("Final Phosphorus", f"{last_row['Phosphorus_kg_ha']}", "kg/ha")
        with m3: render_metric_card("Final Potassium",  f"{last_row['Potassium_kg_ha']}", "kg/ha")
        with m4: render_metric_card("Recovery Score",   f"{last_row['Soil_Recovery_Score']}", "/100")
        with m5: render_metric_card("Organic Reached",  f"{last_row['Organic_Input_Pct']}%", "of input")

        st.plotly_chart(graph1_chemical_vs_organic(report, crop_name), use_container_width=True)
        st.plotly_chart(graph_soil_recovery(report, f'{crop_name} — Ideal'), use_container_width=True)

        st.markdown("#### Weekly Summaries")
        for week in range(1, 8):
            week_data = report[report['Week'] == week]
            if len(week_data):
                render_week_summary(week, week_data.iloc[-1])

        st.markdown("#### Full 42-Day Daily Table")
        st.dataframe(report, use_container_width=True)

        csv = df_to_csv_bytes(report)
        st.download_button("📥 Download Ideal 42-Day Report", csv,
                           f"ideal_42day_{crop_name}.csv", "text/csv")


# ==============================================================================
# PAGE: 42-DAY REAL-WORLD SIMULATION
# ==============================================================================

def page_realworld_simulation():
    st.markdown('<div class="section-header">🌦️ 42-Day Real-World Simulation</div>',
                unsafe_allow_html=True)

    if 'model' not in st.session_state:
        st.warning("Please train the model first.")
        return

    st.markdown("""
    <div class="info-box">
        Enter weather data for each 7-day block manually.
        The AI predicts NPK and soil recovery for every individual day.<br><br>
        <b>IoT-Ready:</b> This manual input layer will be replaced by automatic sensor
        feeds when IoT infrastructure is deployed.
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        crop_name = st.selectbox("Crop", ['Wheat','Rice','Cotton','Mustard','Gram'], key='rw_crop')
        soil_type = st.selectbox("Soil Type", ['Loamy','Sandy','Clay'], key='rw_soil')
    with col2:
        start_N = st.number_input("Starting N (kg/ha)", 50.0, 600.0, 350.0, key='rw_N')
        start_P = st.number_input("Starting P (kg/ha)",  5.0,  60.0,  22.0, key='rw_P')
    with col3:
        start_K        = st.number_input("Starting K (kg/ha)", 80.0, 400.0, 250.0, key='rw_K')
        start_recovery = st.slider("Starting Recovery Score", 25, 100, 35, key='rw_rec')

    st.markdown("#### Enter Weekly Weather Data")
    st.caption("Manual input — IoT sensor feed will replace this in production")

    weekly_weather = []
    risk_colors = {'Low':'#52b788','Medium':'#d4a017','High':'#e07b00','Extreme':'#c1121f'}

    for week in range(1, 8):
        day_start = (week - 1) * 6 + 1
        day_end   = min(week * 6, 42)
        with st.expander(f"Week {week}  (Days {day_start}–{day_end})", expanded=(week == 1)):
            wc1, wc2, wc3 = st.columns(3)
            with wc1:
                temp = st.slider("Temperature °C", 10, 50, 28 + (week-1)*2, key=f'temp_w{week}')
            with wc2:
                rain = st.slider("Rainfall mm", 0, 250, max(0, 120 - (week-1)*15), key=f'rain_w{week}')
            with wc3:
                humidity = st.slider("Humidity %", 20, 95, 65, key=f'hum_w{week}')

            risk, event = classify_weather(temp, rain, humidity)
            rc = risk_colors.get(risk, '#888')
            ev_txt = f" · {event}" if event != 'None' else ""
            st.markdown(
                f'<span style="color:{rc}; font-size:0.85rem; font-weight:600;">'
                f'⚡ Risk: {risk}{ev_txt}</span>',
                unsafe_allow_html=True)
            weekly_weather.append({'temp': temp, 'rain': rain, 'humidity': humidity})

    if st.button("▶ Run 42-Day Real-World Simulation", use_container_width=True):
        model    = st.session_state['model']
        scaler   = st.session_state['scaler']
        encoders = st.session_state['encoders']
        df_full  = st.session_state['df_full']

        with st.spinner("Simulating 42 real-world days..."):
            report_t2 = tool2_realworld_42day(
                model, scaler, encoders, crop_name, soil_type,
                start_N, start_P, start_K, weekly_weather,
                start_recovery=start_recovery)

        st.session_state['report_tool2'] = report_t2

        report_t1 = tool1_ideal_42day(
            model, scaler, df_full, encoders, crop_name, soil_type,
            start_N, start_P, start_K, start_recovery=start_recovery)
        st.session_state['report_tool1'] = report_t1

        last = report_t2.iloc[-1]
        st.markdown("#### Final State (Day 42)")
        m1, m2, m3, m4, m5 = st.columns(5)
        with m1: render_metric_card("Final N",        f"{last['Nitrogen_kg_ha']}", "kg/ha")
        with m2: render_metric_card("Final P",        f"{last['Phosphorus_kg_ha']}", "kg/ha")
        with m3: render_metric_card("Final K",        f"{last['Potassium_kg_ha']}", "kg/ha")
        with m4: render_metric_card("Recovery Score", f"{last['Soil_Recovery_Score']}", "/100")
        with m5: render_alert_badge(last['Alert_Status'])

        st.plotly_chart(
            graph2_initial_vs_weather(report_t1, report_t2, crop_name, start_N, start_P, start_K),
            use_container_width=True)
        st.plotly_chart(graph_soil_recovery(report_t2, f'{crop_name} — Real-World'),
                        use_container_width=True)
        st.plotly_chart(graph_weather_risk_impact(report_t2), use_container_width=True)

        st.markdown("#### Weekly Summaries")
        for week in range(1, 8):
            wd = report_t2[report_t2['Week'] == week]
            if len(wd):
                last_w = wd.iloc[-1]
                risk_w = last_w.get('Weather_Risk', 'N/A')
                ev_w   = last_w.get('Extreme_Event', 'None')
                rc = risk_colors.get(risk_w, '#888')
                st.markdown(f"""
                <div class="week-summary">
                    <strong>Week {week}</strong> &nbsp;|&nbsp;
                    <span style="color:{rc}">Risk: {risk_w}
                    {"· " + ev_w if ev_w != 'None' else ""}</span> &nbsp;|&nbsp;
                    N: <b>{last_w['Nitrogen_kg_ha']}</b> &nbsp;
                    P: <b>{last_w['Phosphorus_kg_ha']}</b> &nbsp;
                    K: <b>{last_w['Potassium_kg_ha']}</b> &nbsp;
                    Recovery: <b>{last_w['Soil_Recovery_Score']}</b> &nbsp;
                    Organic: <b>{last_w['Organic_Input_Pct']}%</b>
                </div>
                """, unsafe_allow_html=True)

        st.markdown("#### Full 42-Day Daily Table")
        st.dataframe(report_t2, use_container_width=True)

        csv = df_to_csv_bytes(report_t2)
        st.download_button("📥 Download Real-World 42-Day Report", csv,
                           f"realworld_42day_{crop_name}.csv", "text/csv")


# ==============================================================================
# PAGE: CROP GROWTH STAGE
# ==============================================================================

def page_crop_growth():
    st.markdown('<div class="section-header">🌾 Crop Growth Stage Prediction</div>',
                unsafe_allow_html=True)

    if 'df_full' not in st.session_state:
        st.warning("Please train the model first.")
        return

    df_full = st.session_state['df_full']

    c1, c2 = st.columns(2)
    with c1:
        crop_name    = st.selectbox("Crop Name", ['Wheat','Rice','Cotton','Mustard','Gram'])
        current_week = st.slider("Current Week (1–7)", 1, 7, 3)
        current_N    = st.number_input("Current N (kg/ha)",  50.0, 600.0, 280.0)
    with c2:
        current_P        = st.number_input("Current P (kg/ha)",   5.0,  60.0,  21.0)
        current_K        = st.number_input("Current K (kg/ha)",  80.0, 400.0, 240.0)
        current_recovery = st.slider("Current Recovery Score", 25, 100, 45)

    if st.button("🌾 Predict Crop Stage", use_container_width=True):
        result = tool3_crop_age_prediction(
            df_full, crop_name, current_N, current_P,
            current_K, current_recovery, current_week)

        render_alert_badge(result['alert'])
        st.markdown("<br>", unsafe_allow_html=True)

        stages    = GROWTH_STAGES.get(crop_name, GROWTH_STAGES['Wheat'])
        stage_idx = min(current_week - 1, len(stages) - 1)

        st.markdown("#### Growth Stage Progression")
        cols = st.columns(len(stages))
        for i, (col, stage) in enumerate(zip(cols, stages)):
            with col:
                if i < stage_idx:
                    bg = "rgba(82,183,136,0.3)"; icon = "✅"
                elif i == stage_idx:
                    bg = "rgba(82,183,136,0.7)"; icon = "📍"
                else:
                    bg = "rgba(255,255,255,0.05)"; icon = "⬜"
                st.markdown(f"""
                <div style="text-align:center; background:{bg}; border-radius:8px;
                            padding:0.5rem; font-size:0.78rem; color:#e8f5e9;">
                    {icon}<br><b>{stage}</b>
                </div>
                """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        r1, r2, r3, r4, r5 = st.columns(5)
        with r1: render_metric_card("Overall Health", f"{result['overall_health']}%")
        with r2: render_metric_card("N Health",       f"{result['n_health']}%",        f"Avg={result['avg_N']}")
        with r3: render_metric_card("P Health",       f"{result['p_health']}%",        f"Avg={result['avg_P']}")
        with r4: render_metric_card("K Health",       f"{result['k_health']}%",        f"Avg={result['avg_K']}")
        with r5: render_metric_card("Recovery Health",f"{result['recovery_health']}%", f"Avg={result['avg_rec']}")

        st.plotly_chart(
            graph_crop_stage_gauge(result['overall_health'], crop_name),
            use_container_width=True)

        fig_radar = go.Figure(go.Scatterpolar(
            r=[result['n_health'], result['p_health'],
               result['k_health'], result['recovery_health'], result['n_health']],
            theta=['Nitrogen', 'Phosphorus', 'Potassium', 'Recovery', 'Nitrogen'],
            fill='toself',
            fillcolor='rgba(82,183,136,0.2)',
            line=dict(color=COLORS['N'], width=2),
            name='Crop Health Profile',
        ))
        fig_radar.update_layout(
            polar=dict(
                bgcolor='rgba(0,0,0,0)',
                radialaxis=dict(range=[0, 110], gridcolor=COLORS['grid']),
                angularaxis=dict(gridcolor=COLORS['grid']),
            ),
            title='NPK + Recovery Health Radar',
            height=380, **PLOT_LAYOUT,
