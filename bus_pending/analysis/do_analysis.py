import pandas as pd
import pathlib
from analysis.analysis import analyze_schedule, filename, query_sch
from analysis.analyze_real_data import determine_time_data, estimate_delay, create_df_stats, label_ghosts


csv_path_stats = pathlib.Path(__file__).parents[2] / "data/stats_df.csv"
csv_path_complete = pathlib.Path(__file__).parents[2] / "data/complete_info.csv"


def do_analysis():
    """
    This function does all the analysis. From analyzing schedule data to analyze
        real data and then compare them to estimate delays. Creates two
        different csv files with information aboute routes. First file contains
        all data by route so the user can derive new stats. Second file contains
        basic stats by route

    Input:
        final_dfs (DataFrame): dataframe cleaned in cleaning directory
    """
    final_dfs = pd.read_csv(pathlib.Path(__file__).parents[2] / "data/trip_time_level.csv")
    final_dfs = final_dfs[final_dfs["consecutive_counts_y"].notna()]
    csv_path_stats = pathlib.Path(__file__).parents[2] / "data/stats_df.csv"
    csv_path_complete = pathlib.Path(__file__).parents[2] / "data/complete_info.csv"
    avg_trip_weekday, avg_trip_weekend = analyze_schedule(filename, query_sch)

    final_dfs[["day_time", "weekend"]] = final_dfs["tmstmp"].apply(
        lambda x: pd.Series(determine_time_data(x))
    )
    final_dfs = label_ghosts(final_dfs)
    estimate_delay(final_dfs, avg_trip_weekday, avg_trip_weekend)
    final_dfs["delay"] = final_dfs["delayed_time"].apply(lambda x: 1 if x > 0 else 0)
    final_dfs.to_csv(csv_path_complete)
    df_stats = create_df_stats(final_dfs)
    df_stats.to_csv(csv_path_stats)

