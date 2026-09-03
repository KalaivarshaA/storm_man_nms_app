"""
Storm Impact & Restoration Dashboard - Standalone Streamlit App
Filename: storm_dashboard_streamlit.py

Description:
This Streamlit app generates  storm-impact data (configurable) and visualizes
multiple views required for storm restoration tracking and impact management:
- Customers Impacted vs Hours
- Devices impacted vs Customers per device
- Hours to Restore (timeline)
- Crews Required vs Days vs Existing Crews
- Past vs Current comparison
- Pie charts and tables
- Simple Outage Detection (based on pole damage + conductor state)
- NMS Event Correlation (simulated)

How to run:
1. Install dependencies: pip install streamlit pandas numpy plotly
2. Run: streamlit run storm_dashboard_streamlit.py

Note: This app is standalone and uses randomly generated  data. You can export CSVs from the UI.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

st.set_page_config(page_title="Storm Impact Dashboard", layout="wide")

# ---------------------- Helpers ----------------------

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import pydeck as pdk
import joblib
import os
MODEL_PATH = "storm_outage_model.pkl"
st.set_page_config(page_title="Storm Impact & Restoration Dashboard", layout="wide")

# ------------------ Data Generator ------------------
def generate_mock_dat(num_records=50, seed=42):
    np.random.seed(seed)
    upstreams = ["Substation A", "Substation B", "Substation C"]
    downstreams = ["Zone 1", "Zone 2", "Zone 3"]
    devices = ["Transformer X", "Transformer Y", "Transformer Z"]
    poles = [f"Pole {i}" for i in range(1, num_records+1)]

    data = {
        "impacted_upstreams": np.random.choice(upstreams, num_records),
        "impacted_downstreams": np.random.choice(downstreams, num_records),
        "devices": np.random.choice(devices, num_records),
        "poles": np.random.choice(poles, num_records),
        "customers": np.random.randint(100, 500, num_records),
        "restoration_time": np.random.randint(5, 24, num_records),
        "crews_required": np.random.randint(3, 20, num_records),
        "severity": np.random.choice(["Moderate", "Severe", "Extreme"], num_records),
        "cost_saving": np.random.randint(2000, 10000, num_records),
        "wind_speed": np.random.randint(40, 150, num_records),
        # Restrict coordinates to land area (South India example)
        "latitude": np.random.uniform(12.5, 19.0, num_records),
        "longitude": np.random.uniform(76.0, 81.0, num_records)
    }

    return pd.DataFrame(data)

# ------------------ Load Mock Data ------------------
data = generate_mock_dat()

st.title("🌩 Storm Impact & Restoration Dashboard")
st.markdown("This dashboard visualizes storm restoration metrics, outages, and customer impact.")

# ------------------ Map Viewer ------------------
st.subheader("🗺 Storm Area & Poles Map")
st.markdown("Poles are highlighted based on storm severity and wind speed.")

map_data = data.copy()
map_data["color"] = map_data["severity"].map({
    "Moderate": [0, 200, 0],
    "Severe": [200, 100, 0],
    "Extreme": [200, 0, 0]
})

# Fit map zoom to data range
view_state = pdk.ViewState(
    latitude=map_data["latitude"].mean(),
    longitude=map_data["longitude"].mean(),
    zoom=6 if len(map_data) > 1 else 10,
    pitch=0
)

scatter_layer = pdk.Layer(
    "ScatterplotLayer",
    data=map_data,
    get_position="[longitude, latitude]",
    get_color="color",
    get_radius="wind_speed * 100",  # scale radius so it's visible
    pickable=True
)

text_layer = pdk.Layer(
    "TextLayer",
    data=map_data,
    get_position="[longitude, latitude]",
    get_text="poles",
    get_size=14,
    get_color=[255, 255, 255],
    get_alignment_baseline="bottom"
)

st.pydeck_chart(pdk.Deck(
    layers=[scatter_layer, text_layer],
    initial_view_state=view_state,
    tooltip={"text": "{poles}: {severity}, Wind: {wind_speed} km/h"}
))

@st.cache_data
def generate_mock_data(num_records=200, start_date=None, seed=42,
                       customer_min=50, customer_max=600,
                       crews_min=1, crews_max=25):
    np.random.seed(seed)
    if start_date is None:
        start_date = datetime.now() - timedelta(days=7)

    records = []
    device_types = ["Transformer", "Pole", "Line", "Substation"]
    severities = ["Low", "Moderate", "High", "Severe"]

    for i in range(num_records):
        event_time = start_date + timedelta(hours=int(np.random.rand() * 24 * 7))
        device_type = np.random.choice(device_types, p=[0.25, 0.4, 0.25, 0.1])
        pole_id = f"P-{np.random.randint(1,500)}" if device_type == "Pole" else None
        device_id = f"D-{np.random.randint(1000,9999)}"
        customers = int(np.random.randint(customer_min, customer_max))
        restoration_hours = int(np.clip(np.random.normal(loc=12, scale=8), 1, 72))
        crews_required = int(np.clip(np.random.randint(crews_min, crews_max), 1, crews_max))
        severity = np.random.choice(severities, p=[0.25, 0.35, 0.25, 0.15])
        age_years = int(np.random.randint(1, 40))
        cost_saving = int(customers * np.random.uniform(10, 30))

        # Pole damage likelihood (simple heuristic)
        pole_condition = "OK"
        if device_type == "Pole":
            # damage chance increases with severity and age
            base = {"Low": 0.02, "Moderate": 0.08, "High": 0.25, "Severe": 0.5}[severity]
            age_factor = min(age_years / 50, 1.0)
            damage_prob = base + 0.3 * age_factor
            damaged = np.random.rand() < damage_prob
            pole_condition = "Broken" if damaged else "Standing"

        # conductor impact
        conductor_affected = False
        if device_type in ["Line", "Pole"]:
            conductor_affected = np.random.rand() < (0.1 if severity=='Low' else 0.25 if severity=='Moderate' else 0.5 if severity=='High' else 0.7)

        records.append({
            "event_time": event_time,
            "device_type": device_type,
            "device_id": device_id,
            "pole_id": pole_id,
            "customers_impacted": customers,
            "restoration_hours": restoration_hours,
            "crews_required": crews_required,
            "severity": severity,
            "age_years": age_years,
            "pole_condition": pole_condition,
            "conductor_affected": conductor_affected,
            "cost_saving": cost_saving,
            "is_outage": True if (device_type in ["Pole","Line"] and (pole_condition=="Broken" or conductor_affected)) else False,
            "record_id": f"R-{i+1}"
        })

    df = pd.DataFrame(records)
    df.sort_values("event_time", inplace=True)
    df.reset_index(drop=True, inplace=True)
    return df

@st.cache_data
def simulate_nms_events(df, noise_factor=0.12, seed=123):
    # Create simulated NMS events which may or may not match actual outages
    np.random.seed(seed)
    events = []
    for _, row in df.iterrows():
        # chance NMS notices event depends on severity and outage status
        chance = 0.05
        if row['is_outage']:
            chance = 0.6 if row['severity'] in ['High','Severe'] else 0.35
        detected = np.random.rand() < (chance * (1 - noise_factor))
        event_type = 'OUTAGE' if detected else ('ALARM' if np.random.rand() < 0.05 else 'INFO')
        events.append({
            'record_id': row['record_id'],
            'nms_event_time': row['event_time'] + timedelta(minutes=int(np.random.randn()*30)),
            'nms_event_type': event_type,
            'nms_matched': detected
        })
    return pd.DataFrame(events)

# ---------------------- UI ----------------------
st.title("⚡ Storm Impact & Restoration Dashboard")
st.write("Standalone Streamlit app to simulate, detect and track storm-related outages, restoration and crew deployment.")

with st.sidebar:
    st.header("Data & Simulation")
    num_records = st.slider("Number of records", min_value=50, max_value=2000, value=400, step=50)
    seed = st.number_input("Random seed", value=42, step=1)
    customer_min = st.number_input("Min customers per device", value=20)
    customer_max = st.number_input("Max customers per device", value=600)
    crews_min = st.number_input("Min crews required", value=1)
    crews_max = st.number_input("Max crews required", value=20)
    st.markdown("---")
    st.header("Quick Actions")
    if st.button("Generate Data"):
        df = generate_mock_data(num_records=num_records, seed=seed,
                                customer_min=customer_min, customer_max=customer_max,
                                crews_min=crews_min, crews_max=crews_max)
        st.success("Data generated — scroll main page to view charts.")
    st.write("You can change parameters and click Generate Data to refresh.")

# Generate or cache
if 'df' not in st.session_state:
    st.session_state.df = generate_mock_data(num_records=num_records, seed=seed,
                                             customer_min=customer_min, customer_max=customer_max,
                                             crews_min=crews_min, crews_max=crews_max)
else:
    # regenerate if slider changed
    if (len(st.session_state.df) != num_records) or (st.session_state.df['customers_impacted'].min() < customer_min) or (st.session_state.df['customers_impacted'].max() > customer_max):
        st.session_state.df = generate_mock_data(num_records=num_records, seed=seed,
                                                 customer_min=customer_min, customer_max=customer_max,
                                                 crews_min=crews_min, crews_max=crews_max)

df = st.session_state.df

# Simulate NMS events and correlate
nms_df = simulate_nms_events(df)
correlation = pd.merge(df, nms_df, on='record_id', how='left')
correlation['nms_matched'] = correlation['nms_matched'].fillna(False)

# Summary cards
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Records", len(df))
col2.metric("Estimated Outages", int(df['is_outage'].sum()))
col3.metric("Total Customers Impacted", int(df['customers_impacted'].sum()))
col4.metric("Avg Restoration (hrs)", round(df['restoration_hours'].mean(),1))

st.markdown("---")

# Layout: Charts
st.subheader("1. Customers Impacted vs Number of Hours")
fig1 = px.line(df.groupby('restoration_hours').customers_impacted.sum().reset_index(),
               x='restoration_hours', y='customers_impacted', markers=True,
               labels={'restoration_hours':'Restoration Hours', 'customers_impacted':'Customers Impacted'})
st.plotly_chart(fig1, use_container_width=True)

st.subheader("2. Devices Impacted vs Customers on Each Device")
device_customers = df.groupby(['device_type','device_id']).customers_impacted.sum().reset_index()
# show top N devices by customers
top_n = st.slider("Top devices to show", min_value=5, max_value=50, value=15)
top_devices = device_customers.sort_values('customers_impacted', ascending=False).head(top_n)
fig2 = px.bar(top_devices, x='device_id', y='customers_impacted', color='device_type',
              labels={'device_id':'Device ID','customers_impacted':'Customers'})
st.plotly_chart(fig2, use_container_width=True)

st.subheader("3. Number of Hours to Restore (Timeline)")
by_time = df.groupby(pd.Grouper(key='event_time', freq='12H')).restoration_hours.mean().reset_index()
fig3 = px.line(by_time, x='event_time', y='restoration_hours', labels={'event_time':'Time','restoration_hours':'Avg Restoration Hours'})
st.plotly_chart(fig3, use_container_width=True)

# Crews chart
st.subheader("4. Crews Required vs Days vs Existing Crews")
# simulate existing crews
existing_crews = st.number_input("Existing crews available", value=8, min_value=1)
days = int(df['event_time'].dt.date.nunique())
crews_by_day = df.groupby(df['event_time'].dt.date).crews_required.sum().reset_index()
crews_by_day.columns = ['date','crews_required']
crews_by_day['existing_crews'] = existing_crews
fig4 = go.Figure()
fig4.add_trace(go.Bar(x=crews_by_day['date'], y=crews_by_day['crews_required'], name='Crews Required'))
fig4.add_trace(go.Scatter(x=crews_by_day['date'], y=crews_by_day['existing_crews'], mode='lines+markers', name='Existing Crews'))
fig4.update_layout(xaxis_title='Date', yaxis_title='Crews')
st.plotly_chart(fig4, use_container_width=True)

st.markdown("---")

# Past vs Current comparison
st.subheader("5. Past Data vs Current Data (Pole counts)")
# create a simple past dataset (simulate older storms)
past_df = generate_mock_data(num_records=int(num_records*0.6), seed=seed+7, start_date=datetime.now()-timedelta(days=30), customer_min=customer_min, customer_max=customer_max)
past_poles = past_df[past_df['device_type']=='Pole'].groupby(past_df['event_time'].dt.date).size().reset_index(name='past_pole_events')
curr_poles = df[df['device_type']=='Pole'].groupby(df['event_time'].dt.date).size().reset_index(name='curr_pole_events')
merge_poles = pd.merge(past_poles, curr_poles, left_on='event_time', right_on='event_time', how='outer').fillna(0)
# align column
merge_poles.columns = ['date','past_pole_events','curr_pole_events']
fig5 = go.Figure()
fig5.add_trace(go.Bar(x=merge_poles['date'], y=merge_poles['past_pole_events'], name='Past Pole Events'))
fig5.add_trace(go.Bar(x=merge_poles['date'], y=merge_poles['curr_pole_events'], name='Current Pole Events'))
fig5.update_layout(barmode='group', xaxis_title='Date', yaxis_title='Pole Events')
st.plotly_chart(fig5, use_container_width=True)

st.markdown("---")

# Pie charts and tables
st.subheader("6. Distribution & Tables")
colA, colB = st.columns(2)
# with colA:
#     severity_counts = df['severity'].value_counts().reset_index()
#     severity_counts.columns = ['severity','count']
#     fig_pie = px.pie(severity_counts, names='severity', values='count', title='Storm Severity Distribution')
#     st.plotly_chart(fig_pie, use_container_width=True)

with colB:
    restored_ratio = pd.DataFrame({
        'status':['Outage','No Outage'],
        'count':[int(df['is_outage'].sum()), int(len(df)-df['is_outage'].sum())]
    })
    fig_pie2 = px.pie(restored_ratio, names='status', values='count', title='Outage vs No Outage')
    st.plotly_chart(fig_pie2, use_container_width=True)

st.subheader("Detailed Table: Events & Outages")
st.dataframe(df[['record_id','event_time','device_type','device_id','pole_id','customers_impacted','severity','restoration_hours','crews_required','pole_condition','conductor_affected','is_outage']].sort_values('event_time').reset_index(drop=True))

st.markdown("---")

# Outage detection and NMS correlation summary
st.subheader("7. Outage Detection & NMS Correlation")
st.write("This section correlates simulated NMS events with detected outages in assets.")
cor_summary = correlation.groupby(['is_outage','nms_matched']).size().reset_index(name='count')
st.table(cor_summary)

st.subheader("Detailed Correlation Table")
st.dataframe(correlation[['record_id','event_time','device_type','device_id','pole_id','is_outage','nms_event_type','nms_matched']].sort_values('event_time'))

st.markdown("---")

# Export functionality
st.subheader("Export Data")
colexp1, colexp2 = st.columns(2)
with colexp1:
    st.download_button("Download data (CSV)", data=df.to_csv(index=False).encode('utf-8'), file_name='storm_data.csv')
with colexp2:
    st.download_button("Download NMS correlation (CSV)", data=correlation.to_csv(index=False).encode('utf-8'), file_name='nms_correlation.csv')

# st.markdown("---")

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix

st.markdown("---")
st.subheader("8. Train & Save Outage Prediction Model")

if st.button("Train & Save Model on Data"):
    # Prepare features and labels
    features = ["customers_impacted", "restoration_hours", "crews_required", "age_years"]
    X = df[features]
    y = df["is_outage"].astype(int)

    # Train-test split
    from sklearn.model_selection import train_test_split
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.metrics import classification_report, confusion_matrix

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42)

    # Train model
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    # Save model to disk
    joblib.dump(model, MODEL_PATH)

    # Evaluate
    y_pred = model.predict(X_test)
    st.write("### Model Performance")
    st.text(classification_report(y_test, y_pred))
    st.write("Confusion Matrix")
    st.write(confusion_matrix(y_test, y_pred))

    st.success(f"Model trained and saved as {MODEL_PATH}")

# Load existing model
if os.path.exists(MODEL_PATH):
    model = joblib.load(MODEL_PATH)
    st.session_state.outage_model = model
    st.info("Loaded trained model from disk.")

# Prediction form
if "outage_model" in st.session_state:
    st.markdown("### Test the Saved Model")
    cust = st.number_input("Customers Impacted", 50, 2000, 500)
    resto = st.number_input("Restoration Hours", 1, 72, 12)
    crews = st.number_input("Crews Required", 1, 25, 5)
    age = st.number_input("Asset Age (years)", 1, 50, 10)

    if st.button("Predict Outage"):
        X_new = [[cust, resto, crews, age]]
        pred = st.session_state.outage_model.predict(X_new)[0]
        prob = st.session_state.outage_model.predict_proba(X_new)[0][1]
        st.write(f"Prediction: **{'Outage' if pred==1 else 'No Outage'}** (probability: {prob:.2f})")

# st.subheader("8. Example: How outage records would be created in an NMS")
# st.write("The example below simulates an API payload for outages that would be pushed to a Network Management System (NMS).")
# example_outages = df[df['is_outage']].head(10)
# example_payload = []
# for _, r in example_outages.iterrows():
#     example_payload.append({
#         'asset_id': r['device_id'] if pd.notnull(r['device_id']) else r['pole_id'],
#         'asset_type': r['device_type'],
#         'detected_at': r['event_time'].isoformat(),
#         'customers_impacted': int(r['customers_impacted']),
#         'severity': r['severity'],
#         'estimated_restore_hours': int(r['restoration_hours']),
#         'crew_required': int(r['crews_required'])
#     })

# st.code(pd.DataFrame(example_payload).to_json(orient='records', indent=2))

# st.markdown("---")
# ------------------ Updated Charts Section ------------------

st.markdown("---")
st.subheader("Charts & Insights")

# Dropdown to filter by severity
severity_filter = st.selectbox("Select Storm Severity", ["All", "Severe", "Moderate"])
if severity_filter != "All":
    df_filtered = df[df["severity"] == severity_filter]
else:
    df_filtered = df

# ---------------- Chart 1 ----------------
st.subheader("1. Restoration Time vs. Number of Outages")
resto_outages = df_filtered.groupby("restoration_hours").is_outage.sum().reset_index()
fig1 = px.scatter(
    resto_outages, x="restoration_hours", y="is_outage",
    labels={"restoration_hours": "Restoration Time (hours)", "is_outage": "Number of Outages"},
    title="Restoration Time vs Number of Outages"
)
st.plotly_chart(fig1, use_container_width=True)

# ---------------- Chart 2 ----------------
st.subheader("2. Customers Affected vs. Types of Poles")
# Example pole type mapping
pole_types = ["Wooden", "Metal", "Concrete"]
df_filtered["pole_type"] = np.where(df_filtered["device_type"] == "Pole",
                                    np.random.choice(pole_types, size=len(df_filtered)),
                                    "Other")
pole_customers = df_filtered[df_filtered["device_type"] == "Pole"].groupby("pole_type").customers_impacted.sum().reset_index()
fig2 = px.pie(
    pole_customers, names="pole_type", values="customers_impacted",
    title="Customers Affected by Pole Type"
)
st.plotly_chart(fig2, use_container_width=True)

# ---------------- Chart 3 ----------------
st.subheader("3. Number of Outages/Issues to be Resolved by Crew")
crew_issues = df_filtered.groupby("crews_required").is_outage.sum().reset_index()
fig3 = px.bar(
    crew_issues, x="crews_required", y="is_outage",
    labels={"crews_required": "Crews Required", "is_outage": "Number of Issues"},
    title="Outages/Issues Assigned to Crews"
)
st.plotly_chart(fig3, use_container_width=True)

# ---------------- Chart 4 ----------------
st.subheader("4. Estimated Restoration Time vs. Customer Count")
fig4a = px.scatter(
    df_filtered, x="restoration_hours", y="customers_impacted",
    labels={"restoration_hours": "Restoration Hours", "customers_impacted": "Customers Affected"},
    title="Restoration Hours vs Customers"
)
fig4b = px.scatter(
    df_filtered, x="customers_impacted", y="restoration_hours",
    labels={"customers_impacted": "Customers Affected", "restoration_hours": "Restoration Hours"},
    title="Customers vs Restoration Hours"
)
st.plotly_chart(fig4a, use_container_width=True)
st.plotly_chart(fig4b, use_container_width=True)

# ---------------- Chart 5 ----------------
st.subheader("5. Restoration Status (Yet to be Restored vs. Already Restored in d Hours)")
d_hours = st.slider("Select timeframe (d hours)", min_value=6, max_value=72, value=24, step=6)
restored = (df_filtered["restoration_hours"] <= d_hours).sum()
not_restored = (df_filtered["restoration_hours"] > d_hours).sum()
resto_status = pd.DataFrame({
    "status": ["Already Restored", "Yet to be Restored"],
    "count": [restored, not_restored]
})
fig5 = px.bar(
    resto_status, x="status", y="count", color="status",
    title=f"Restoration Status within {d_hours} Hours"
)
st.plotly_chart(fig5, use_container_width=True)


st.subheader("Notes & Next Steps")
st.markdown("- This app is a  data generator and visualization tool. Replace the data generator with real telemetry/NMS APIs and asset databases to make it production-ready.\n- For asset impact evaluation, integrate an asset inventory with age, make, and maintenance history to compute failure probabilities more accurately.\n- Add authentication and role-based access when deploying in operations environment.")

st.caption("Built with ❤️ — modify the  generator heuristics to better match your real-world distribution and asset models.")
