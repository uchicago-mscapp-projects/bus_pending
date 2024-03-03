import pandas as pd
import sqlite3
import pyarrow
import numpy as np
import pathlib

#scraped_filename = pathlib.Path(__file__).parent.parent/"data/buses_static_2024-02-29.db"

def import_data(filename):

    """
    read our database into a Pandas dataframe

    Input(str):
        filename: path of the file
    Output(Pandas dataframe):
        df: raw data frame from scraped data file
    """
    # import data from database
    conn = sqlite3.connect(filename)
    # for consistency of the raw data, we use data from 20240221 00:00
    query = "SELECT * FROM buses WHERE tmstmp > '20240220 23:59'"
    df = pd.read_sql_query(query, conn)
    conn.close()

    return df

def ghostbuses(df):

    """
    If a bus only appears in the data frame for one minute, we
    consider it as a ghost bus that lost GPS connection.

    Count the # of observations for each bus.
    If # =1, 'status' of this bus would be 'ghost'.
    Set the 'pdist' of the bus to 0

    Input(Pandas dataframe): 
        df: Scraped raw dataframe
    Output(Pandas dataframe): 
        df: Dataframe with a column specifying the status of the bus
    """

    df = df.copy()
    df['GroupSize'] = df.groupby('vid')['vid'].transform('count')
    df['status'] = np.where(df['GroupSize'] == 1, 'Ghost', pd.NA)
    df.loc[df['status'] == 'Ghost', 'pdist'] = 0

    return df


def determine_occurrence(subset):

    """
    If the bus changes its direction from last minute, 
    we consider it as finishing this trip and beginning next trip.

    We try to get how many consective rows a bus has run towards the same destination, 
    before changing destination.
    The value of consective_counts is considered to be the number of observations of this
    trip of this bus(vid).

    Input(Pandas dataframe): 
        subset: vid-tmstmp data labled with whether it's a ghost bus or not in the status
    Output(Pandas dataframe): 
        final_df: vid-tmstmp data with status and consecutive_counts
    """

    subset = subset.copy()
    # check if this row's destination is the same as last row
    # (i.e.whether this bus changes destination in this minute.)
    subset['change'] = subset['des'] != subset['des'].shift()
    # rows with the same group number of this vehicle means those are data points of the same trip
    subset['group'] = subset['change'].cumsum()
    # number of consective rows before the bus enter the next trip
    consecutive_counts = subset.groupby('group').size()
    counts_df = consecutive_counts.reset_index(name='consecutive_counts').set_index('group')
    final_df = pd.merge(subset, counts_df, left_on='group', right_index=True, how='left')

    return final_df


def error_dealing(subset):

    """
    In our scraping data, there are buses that are in the middle of trips when our scraping begins
    and buses that did not finish trips when our scraping ends. We consider those rows as 'middle cuts'.

    There are also rows that have the same destination for less than 10 minutes. We consider this to be 
    a kind of misoperation by the bus driver. We lable those rows as 'misoperation'.

    Other rows will be labeled as 'complete'.

    In our analysis, we only include data that represents a bus running a complete journey

    Input(Pandas dataframe): 
        subset: dataframe with consective_counts data
    Output(Pandas dataframe): 
        subset: dataframe with error type of the bus 
    """

    trip_sequence = list(set(subset['group'].values.tolist()))
    # first we filter out top and bottom rows
    subset['error']=np.where(subset['group'].isin(trip_sequence[1:-1:1]),'complete', 
                             'middle_cut')
    # then we deal with the rest
    condition = subset['error'] == 'complete'
    subset.loc[condition, 'error'] = np.where(subset.loc[condition, 'consecutive_counts'] <= 10, 'misoperation', 'complete')
    
    return subset


def final_observation(df):

    """
    To map with scheduled data, we take the last observation of one trip of a bus, and return its direction.
    We also get the total distance the bus has run in this trip to double-check if the trip has errors in Analysis
    part.

    Input(Pandas dataframe): 
        df: dataframe with group index
    Output(Pandas dataframe):
        df: dataframe with columns specifying the directiona and total distance at the last obervation of the trip
    """

    grouped_sum = df.groupby('group')['pdist'].transform('max')
    df['total_dist'] = grouped_sum 
    last_values = df.groupby('group')['hdg'].transform('last')
    df['last_value'] = last_values

    return df

def turn_degree_to_dir(df):

    """
    Turn numerical degree for direction into string-type direction.

    Input(Pandas dataframe):
        df: dataframe with a column specifying the degree direction of the bus
    Output(Pandas dataframe):
        df: dataframe with a column specifying direction: N, E, S, W
    """

    DIRECTION_BOUNDS = ([0, 90,180,270,360], ["North", "East", "South", "West"])
    df['direction'] = pd.cut(df['last_value'], bins = DIRECTION_BOUNDS[0],
                                     labels=DIRECTION_BOUNDS[1], 
                                     right=False)
    
    return df


def create_duration_df(filename):

    """
    This function is used to create a restricted sample of trip-time level data

    Input(str):
        filename:path of the scraped data
    Output(None)
        this function will write trip-time level dataframe into a csv and put it under data folder 
    """

    df = import_data(filename)
    df = ghostbuses(df)
    concat_subsets = []
    for name, subset in df.groupby(by = 'vid'):
        subset.sort_values(by = 'tmstmp')
        subset = determine_occurrence(subset)
        subset = error_dealing(subset)
        complete_subset = determine_occurrence(subset[subset['error'] == 'complete'])
        final_bus_level = final_observation(complete_subset)
        final_bus_level.sort_values(['group', 'tmstmp'], inplace=True)
        collapsed_df = final_bus_level.groupby('group').last().reset_index()
        concat_subsets.append(collapsed_df)
    final_dfs = pd.concat(concat_subsets)
    final_dfs = turn_degree_to_dir(final_dfs)
    final_dfs.drop(final_dfs.columns[1], axis=1,inplace=True)
    final_dfs = final_dfs.reset_index(drop=True)

    final_dfs.to_csv(pathlib.Path(__file__).parent.parent/'data/trip_time_level.csv')
    return


#create_duration_df(scraped_filename)










    
    
