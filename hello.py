from dotenv import load_dotenv
import streamlit as st
from baml_client import reset_baml_env_vars
from baml_client.async_client import b
from baml_client.types import Trip, CityState, ZipCode
from baml_client.partial_types import Trip as PartialTrip
from baml_client.partial_types import CityState as PartialCityState
from baml_client.partial_types import ZipCode as PartialZipCode
import pandas as pd
from opencage.geocoder import OpenCageGeocode
import os
import pydeck as pdk
from multiprocessing.pool import ThreadPool

geocoder = OpenCageGeocode(os.getenv("OPEN_CAGE_API_KEY"))

def get_coordinates(location: CityState | ZipCode | PartialCityState | PartialZipCode | None):
    if location is None:
        return None
    if isinstance(location, (CityState, PartialCityState)):
        query = f"{location.city}, {location.state}"
    elif isinstance(location, (ZipCode, PartialZipCode)):
        query = f"{location.zip_code}"
    results = geocoder.geocode(query, countrycode="us")
    if results and isinstance(results, list) and len(results) > 0 and isinstance(results[0], dict) and 'geometry' in results[0]:
        return results[0]['geometry']
    return None

def get_coordinates_batch(locations: list[CityState | ZipCode | PartialCityState | PartialZipCode | None], batch_size: int = 5):
    coordinates = []
    with ThreadPool(processes=batch_size) as pool:
        coordinates = pool.map(get_coordinates, locations)
    return coordinates

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
    
    # Create placeholder for the map that we'll update
    map_placeholder = st.empty()
    
    # Main trip details
    with st.container():
        st.subheader("Trip Overview")
        st.markdown(f"**Trip Name:** {trip.name if trip.name else 'Planning...'}")
        st.markdown(f"**Trip Type:** {trip.type if trip.type else 'Planning...'}")
    
    # Start and End locations
    for location_type, location_data in [("Start Location", trip.start), ("End Location", trip.end)]:
        with st.container():
            st.subheader(location_type)
            if location_data:
                if isinstance(location_data, CityState):
                    st.markdown(f"**City:** {location_data.city}")
                    st.markdown(f"**State:** {location_data.state}")
                elif isinstance(location_data, ZipCode):
                    st.markdown(f"**Zip Code:** {location_data.zip_code}")
    
    # Initialize map data
    map_data = []
    accommodation_data = []
    
    def update_map():
        if not map_data:
            return
        
        map_df = pd.DataFrame(map_data)
        
        # Assign colors based on stop type
        color_map = {
            "charging": [255, 0, 0],   # Red
            "overnight": [0, 0, 255]  # Blue
        }
        map_df["color"] = map_df["type"].apply(lambda x: color_map.get(x, [0, 255, 0]))

        # Create line data for connecting points
        line_data = []
        for i in range(len(map_data) - 1):
            line_data.append({
                "sourcePosition": [map_data[i]["lon"], map_data[i]["lat"]],
                "targetPosition": [map_data[i + 1]["lon"], map_data[i + 1]["lat"]],
            })

        # Create scatter plot layer for points
        scatter_layer = pdk.Layer(
            "ScatterplotLayer",
            map_df,
            get_position=["lon", "lat"],
            get_color="color",
            get_radius=10000,
            pickable=True,
            tooltip={
                "html": "<b>Stop Type:</b> {type}<br><b>Reason:</b> {reason}",
                "style": {"backgroundColor": "steelblue", "color": "white"},
            },
        )

        # Create line layer for connecting points
        line_layer = pdk.Layer(
            "LineLayer",
            line_data,
            get_width=3,
            get_color=[128, 128, 128],  # Gray color for lines
            pickable=False,
        )

        view_state = pdk.ViewState(
            latitude=map_df["lat"].mean(),
            longitude=map_df["lon"].mean(),
            zoom=4,
            pitch=0,
        )

        r = pdk.Deck(
            layers=[line_layer, scatter_layer],
            initial_view_state=view_state,
        )
        map_placeholder.pydeck_chart(r)
    
    # Process stops in smaller batches for incremental updates
    batch_size = 3  # Process 3 locations at a time
    all_locations = [ trip.start] + [stop.location for stop in trip.stops] + [trip.end]
    
    progress_bar = st.progress(0)
    status_text = st.empty()

    data = [None] + [stop for stop in trip.stops] + [None]
    
    for i in range(0, len(all_locations), batch_size):
        batch = all_locations[i:i + batch_size]
        status_text.text(f"Processing stops {i+1} to {min(i+batch_size, len(all_locations))}...")
        
        # Get coordinates for this batch
        coords_batch = get_coordinates_batch(batch, batch_size=len(batch))
        
        # Process this batch of stops
        for j, (stop, coords) in enumerate(zip(data[i:i + batch_size], coords_batch)):
            if stop is None:
                continue
            with st.expander(f"Stop {i+j+1}", expanded=False):
                st.markdown(f"**Stop Type:** {stop.type}")
                if isinstance(stop.location, CityState):
                    st.markdown(f"**Location:** City: {stop.location.city}, State: {stop.location.state}")
                elif isinstance(stop.location, ZipCode):
                    st.markdown(f"**Location:** Zip Code: {stop.location.zip_code}")
                st.markdown(f"**Reason:** {stop.reason}")
                
                # Add to map data
                if coords:
                    map_data.append({
                        "lat": coords["lat"],
                        "lon": coords["lng"],
                        "type": stop.type,
                        "reason": stop.reason
                    })
                    
                    # Fetch accommodations for overnight stops
                    if stop.type == "overnight":
                        accommodations = find_accommodations(coords, i+j+1)
                        accommodation_data.extend(accommodations)
        
        # Update progress
        progress = min((i + batch_size) / len(all_locations), 1.0)
        progress_bar.progress(progress)
        
        # Update map with new data
        update_map()
    
    status_text.text("All stops processed!")
    progress_bar.empty()

async def main():
    st.title("Trip Planner")
    message = st.text_area("Enter your trip details:", 
        "Create a route from Columbus, Ohio to Seattle via Dallas, TX for my trip in Tesla Model Y with stops every 200 miles for charging and food. Also, stop around 5 pm to rest for about 10 hours every evening. Show accommodations including RV parks that allow charging and camping in Tesla for the night stay.")
    
    if st.button("Plan Trip"):
        # Create placeholders for dynamic updates
        plan_status = st.empty()
        trip_container = st.container()
        
        with plan_status:
            with st.spinner("Planning your trip..."):
                # Start streaming the trip planning
                result = await b.GetTrip(message)
                
                # async for partial_trip in stream:
                #     # Show current state of the trip
                #     if partial_trip.start and partial_trip.end:  # Only show if we have at least start/end
                #         with trip_container:
                #             show_trip(partial_trip)
                
                # Get and show final trip
                with trip_container:
                    show_trip(result)
                
                plan_status.success("Trip planning completed!")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())