import sys
import pathlib
import scraping.scrape as scrape

if __name__ == '__main__':
    
    # Check if key exists
    key = pathlib.Path(".apikey")
    if not key.exists():
        FileNotFoundError(".apikey file with your key is required to scrape the API.")

    # Check if pos.json exists and prompt to delete it if so
    pos_json = pathlib.Path("pos.json")
    if pos_json.exists():
        print("pos.json already exists. Scrape again? [y/n]")
        if input().lower() == "y":
            scrape.create_test_data(10, "pos") # TODO Replace back to scrape_bus_api
    else:
        scrape.create_test_data(10, "pos")
    
