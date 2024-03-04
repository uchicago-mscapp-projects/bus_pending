import sys
import pathlib

import bus_pending.app as app
import bus_pending.analysis.analyze_real_data as analyze
import bus_pending.cleaning.clean as clean
import bus_pending.visualizations.acs as viz_acs
import bus_pending.visualizations.maps as viz_maps
import bus_pending.visualizations.preprocessing_for_plotly as viz_plotly
import bus_pending.visualizations.preprocessing_for_pydeck as viz_pydeck


if __name__ == '__main__':

    # If data doesn't exist exit with error
    db = pathlib.Path(__file__).parents[1] / 'data/buses.db'
    if not db.exists():
        raise FileNotFoundError('data/buses.db is needed to run the app.')
    
    # First clean and analyze data
    # clean.write(db)
    clean_data = pathlib.Path(__file__).parents[1] / 'data/trip_time_level.csv'
    analyze.do_analysis()
    
    # Check for income raw files
    for year in range(2018, 2023): 
        csv_name = 'visualizations/acsdata/acs_income_zipcodes_' + str(year) + ".csv"
        acs_data = pathlib.Path(__file__) / csv_name

        if not acs_data.exists(): 
            raise FileNotFoundError(f"ACS data for {year} is missing.")

    viz_plotly.write_income_series()   
    
        
    # Check for 