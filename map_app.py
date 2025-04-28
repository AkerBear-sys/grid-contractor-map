import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

# --------------------------
# SIMPLE LOGIN AUTHENTICATION
# --------------------------
# Define login credentials
USERNAME = "Aker"
PASSWORD = "ENTR"

# Create a simple login form
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    with st.form("Login"):
        st.title("🔐 Please log in")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")

        if submitted:
            if username == USERNAME and password == PASSWORD:
                st.session_state.authenticated = True
                st.success("✅ Login successful!")
                st.experimental_rerun()
            else:
                st.error("❌ Incorrect username or password.")

    st.stop()  # 🚫 Stop the app here if not authenticated
# --------------------------

# Load contractors from CSV
# --------------------------
df = pd.read_csv("contractors_data.csv")

# Parse contractors into a list of dicts
contractors = []
for _, row in df.iterrows():
    contractor = {
        "name": row["name"],
        "coords": [row["latitude"], row["longitude"]],
        "region": row["region"],
        "country": row["country"],
        "services": [s.strip() for s in str(row["services"]).split(";")],
        "description": row["description"],
        "company_type": row.get("company_type", "Unknown"),
        "website": row.get("website", "")
    }
    contractors.append(contractor)

# --------------------------
# Streamlit Page Layout
# --------------------------
st.set_page_config(layout="wide")
st.title("⚡ Grid-Civil Contractor Map")

# --------------------------
# Sidebar Filters with Reset Logic
# --------------------------
with st.sidebar.expander("🔎 Filters", expanded=True):
    if st.button("🔄 Clear All Filters"):
        st.query_params.clear()
        st.session_state.country_filter = "All"
        st.session_state.company_type_filter = "All"
        st.session_state.selected_services = []
        st.session_state.region_filter = "All"

    region_options = sorted(set([c["region"] for c in contractors]))
    region_filter = st.selectbox("🌍 Select region", ["All"] + region_options, key="region_filter")

    country_options = sorted(set([c["country"] for c in contractors]))
    country_filter = st.selectbox("🏳️ Select country", ["All"] + country_options, key="country_filter")

    service_options = [
        "Substation Civil", "Transmission Lines", "Landfall HDD",
        "Nearshore Civil Works", "Cable Ducting", "Access Roads",
        "Excavation & Earthworks", "Foundations & Piling", "Grid Connection Civils"
    ]
    if "selected_services" not in st.session_state:
        st.session_state.selected_services = []
    selected_services = st.multiselect("🧰 Select services", service_options, default=st.session_state.selected_services, key="selected_services")

    company_type_options = sorted(set([c["company_type"] for c in contractors]))
    company_type_filter = st.selectbox("🏗️ Company type", ["All"] + company_type_options, key="company_type_filter")

# --------------------------
# Determine Filtered Contractors
# --------------------------
filtered_contractors = [
    c for c in contractors
    if (region_filter == "All" or c["region"] == region_filter)
    and (country_filter == "All" or c["country"] == country_filter)
    and (not selected_services or any(service in c["services"] for service in selected_services))
    and (company_type_filter == "All" or c["company_type"] == company_type_filter)
]

# --------------------------
# Map Initialization (no world wrapping)
# --------------------------
if region_filter == "All" and country_filter == "All" and not selected_services and company_type_filter == "All":
    m = folium.Map(location=[30, 0], zoom_start=3, tiles='CartoDB dark_matter', prefer_canvas=True, no_wrap=True)
elif filtered_contractors:
    bounds = [[c["coords"][0], c["coords"][1]] for c in filtered_contractors]
    m = folium.Map(location=[30, 0], zoom_start=3, tiles='CartoDB dark_matter', prefer_canvas=True, no_wrap=True)
    m.fit_bounds(bounds, padding=(50, 50))
else:
    m = folium.Map(location=[30, 0], zoom_start=3, tiles='CartoDB dark_matter', prefer_canvas=True, no_wrap=True)

# --------------------------
# Display Filtered Contractors
# --------------------------
for contractor in filtered_contractors:
    website_link = f'<br><a href="{contractor["website"]}" target="_blank">Visit Website</a>' if contractor["website"] else ""

    popup_html = f"""
<b>{contractor['name']}</b><br>
<i>{contractor['region']}</i><br>
{contractor['description']}<br>
<b>Services:</b> {', '.join(contractor['services'])}<br>
<b>Country:</b> {contractor['country']}<br>
<b>Type:</b> {contractor['company_type']}{website_link}
"""

    marker_color = 'blue' if contractor['company_type'] == 'Civil Engineering' else 'red'

    folium.CircleMarker(
        location=contractor["coords"],
        radius=6,
        color=marker_color,
        weight=8,
        fill=True,
        fill_color=marker_color,
        fill_opacity=0.9,
        tooltip=contractor["name"],
        popup=folium.Popup(popup_html, max_width=300)
    ).add_to(m)

# --------------------------
# Render Map in Streamlit
# --------------------------
st_folium(m, width=2200, height=1300)
