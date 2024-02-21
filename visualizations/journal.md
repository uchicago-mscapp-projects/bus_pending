----------------------------------

# CTA INFO
- Download routesshape file: https://catalog.data.gov/dataset/cta-bus-routes-shapefile
- Download bus stops shapefile: https://catalog.data.gov/dataset/cta-bus-stops-shapefile


----------------------------------
## GEOGRAPHIC UNITS: 
- Sociodemographic data will be extracted from the ACS
- There are no estimates for "neighborhoods"
- The closes units are "ZIP codes"
	- We must check if there are annual estimates for every Chicago zip code
	- No, there is not. 
	- ZIP code data is published on the five-year estimates

- What is a census tract?
- What is a block group?
- Block (220,333) > zip code (33,120) 
- If block refers to streets, then we may be able to build neighborhoods with this.
- What is "public use microdata area" (n = 2,378)  
	- Nonoverlapping areas that partition each state into contiguous geographic units containing no 100,000 people each.

## ACS GIS Shapefiles and Geodatabases Files 
- Spatial extracts from the Census Bureau's Master Address File 
- Are block shapefiles available?


## ACS TABLES: 
- We're going to use the "Detailed Tables", since they provide: 
	- all subjects in the ACS
	- block group level 
	- five years estimates that are more precise

## ACS ADVANCED TOOLS 
- "Summary File" is currently the only source for accessing block groups 

---------------------------------------

## DOWNLOADING DATA 
https://data.census.gov/table?t=Income+and+Poverty&g=050XX00US17031%241000000%2C17031%241500000&y=2022&d=ACS+5-Year+Estimates+Detailed+Tables 

Geography: All Block Groups within Cook County, Illinois
Topics: Income and Poverty 
Survey: American Community Survey (ACS 5-Year Estimates Detailed Tables)
Years: 2022


#### Income and poverty of all of Cook County's blocks
https://data.census.gov/table/ACSDT5Y2022.B17010?t=Income+and+Poverty&g=050XX00US17031%241500000&y=2022&d=ACS+5-Year+Estimates+Detailed+Tables

#### Income and poverty of all 