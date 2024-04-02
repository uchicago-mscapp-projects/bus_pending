import dash
from dash import html

# 0. Register as Dash page ----------------------------------------------------
dash.register_page(__name__, path="/")

## 1. App Layout --------------------------------------------------------------

layout = html.Div(
    [
        html.H3("Welcome to Bus Pending"),
        html.P(
            "We are CAPP30122 students! And we wanted to know how late buses are in Chicago."
        ),
        html.P("Feel free to wonder around this page and see some of what we found."),
        html.P(
            'Note: If you open a Pydeck plot, return to this home page with the web browser navigator "back" button. These are the "CTA Bus Grid" page (that shows every bus route and stop in Chicago) and the "Bus trips" page that display ~20 minutes of bus data (in green are buses on time and on red delayed buses).'
        ),
        html.H3("About this project"),
        html.P(
            "Bus Pending collects and analyzes high-frequency location data of Chicago’s public buses to better understand how often buses are delayed, and for whom delays occur. It combines live bus position data with bus schedules and demographic information on Chicago buses. These data are displayed in a live dashboard. This application also contains resources to schedule and request location data to continue the project. The data linked here represents one week of bus positions, from February 22nd to 28th, 2024."
        ),
        html.H4("Data Sources"),
        html.P("We use the following data sets:"),
        html.Div(
            id="data_sources_list",
            children=[
                html.Ul(
                    id="actual_list",
                    children=[
                        html.Li(
                            "CTA bus locations: The CTA bus tracker API provides bus locations each minute on their bus tracker API."
                        ),
                        html.Li(
                            "CTA schedule: The CTA provides data in the General Transit Feed Specification (GTFS) that describes scheduled routes."
                        ),
                        html.Li(
                            "CTA Route GeoData: CTA routes are publicly accessible as shapefiles on the City of Chicago’s Open Data portal."
                        ),
                        html.Li(
                            "Chicago Community Area GeoData: Chicago community area boundaries are publicly accessible as shapefiles on the City of Chicago’s Open Data portal."
                        ),
                        html.Li(
                            "American Community Survey: We use block-level income and poverty measures from the American Community Survey for our map backgrounds. This links the table referenced."
                        ),
                    ],
                )
            ],
        ),
        html.H4("Libraries"),
        html.P(
            "We scrape, clean, and analyze these data using Python 3.12, store the data in sqlite3, and visualize the data on a Dash app using Plotly and PyDeck. Our cleaning frameworks are Pandas and GeoPandas."
        ),
        html.H4("Acknoledgments"),
        html.P(
            "We owe a big thank you to guidance and encouragement from our professor, James Turk, and our Teaching Assistant: Katherine Dumais. This project wouldn’t have been possible without either of them. We also would like to thank the open source community who have invested time and effort building and documenting the tools we used for this project."
        ),
    ]
)
