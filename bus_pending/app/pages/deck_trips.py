import dash
from dash import Dash, html, dcc, Input, Output
import pandas as pd
import pydeck as pdk
import dash_deck

# Register as Dash page -------------------------------------------------------

dash.register_page(
    __name__,
    path="/bus_trips_pydeck",
    title="Bus trips (Pydeck)",
    name="Bus trips (Pydeck)",
)

# 0. Load Mapbox token --------------------------------------------------------

# mapbox_key = get_stored_data('visualizations/.apikey', 'key')
mapbox_key = ""

# 1. Clean and plot data ------------------------------------------------------

## 1.5. Geo data: Trips trails ------------------------------------------------

file = open("../visualizations/geodata/trips_trails.json")
df_trips_trails = pd.read_json(file)
file.close()

layer = pdk.Layer(
    "TripsLayer",
    df_trips_trails,
    get_path="coordinates",
    get_timestamps="tmstmp",
    get_color=[253, 128, 93],
    width_min_pixels=5,
    current_time=2340,
    trail_length=800,
    rounded=True,
)

# Define initial view of Chicago
view_chicago = pdk.ViewState(
    latitude=41.8781, longitude=-87.6298, zoom=10, bearing=0, pitch=45
)

chi_trails = pdk.Deck(
    layers=[layer],
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
    # style={"width": "50vw", "height": "50vh"}
)

# 2. APP ----------------------------------------------------------------------
# 2.1 Initialize app ----------------------------------------------------------

# App layout with deck components
# https://medium.com/@lorenzoperozzi/a-journey-into-plotly-dash-5791228212ff

# 2.2 Define app layout -------------------------------------------------------

layout = html.Div(
    [
        ## CTA Bus Stops with pydec
        html.H4("Some trips we scrapped from the CTA webpage!"),
        html.P("This plot was made with pydeck"),
        deck_component_trails,
    ]
)
