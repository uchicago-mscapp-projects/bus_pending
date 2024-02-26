from dash import Dash, html, dcc, Input, Output
import plotly.express as px 
import plotly.graph_objects as go
import geopandas as gpd
import pandas as pd
import pydeck as pdk
import json
import dash_deck 

# MAPBOX Token 
mapbox_api_token = ""

# Initialize app --------------------------------------------------------------

app = Dash(__name__)

# Clean data ------------------------------------------------------------------

### Income data 
# Load income data 
file = open("acs_data/df_income_zip_code_series.csv")
df_income = pd.read_csv(file)
file.close()

# Load geodata for zip codes 
file = open("geodata/Boundaries_ZIP_Codes.geojson")
geo_zip_codes = json.load(file)
file.close()

# Building a trial dataset 
chicago_zip_codes= []

for zip in geo_zip_codes["features"]:
    # print(zip["properties"]["zip"])
    chicago_zip_codes.append(zip["properties"]["zip"])

# Build a data set with all zip codes
df_income["zip"] = df_income["zip"].astype("string")
df_income_chicago = df_income[df_income["zip"].isin(chicago_zip_codes)]


### Bus stops geo data
geo_bus_stops = gpd.read_file("geodata/CTA_Bus_Stops.geojson")

fig_stops = px.scatter_geo(geo_bus_stops, 
                lat = geo_bus_stops.geometry.y, 
                lon = geo_bus_stops.geometry.x, 
                hover_name = "public_nam")


fig_stops.update_geos(fitbounds="locations")
fig_stops.update_layout(margin={"r":0,"t":0,"l":0,"b":0})


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
    mapboxKey=mapbox_api_token,
)

# APP Layout ------------------------------------------------------------------

app.layout = html.Div([
    html.H2("Welcome to bus_pending"), 
    html.H3("Results should arrive soon!"),

    # INCOME DATA BY ZIP CODE 
    html.H4("Chicago income differentials by zip code"), 
    html.P("Select an option:"), 
    # Input for interactive map
    dcc.Dropdown(
       id = "user_year", 
       options = df_income["year"].unique(), 
       value = 2022, 
    ), 
    # Callout to map
    dcc.Graph(id = "map_chi_zips"),

    # CTA Bus Stops with Plotly
    html.H4("Every bus stop in Chicago!"), 
    html.P("This plot was made with ploty"), 
    dcc.Graph(figure = fig_stops), 
    
    ## CTA Bus Stops with pydec
    html.H4("Every bus stop in Chicago!"), 
    html.P("This plot was made with pydeck"), 
    deck_component
  
])


# Interactive maps ------------------------------------------------------------
@app.callback(
    Output("map_chi_zips", "figure"), 
    Input("user_year", "value"), 
    )

def display_choropleth(user_year):

    fig = px.choropleth(
        # Data frame with variables of interest
        df_income_chicago[df_income_chicago["year"] == user_year], 
        # Geojson with geography 
        geojson = geo_zip_codes, 
        # Variable that is to be mapped as color
        color = "income",
        # Key in geojson to link with data frame
        featureidkey = "properties.zip",
        locations = "zip", 
        # Coordinate to center the map around
        center = dict(lat = 41.8781, lon = -87.6298), 
        # 
        projection = "mercator"
    )   

    # Adjust zoom to display Chicago (based on the shapefile)
    fig.update_geos(fitbounds="locations")
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    
    return fig


# -----------------------------------------------------------------------------
if __name__ == '__main__':
    app.run(debug=True)
