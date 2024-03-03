import sys
import pathlib
import scraping.scrape_buses as buses
import scraping.scrape_routes as route
import scraping.scrape_schedules as schedules
import scraping.make_db as make_db

if __name__ == '__main__':

    # Check options    
    if '--quiet' in sys.argv:
        quiet = True
    else:
        quiet = False

    # Check if key exists
    key = pathlib.Path(__file__).parents[2] / '.apikey'
    if not key.exists():
        raise FileNotFoundError('.apikey file with your key is required.')

    # Check if routes list exists
    routes = pathlib.Path(__file__).parents[2] / 'routes.txt'
    if routes.exists() and not quiet:
        print('routes.txt already exists. Scrape again? [y/n]')
        if input().lower() == 'y':
            route.get_routes(routes)
    elif routes.exists() and quiet:
        pass
    else:
        route.get_routes(routes)

    # Check if database exists
    db = pathlib.Path(__file__).parents[2] / 'data/buses.db'
    if db.exists() and not quiet:
        print('buses.db already exists. Build and add schedules [y/n]')
        if input().lower() == 'y':
            make_db.make_db()
            schedules.scrape()
    elif db.exists() and quiet:
        pass
    else:
        make_db.make_db()
        schedules.scrape()

    # Conduct scrape
    buses.scrape_bus_api(db)
