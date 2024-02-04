import sys
import pathlib
import scraping.scrape_buses as buses
import scraping.scrape_routes as route
import scraping.create_test_data as test # TODO: Delete

if __name__ == '__main__':
    
    # TODO: Supress command line checks if option quietly specified

    # Check if key exists
    key = pathlib.Path(".apikey")
    if not key.exists():
        FileNotFoundError(".apikey file with your key is required to scrape the API.")

    # Check if routes list exists
    routes = pathlib.Path("routes.txt")
    if routes.exists():
        print("routes.txt already exists. Scrape again? [y/n]")
        if input().lower() == "y":
            route.get_routes()
    else:
        route.get_routes()

    # Conduct scrape
    buses.scrape_bus_api("data/buses.db")

    # TODO: Test below
    # Check if pos.json exists and prompt to delete it if so
    #pos_json = pathlib.Path("pos.json")
    #if pos_json.exists():
    #    print("pos.json already exists. Scrape again? [y/n]")
    #    if input().lower() == "y":
    #        test.create_test_data(10, "pos") # TODO Replace back to scrape_bus_api
    #else:
    #    test.create_test_data(10, "pos")
