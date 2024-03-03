import dash
from dash import Dash, html, dcc, Input, Output
import plotly.express as px 
import geopandas as gpd
import pandas as pd
import pydeck as pdk
import dash_deck 
import fsspec
import dash_bootstrap_components as dbc


# Register as Dash page -------------------------------------------------------

dash.register_page(__name__, 
                   path = "/bus_routes_pydeck", 
                   title = "Bus routes (Pydeck)", 
                   name =  "Bus routes (Pydeck)")

# 0. Load Mapbox token --------------------------------------------------------

# mapbox_key = get_stored_data('visualizations/.apikey', 'key')
mapbox_key = ""

# 1. Clean and plot data ------------------------------------------------------

## 1.3. Geo data: Chicago bus stops -------------------------------------------

### Bus stops geo data
geo_bus_stops = gpd.read_file("../visualizations/geodata/CTA_Bus_Stops.geojson")

fig_stops = px.scatter_geo(geo_bus_stops, 
                lat = geo_bus_stops.geometry.y, 
                lon = geo_bus_stops.geometry.x, 
                hover_name = "public_nam")


fig_stops.update_geos(fitbounds="locations")
fig_stops.update_layout(margin={"r":0,"t":0,"l":0,"b":0})

## 1.4. Geo data: Chicago bus routes ------------------------------------------

path = "../visualizations/geodata/CTA_BusRoutes__2_.zip"
with fsspec.open(path) as file:
    gdf_bus_routes = gpd.read_file(file)

# Convert geometries to lan lon 
# Source: https://stackoverflow.com/questions/71278585/how-to-get-valid-latitude-and-longitude-from-linestring
gdf_bus_routes_latlon = gdf_bus_routes.to_crs(4326)

layers_routes = [
        pdk.Layer(
        "GeoJsonLayer",
        data=gdf_bus_routes_latlon,
        get_path="geometry",
        get_line_color=[227, 0, 25, 55],
        get_line_width = 10
    )
]

# Center plot around Chicago 
view_chicago = pdk.ViewState(
    latitude = 41.8781, longitude = -87.6298, zoom = 12)


# Render Deck object with centered view and scatter layer
chi_routes = pdk.Deck(
    layers = layers_routes, 
    initial_view_state = view_chicago, 
    map_style='light', 
    )

# Convert to html
chi_routes.to_html("example.html")

# Save as deck_compontent to render in dash 
deck_component_routes = dash_deck.DeckGL(
    chi_routes.to_json(), id="deck-gl", tooltip=True, 
    mapboxKey=mapbox_key,
)

# 2. APP ----------------------------------------------------------------------
# 2.1 Initialize app ----------------------------------------------------------

# App layout with deck components 
# https://medium.com/@lorenzoperozzi/a-journey-into-plotly-dash-5791228212ff

# 2.2 Define app layout -------------------------------------------------------

layout = html.Div([
    html.P("This plot was made with pydeck"), 
    dbc.Row([
        dbc.Col(deck_component_routes, 
                style = {'margin-left':'15px', 'margin-top':'7px', 'margin-right':'15px'})])
    ])


