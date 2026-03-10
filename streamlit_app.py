import streamlit as st
import pandas as pd
import pydeck as pdk
import json
import pathlib

# -----------------------------
# Data loading
# -----------------------------
def load_data():
    DATA_PATH = pathlib.Path(__file__).parent / "export.geojson"

    with open(DATA_PATH, "r", encoding="utf-8") as f:
        geojson = json.load(f)

    rows = []

    for feature in geojson["features"]:
        if feature["geometry"]["type"] != "Point":
            continue

        coords = feature["geometry"]["coordinates"]
        props = feature.get("properties", {})

        props["lon"] = coords[0]
        props["lat"] = coords[1]

        # Nettoyage des colonnes importantes
        props["name"] = props.get("name", "Unnamed place").lower()
        props["amenity"] = props.get("amenity", "").lower()
        props["mood"] = props.get("mood", "unknown").lower()
        props["outdoor_seating"] = props.get("outdoor_seating", "no").lower()
        props["wheelchair"] = props.get("wheelchair", "no").lower()

        rows.append(props)

    df = pd.DataFrame(rows)

    return df


df = load_data()

# évite certains crashs si données manquantes
df = df.fillna("")

# -----------------------------
# App title
# -----------------------------
st.title("🍹 Recommender System - Places to Visit Based on Your Mood")

# -----------------------------
# User filters
# -----------------------------
selected_types = st.multiselect(
    "Type of venue",
    options=["pub", "bar", "nightclub"],
    default=["pub", "bar", "nightclub"]
)

outdoor = st.radio(
    "Outdoor seating",
    ["yes", "no"]
)

wheelchair = st.radio(
    "Wheelchair access",
    ["yes", "no", "limited"]
)

selected_moods = st.multiselect(
    "Preferred music atmosphere",
    options=["jazz", "rock", "techno", "pop", "indie", "house"],
    default=["jazz", "rock", "techno", "pop", "indie", "house"]
)

# -----------------------------
# Apply filters
# -----------------------------
filtered_df = df[
    df["amenity"].isin([t.lower() for t in selected_types]) &
    (df["outdoor_seating"] == outdoor) &
    (df["wheelchair"] == wheelchair) &
    (df["mood"].isin(selected_moods))
]

st.subheader(f"🎯 {len(filtered_df)} place(s) found")

# -----------------------------
# Map
# -----------------------------
if not filtered_df.empty:

    layer = pdk.Layer(
        "ScatterplotLayer",
        data=filtered_df,
        get_position='[lon, lat]',
        get_radius=20,
        get_fill_color=[255, 0, 0],
        pickable=True,
        radius_min_pixels=4,
        radius_max_pixels=10,
        auto_highlight=True,
    )

    view_state = pdk.ViewState(
        latitude=filtered_df["lat"].mean(),
        longitude=filtered_df["lon"].mean(),
        zoom=13,
        pitch=0,
    )

    tooltip = {
        "html": "<b>{name}</b><br/>Type: {amenity}<br/>Outdoor: {outdoor_seating}<br/>Access: {wheelchair}<br/>Mood: {mood}",
        "style": {"backgroundColor": "white", "color": "black"}
    }

    st.pydeck_chart(
        pdk.Deck(
            map_style="light",
            initial_view_state=view_state,
            layers=[layer],
            tooltip=tooltip
        )
    )

    st.dataframe(
        filtered_df[
            ["name", "amenity", "mood", "outdoor_seating", "wheelchair", "lat", "lon"]
        ]
    )

else:
    st.warning("No place matches your search criteria.")