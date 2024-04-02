import sys
import pathlib

# import bus_pending.app as app
import bus_pending.cleaning.clean as clean
import bus_pending.analysis.do_analysis as analyze
import bus_pending.visualizations.preprocessing_for_plotly as viz_plotly
import bus_pending.visualizations.preprocessing_for_pydeck as viz_pydeck


if __name__ == '__main__':

    # If data doesn't exist exit with error
    db = pathlib.Path(__file__).parents[1] / 'data/buses.db'
    if not db.exists():
        raise FileNotFoundError('data/buses.db is needed to run the app.')
    
    # First clean and analyze data
    print('Cleaning data...')
    clean.write(db)
    print('Analyzing data...')
    analyze.do_analysis()
    
    # Check for income raw files (this is dowloaded from ACS website)
    for year in range(2018, 2023): 
        csv_name = 'visualizations/acs_data/acs_income_zipcodes_' + str(year) + ".csv"
        acs_data = pathlib.Path(__file__).parents[0] / csv_name

        if not acs_data.exists(): 
            raise FileNotFoundError(f"ACS data for {year} is missing. File path: {acs_data}")

    # Launch site
    print("Creating maps...")     
    viz_plotly.write_income_series()   
    # Clean bus trips data (this is scraped data)
    viz_pydeck.clean_bus_trips()
