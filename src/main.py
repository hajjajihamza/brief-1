from transformation import transform
from loading import load
from extraction import extract

if __name__ == '__main__':
    load(transform(extract('data/row.csv')))