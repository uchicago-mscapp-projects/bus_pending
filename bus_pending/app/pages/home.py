import dash
from dash import html

dash.register_page(__name__, path='/')

layout = html.Div([
    html.H3('Welcome to Bus Pending'),    
    html.P('We are CAPP30122 students! And we wanted to know how late buses are in Chicago.'),
    html.P('Feel free to wonder around this page and see some of what we found.'),
    html.P('Note: If you open a Pydeck plot, return to this home page with the web browser navigator \"back\" button.'),
    
    html.H3('About this project'),
    html.P('Bus Pending collects and analyzes high-frequency location data of Chicago’s public buses to better understand how often buses are delayed, and for whom delays occur. It combines live bus position data with bus schedules and demographic information on Chicago buses. These data are displayed in a live dashboard. This application also contains resources to schedule and request location data to continue the project. The data linked here represents one week of bus positions, from February 22nd to 28th, 2024.'),

    html.H4('Data Sources'), 
    html.P('We use the following data sets:'), 
    html.Div(
        id = "data_sources_list", 
        children = [
            html.Ul(
                id = "actual_list", 
                children = [
                    html.Li("CTA bus locations: The CTA bus tracker API provides bus locations each minute on their bus tracker API."), 
                    html.Li("CTA schedule: The CTA provides data in the General Transit Feed Specification (GTFS) that describes scheduled routes."),
                    html.Li("CTA Route GeoData: CTA routes are publicly accessible as shapefiles on the City of Chicago’s Open Data portal."),
                    html.Li("Chicago Community Area GeoData: Chicago community area boundaries are publicly accessible as shapefiles on the City of Chicago’s Open Data portal."),
                    html.Li("American Community Survey: We use block-level income and poverty measures from the American Community Survey for our map backgrounds. This links the table referenced.")
                ]  
            )
        ]
    ), 
    html.H4('Methodology'), 
    html.H4('Libraries and dependencies')

])