"""
Name: Ze Hong Wu
Email: zehong.wu@macaulay.cuny.edu
Resources:
Pandas documentation for all manner of debugging help
Title: -
URL: -
"""

import pandas as pd

def import_housing(csv_name, columns_to_use):
    """
    This function takes two inputs:
    csv_name: the name of a .csv file to read.
    columns_to_use: a list of columns to keep.

    The data in the .csv file is read into a DataFrame.
    If a valid list of columns is provided, only those columns will be kept.

    Returns an imputed version of the DataFrame.
    """
    df = None
    df = pd.read_csv(csv_name)
    if columns_to_use != []:
        df = df[columns_to_use]
    #print("Finished importing; printing some sample columns")
    return impute_housing(df)

def choose_date(date, default_date):
    """
    This function takes two inputs:
    date: a potentially NaN date.
    default_date: a non-NaN default date to return.

    Returns date if it is not NaN, or default_date otherwise.
    """
    if pd.isna(date):
        return pd.to_datetime(default_date)
    return pd.to_datetime(date)

def choose_postcode(postcode, boro):
    """
    This function takes two inputs:
    postcode: a potentially NaN zip code.
    boro: a non-NaN string containing a borough.

    Returns postcode if it is not empty, or the ZIP corresponding to boro otherwise.
    Based on impute_zip() in Assignment 4.
    """
    #print("Choosing postcode or boro")
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

    The following columns will be added to the DataFrame:
    Project Start Year: year project starts
    Project End Year: year project ends
    Percent: All Counted Units / Total Units

    The imputing will be done "manually" (unique code for every column).
    This is bad coding form, but circumstances make a more "elegant" solution difficult.

    Returns the imputed DataFrame.
    """

    df["Project Completion Date"] = df["Project Completion Date"]\
                                .apply(lambda date: choose_date(date,"01/01/2024"))
    df["Project Start Date"] = df["Project Start Date"]\
                                .apply(lambda date: choose_date(date,"01/01/2024"))

    df["Postcode"] = df.apply(lambda row: choose_postcode(row["Postcode"], row["Borough"]), axis=1)
    df["Postcode"] = df["Postcode"].apply(int)

    df["Project Start Year"] = df["Project Start Date"]\
                            .apply(lambda date: date.year)

    df["Project End Year"] = df["Project Completion Date"]\
                            .apply(lambda date: date.year)

    df["Percent"] = 0.0
    df["Percent"] = df["All Counted Units"] / df["Total Units"]
    df["Percent"] = df["Percent"].apply(lambda percent: int(percent*100))
    return df

def clean_store_ahs_data():
    """
    Step 1: clean up the Affordable Housing data and save it to a csv file.
    """
    desired_columns = [ "Project ID", "Project Start Date", "Project Completion Date",\
                        "Borough", "Postcode", "Census Tract",\
                        "NTA - Neighborhood Tabulation Area",\
                        "Building Completion Date", "Reporting Construction Type",\
                        "Extended Affordability Only", "Extremely Low Income Units",\
                        "Very Low Income Units", "Low Income Units", "Middle Income Units",\
                        "All Counted Units", "Total Units"]
    # print("Before import")
    # print(desired_columns)
    df_housing = import_housing("Affordable_Housing_Production_by_Building.csv", desired_columns)

    # saving intermediate work to .csv files
    # to skip earlier work in later sections
    # to do everything in one go, cmment out all save lines
    df_housing.to_csv("AHP_by_Building_cleaned.csv", index=False)

    #df_housing = pd.read_csv("AHP_by_Building_cleaned.csv")
    print(df_housing)

def strip_letters(index):
    """
    This function takes one input:
    index: a string for a DataFrame index.

    Returns a version of index with only numbers.

    Example:
    input: 'ZCTAS 10101 Estimate'
    Returns: '10101'
    """
    output = ""
    for char in index:
        if "0" <= char <= "9":
            output += char
    return output[1:]

def import_income(csv_name):
    """
    This function takes one input:
    csv_name: the name of a .csv file to read.

    The data in the .csv file is read into a DataFrame.
    The DataFrame undergoes the following changes:
    - Rotate 90 degrees
    - Rename indices and columns for easier reading
    - Drop some useless columns

    Returns the modified DataFrame.
    """
    df_zip_income = pd.read_csv(csv_name, index_col=[0])
    #print(df_zip_income)
    # for column_label in df_zip_income:
    #     print("Printing a column label")
    #     print(column_label)
    df_zip_income_transposed = df_zip_income.transpose()
    #print(df_zip_income_transposed)

    # rename indices
    rename_index_dict = {}
    for idx in df_zip_income_transposed.index:
        if idx == "New York city, New York!!Households!!Estimate":
            rename_index_dict[idx] = "NYC"
        else:
            rename_index_dict[idx] = strip_letters(idx)
    df_zip_income_transposed.rename(index=rename_index_dict, inplace=True)

    # rename columns
    rename_column_dict = {}
    for col in df_zip_income_transposed.columns:
        rename_column_dict[col] = col.strip()
    df_zip_income_transposed.rename(columns=rename_column_dict, inplace=True)

    # drop useless columns
    # print(df_zip_income_transposed)
    # print(df_zip_income_transposed.columns)
    columns_to_drop = ["PERCENT ALLOCATED", "Family income in the past 12 months",\
                       "Nonfamily income in the past 12 months"]
    df_zip_income_transposed.drop(columns=columns_to_drop, inplace=True)

    df_zip_income_transposed.index.name = "Zipcode"
    return df_zip_income_transposed

def clean_store_income_data():
    """
    Step 2: clean up the 2021 Income by ZIP data and save it to a csv file.
    """
    df_zip_income = import_income("NYC_income_by_zip_2021_untransposed_truncated.csv")
    df_zip_income.to_csv("NYC_Income_Brackets_by_ZIP_cleaned.csv", index=True)

def main():
    """
    main function
    """
    # clean_store_ahs_data()
    clean_store_income_data()

if __name__ == "__main__":
    main()
