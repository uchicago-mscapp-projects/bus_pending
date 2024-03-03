import dash
from dash import html

dash.register_page(__name__, path='/')

layout = html.Div([
    html.H3('About this project'),
    html.P('We are CAPP30122 students! And we wanted to know how late buses are in Chicago.'),
    html.P('Feel free to wonder around this page and see some of what we found.'),
    html.P('Note: If you open a Pydeck plot, return to this home page with the web browser navigator \"back\" button.'),

    html.H4('Data Sources'), 
    html.H4('Methodology'), 
    html.H4('Libraries and dependencies')

])