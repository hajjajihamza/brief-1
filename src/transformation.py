from cleaning import *

def transform(df):
    return pseudonymisation(
            structural_standardisation(
                imputation(
                    impossible_and_suspicious_values(
                        data_types_parsing(
                            text_cleaning(
                                duplicate_data(df)
                            )
                        )
                    )
                )
            )
        )