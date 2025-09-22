import datetime
import streamlit as st
import pandas as pd
import random
import os
from dotenv import load_dotenv
from openai import AzureOpenAI

# -----------------------------
# Load environment variables
# -----------------------------
load_dotenv()

AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_API_VERSION = "2024-12-01-preview"
AZURE_OPENAI_DEPLOYMENT_NAME = "gpt-4o-raj"

# -----------------------------
# Azure OpenAI Client
# -----------------------------
client = AzureOpenAI(
    api_key=AZURE_OPENAI_API_KEY,
    api_version=AZURE_OPENAI_API_VERSION,
    azure_endpoint=AZURE_OPENAI_ENDPOINT
)

# -----------------------------
# Helper Functions
# -----------------------------
def call_gpt(prompt: str) -> str:
    """Call Azure OpenAI GPT for a given prompt."""
    try:
        res = client.chat.completions.create(
            model=AZURE_OPENAI_DEPLOYMENT_NAME,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4
        )
        return res.choices[0].message.content.strip()
    except Exception as e:
        return f"GenAI error: {e}"

def calculate_criticality(row):
    score = 0
    if row["Failure Rate"] > 0.2:
        score += 2
    elif row["Failure Rate"] > 0.1:
        score += 1

    if row["Stock"] < row["Forecast Qty"]:
        score += 2
    elif row["Stock"] < row["Forecast Qty"] * 1.5:
        score += 1

    if row["Lead Time (days)"] > 30:
        score += 2
    elif row["Lead Time (days)"] > 15:
        score += 1

    if score >= 5:
        return "Critical"
    elif score >= 3:
        return "High"
    elif score >= 1:
        return "Medium"
    else:
        return "Low"

def get_colored_circle(criticality):
    if criticality == "High":
        return "🔴 High"
    elif criticality == "Medium":
        return "🟡 Medium"
    elif criticality == "Low":
        return "🟢 Low"
    else:
        return "⚪ Unknown"

def generate_parts(company_type):
    part_names = {
        "Transmission Operator": [
            "Transformer Coil", "HV Cable Drum", "Insulator Bushing", "Surge Arrester", "Load Tap Changer",
            "Current Transformer", "Voltage Transformer", "Transmission Relay", "Circuit Breaker", "Bushings"
        ],
        "Distribution Operator": [
            "Feeder Line Kit", "Fuse Switch", "Distribution Box", "Service Drop Cable", "Cutout Fuse",
            "Pole-Mounted Transformer", "Pad-Mounted Switchgear", "Recloser", "Line Tap", "Neutral Grounding Resistor"
        ],
        "Generation Company": [
            "Turbine Blade", "Generator Brush", "Cooling Fan", "Lubrication Pump", "Control Rod Assembly",
            "Fuel Injector", "Excitation System", "Bearing Set", "Governor Valve", "Steam Seal Ring"
        ],
        "Integrated Utility": [
            "Transformer Coil", "Fuse Switch", "Turbine Blade", "Service Drop Cable", "Excitation System",
            "Pad-Mounted Switchgear", "Current Transformer", "Cooling Fan", "Load Tap Changer"
        ]
    }
    warehouse_locations = ["London", "Leeds", "Glasgow", "Manchester", "Bristol"]
    conditions = ["New", "Used", "Refurbished"]

    parts = part_names.get(company_type, [])
    df = pd.DataFrame([{
        "Part Name": parts[i % len(parts)],
        "Installed Base": random.randint(50, 300),
        "Stock": random.randint(1, 20),
        "Lead Time (days)": random.choice([7, 14, 21, 28]),
        "Failure Rate": round(random.uniform(0.01, 0.15), 2),
        "Warehouse": random.choice(warehouse_locations),
        "Condition": random.choice(conditions)
    } for i in range(12)])
    return df

# -----------------------------
# Streamlit App
# -----------------------------
st.set_page_config(page_title="Supply Chain Optimization Assistant", layout="wide")

main_tabs = st.tabs(["📘 Overview", "🏠 Main App"])

with main_tabs[0]:
    st.title("📘 What This App Does")
    st.markdown("""
    This **Supply Chain Optimization Assistant** helps manage **spare parts, vendors, and forecast-driven procurement** 
    for the **UK Energy & Utilities sector** using real-time data and GenAI insights.
    ---
    - 🏭 **Supports Transmission, Distribution, Generation, Integrated Utilities**
    - 🛒 **Retail Energy Suppliers handled separately**
    - 📦 **Spare parts forecasting with EOQ**
    - 🏭 **Vendor selection and reorder prioritization**
    - 🌍 **Emissions tracking**
    - 🤖 **Azure OpenAI-powered executive summaries**
    """)

with main_tabs[1]:
    st.title("🏭 Supply Chain Optimization Assistant")

company_type = st.selectbox("Select Company Type", [
    "Transmission Operator",
    "Distribution Operator",
    "Generation Company",
    "Retail Energy Supplier",
    "Integrated Utility"
])

# -----------------------------
# Non-Retail Tabs
# -----------------------------
if company_type != "Retail Energy Supplier":
    forecast_months = st.slider("📆 Forecast Horizon (months)", 1, 12, 3)

    tabs = st.tabs([
        "📦 Spare Parts", "📊 Forecast Qty", "📉 Emissions",
        "📊 GenAI Summary", "🏭 Vendors", "🔁 Reorder Parts"
    ])

    with tabs[0]:
        df_spares = generate_parts(company_type)
        df_spares["Forecast Qty"] = (df_spares["Installed Base"] * df_spares["Failure Rate"] * forecast_months).round().astype(int)
        df_spares["Criticality"] = df_spares.apply(lambda row: calculate_criticality(pd.Series({
            "Stock": row["Stock"],
            "Lead Time (days)": row["Lead Time (days)"],
            "Failure Rate": row["Failure Rate"],
            "Forecast Qty": row["Forecast Qty"]
        })), axis=1)
        df_spares["Criticality"] = df_spares["Criticality"].apply(get_colored_circle)
        st.subheader(f"📦 Spare Parts for {company_type}")
        st.dataframe(df_spares, use_container_width=True)
        st.session_state.df_spares = df_spares

    with tabs[1]:
        st.subheader("📊 Forecasted Demand")
        forecast_df = st.session_state.df_spares[["Part Name", "Installed Base", "Failure Rate", "Forecast Qty", "Stock"]]
        forecast_df["Expected Shortage"] = forecast_df["Forecast Qty"] - forecast_df["Stock"]
        st.dataframe(forecast_df, use_container_width=True)

    with tabs[2]:
        emission_val = round(random.uniform(1000, 9000), 2)
        st.subheader("📉 Estimated Emissions")
        st.metric("Emissions (kg CO₂)", emission_val)

    with tabs[3]:
        st.subheader("📊 GenAI Summary")
        summary_prompt = f"Generate an executive summary for {company_type} with spare parts: {df_spares.to_dict(orient='records')}."
        st.info(call_gpt(summary_prompt))

    with tabs[4]:
        st.subheader("🏭 Vendor Overview")
        parts = df_spares["Part Name"].unique()
        vendor_records = []
        for part in parts:
            for loc in random.sample(["London", "Leeds", "Glasgow", "Manchester", "Bristol"], 3):
                vendor_records.append({
                    "Part Name": part,
                    "Vendor": f"{part[:3].upper()}-{random.randint(10,99)}-{loc[:2].upper()}",
                    "Unit Cost (£)": round(random.uniform(100, 500), 2),
                    "Lead Time (days)": random.choice([7, 14, 21]),
                    "Reliability (%)": round(random.uniform(85, 99), 2)
                })
        vendor_df = pd.DataFrame(vendor_records)
        st.dataframe(vendor_df, use_container_width=True)

    with tabs[5]:
        st.subheader("🔁 Reorder Parts")
        df_spares["EOQ"] = ((2 * df_spares["Forecast Qty"] * 50) / 10) ** 0.5
        df_spares["EOQ"] = df_spares["EOQ"].round().astype(int)
        df_spares["Expected Shortage"] = df_spares["Forecast Qty"] - df_spares["Stock"]
        df_spares["Recommended Qty"] = df_spares.apply(lambda r: max(r["EOQ"], r["Expected Shortage"]), axis=1)
        st.dataframe(df_spares[["Part Name", "EOQ", "Recommended Qty", "Stock", "Forecast Qty"]], use_container_width=True)

# -----------------------------
# Retail Tabs (unchanged except GenAI via Azure)
# -----------------------------
else:
    st.subheader("💰 Retail Energy Supplier - Tariff & Demand")
    tariff_df = pd.DataFrame([
        {"Customer Type": "Residential", "Rate (£/MWh)": 165.5, "Volume (MWh)": 18000},
        {"Customer Type": "Small Business", "Rate (£/MWh)": 172.1, "Volume (MWh)": 4200},
        {"Customer Type": "Large Commercial", "Rate (£/MWh)": 158.2, "Volume (MWh)": 11500}
    ])
    st.dataframe(tariff_df, use_container_width=True)
    st.info(call_gpt(f"Analyze tariff strategy: {tariff_df.to_dict(orient='records')}"))
