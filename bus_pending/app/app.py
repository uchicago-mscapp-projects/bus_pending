import dash
from dash import Dash, html, dcc
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import load_figure_template

# App styling
# Source: https://towardsdatascience.com/3-easy-ways-to-make-your-dash-application-look-better-3e4cfefaf772
# Themes: https://dash-bootstrap-components.opensource.faculty.ai/docs/themes/explorer/
load_figure_template('FLATLY')
# style = {'margin-left':'7px', 'margin-top':'7px'}
         
app = Dash(__name__, use_pages=True, 
           external_stylesheets=[dbc.themes.LUX])

app.layout = html.Div(children = [
    dbc.Row([
        html.H1('Bus Pending', style = {"color": "white"}),
        html.H3('Your bus should arrive soon!', style = {"color": "white"}),
    ],
    style = {'background-color': '#800000'}
    ),
    dbc.Row([
        dbc.Col(            
            html.Div([
                html.Div(
                    dcc.Link(f"{page['name']}", href=page["relative_path"])
                    ) for page in dash.page_registry.values()]),
            style = {'background-color': '#D6D6CE'}
            ), 
        dbc.Col(
            dash.page_container, width = 10, style = {'margin-left':'15px', 
                                                     'margin-top':'7px', 
                                                     'margin-right':'15px', 
                                                     }, ),
        # dbc.Col(width = 1),
        ] ), 
    # dbc.Row([]), 
    dbc.Row([
        html.P('This project was done for the CAPP 30122 course by Michael Rosenbaum, Keling Yue, Daniel Muñoz, and Regina Isabel Medina'),
    ])
])

if __name__ == '__main__':
    app.run(debug=True)
