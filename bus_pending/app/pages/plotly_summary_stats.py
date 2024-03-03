import dash
from dash import Dash, html, dcc, Input, Output, callback 
import plotly.express as px 
import pandas as pd
import pathlib
import numpy as np

# Register as Dash page -------------------------------------------------------

dash.register_page(__name__, 
                   path = "/summary_stats", 
                   title = "Delays statistics", 
                   name =  "Delays statistics")


# Load data -------------------------------------------------------------------

filename = pathlib.Path(__file__).parents[2] / "visualizations/scraped_data/stats_df.csv"
df_stats = pd.read_csv(filename)


# Wide format and average indicators
df_stats_long = pd.melt(
    df_stats, 
    id_vars = ["rt"],
    value_vars = ["percentage_delayed", "n_delayed", "max_delayed_time"], 
    )

df_average = df_stats_long.groupby(["variable"]).agg(
    value = pd.NamedAgg(column = "value", aggfunc=np.mean), 
    ).reset_index()

df_average["rt"] = "Average"



# Find your route plot --------------------------------------------------------

# Percentage of delays --------------------------------------------------------

plot_data = df_stats[:15]
fig_percentage = px.bar(
    plot_data, 
    x = "percentage_delayed", 
    y = "rt", 
    title = "Bus routes with most delays",
    labels = {
        "rt": "Bus route", 
        "percentage_delayed": "Percentage of delayed trips", 
    },
    template = "simple_white")


# Configure yaxis
fig_percentage.update_layout(yaxis=dict(autorange="reversed"))

# Configure xaxis
fig_percentage.update(layout_xaxis_range = [0, 100])
fig_percentage.update_xaxes( # the y-axis is in dollars
    ticksuffix=" %", showgrid=True
)
fig_percentage.update_traces(marker_color = "#8F3931")

# fig.show()

# Longest waiting times -------------------------------------------------------

data_max_time = df_stats.sort_values("max_delayed_time", ascending=False)[:15]

fig_max_time = px.bar(
    data_max_time, 
    x = "max_delayed_time", 
    y = "rt", 
    title = "Routes with the worst recorded waiting times",
    labels = {
        "rt": "Bus route", 
        "max_delayed_time": "Longest waiting time (in minutes)", 
    }, 
    template = "simple_white")

fig_max_time.update_layout(yaxis=dict(autorange="reversed"))
fig_max_time.update_traces(marker_color = "#8F3931")


# Total delays ----------------------------------------------------------------

# Number of delayed buses in a week 
data_num_delays = df_stats.sort_values("n_delayed", ascending=False)[:15]

fig_num_delays = px.bar(
    data_num_delays, 
    x = "n_delayed", 
    y = "rt", 
    title = "Bus routes with most delays",
    labels = {
        "rt": "Bus route", 
        "n_delayed": "Total delayed trips in a week", 
    }, 
    template = "simple_white")

fig_num_delays.update_layout(yaxis=dict(autorange="reversed"))
fig_num_delays.update_traces(marker_color = "#8F3931")

## 1.3. Layout ----------------------------------------------------------------

layout = html.Div([
    # Delays
    html.H4("Summary statistics in delay times"), 
    html.P("This plot was made with ploty"), 
    html.H5("Choose your route:"), 
    
    dcc.Dropdown(
        id = "user_route", 
        options = df_stats["rt"].unique(), 
        value = "171"),
    dcc.Graph(id = "bar_indicators"),

    html.H5("Bus routes with worst performance"), 
    dcc.Graph(figure = fig_percentage),
    dcc.Graph(figure = fig_max_time), 
    dcc.Graph(figure = fig_num_delays)
 
])



# 1.4 Interactive controls ----------------------------------------------------

@callback(
    Output("bar_indicators", "figure"), 
    Input("user_route", "value"), 
    )

def compare_route_with_average(user_route):
    df_route = df_stats_long[df_stats_long["rt"] == user_route]
    df_indicators = pd.concat([df_route, df_average], axis = 0)
    df_indicators = pd.DataFrame(df_indicators)

    df_indicators.loc[df_indicators["variable"] == "n_delayed", "variable"] = "Total delayed trips"
    df_indicators.loc[df_indicators["variable"] == "percentage_delayed", "variable"] = "% trips delayed"
    df_indicators.loc[df_indicators["variable"] == "max_delayed_time", "variable"] = "Highest waiting time registered"


    fig_compare =  px.bar(
    df_indicators, 
    x = "rt", y = "value", facet_col = "variable", color = "rt", 
    title = f"Bus route {user_route} delay indicators against average",
    labels = {
        "rt": "", 
        "value": "", 
    }, 
    color_discrete_map={"Average": "#8F3931", 
                        user_route: "#FFA319"}, 
    )
    fig_compare.update_yaxes(matches=None)
    fig_compare.update_yaxes(showticklabels=True)
    fig_compare.for_each_annotation(lambda a: a.update(text=a.text.replace("variable=", "")))
    fig_compare.update_traces(hovertemplate = None)
    fig_compare.update_layout(hovermode = "x")
    return fig_compare

