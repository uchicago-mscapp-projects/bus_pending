import dash
from dash import Dash, html, dcc, Input, Output
import plotly.express as px 
import geopandas as gpd
 
# Register as Dash page -------------------------------------------------------

dash.register_page(__name__, 
                   path = "/bus_stops_plotly", 
                   title = "Bus Stops (Plotly)", 
                   name =  "Bus Stops (Plotly)")


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


# 2. APP ----------------------------------------------------------------------
# 2.1 Initialize app ----------------------------------------------------------

# App layout with deck components 
# https://medium.com/@lorenzoperozzi/a-journey-into-plotly-dash-5791228212ff

# 2.2 Define app layout -------------------------------------------------------

layout = html.Div([
    html.H2("Welcome to bus_pending"), 
    html.H3("Results should arrive soon!"),

    # CTA Bus Stops with Plotly
    html.H4("Every bus stop in Chicago!"), 
    html.P("This plot was made with ploty"), 
    dcc.Graph(figure = fig_stops), 
])

