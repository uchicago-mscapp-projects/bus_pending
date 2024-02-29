from dash import Dash, html, dcc, Input, Output
import plotly.express as px 
import plotly.graph_objects as go
import geopandas as gpd
import pandas as pd
import pydeck as pdk
import json
import dash_deck 

# Procesing data --------------------------------------------------------------

### Bus stops geo data 
geo_bus_stops = gpd.read_file("geodata/CTA_Bus_Stops.geojson")

# Map with deck --------------------------------------------------------------

# Center plot around Chicago 
view_chicago = pdk.ViewState(
    latitude = 41.8781, longitude = -87.6298, zoom = 12)

# Build scatterplot layer
my_layers = [
    # Bus Stops 
    pdk.Layer(
        type = "ScatterplotLayer", 
        data = geo_bus_stops, 
        pickable = True, 
        get_position = "geometry.coordinates", 
        get_fill_color = [255, 0, 0],
        radius_scale = 15
    )
]

# Render Deck object with centered view and scatter layer
chi = pdk.Deck(
    layers = my_layers, 
    initial_view_state = view_chicago, 
    map_style='light', 
    )

# Convert to html
chi.to_html("example.html")

# Save as deck_compontent to render in dash 
deck_component = dash_deck.DeckGL(
    chi.to_json(), id="deck-gl", tooltip=True, 
    # mapboxKey=chi.mapbox_key
)


# Initialize app --------------------------------------------------------------

app = Dash(__name__)
app.layout = html.Div(deck_component)

# End. ------------------------------------------------------------------------