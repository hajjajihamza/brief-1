from cleaning import *

def transform():
    duplicate_data()
    text_cleaning()
    data_types_parsing()
    impossible_and_suspicious_values()
    imputation()
    structural_standardisation()
    pseudonymisation()
    return get_data_frame()