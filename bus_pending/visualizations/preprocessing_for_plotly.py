import pandas as pd
import geopandas as gpd
import numpy as np
from skimpy import clean_columns
import pathlib


def clean_income_data(path: str, year: int) -> pd.core.data.frame.DataFrame:
    """
    Takes income data from ACS tables and aggregates it by zipcode in a format
    that easily readable by plotly.

    The desaggregation for the ACS tables is: zip code, income.

    Args:
        - file (str): Common path were the files are stored
        - year (int): the year to be processed

    Returns (pandas data frame): a data frame with income data by zip code
    by year.
    """
    # Open file
    file = open(path)
    df_income_raw = pd.read_csv(file)
    file.close()

    # Clean data set
    # Clean variable names from income table
    df_income_wide = clean_columns(df_income_raw)
    df_income_wide = df_income_wide.drop(
        df_income_wide.filter(regex="margin_").columns, axis=1
    )

    # Select total population
    df_income_wide = df_income_wide[
        df_income_wide["label_grouping"].str.contains("Total")
    ]

    # Change to long format
    # Store all column names for zip codes
    zip_cols = df_income_wide.columns[1:1399]
    df_income = pd.melt(df_income_wide, id_vars="label_grouping", value_vars=zip_cols)

    df_income = df_income.rename(columns={"variable": "zip", "value": "income"})
    df_income = df_income.drop("label_grouping", axis=1)

    df_income["zip"] = df_income["zip"].str.replace(r"zcta_5_", "")
    df_income["zip"] = df_income["zip"].str.replace(r"_estimate", "")
    df_income["income"] = df_income["income"].str.replace(r",", "")
    df_income["income"] = df_income["income"].str.replace(r"-", "")

    # Replace observations that are entirely white space with NaN
    # Source: https://stackoverflow.com/questions/13445241/replacing-blank-values-white-space-with-nan-in-pandas
    df_income["income"] = (
        df_income["income"].replace(r"^\s*$", np.nan, regex=True).astype(float)
    )
    df_income["year"] = year

    return df_income


def write_income_series(min_year: int = 2018, max_year: int = 2022) -> None:
    """
    Build panel data on income by zip code.

    Args:
        - min_year (int): Starting year for the series
        - max_year (int): Ending year for the series

    Returns: No returns, but instead it writes the clean acs data.
    """
    df_income_zip_code_series = pd.DataFrame()

    for year in range(min_year, max_year + 1):
        csv_name = "acs_data/acs_income_zipcodes_" + str(year) + ".csv"
        path = pathlib.Path(__file__).parents[0] / csv_name

        df_year = clean_income_data(path, year)

        df_income_zip_code_series = pd.concat([df_income_zip_code_series, df_year])

    write_path = (
        pathlib.Path(__file__).parents[0] / "acs_data/df_income_zip_code_series.csv"
    )
    df_income_zip_code_series.to_csv(write_path, index=False)


# Convert shapefiles into geodata
def convert_shapefiles(file_location: str, file_extension: str) -> None:
    """
    Import original shape file published by the City of Chicago and transform
    into geojson data for plotly package.

    Args:
        -   file_location (str): path to access file with .spx extension
        -   file_extension (str): file extension
    Returns: No returns, but instead it writes geojson data
    """
    chicago_geodata = gpd.read_file(file_location + file_extension)
    chicago_geodata.to_file(file_location + ".geojson", driver="GeoJSON")
