import pathlib
import pandas as pd
from cleaning.clean import write

filename = pathlib.Path(__file__).parent/"data/your_database"

if __name__ == '__main__':

    write(filename)