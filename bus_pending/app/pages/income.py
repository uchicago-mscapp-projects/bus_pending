
import dash
from dash import Dash, html, dcc, Input, Output, callback 
import plotly.express as px 
import pandas as pd
import json


# Register as Dash page -------------------------------------------------------

dash.register_page(__name__, 
                   path = "/income_data", 
                   title = "Income data (Plotly)", 
                   name =  "Income data (Plotly)")


## 1.1. Income data -----------------------------------------------------------

# Load income data 
file = open("../visualizations/acs_data/df_income_zip_code_series.csv")
df_income = pd.read_csv(file)
file.close()

## 1.2. Geo data: Chicago zip code boundaries ---------------------------------

# Load geodata for zip codes 
file = open("../visualizations/geodata/Boundaries_ZIP_Codes.geojson")
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

## 1.3. Layout ----------------------------------------------------------------

layout = html.Div([

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
  
])

# 1.4 Interactive controls ----------------------------------------------------

@callback(
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

