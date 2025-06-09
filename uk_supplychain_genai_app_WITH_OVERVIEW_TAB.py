
def get_colored_circle(criticality):
    if criticality == "High":
        return "🔴 High"
    elif criticality == "Medium":
        return "🟡 Medium"
    elif criticality == "Low":
        return "🟢 Low"
        return "⚪ Unknown"



def generate_parts(company_type):
    part_names = {
        "Transmission Operator": [
            "Transformer Coil", "HV Cable Drum", "Insulator Bushing", "Surge Arrester", "Load Tap Changer",
            "Current Transformer", "Voltage Transformer", "Transmission Relay", "Circuit Breaker", "Bushings"
        ],
        "Distribution Operator": [
            "Feeder Line Kit", "Fuse Switch", "Distribution Box", "Service Drop Cable", "Cutout Fuse",
            "Pole Top Transformer", "Line Tap", "Underground Vault", "Switchgear", "Smart Meter"
        ],
        "Generation Company": [
            "Gas Turbine Blade", "Steam Turbine Rotor", "Generator Exciter", "Lube Oil Filter", "Heat Exchanger",
            "Control Valve", "Condensate Pump", "Air Inlet Filter", "Fuel Injector", "Coolant Pump"
        ],
        "Retail Energy Supplier": [
            "Smart Meter", "Home Energy Monitor", "WiFi Gateway", "Prepaid Meter", "Billing Module"
        ],
        "Integrated Utility": [
            "Universal Switchgear", "Multi-purpose Relay", "Integrated Controller", "Flex Power Cable", "Hybrid Transformer"
        ]
    }

    selected_parts = random.sample(part_names.get(company_type, []), k=min(5, len(part_names.get(company_type, []))))
    return selected_parts


import datetime

import streamlit as st
import pandas as pd
import random
import os
from dotenv import load_dotenv
import openai

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
        return "Low"

def call_gpt(prompt):
    try:
        res = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4
        )
        return res.choices[0].message.content.strip()
    except Exception as e:
        return f"GenAI error: {e}"

load_dotenv()
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

st.set_page_config(page_title="Supply Chain Optimization Assistant", layout="wide")



main_tabs = st.tabs(["📘 Overview", "🏠 Main App"])

with main_tabs[0]:
        st.title("📘 What This App Does")
        st.markdown("""
        This **Supply Chain Optimization Assistant** is designed for companies in the **UK Energy & Utilities sector** to help manage **spare parts, vendors, and forecast-driven procurement** using real-time data and intelligent recommendations.

        ---

        ### 🏢 Who Uses This?
        - **Transmission Operators**
        - **Distribution Operators**
        - **Generation Companies**
        - **Integrated Utilities**
        - (Handled together as a group with common supply chain challenges)

        - **Retail Energy Suppliers**
          (Handled separately due to different tariff, customer, and compliance needs)

        ---

        ### 📊 How Forecasting Works (Spare Parts)
        For each spare part:
        - **Forecast Qty = Installed Base × Failure Rate × Forecast Horizon (months)**
        - The app uses sliders and real-time failure estimates to calculate demand.

        ---

        ### 🔁 EOQ vs. Recommended Quantity
        - **EOQ (Economic Order Quantity)** optimizes based on cost factors.
        - **Recommended Qty** looks at the **shortage**, **criticality**, and ensures you order enough even if EOQ is small.

        ---

        ### 🏭 Vendor Selection Logic
        - Each part has 3–5 vendors (auto-generated for demo; API-ready)
        - Vendors are evaluated using:
          - Unit Cost
          - Lead Time
          - Reliability
          - Risk Score

        ---

        ### 🔁 Reorder Prioritization
        - Parts are ranked using an **Urgency Score**:
          - Based on expected shortage, lead time, and failure rate
        - User selects preferred vendor per part
        - App calculates cost, lead time, delivery date

        ---

        ### 🌍 Emissions Estimation
        - Emissions are estimated for each company type (CO₂ kg or tons)
        - Retail also calculates per-customer metrics

        ---

        ### 🤖 GenAI-Powered Executive Summaries
        - AI-generated insights are used to:
          - Summarize risks and trends
          - Recommend procurement actions
          - Assess regulatory posture (Retail)

        ---

        ### 🔄 What Inputs Are Real-Time or Simulated?
        - **Failure rate** (simulated per part)
        - **Installed base** (simulated)
        - **Lead time** (per vendor)
        - **Weather/load impact** (forecasted)
        - **Stock levels** (live input via simulation/API)
        - **Vendor metrics** (mocked now, API-ready)

        ---

        ### ✅ How to Make It Production-Ready
        - Use real **inventory APIs** to fetch stock, install base, parts list
        - Connect to **vendor master systems** (SAP, Oracle, etc.)
        - Integrate **weather and load forecasts** from BMRS/National Grid
        - Use **Azure/AWS/GCP** for secure deployment
        - Add **role-based access** for Supervisor, Analyst, Buyer
        - Store all PO decisions and GenAI outputs for audit

        ---

        ### 👨‍💼 Final Output
        - Executive summary + reorder suggestions
        - Editable vendor decisions
        - GenAI-powered insights
        - Optional: PO export, compliance logs

        ---

        > ⚡ Built to help energy supply chains respond faster, smarter, and cleaner.
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

def get_colored_circle(criticality):
    if criticality == "High":
        return "🔴 High"
    elif criticality == "Medium":
        return "🟡 Medium"
    elif criticality == "Low":
        return "🟢 Low"
    else:
        return "Low"

if company_type != "Retail Energy Supplier":
    forecast_months = st.slider("📆 Select Forecast Horizon (months)", min_value=1, max_value=12, value=3, key="forecast_slider_non_retail")

    tabs = st.tabs(["📦 Spare Parts", "📊 Forecast Qty", "📉 Emissions", "📊 GenAI Summary", "🏭 Vendors", "🔁 Reorder Parts"])

    with tabs[0]:
        st.subheader(f"📦 Spare Parts Inventory for {company_type}")
        df_spares = generate_parts(company_type)
        df_spares["Forecast Qty"] = (df_spares["Installed Base"] * df_spares["Failure Rate"] * forecast_months).round().astype(int)
        df_spares["Criticality"] = df_spares.apply(lambda row: calculate_criticality(pd.Series({
            "Stock": row["Stock"],
            "Lead Time (days)": row["Lead Time (days)"],
            "Failure Rate": row["Failure Rate"],
            "Forecast Qty": row["Forecast Qty"]
        })), axis=1)
        df_spares["Criticality"] = df_spares["Criticality"].apply(get_colored_circle)
        st.dataframe(df_spares.drop(columns=["Forecast Qty"]), use_container_width=True)
        st.session_state.df_spares = df_spares

    with tabs[1]:
        st.subheader("📊 Forecasted Spare Part Demand")
        forecast_df = st.session_state.df_spares[["Part Name", "Installed Base", "Failure Rate", "Forecast Qty", "Stock"]]
        forecast_df["Expected Shortage"] = forecast_df["Forecast Qty"] - forecast_df["Stock"]
        st.dataframe(forecast_df, use_container_width=True)

        st.subheader("📈 Load Forecast (24h)")
        load_forecast = [round(50 + random.uniform(-10, 10), 1) for _ in range(24)]
        st.line_chart(load_forecast)

    with tabs[2]:
        emission_val = round(random.uniform(1000, 9000), 2)
        st.subheader("📉 Estimated Emissions")
        st.metric("Emissions (kg CO₂)", emission_val)

    with tabs[3]:
        summary_prompt = f"Generate an executive summary for {company_type} with spares {df_spares.to_dict(orient='records')}, emissions {emission_val}kg CO2. Provide 3–5 key insights."
        st.subheader("📊 GenAI Summary")
        st.info(call_gpt(summary_prompt))

    with tabs[4]:
        st.subheader("🏭 Approved Vendors by Part and Region")
        parts = df_spares["Part Name"].unique()
        locations = ["London", "Leeds", "Glasgow", "Manchester", "Bristol"]
        vendor_records = []
        for part in parts:
            for loc in random.sample(locations, random.randint(3, 5)):
                vendor_name = f"{part[:3].upper()}-{random.choice(['Techline', 'PowerGrid', 'Voltix', 'GridNova', 'Electra'])}-{loc[:2].upper()}"
                cost = round(random.uniform(100, 500), 2)
                reliability = round(random.uniform(85, 99), 2)
                lead_time = random.choice([7, 10, 14, 21])
                vendor_records.append({
                    "Part Name": part,
                    "Company Type": company_type,
                    "Location": loc,
                    "Vendor": vendor_name,
                    "Unit Cost (£)": cost,
                    "Lead Time (days)": lead_time,
                    "Reliability (%)": reliability,
                    "⭐ Rating": round(random.uniform(3.0, 5.0), 1),
                    "⚠️ Risk Score": round((100 - reliability) * 0.6 + lead_time * 1.5 + random.uniform(0, 10), 1)
                })
        vendor_df = pd.DataFrame(vendor_records)
        st.dataframe(vendor_df, use_container_width=True)




    with tabs[5]:
        st.subheader("🔁 Reorder Parts Based on Criticality & Forecast")
        ordering_cost = 50
        holding_cost_per_unit = 10
        df_spares["EOQ"] = ((2 * df_spares["Forecast Qty"] * ordering_cost) / holding_cost_per_unit) ** 0.5
        df_spares["EOQ"] = df_spares["EOQ"].round().astype(int)
        df_spares["Expected Shortage"] = df_spares["Forecast Qty"] - df_spares["Stock"]
        df_spares["Urgency Score"] = (
            df_spares["Expected Shortage"] * 0.4 +
            df_spares["Lead Time (days)"] * 0.3 +
            df_spares["Failure Rate"] * 100 * 0.3
        ).round(2)
        df_spares["Recommended Qty"] = df_spares.apply(
            lambda row: max(row["Expected Shortage"], row["EOQ"]), axis=1
        ).astype(int)

        vendor_records = []
        for part in df_spares["Part Name"]:
            for _ in range(3):
                vendor_records.append({
                    "Part Name": part,
                    "Vendor": f"{part[:3].upper()}-V{random.randint(1,99)}",
                    "Unit Cost (£)": round(random.uniform(100, 300), 2),
                    "Lead Time (days)": random.choice([7, 10, 14])
                })
        vendor_df = pd.DataFrame(vendor_records)

        output_rows = []
        for idx, row in df_spares.iterrows():
            st.markdown("---")
            st.markdown(f"### 🔧 {row['Part Name']}")
            cols = st.columns([2, 2, 2, 2, 2, 2])
            vendors = vendor_df[vendor_df["Part Name"] == row["Part Name"]]
            vendor_names = vendors["Vendor"].tolist()
            selected_vendor = cols[0].selectbox("Vendor", vendor_names, key=f"vendor_{idx}_{row['Part Name'].replace(' ', '_')}")
            chosen_vendor = vendors[vendors["Vendor"] == selected_vendor].iloc[0]
            total_cost = round(row["Recommended Qty"] * chosen_vendor["Unit Cost (£)"], 2)
            expected_delivery = (datetime.date.today() + datetime.timedelta(days=int(chosen_vendor["Lead Time (days)"]))).isoformat()

            cols[1].metric("EOQ", row["EOQ"])
            cols[2].metric("Recommended Qty", row["Recommended Qty"])
            cols[3].metric("Unit Cost (£)", chosen_vendor["Unit Cost (£)"])
            cols[4].metric("Lead Time (days)", chosen_vendor["Lead Time (days)"])
            cols[5].metric("Total Cost (£)", total_cost)

            output_rows.append({
                "Part Name": row["Part Name"],
                "Selected Vendor": selected_vendor,
                "EOQ": row["EOQ"],
                "Recommended Qty": row["Recommended Qty"],
                "Unit Cost (£)": chosen_vendor["Unit Cost (£)"],
                "Lead Time (days)": chosen_vendor["Lead Time (days)"],
                "Total Cost (£)": total_cost,
                "Expected Delivery": expected_delivery
            })

        reorder_df = pd.DataFrame(output_rows)
        st.markdown("### 📋 Final Reorder Table")
        st.dataframe(reorder_df, use_container_width=True)

if company_type == "Retail Energy Supplier":
    forecast_months = st.slider("📆 Select Forecast Horizon (months)", min_value=1, max_value=12, value=6, key="forecast_slider_retail")
    retail_tabs = st.tabs([
        "💰 Tariff Strategy",
        "👥 Customer Insights",
        "⚖️ Regulatory Risk",
        "🌍 Emissions",
        "📊 Executive Summary",
        "📈 Forecasted Energy Demand"
    ])

    with retail_tabs[0]:
        st.subheader("💰 Tariff Strategy Overview")
        tariff_portfolio = pd.DataFrame([
            {"Customer Type": "Residential", "Contract": "Dual", "Tariff Type": "Fixed", "Rate (£/MWh)": 165.5, "Volume (MWh)": 18000, "Margin (£)": 6.3, "Churn Risk": "9.4%"},
            {"Customer Type": "Small Business", "Contract": "Electric", "Tariff Type": "Market", "Rate (£/MWh)": 172.1, "Volume (MWh)": 4200, "Margin (£)": 4.9, "Churn Risk": "14.1%"},
            {"Customer Type": "Large Commercial", "Contract": "Gas", "Tariff Type": "Fixed", "Rate (£/MWh)": 158.2, "Volume (MWh)": 11500, "Margin (£)": 8.1, "Churn Risk": "11.2%"},
            {"Customer Type": "Municipal", "Contract": "Dual", "Tariff Type": "Market", "Rate (£/MWh)": 169.3, "Volume (MWh)": 8000, "Margin (£)": 5.7, "Churn Risk": "12.9%"},
            {"Customer Type": "Industrial", "Contract": "Gas", "Tariff Type": "Fixed", "Rate (£/MWh)": 160.9, "Volume (MWh)": 13400, "Margin (£)": 7.2, "Churn Risk": "8.3%"}
        ])
        st.dataframe(tariff_portfolio, use_container_width=True)
        prompt = f"As a UK retail energy supplier with portfolio: {tariff_portfolio.to_dict(orient='records')}, analyze pricing, churn, margin and suggest a hedging and pricing strategy."
        st.markdown("**🧠 GenAI Advice:**")
        st.info(call_gpt(prompt))

    with retail_tabs[1]:
        customers = pd.DataFrame([
            {"Segment": "Large Commercial", "Count": 240, "Avg Consumption (MWh)": 580},
            {"Segment": "Small Business", "Count": 1320, "Avg Consumption (MWh)": 110},
            {"Segment": "Residential", "Count": 16400, "Avg Consumption (MWh)": 6.2}
        ])
        st.subheader("👥 Customer Segments & Risk")
        st.dataframe(customers, use_container_width=True)
        prompt = f"As a UK retail supplier with customer segments {customers.to_dict(orient='records')}, recommend churn mitigation strategies and segment focus."
        st.markdown("**🧠 GenAI Insight:**")
        st.info(call_gpt(prompt))

    with retail_tabs[2]:
        reg_flags = {
            "Ofgem Alerts": random.choice(["None", "Pending Inquiry", "Compliance Review"]),
            "Price Cap Proximity": round(random.uniform(-5, 2), 2),
            "Complaint Rate (%)": round(random.uniform(0.5, 4.0), 2)
        }
        st.subheader("⚖️ Regulatory & Compliance View")
        st.dataframe(pd.DataFrame([reg_flags]), use_container_width=True)
        prompt = f"Ofgem alert status is '{reg_flags['Ofgem Alerts']}', margin to price cap is £{reg_flags['Price Cap Proximity']}, and complaint rate is {reg_flags['Complaint Rate (%)']}%. Recommend compliance and risk mitigation actions."
        st.markdown("**🧠 GenAI Compliance Review:**")
        st.info(call_gpt(prompt))

    with retail_tabs[3]:
        emissions = {
            "Scope 3 CO₂ Estimate (tons)": round(random.uniform(10000, 30000), 2),
            "Per Customer (kg)": round(random.uniform(500, 1500), 2)
        }
        st.subheader("🌍 Emissions Estimate")
        st.dataframe(pd.DataFrame([emissions]), use_container_width=True)
        prompt = f"As a retail energy supplier, with Scope 3 emissions at {emissions['Scope 3 CO₂ Estimate (tons)']} tons and {emissions['Per Customer (kg)']} kg per customer, suggest how to position eco-friendly products or offsets."
        st.markdown("**🧠 GenAI Sustainability Tips:**")
        st.info(call_gpt(prompt))

    with retail_tabs[4]:
        summary_prompt = f"Generate an executive summary for a UK Retail Energy Supplier with: Customer data: {customers.to_dict(orient='records')}, Regulatory flags: {reg_flags}, Emissions: {emissions}. Give 5 actionable insights."
        st.subheader("📊 GenAI Executive Summary")
        st.info(call_gpt(summary_prompt))

    with retail_tabs[5]:
        st.subheader("📈 Forecasted Energy Demand by Segment")
        seasonality = [1.0, 1.05, 1.08, 1.1, 1.15, 1.2, 1.1, 1.08, 1.05, 1.0, 0.95, 0.9]
        segments = ["Residential", "Small Business", "Large Commercial"]
        base_data = {
            "Residential": {"count": 16400, "avg": 6.2},
            "Small Business": {"count": 1320, "avg": 110},
            "Large Commercial": {"count": 240, "avg": 580}
        }
        data = []
        for m in range(forecast_months):
            row = {"Month": f"Month {m+1}"}
            total = 0
            for seg in segments:
                base = base_data[seg]["count"] * base_data[seg]["avg"]
                seasonal_demand = round(base * seasonality[m % 12], 1)
                row[seg] = seasonal_demand
                total += seasonal_demand
            row["Total"] = round(total, 1)
            data.append(row)
        df_forecast = pd.DataFrame(data)
        st.dataframe(df_forecast, use_container_width=True)
        st.line_chart(df_forecast.set_index("Month")["Total"])