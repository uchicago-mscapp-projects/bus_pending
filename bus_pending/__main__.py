import sys
import pathlib

import bus_pending.app as app
#import bus_pending.analysis.analyze_real_data as analyze
import bus_pending.cleaning.clean as clean
import bus_pending.visualizations.acs as viz_acs
import bus_pending.visualizations.maps as viz_maps
import bus_pending.visualizations.plotly_maps as viz_plotly
import bus_pending.visualizations.pydeck_maps as viz_pydeck


if __name__ == '__main__':

    # If data doesn't exist exit with error
    db = pathlib.Path(__file__).parents[1] / 'data/buses.db'
    if not db.exists():
        raise FileNotFoundError('data/buses.db is needed to run the app.')
    
    # First clean and analyze data
    clean.write(db)
    clean_data = pathlib.Path(__file__).parents[1] / 'data/trip_time_level.csv'
    #analyze.do_analysis(clean_data)
    