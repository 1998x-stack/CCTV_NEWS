# coding=utf-8
import sys
import os
sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/' + '..'))

from typing import Tuple, Optional

import pandas as pd
import folium
from folium.plugins import HeatMap
import cpca
from cpca import _init_data

from util.log_utils import logger

# Initialize adcode data and matcher
AD_2_ADDR_DICT, MATCHER = _init_data()

def get_lat_lon(city: str) -> Tuple[Optional[float], Optional[float]]:
    """
    Get the latitude and longitude of a city using cpca.

    Args:
        city (str): The name of the city.

    Returns:
        Tuple[Optional[float], Optional[float]]: A tuple containing the latitude and longitude,
        or (None, None) if the city cannot be matched.
    """
    # Extract province, city, and district information using cpca
    location_df = cpca.transform([city], pos_sensitive=True)
    
    if location_df.empty:
        logger.log_info(f"City {city} cannot be parsed, skipping.")
        return None, None
    
    adcode = location_df.iloc[0].get('adcode')
    if pd.isna(adcode):
        logger.log_info(f"Cannot get adcode for city {city}, skipping.")
        return None, None
    
    # Get address information from adcode
    addr_info = AD_2_ADDR_DICT.get(adcode.ljust(12, '0'))
    if addr_info:
        return float(addr_info.latitude), float(addr_info.longitude)
    else:
        logger.log_info(f"No matching address information found for city {city}'s adcode, skipping.")
        return None, None

def create_heatmap(city_count: pd.DataFrame, kind: str = 'province', heatmap_html_path: Optional[str] = None) -> str:
    """
    Create a heatmap based on city count data.

    Args:
        city_count (pd.DataFrame): DataFrame containing city names and their counts.
        kind (str, optional): Type of administrative division. Defaults to 'province'.
        heatmap_html_path (Optional[str], optional): Path to save the heatmap HTML file. 
            If None, a default path will be used.

    Returns:
        str: Path to the saved heatmap HTML file.
    """
    data = []
    # Set default HTML path if not provided
    if heatmap_html_path is None:
        heatmap_html_path = os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            f'figures/{kind}_heatmap.html'
        )
    
    # Iterate through each city and its count
    for _, row in city_count.iterrows():
        city, count = row[0], row[1] * 100
        try:
            lat, lon = get_lat_lon(city)
        except Exception as e:
            lat, lon = None, None
            logger.log_exception()
        
        if lat is None or lon is None:
            logger.log_info(f"{kind}: {city} - Unable to find coordinates, skipping.")
            continue
        
        # Add city's coordinates and count to the data list
        data.append([lat, lon, count])
    
    # Create Folium map object
    map_center = [35.8617, 104.1954]  # Center of China
    m = folium.Map(location=map_center, zoom_start=5)
    
    # Add heatmap data to the map
    HeatMap(data).add_to(m)
    
    # Save the generated map as an HTML file
    m.save(heatmap_html_path)
    
    return heatmap_html_path