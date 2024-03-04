![Build Status](https://img.shields.io/github/issues/RMedina19/bus_pending)
![Build Status](https://img.shields.io/github/forks/RMedina19/bus_pending)
![Build Status](https://img.shields.io/github/stars/RMedina19/bus_pending)
![Build Status](https://img.shields.io/github/license/RMedina19/bus_pending)

# Bus Pending 🚌
Welcome to Bus Pending!

Bus Pending collects and analyzes high-frequency location data of Chicago’s public buses to better understand how often buses are delayed, and for whom delays occur. It combines live bus position data with bus schedules and demographic information on Chicago buses. These data are displayed in a live dashboard.

This application also contains resources to schedule and request location data to continue the project. The data linked here represents one week of bus positions, from February 22nd to 28th, 2024. 

Our approach is described in more detail in our [report](https://github.com/RMedina19/bus_pending/blob/main/report/00_report.pdf).

## Instructions:

1. Download the Bus Pending Github Repository to your local machine by running `git clone ‘https://github.com/RMedina19/bus_pending.git’` to you preferred directory.
2. Run `poetry install` from the top-level directory ‘/bus-pending’ to set up the working environment in Python. Note: this requires installing Python and Poetry, a Python package manager.
3. Download our [database of bus position](https://drive.google.com/file/d/1e97aufUhLLLAIf2sp-jjQ__-gJ13n83f/view?usp=drive_link) (826 mb) and place it in a data directory ‘/bus-pending/data’ or scrape data yourself. See [below](#scraping) for details on scraping data yourself.
4. Clean and analyze data by running `poetry run python -m bus-pending`
5. Launch the dashboard by `poetry run python -m bus_pending/app`

## Data and Technology:
We use the following data sets:

- [CTA bus locations](https://www.transitchicago.com/developers/bustracker/): The CTA bus tracker API provides bus locations each minute on their bus tracker API..
- [CTA schedule](https://www.transitchicago.com/developers/gtfs/): The CTA provides data in the General Transit Feed Specification (GTFS) that describes scheduled routes. 
- [CTA Route GeoData](https://data.cityofchicago.org/Transportation/CTA-Bus-Routes-kml/rytz-fq6y/about_data): CTA routes are publicly accessible as shapefiles on the City of Chicago’s Open Data portal.
- [Chicago Community Area GeoData](https://data.cityofchicago.org/Facilities-Geographic-Boundaries/Boundaries-Community-Areas-current-/cauq-8yn6): Chicago community area boundaries are publicly accessible as shapefiles on the City of Chicago’s Open Data portal.
- [American Community Survey](https://data.census.gov/table?t=Income+and+Poverty&g=050XX00US17031%241000000%2C17031%241500000&y=2022&d=ACS+5-Year+Estimates+Detailed+Tables): We use block-level income and poverty measures from the American Community Survey for our map backgrounds. This links the table referenced.

We scrape, clean, and analyze these data using Python 3.12, store the data in sqlite3, and visualize the data on a Dash app using Plotly and PyDeck. Our cleaning frameworks are Pandas and GeoPandas.

## Scraping
Requesting data from the CTA requires an [API key](https://www.ctabustracker.com/home). A key can be requested for free.

Once you have an API key, we include a shell script to regularly scrape data from the CTA. Although we scraped bus locations each minute, this will exceed the rate limit of 10,000 requests per day, as each minute requires 13 requests to the CTA API for 18,740 requests per day. 
To scrape the script, do the following once you have the working environment set-up as suggested in [Instructions](#instructions):
1. Put your working directory into the bus_pending file by running `cd/bus_pending/bus_pending`.
2. Create a database using `poetry run python -m scraping –makedb`. This will scrape the scheduled routes and provide users the ability to select which components to scrape.
3. Run each iteration of the scraper by running `poetry run python -m scraping –quiet`. The --quiet option automatically loads the database if /data/buses.db does not exist and then downloads the full list of routes from the CTA API to scrape without requiring user input.

We provide a shell script schedule.sh, in the bus-pending/ folder to automate this process.

## Acknowledgments
We owe a big thank you to guidance and encouragement from our professor, James Turk, and our Teaching Assistant: Katherine Dumais. This project wouldn’t have been possible without either of them.

# Authors :writing_hand:
Author | GitHub Link | Lead |
:------------: | :-------------: | :-------------: |
Michael Rosenbaum      | [GitHub](https://github.com/m-rosenbaum) | Scraping
Keling Yue             | [GitHub](https://github.com/keling888) | Cleaning
Daniel Muñoz           | [GitHub](https://github.com/dmunozbatista) | Analysis
Regina Isabel Medina   | [GitHub](https://github.com/RMedina19) | Visualization and Server

# License :scroll:
This repository's content must be used under the terms and conditions of the [MIT License](LICENSE)
