import dash
from dash import html
import pandas as pd
import pydeck as pdk
import dash_deck
import pathlib
import os

# 0. Register as Dash page ----------------------------------------------------

dash.register_page(
    __name__,
    path="/bus_trips_pydeck",
    title="Bus trips (Pydeck)",
    name="Bus trips (Pydeck)",
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

## 2.0. Geo data: Trips trails ------------------------------------------------

file = open("../visualizations/geodata/trips_trails.json")
df_trips_trails = pd.read_json(file)
file.close()

# Separete data frame by delay
df_delays = df_trips_trails[df_trips_trails["delay"]]
delayed_buses = list(df_delays["vid"])
df_on_time = df_trips_trails[~df_trips_trails["vid"].isin(delayed_buses)]


layer_delay = pdk.Layer(
    "TripsLayer",
    df_delays,
    get_path="coordinates",
    get_timestamps="tmstmp",
    get_color=[237, 28, 36],
    # get_color = "colors",
    width_min_pixels=5,
    current_time=2340,
    trail_length=800,
    rounded=True,
)

layer_on_time = pdk.Layer(
    "TripsLayer",
    df_on_time,
    get_path="coordinates",
    get_timestamps="tmstmp",
    get_color=[77, 184, 72],
    # get_color = "colors",
    width_min_pixels=5,
    current_time=2340,
    trail_length=800,
    rounded=True,
)

# Define initial view of Chicago
view_chicago = pdk.ViewState(
    latitude=41.8781, longitude=-87.6298, zoom=11, bearing=0, pitch=45
)

chi_trails = pdk.Deck(
    layers=[layer_delay, layer_on_time],
    initial_view_state=view_chicago,
    # map_style='light',
)
chi_trails.to_html("trips_trails.html")

# Save as deck_compontent to render in dash
deck_component_trails = dash_deck.DeckGL(
    chi_trails.to_json(),
    id="deck-gl",
    tooltip=True,
    mapboxKey=mapbox_key,
)


# 3. Define app layout --------------------------------------------------------

# App layout with deck components
# Source: https://medium.com/@lorenzoperozzi/a-journey-into-plotly-dash-5791228212ff

layout = html.Div(
    [
        ## CTA Bus Stops with pydec
        html.H4("Some trips we scrapped from the CTA webpage!"),
        html.P("This plot was made with pydeck"),
        deck_component_trails,
    ]
)
