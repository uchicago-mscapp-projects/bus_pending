import dash
from dash import html
import geopandas as gpd
import pydeck as pdk
import dash_deck
import fsspec
import pathlib
import os

# 0. Register as Dash page ----------------------------------------------------

dash.register_page(
    __name__,
    path="/bus_stops_pydeck",
    title="CTA Bus Grid (Pydeck)",
    name="CTA Bus Grid (Pydeck)",
)

# 1. Load Mapbox token --------------------------------------------------------

mapbox_key_path = pathlib.Path(__file__).parents[0] / ".apikey"

if os.path.exists(mapbox_key_path):
    file = open(mapbox_key_path)
    mapbox_key = file.read()
    file.close()
else:
    mapbox_key = ""


# 2. Clean and plot data ------------------------------------------------------

## 2.0. Geo data: Chicago bus stops -------------------------------------------

### Bus stops geo data
geo_bus_stops = gpd.read_file("../visualizations/geodata/CTA_Bus_Stops.geojson")

# Build scatterplot layer
layers_stops = [
    # Bus Stops
    pdk.Layer(
        type="ScatterplotLayer",
        data=geo_bus_stops,
        pickable=True,
        get_position="geometry.coordinates",
        get_fill_color=[255, 0, 0],
        radius_scale=15,
    )
]


## 2.1. Geo data: Chicago bus routes ------------------------------------------

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
        get_line_width=10,
    )
]


# Center plot around Chicago
view_chicago = pdk.ViewState(latitude=41.8781, longitude=-87.6298, zoom=11, pitch=45)


# Build scatterplot layer
layers_stops = [
    # Bus Stops
    pdk.Layer(
        type="ScatterplotLayer",
        data=geo_bus_stops,
        pickable=True,
        get_position="geometry.coordinates",
        get_fill_color=[255, 0, 0],
        radius_scale=15,
    )
]

# Edit a tooltip in a multilayred pydec
# Source: https://discuss.streamlit.io/t/is-it-possible-to-implement-multi-layer-tooltips-with-pydeck/13614

# Render Deck object with centered view and scatter layer
chi_stops_routes = pdk.Deck(
    layers=[layers_routes, layers_stops],
    initial_view_state=view_chicago,
    map_style="light",
    tooltip={"text": "Bus stop {public_nam}", "style": {"color": "white"}},
)
# Convert to html
chi_stops_routes.to_html("bus_grid.html")

# Save as deck_compontent to render in dash
deck_component_bus_grid = dash_deck.DeckGL(
    chi_stops_routes.to_json(),
    id="deck-gl",
    tooltip=True,
    mapboxKey=mapbox_key,
)


# 3 Define app layout ---------------------------------------------------------

# App layout with deck components
# Source: https://medium.com/@lorenzoperozzi/a-journey-into-plotly-dash-5791228212ff

layout = html.Div(
    [
        ## CTA Bus Stops with pydec
        html.H4("Every bus stop in Chicago!"),
        html.P("This plot was made with pydeck"),
        deck_component_bus_grid,
    ]
)
