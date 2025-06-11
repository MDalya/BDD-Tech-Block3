import streamlit as st
import geopandas as gpd
import pydeck as pdk

# Data loading
def load_data():
    gdf = gpd.read_file("export.geojson")
    gdf.columns = gdf.columns.str.strip().str.lower()

    # Keep only valid points
    gdf = gdf[gdf.geometry.type == "Point"]
    gdf = gdf[gdf.geometry.notnull()]

    # Extract coordinates
    gdf["lon"] = gdf.geometry.x
    gdf["lat"] = gdf.geometry.y

    # Clean relevant columns
    for col in ["outdoor_seating", "wheelchair"]:
        gdf[col] = gdf[col].fillna("no").str.lower()

    gdf["name"] = gdf["name"].fillna("Unnamed place")
    gdf["mood"] = gdf["mood"].fillna("unknown").str.lower()
    gdf["amenity"] = gdf["amenity"].fillna("").str.lower()

    return gdf

df = load_data()

# Main title
st.title("🍹 Recommender System - Places to Visit Based on Your Mood")

# User filters
selected_types = st.multiselect(
    "Type of venue",
    options=["pub", "bar", "nightclub"],
    default=["pub", "bar", "nightclub"]
)

outdoor = st.radio("Outdoor seating", ["yes", "no"])
wheelchair = st.radio("Wheelchair access", ["yes", "no", "limited"])

selected_moods = st.multiselect(
    "Preferred music atmosphere",
    options=["jazz", "rock", "techno", "pop", "indie", "house"],
    default=["jazz", "rock", "techno", "pop", "indie", "house"]
)

# Apply filters
filtered_df = df[
    df["amenity"].isin([t.lower() for t in selected_types]) &
    (df["outdoor_seating"] == outdoor) &
    (df["wheelchair"] == wheelchair) &
    (df["mood"].isin(selected_moods))
]

st.subheader(f"🎯 {len(filtered_df)} place(s) found")

if not filtered_df.empty:
    # Interactive map
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

    st.pydeck_chart(pdk.Deck(
        map_style="mapbox://styles/mapbox/streets-v11",
        initial_view_state=view_state,
        layers=[layer],
        tooltip=tooltip
    ))

    # Results table
    st.dataframe(filtered_df[["name", "amenity", "mood", "outdoor_seating", "wheelchair", "lat", "lon"]])

else:
    st.warning("No place matches your search criteria.")
