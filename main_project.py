"""
Name: Ze Hong Wu
Email: zehong.wu@macaulay.cuny.edu
Resources: -
Title: -
URL: -
"""

import pandas as pd

def import_data(csv_name, columns_to_use):
    """
    This function takes two inputs:
    csv_name: the name of a .csv file to read.
    columns_to_use: a list of columns to keep.

    The data in the .csv file is read into a DataFrame.
    If a valid list of columns is provided, only those columns will be kept.

    Returns the DataFrame.
    """
    df = None
    if columns_to_use != []:
        df = pd.read_csv(csv_name, columns_to_use)
    else:
        df = pd.read_csv(csv_name)
    return impute_housing(df)

def choose_date(date, default_date):
    """
    This function takes two inputs:
    date: a potentially NaN date.
    default_date: a non-NaN default date to return..

    Returns date if it is not NaN, or default_date otherwise.
    """
    if pd.isna(date):
        return default_date
    return date

def choose_postcode(postcode, boro):
    """
    This function takes two inputs:
    postcode: a potentially NaN zip code.
    boro: a non-NaN string containing a borough.

    Returns postcode if it is not empty, or the ZIP corresponding to boro otherwise.
    Based on impute_zip() in Assignment 4.
    """
    boro_dict = {"Bronx": 10451,
                "Brooklyn": 11201,
                "Manhattan": 10001,
                "Queens": 11431,
                "Staten Island": 10341}
    if pd.isna(postcode):
        return boro_dict[boro]
    return postcode

def impute_housing(df):
    """
    This function takes one inputs:
    df: a DataFrame object containing Affordable Housing Unit data.

    Missing values in the following columns are replaced with the following default values:
    Project Completion Date: January 1, 2024
    Postcode: the default post-codes of each borough

    The imputing will be done "manually" (unique code for every column).
    This is bad coding form, but circumstances make a more "elegant" solution difficult.

    Returns the imputed DataFrame.
    """

    df["Project Completion Date"] = df["Project Completion Date"]\
                                    .apply(lambda date: choose_date(date,\
                                            pd.to_datetime("2024-01-01")))
    df["Postcode"] = df.apply(lambda row: choose_postcode(row["Postcode"], row["Borough"]))
    return df

def main():
    """
    main function
    """
    desired_columns = [ "Project ID", "Project Start Date", "Project Completion Date",\
                        "Borough", "Postcode", "Census Tract",\
                        "NTA - Neighborhood Tabulation Area",\
                        "Building Completion Date", "Reporting Construction Type",\
                        "Extended Affordability Only", "Extremely Low Income Units",\
                        "Very Low Income Units", "Low Income Units", "Middle Income Units",\
                        "All Counted Units", "Total Units"]
    df = import_data("Affordable_Housing_Production_by_Building.csv", desired_columns)

    # saving intermediate work to .csv files
    # to skip earlier work in later sections
    # to do everything in one go, cmment out all save lines
    df.to_csv("AHP_by_Building_cleaned.csv")

if __name__ == "__main__":
    main()
