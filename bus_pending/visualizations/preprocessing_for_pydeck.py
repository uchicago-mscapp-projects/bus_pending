import geopandas
import geopandas as gpd
import pandas as pd
import pathlib
import json


def make_time_unix(
    gdf: geopandas.geodataframe.GeoDataFrame, time_column_name: str
) -> geopandas.geodataframe.GeoDataFrame:
    """
    Takes a pands column with time data and converts it into unix format.
    It then standardizes it to start from 0.

    Args:
        - df (geopandas data frame): A data frame with a time column
        - time_column_name (string): The name of  pandas column with time data
        stored as a string with "yyyy-mm-dd hh:mm" format.

    Returns (pandas data frame): A pandas data frame with a new column with
    time as unix format and
    """

    gdf["unix_tmstmp"] = gdf[time_column_name].astype("datetime64[s]").astype("int")
    gdf["unix_tmstmp"] = gdf["unix_tmstmp"] - min(gdf["unix_tmstmp"])

    return gdf


def transform_points_to_paths(
    gdf: geopandas.geodataframe.GeoDataFrame, points_col_name: str, time_col_name: str
):
    """
    Collapses a series of points observations (stored as a geometry column)
    into a single "path" observation. The format complies with pydeck
    specifications to plot paths.

    Args:
    - gdf (geopandas data frame): A data frame with trips information,
    the unit of analysis is a snaptshot of all buseses at differents points in
    time.
    - points_col_name (string): The name of a column with geometry data in the
    form of points.
    - time_col_name (string): The name of column with time data in
    unix format.

    Returns (data frame): A pandas data frame with trips data. The unit of
    analysis is one observation per complete trip (instead of point in time).
    Returned data frame has a format that is readable by pydeck.

    """
    trips = gdf["vid"].unique()
    df_trips_trails = pd.DataFrame()

    for trip in trips:
        df_bus = gdf[gdf["vid"] == trip]
        route = df_bus["rt"].unique()[0]
        delay = df_bus["dly"].unique()[0]
        df_bus = pd.DataFrame(df_bus[[points_col_name, time_col_name]])

        list_coordinates = list(df_bus[points_col_name])
        list_tmstmp = list(df_bus[time_col_name])

        data = [[route, trip, delay, list_coordinates, list_tmstmp]]

        # Create the pandas DataFrame
        df_bus_trail = pd.DataFrame(
            data, columns=["route", "vid", "delay", "coordinates", "tmstmp"]
        )

        df_trips_trails = pd.concat([df_trips_trails, df_bus_trail], axis=0)

    return df_trips_trails


def clean_bus_trips() -> None:
    """
    Takes bus scraped data and turns it into a format that pydeck "PathLayer"
    can read. This is used for the "trips" visualizations in the dashboard.
    """
    # STEP 1. Convert raw scraped data into json
    filename = pathlib.Path(__file__).parents[0] / "scraped_data/bus_positions.json"

    file = open(filename)
    bus_positions = json.load(file)
    file.close()

    # Collapse data into buses
    all_buses = []

    for response in bus_positions:
        if "vehicle" in response["bustime-response"]:
            for bus in response["bustime-response"]["vehicle"]:
                bus["coordinates"] = [bus["lon"], bus["lat"]]
                all_buses.append(bus)

    df_buses = pd.read_json(json.dumps(all_buses))
    df_buses["geometry"] = gpd.points_from_xy(df_buses.lon, df_buses.lat)
    gdf_buses = gpd.GeoDataFrame(df_buses, geometry="geometry")

    gdf_buses_unix_time = make_time_unix(gdf_buses, "tmstmp")
    df_trails = transform_points_to_paths(
        gdf_buses_unix_time, "coordinates", "unix_tmstmp"
    )

    write_path = pathlib.Path(__file__).parents[0] / "geodata/trips_trails.json"
    df_trails.to_json(write_path, orient="records")
