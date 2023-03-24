"""
Name: Ze Hong Wu
Email: zehong.wu@macaulay.cuny.edu
Resources:
Pandas documentation for all manner of debugging help
Title: -
URL: -

I will be using this space to put down some notes about my coding decisions.

Some of the functions store data into .csv files.
This is so that I do not have to clean the data all over again
and can instead start with some of the work already done.
You can un-comment all of the functions calls in main()
to do everything from start to finish in one go.
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def import_housing(csv_name: str, columns_to_use: dict)->pd.DataFrame:
    """
    This function takes two inputs:
    csv_name: the name of a .csv file to read.
    columns_to_use: a list of columns to keep.

    The data in the .csv file is read into a DataFrame.\n
    If a valid list of columns is provided, only those columns will be kept.\n
    The DataFrame is then passed to impute_housing().

    Returns an imputed version of the DataFrame.
    """
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

    Returns postcode if it is not empty, or the ZIP corresponding to boro otherwise.\n
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

def impute_housing(df: pd.DataFrame)->pd.DataFrame:
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

    The imputing will be done "manually" (unique code for every column).\n
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
    # 3 places after the decimal should be enough precision here
    df["Percent"] = df["Percent"].apply(lambda percent: round(percent, 3))
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
                        "Very Low Income Units", "Low Income Units", "Moderate Income Units",\
                        "Middle Income Units", "All Counted Units", "Total Units"]
    # print("Before import")
    # print(desired_columns)
    df_housing = import_housing("Affordable_Housing_Production_by_Building.csv", desired_columns)

    # saving intermediate work to .csv files
    # to skip earlier work in later sections
    # to do everything in one go, cmment out all save lines
    df_housing.to_csv("AHP_by_Building_cleaned.csv", index=False)

    # df_housing = pd.read_csv("AHP_by_Building_cleaned.csv")
    # print(df_housing)

def strip_letters(index: str)->str:
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
    # Removes a stray 5 that slips into output
    return output[1:]

def strip_punctuation(value: str)->str:
    """
    This function takes one input:
    value: a number-like value from a DataFrame

    Returns a version of value without any percent signs.

    Example:
    input: '22.5%'
    Returns: '22.5'
    """
    if pd.isna(value) or not isinstance(value, str):
        return value
    output = ""

    for char in value:
        if ("0" <= char <= "9") or char == ".":
            output += char

    if output == "":
        output = "0"
    return output

def strip_quotations(column: str)->str:
    """
    This function takes one input:
    column: a column name from a DataFrame

    Returns a version of column without quotations.
    """
    if pd.isna(column) or not isinstance(column, str):
        return column
    output = ""

    for char in column:
        if char != "\"":
            output += char
    return output

def impute_income(df: pd.DataFrame)->pd.DataFrame:
    """
    This function takes one input:
    df: a DataFrame object containing Income by ZIP code data.

    The DataFrame undergoes the following changes:
    - Remove all columns that isn't an estimate of number of households
    - Rename columns to a more readable format
    - Drop some columns that contain no useful data
    - Set index name to "Zipcode"
    - Convert columns with dtype "object" to "int" or "float" when appropriate
    - Discard rows with a "Total" value of 0

    Returns the imputed DataFrame.
    """
    # drop undesired columns
    drop_idx_list = []
    for idx in df.index:
        if "!!Households!!" not in idx:
            drop_idx_list.append(idx)
    df.drop(index=drop_idx_list, inplace=True)

    # rename indices
    rename_index_dict = {}
    for idx in df.index:
        if idx == "New York city, New York!!Households!!Estimate":
            rename_index_dict[idx] = "10000"
        else:
            rename_index_dict[idx] = strip_letters(idx)
    df.rename(index=rename_index_dict, inplace=True)

    # rename columns
    rename_column_dict = {}
    for col in df.columns:
        rename_column_dict[col] = strip_quotations(col.strip())
    df.rename(columns=rename_column_dict, inplace=True)

    # drop useless columns
    columns_to_drop = ["PERCENT ALLOCATED", "Family income in the past 12 months",\
                       "Nonfamily income in the past 12 months"]
    df.drop(columns=columns_to_drop, inplace=True)

    df.index.name = "Zipcode"

    # convert 'object' dtypes to 'int' or 'float'
    # also discard zips that contain no residents
    for col in df.columns:
        df[col] = df[col].apply(strip_punctuation)
        df = df[df["Total"] != 0]

        if col in ["Zipcode", "Total", "Median income (dollars)", "Mean income (dollars)"]:
            df[col] = df[col].astype(int)
        else:
            df[col] = df[col].astype(float)

    # a more descriptive column name
    df.rename(columns={"Total": "Total Households"}, inplace=True)

    # turning the percent columns into easier to work with decimals between 0 and 1
    rescale_column_list = ["Less than $10,000",
                           "$10,000 to $14,999",
                           "$15,000 to $24,999",
                           "$25,000 to $34,999",
                           "$35,000 to $49,999",
                           "$50,000 to $74,999",
                           "$75,000 to $99,999",
                           "$100,000 to $149,999",
                           "$150,000 to $199,999",
                           "$200,000 or more"]
    for col in rescale_column_list:
        df[col] = df[col].apply(lambda percent: round(percent/100, 3))

    return df[df["Total Households"] != 0]

def import_income(csv_name: str)->pd.DataFrame:
    """
    This function takes one input:
    csv_name: the name of a .csv file to read.

    The data in the .csv file is read into a DataFrame and then transposed.\n
    The DataFrame is then passed to impute_income().

    Returns an imputed version of the modified DataFrame.
    """
    df_zip_income = pd.read_csv(csv_name, index_col=[0])
    #print(df_zip_income)
    # for column_label in df_zip_income:
    #     print("Printing a column label")
    #     print(column_label)
    df_zip_income = df_zip_income.transpose()
    #print(df_zip_income)

    return impute_income(df_zip_income)

def clean_store_income_data():
    """
    Step 2: clean up the 2021 Income by ZIP data and save it to a csv file.
    """
    df_zip_income = import_income("NYC_income_by_zip_2021_untransposed.csv")
    df_zip_income.to_csv("NYC_Income_Brackets_by_ZIP_cleaned.csv", index=True)

def placeholder():
    """
    Docstring
    """

def add_data_to_income():
    """
    Step 3: add to the Income by ZIP csv columns of possibly useful data.

    The data produced by Steps 1 and 2 are loaded into DataFrames.\n
    The Income by ZIP DataFrame gains the following columns:
    - Total Affordable Housing: number of affordable housing units present in each zip code.
    - Housing to Household Ratio: assuming every affordable housing unit is occupied, [num] of
    the population of this zip will live in an affordable housing unit.
    - [bracket] Households: number of households that fall under a given percent based bracket
    - [bracket] H/H ratio: percent of households in that bracket that could receive affordable
    housing, assuming a random and fair assignment of housing to households

    The DataFrame is then saved to a new .csv file.
    """
    print("Beginning Step 3: adding data to income")
    df_zip_income = pd.read_csv("NYC_Income_Brackets_by_ZIP_cleaned.csv")
    df_housing = pd.read_csv("AHP_by_Building_cleaned.csv")

    def extract_housing_sum(zipcode: int, unit_type: str)->int:
        """
        This function takes two inputs:
        zipcode: a zip code.
        unit_type: name of a DataFrame column corresponding to a type of affordable housing.

        An internal function to do some math.\n
        This workaround avoids a "Can only compare identically labeled Series objects"
        value error that appears if you try to run the commented out code.

        I chose to define this function inside of add_data_to_income() because
        this function needs access to df_housing and I would much rather not pass
        df_housing to it every time it gets called (and take up unnecessary memory).
        """
        return df_housing[df_housing["Postcode"] == zipcode][unit_type].sum()

    def convert_percent_to_raw(zipcode: int, percent_bracket_name: str)->int:
        """
        This function takes two inputs:
        zipcode: a zip code.
        percent_bracket_name: DataFrame column name corresponding to a type of affordable housing.

        Another internal function.
        This function hopes to derive an approximate number for the number of people who fall
        into one of the % based income brackets in the AHP csv.

        The math goes as follows:
        - Take in a zipcode and the name of a percent income bracket.
        - Identify that zip's median and the percent value correlating to the bracket name.
            - Example: "Extremely Low Income Units" will return a value of 0.3.
        - Multiply the two to get an `upper raw income limit` for that percent bracket for that zip.
        - Iterate through each raw income bracket for that zip from lowest to highest.
        - For each column, derive the `max income` of its bracket.
            - Example: "$10000 to $14999" will return a max of 15000.
        - See if the raw income bracket partially or fully falls below `upper raw income limit`.
            - If it fully falls under limit: += the entire bracket population to an output value.
            - If it partially falls under limit: += household count * (`raw limit` / `max income`).
            - End the loop by then, since all remaining brackets will not fall under the limit.
        - Return the output value.

        Example: given a ZIP of 12345 and a percent bracket of "Extremely Low Income Units",
        return a value that denotes "this many people in this zip qualify for Extremely Low category".
        """
        percent_income_dict = {"Extremely Low Income Units":0.3,
                               "Very Low Income Units":0.5,
                               "Low Income Units":0.8,
                               "Moderate Income Units":1.2,
                               "Middle Income Units":1.65}
        max_income_dict = {"Less than $10,000":10000,
                               "$10,000 to $14,999":15000,
                               "$15,000 to $24,999":25000,
                               "$25,000 to $34,999":35000,
                               "$35,000 to $49,999":50000,
                               "$50,000 to $74,999":75000,
                               "$75,000 to $99,999":100000,
                               "$100,000 to $149,999":150000,
                               "$150,000 to $199,999":200000,
                               "$200,000 or more":500000}
        # Chain indexing returns a Series of 1 thing, so the iloc is necessary
        median = (df_zip_income[df_zip_income["Zipcode"] == zipcode]\
                  ["Median income (dollars)"]).iloc[0]
        percent_multiplier = percent_income_dict[percent_bracket_name]
        upper_raw_income = median * percent_multiplier
        output = 0
        total_households = (df_zip_income[df_zip_income["Zipcode"] == zipcode]\
                            ["Total Households"]).iloc[0]

        # This system is imperfect as it over-counts people from lower brackets.
        # This will be fixed outside this inner function.
        for col in max_income_dict.items():
            household_percent = df_zip_income[df_zip_income["Zipcode"] == zipcode][col[0]].iloc[0]
            if col[1] < upper_raw_income:
                output += int(household_percent * total_households)
            else:
                portion = total_households * (upper_raw_income / col[1])
                output += int(household_percent * portion)
                break
        return output

    # ============================================================================================
    # Helpers end here, actual coding begins here

    df_zip_income["Total Affordable Housing"] = \
        df_zip_income["Zipcode"].apply\
            (lambda zipcode: extract_housing_sum(zipcode,"All Counted Units"))
    df_zip_income["Housing to Households Ratio"] =\
        df_zip_income["Total Affordable Housing"] / df_zip_income["Total Households"]
    df_zip_income["Housing to Households Ratio"] = \
        df_zip_income["Housing to Households Ratio"].apply(lambda ratio: round(ratio, 3))

    # "Can only compare identically labeled Series objects" error appears if you run this:
    # df_zip_income["Total Affordable Housing"] = \
    #     df_housing[df_housing["Postcode"] == df_zip_income["Zipcode"]]\
    #         ["All Counted Units"].sum()

    new_column_names = {"Extremely Low Income Units":"Extremely Low Income Households",
                        "Very Low Income Units":"Very Low Income Households",
                        "Low Income Units":"Low Income Households",
                        "Moderate Income Units":"Moderate Income Households",
                        "Middle Income Units":"Middle Income Households"}
    for col in new_column_names.items():
        df_zip_income[col[1]] =\
            df_zip_income["Zipcode"].apply\
                (lambda zipcode: convert_percent_to_raw(zipcode,col[0]))

    # convert_percent_to_raw() overcounts households for 4 of the 5 percent brackets
    # this subtracts the over-counted households to yield more accurate household counts
    df_zip_income["Middle Income Households"] -= df_zip_income["Moderate Income Households"]
    df_zip_income["Moderate Income Households"] -= df_zip_income["Low Income Households"]
    df_zip_income["Low Income Households"] -= df_zip_income["Very Low Income Households"]
    df_zip_income["Very Low Income Households"] -= df_zip_income["Extremely Low Income Households"]

    # Adding columns of "total number of housing for this bracket"
    housing_column_names = {"Extremely Low Income Units":"Extremely Low Housing",
                            "Very Low Income Units":"Very Low Housing",
                            "Low Income Units":"Low Housing",
                            "Moderate Income Units":"Moderate Housing",
                            "Middle Income Units":"Middle Housing"}
    for col in housing_column_names.items():
        df_zip_income[col[1]] = \
            df_zip_income["Zipcode"].apply\
                (lambda zipcode: extract_housing_sum(zipcode, col[0]))

    # Adding columns of "enough housing for x% of this income bracket".
    # "H/H Ratio" is short for Housing / Household Ratio.
    housing_household_names = [["Extremely Low H/H Ratio",
                                "Extremely Low Housing",
                                "Extremely Low Income Households"],
                                ["Very Low H/H Ratio",
                                 "Very Low Housing",
                                 "Very Low Income Households"],
                                ["Low H/H Ratio",
                                 "Low Housing",
                                 "Low Income Households"],
                                ["Moderate H/H Ratio",
                                 "Moderate Housing",
                                 "Moderate Income Households"],
                                ["Middle H/H Ratio",
                                 "Middle Housing",
                                 "Middle Income Households"]]
    for name_dict in housing_household_names:
        df_zip_income[name_dict[0]] = \
            df_zip_income[name_dict[1]] / df_zip_income[name_dict[2]]
        df_zip_income[name_dict[0]] = df_zip_income[name_dict[0]].apply\
            (lambda number: round(number, 3))

    print(df_zip_income)
    df_zip_income.to_csv("NYC_Income_by_ZIP_Expanded.csv", index=False)

def draw_graphs():
    """
    Step 4: draw stuff.
    """
    print("Beginning Step 4: drawing graphs")
    df_zip_income = pd.read_csv("NYC_Income_by_ZIP_expanded.csv")
    df_housing = pd.read_csv("AHP_by_Building_cleaned.csv")

    # scatter plot: area median income vs. Housing to Households Ratio
    xcol = df_zip_income[df_zip_income["Housing to Households Ratio"] > 0]\
                        ["Median income (dollars)"]
    ycol = df_zip_income[df_zip_income["Housing to Households Ratio"] > 0]\
                        ["Housing to Households Ratio"]
    plt.scatter(xcol,
                ycol,
                c="Blue")
    plt.title("Area income and housing availability, by ZIP")
    plt.xlabel("Median income (US Dollars)")
    plt.ylabel("Housing to Household Ratio")
    plt.show()

def main():
    """
    Main function.
    Each function call below correlates to a "step" of this project.

    Plans for next steps:
    For every zip in income data:
    scour through ahs data to find all rows of buildings available by 2021
    defined as (end date before 2021)

    using these rows, derive these data:
    - number of affordable housing units available
    - ratio of affordable housing units divided by total households
    - number of people
    - estimated number of households falling into various income brackets
        - "extremely low income", "very low income", "low income", "moderate income"...
    - ratio for each of these income brackets

    insert this data into new rows of the income data df
    save this df to a new csv file

    figure out what to predict (x and y values)
    possible x and y values (for a given zip, or for all of NYC):
    - x: number of in-need households
    - y: number of affordable housing
    figure out how to draw choropleth graphs and other graphs as noted in project proposal
    """
    print("Beginning project steps")
    # clean_store_ahs_data()
    # clean_store_income_data()
    # add_data_to_income()
    draw_graphs()

if __name__ == "__main__":
    main()
