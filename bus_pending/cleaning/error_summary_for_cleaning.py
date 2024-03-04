import pandas as pd
import pathlib
from clean import create_error_summary
scraped_filename = pathlib.Path(__file__).parent.parent/"data/buses_static_2024-02-29.db"

raw_data = create_error_summary(scraped_filename)
#print(raw_data.head())
a = raw_data[raw_data['vid'] == 4]
print(a['tmstmp'].max() - a['tmstmp'].min())