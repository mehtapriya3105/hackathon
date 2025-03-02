

import json
import streamlit as st
import folium
from streamlit_folium import folium_static
import requests

API_URL = "http://localhost:8000"

def get_coordinates(response, address):
    """
    Get latitude and longitude using Photon API (OpenStreetMap-based).
    """
    base_url = "https://photon.komoot.io/api/"
    params = {"q": address, "limit": 1}

    try:
        response = requests.get(base_url, params=params, timeout=5)
        response.raise_for_status()
        data = response.json()

        if "features" in data and data["features"]:
            lat = data["features"][0]["geometry"]["coordinates"][1]
            lon = data["features"][0]["geometry"]["coordinates"][0]
            return lat, lon
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching coordinates for address '{address}': {e}")
        return None, None

    return None, None

# def plot_addresses_on_map(response,addresses):
#     """
#     Plot multiple addresses on a folium map.
#     """
#     if not addresses:
#         st.error("No addresses provided!")
#         return None

#     # Initialize the map with the first address coordinates
#     first_lat, first_lon = get_coordinates(response, addresses[0])
#     if first_lat is None:
#         st.error(f"Unable to get coordinates for the first address: {addresses[0]}")
#         return None

#     map_obj = folium.Map(location=[first_lat, first_lon], zoom_start=10)

#     # Add markers for each address
#     markers_added = 0
#     for address in addresses:
#         lat, lon = get_coordinates(response,address)
#         print(response)
#         if lat and lon:
#             for patient in response.get('patients', []):
               
#                 first_name = patient.get('firstName', '')
#                 last_name = patient.get('lastName', '')
#                 # number = patient.get('contact','')
                
#                 popup_text = (f"{first_name} {last_name} ")
#                 folium.Marker([lat, lon], popup=popup_text).add_to(map_obj)
#                 markers_added += 1
#             # folium.Marker([lat, lon], popup=(response.get('firstName'))).add_to(map_obj)
#             # markers_added += 1
#         else:
#             st.warning(f"Could not locate address: {address}")

#     # Display a message if no markers were added
#     if markers_added == 0:
#         st.warning("No valid locations found to add markers.")

#     return map_obj


def plot_addresses_on_map(response, addresses):
    """
    Plot multiple addresses on a folium map.
    """
    if not addresses:
        st.error("No addresses provided!")
        return None

    # Initialize the map with the first address coordinates
    first_lat, first_lon = get_coordinates(response, addresses[0])
    if first_lat is None:
        st.error(f"Unable to get coordinates for the first address: {addresses[0]}")
        return None

    map_obj = folium.Map(location=[first_lat, first_lon], zoom_start=10)

    # Add markers for each address
    markers_added = 0
    patients = response.get('patients', [])
    
    for address, patient in zip(addresses, patients):
        lat, lon = get_coordinates(response, address)
        if lat and lon:
            first_name = patient.get('firstName', '')
            last_name = patient.get('lastName', '')
            
            popup_text = f"{first_name} {last_name}"
            folium.Marker([lat, lon], popup=popup_text).add_to(map_obj)
            markers_added += 1
        else:
            st.warning(f"Could not locate address: {address}")

    # Display a message if no markers were added
    if markers_added == 0:
        st.warning("No valid locations found to add markers.")

    return map_obj


def fetch_patients_by_disease(disease):
    """Fetch patient data from the FastAPI endpoint"""
    try:
        response = requests.get(f"{API_URL}/get_patients_by_disease", params={"disease": disease})
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Error fetching data: {response.status_code}")
            return {"patients": []}
    except Exception as e:
        st.error(f"Error connecting to API: {e}")
        return {"patients": []}

# Function to parse address dictionary into a formatted string
def parse_address(address_dict):
    """
    Convert an address dictionary into a properly formatted string.
    """
    if not isinstance(address_dict, dict):
        return ""
    
    # Extract address components
    street = address_dict.get("street", "")
    city = address_dict.get("city", "")
    state = address_dict.get("state", "")
    country = address_dict.get("country", "")
    
    # Combine components into a single string
    address_parts = [street, city, state, country]
    return ", ".join(part for part in address_parts if part)

# Streamlit app logic
st.title("Disease-Based Patient Mapping")

disease_name = st.text_input("Enter the disease name:", value="Tuberculosis")

if disease_name:
    addresses = fetch_patients_by_disease(disease_name)
    addresses_list = [parse_address(patient.get("address", {})) for patient in addresses.get("patients", [])]
    map_obj = plot_addresses_on_map(addresses, addresses_list)

    if map_obj:
        folium_static(map_obj)