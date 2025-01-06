from dotenv import load_dotenv
load_dotenv()

import streamlit as st

from baml_client import b
from baml_client.types import Trip, CityState, ZipCode


def show_trip(trip: Trip):
    st.title("Trip Details")
    
    # Main trip details
    with st.container():
        st.subheader("Trip Overview")
        st.markdown(f"**Trip Name:** {trip.name}")
        st.markdown(f"**Trip Type:** {trip.type}")
    
    # Start location
    with st.container():
        st.subheader("Start Location")
        if isinstance(trip.start, CityState):
            st.markdown(f"**City:** {trip.start.city}")
            st.markdown(f"**State:** {trip.start.state}")
        elif isinstance(trip.start, ZipCode):
            st.markdown(f"**Zip Code:** {trip.start.zip_code}")
    
    # End location
    with st.container():
        st.subheader("End Location")
        if isinstance(trip.end, CityState):
            st.markdown(f"**City:** {trip.end.city}")
            st.markdown(f"**State:** {trip.end.state}")
        elif isinstance(trip.end, ZipCode):
            st.markdown(f"**Zip Code:** {trip.end.zip_code}")
    
    # Stops
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


def main():
    st.title("Trip Planner")
    message = st.text_area("Enter your trip details:", "Create a route from columbus, ohio to Seattle via Dallas, TX for my trip in Tesla Model Y with stop every 200 miles for charging and food. Also, stop around 5 pm to rest for about 10 hours every evening. Show accommodations including RV PARKS that allow charging and camping in Tesla for the night stay.")
    
    if st.button("Plan Trip"):
        trip = b.GetTrip(message)
        show_trip(trip)

if __name__ == "__main__":
    main()
