from dotenv import load_dotenv
load_dotenv()

import streamlit as st
from baml_client import b
from baml_client.types import Trip, CityState, ZipCode
import pandas as pd
from opencage.geocoder import OpenCageGeocode
import os
import pydeck as pdk

geocoder = OpenCageGeocode(os.getenv("OPEN_CAGE_API_KEY"))

def get_coordinates(location: CityState | ZipCode):
    if isinstance(location, CityState):
        query = f"{location.city}, {location.state}"
    elif isinstance(location, ZipCode):
        query = f"{location.zip_code}"
    results = geocoder.geocode(query, countrycode="us")
    if results:
        return results[0]['geometry']
    return None

def find_accommodations(location, stop_index):
    # Dummy implementation to simulate fetching hotel data.
    # Replace this with an actual API call to a hotel search service (e.g., Expedia, Booking.com).
    accommodations = [
        {"name": f"Hotel {stop_index}A", "price": "$100", "rating": 4.5, "lat": location["lat"] + 0.01, "lon": location["lng"] - 0.01},
        {"name": f"Hotel {stop_index}B", "price": "$120", "rating": 4.0, "lat": location["lat"] - 0.01, "lon": location["lng"] + 0.01},
        {"name": f"Hotel {stop_index}C", "price": "$90", "rating": 3.8, "lat": location["lat"], "lon": location["lng"]},
    ]
    return accommodations

def show_trip(trip: Trip):
    st.title("Trip Details")
    st.session_state["trip"] = trip  # Save the trip in session state
    
    # Main trip details
    with st.container():
        st.subheader("Trip Overview")
        st.markdown(f"**Trip Name:** {trip.name}")
        st.markdown(f"**Trip Type:** {trip.type}")
    
    # Start and End locations
    for location_type, location_data in [("Start Location", trip.start), ("End Location", trip.end)]:
        with st.container():
            st.subheader(location_type)
            if isinstance(location_data, CityState):
                st.markdown(f"**City:** {location_data.city}")
                st.markdown(f"**State:** {location_data.state}")
            elif isinstance(location_data, ZipCode):
                st.markdown(f"**Zip Code:** {location_data.zip_code}")
    
    # Stops and Map Data
    map_data = []
    accommodation_data = []
    with st.container():
        st.subheader("Stops")
        for index, stop in enumerate(trip.stops, start=1):
            with st.expander(f"Stop {index}"):
                st.markdown(f"**Stop Type:** {stop.type}")
                if isinstance(stop.location, CityState):
                    st.markdown(f"**Location:** City: {stop.location.city}, State: {stop.location.state}")
                elif isinstance(stop.location, ZipCode):
                    st.markdown(f"**Location:** Zip Code: {stop.location.zip_code}")
                st.markdown(f"**Reason:** {stop.reason}")
                
                # Add to map data
                coords = get_coordinates(stop.location)
                if coords:
                    map_data.append({
                        "lat": coords["lat"],
                        "lon": coords["lng"],
                        "type": stop.type,
                        "reason": stop.reason
                    })
                    
                    # Fetch accommodations for overnight stops
                    if stop.type == "overnight":
                        accommodations = find_accommodations(coords, index)
                        accommodation_data.extend(accommodations)
    
    # Display map for stops
    if map_data:
        st.subheader("Trip Map")
        map_df = pd.DataFrame(map_data)

        # Assign colors based on stop type
        color_map = {
            "charging": [255, 0, 0],   # Red
            "overnight": [0, 0, 255]  # Blue
        }
        map_df["color"] = map_df["type"].apply(lambda x: color_map.get(x, [0, 255, 0]))

        layer = pdk.Layer(
            "ScatterplotLayer",
            map_df,
            get_position=["lon", "lat"],
            get_color="color",
            get_radius=10000,
            pickable=True,
            tooltip=True,
        )

        view_state = pdk.ViewState(
            latitude=map_df["lat"].mean(),
            longitude=map_df["lon"].mean(),
            zoom=4,
            pitch=0,
        )

        tooltip = {
            "html": "<b>Stop Type:</b> {type}<br><b>Reason:</b> {reason}",
            "style": {"backgroundColor": "steelblue", "color": "white"},
        }

        r = pdk.Deck(
            layers=[layer],
            initial_view_state=view_state,
            tooltip=tooltip,
        )
        st.pydeck_chart(r)
    
    # Display accommodations
    if accommodation_data:
        st.subheader("Recommended Accommodations")
        for accommodation in accommodation_data:
            with st.container():
                st.markdown(f"**Name:** {accommodation['name']}")
                st.markdown(f"**Price:** {accommodation['price']}")
                st.markdown(f"**Rating:** {accommodation['rating']} stars")
                st.map(pd.DataFrame([accommodation], columns=["lat", "lon"]))

def main():
    st.title("Trip Planner")
    message = st.text_area("Enter your trip details:", 
        "Create a route from Columbus, Ohio to Seattle via Dallas, TX for my trip in Tesla Model Y with stops every 200 miles for charging and food. Also, stop around 5 pm to rest for about 10 hours every evening. Show accommodations including RV parks that allow charging and camping in Tesla for the night stay.")
    
    if st.button("Plan Trip"):
        trip = b.GetTrip(message)
        show_trip(trip)

if __name__ == "__main__":
    main()
