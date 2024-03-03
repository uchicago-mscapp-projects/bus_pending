"""
Data sources: 
    - Chicago Neighborhoods shapefiles (NOT USED):
        https://catalog.data.gov/dataset/boundaries-neighborhoods
    - Chicago Community areas geodata:
        https://data.cityofchicago.org/Facilities-Geographic-Boundaries/Boundaries-Community-Areas-current-/cauq-8yn6

"""

import plotly.express as px
import pandas as pd 
import geopandas as gpd
import json


# Convert shapefiles into geodata 
def convert_shapefiles(file_location, file_extension): 
    """
    Import original shape file published by the City of Chicago and transform 
    into geojson data for plotly package. 

    Args: 
        -   file_location (str): path to access file with .spx extension  
        -   file_extension (str): file extension
    """
    chicago_geodata = gpd.read_file(file_location + file_extension)
    chicago_geodata.to_file(file_location + ".geojson", 
                            driver = "GeoJSON")

def make_trial_data(geojson, locations): 
    """
    Takes jsonfile and extracts the list of communities/zip codes.
    Then it adds trial data that holds no meaning

    Args: 
    - geojson (geojson): shape file in geojson format, 
    - locations (str): name of the variable that has the locations names
    
    """
    df = pd.DataFrame(geojson, columns = [locations])
    df["trial_numbers"] = range(50, 50 + len(df))


# Build Chicago Neighborhoods map
def map_neighborhoods(): 
    
    # Import shapefiles 
    file = open("../data/geodata/Boundaries - Community Areas (current).geojson")
    geojson = json.load(file)
    file.close()

    df = make_trial_data(geojson, "community_name")

    fig = px.choropleth(
        # Data frame with variables of interest
        df, 
        # Geojson with geography 
        geojson = geojson, 
        # Variable that is to be mapped as color
        color = "trial_numbers",
        # Key in geojson to link with data frame
        featureidkey = "properties.community",
        locations = "community_name", 
        # Coordinate to center the map around
        center = dict(lat = 41.8781, lon = -87.6298), 
        # 
        projection = "mercator"
    )

    # Adjust zoom to display Chicago (based on the shapefile)
    fig.update_geos(fitbounds="locations")
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})


