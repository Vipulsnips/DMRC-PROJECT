import streamlit as st
from dmrc_logic import (
    get_all_stations,
    get_route_and_fare,
    build_route_figure,
)


st.title("DMRC Metro Route & Fare Finder 🚇")
st.write(
    """
    Choose your source and destination metro stations 
    to view the suggested route, fare, and route map.
    """
)

# -------- Station selection --------
stations = sorted(get_all_stations())

col1, col2 = st.columns(2)

with col1:
    source = st.selectbox("Source station", stations)

with col2:
    destination = st.selectbox("Destination station", stations)

if st.button("Find Route"):
    if source == destination:
        st.warning("Source and destination are same. Please choose different stations.")
    else:
        route, fare = get_route_and_fare(source, destination)

        st.subheader("Route (stations)")
        st.write(" ➜ ".join(route))

        st.subheader("Estimated Fare")
        st.write(f"₹ {fare}")

        st.subheader("Journey Summary")
        st.write(f"Total stations: {len(route)}")

        # use your original-style full map
        fig = build_route_figure(route, source, destination)
        st.subheader("Route Map")
        st.pyplot(fig)
