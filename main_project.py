"""
Name: Ze Hong Wu
Email: zehong.wu@macaulay.cuny.edu
Resources:
Pandas documentation for all manner of debugging help
Other resources cited in COPYRIGHT.txt
Link to GitHub repo containing this file and COPYRIGHT.txt:
https://github.com/JasonWu00/39542-research-project
Title: Affordable Housing in NYC: Distribution and Availability Over Time
URL: https://jasonwu00.github.io/39542-research-project/

IMPORTANT INFO

The reasona all of the Python code is in one file is due to project requirements
issued by the instructors (something involving the limitations of the submission portal).

I opted to save data produced by some of the project steps into .csv files
so that I can pick up from existing work as I test my work
and so that I can inspect them more closely if I want.
This means that some of the project steps can be run on separate calls of this file
so long as the required .csv files are present.

Copyright names will be updated once the course is over
and I am not constrained by official roster name issues.

Copyright (C) 2023 Ze Hong Wu

This program is free software: you can redistribute it and/or modify it under the
terms of the GNU General Public License as published by the Free Software Foundation,
either version 3 of the License, or (at your option) any later version.
This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
See the GNU General Public License for more details.
You should have received a copy of the GNU General Public License along with this program.
If not, see <https://www.gnu.org/licenses/>.
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import folium
import geojson
from sklearn import linear_model
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import PolynomialFeatures

def import_housing(csv_name: str, columns_to_use: dict)->pd.DataFrame:
    """
    This function takes two inputs:
    csv_name: the name of an Affordable Housing in NYC .csv file to read.
    columns_to_use: a list of columns to keep.

    The data in the .csv file is read into a DataFrame.
    If a valid list of columns is provided, only those columns will be kept.
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

def impute_housing(df: pd.DataFrame)->pd.DataFrame:
    """
    This function takes one input:
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

    df["Postcode"] = df.apply(lambda row: choose_postcode(row["Postcode"], row["Borough"]),
                              axis=1)
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

def clean_store_ahs_data(import_name: str, savefile_name: str):
    """
    Step 1: clean up the Affordable Housing data and save it to a csv file.

    This function takes two inputs:
    import_name: name of a Affordable Housing .csv file to import data from.
    savefile_name: name of a .csv file to save cleaned data to.

    This function imports the given Affordable Housing data set, processes its contents,
    and saves it to another filename. Most of the actual work occurs in import_housing.
    """
    print("Beginning step 1: importing Affordable Housing data")
    desired_columns = [ "Project ID", "Project Start Date", "Project Completion Date",\
                        "Borough", "Postcode", "Census Tract",\
                        "NTA - Neighborhood Tabulation Area",\
                        "Building Completion Date", "Reporting Construction Type",\
                        "Extended Affordability Only", "Extremely Low Income Units",\
                        "Very Low Income Units", "Low Income Units", "Moderate Income Units",\
                        "Middle Income Units", "All Counted Units", "Total Units"]
    # print("Before import")
    # print(desired_columns)
    df_housing = import_housing(import_name, desired_columns)

    # saving intermediate work to .csv files
    # to skip earlier work in later sections
    df_housing.to_csv(savefile_name, index=False)

    # df_housing = pd.read_csv("AHP_by_Building_cleaned.csv")
    # print(df_housing)

def strip_letters(index: str)->str:
    """
    This function takes one input:
    index: a string containing a zip code.

    Returns the zip code without the extra letters.

    Example:
    input: 'ZCTA5 10101 Estimate'
    Returns: '10101'
    """
    output = ""
    for char in index:
        if "0" <= char <= "9":
            output += char
    # Removes the stray 5 that slips into output
    return output[1:]

def strip_punctuation(value: str)->str:
    """
    This function takes one input:
    value: a string containing a percentage value from a DataFrame

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

def impute_income(df: pd.DataFrame, year: int)->pd.DataFrame:
    """
    This function takes two inputs:
    df: a DataFrame object containing Income by ZIP code data.
    year: the year the data corresponds to.

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

    # older versions of the income by zip files has percent imputed instead of percent allocated
    # this is a hot-fix to deal with this without modifying other lines of code
    if year <= 2015:
        df.rename(columns={"PERCENT IMPUTED":"PERCENT ALLOCATED"}, inplace=True)

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

def import_income(csv_name: str, year: int)->pd.DataFrame:
    """
    This function takes two inputs:
    csv_name: the name of an Income by ZIP .csv file to read.
    year: the year the file's data corresponds to.

    The data in the .csv file is read into a DataFrame and then transposed.
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

    return impute_income(df_zip_income, year)

def clean_store_income_data(import_name: str, savefile_name: str, year: int):
    """
    Step 2: clean up the 2021 Income by ZIP data and save it to a csv file.

    This function takes in three inputs:
    import_name: the name of an Income by ZIP .csv file to read from.
    savefile_name: the name of a .csv file to save cleaned income data to.
    year: the year the Income by ZIP data corresponds to.
    """
    print("Beginning Step 2: cleaning Income by ZIP data")
    df_zip_income = import_income(import_name, year)
    df_zip_income.to_csv(savefile_name, index=True)

def add_data_to_income(import_name: str, savefile_name: str, year: int):
    """
    Step 3: add to the Income by ZIP csv columns of possibly useful data.

    This function takes three inputs:
    import_name: the name of a Income by ZIP csv file to read from.
    savefile_name: the name of a csv file to save modified Income by ZIP data to.
    year: a cutoff that tells the code to drop all rows with completion years after it.

    The data produced by Steps 1 and 2 are loaded into DataFrames.

    The Income by ZIP DataFrame gains the following columns:
    - Total Affordable Housing: number of affordable housing units present in each zip code.
    - Housing to Household Ratio: assuming every affordable housing unit is occupied, [%] of
    the population of this zip will live in an affordable housing unit.
    - [bracket] Households: number of households that fall under a given percent based bracket
    - [bracket] Housing: number of affordable housing intended for this percent income bracket
    - [bracket] H/H ratio: percent of households in that bracket that could receive affordable
    housing designated for their bracket, assuming a fair assignment of housing to households
    - Borough: the borough for a given zip code.

    The DataFrame is then saved to a new .csv file.
    """
    print("Beginning Step 3: adding data to Income by ZIP data")
    df_zip_income = pd.read_csv(import_name)
    # hard-coded affordable housing csv name, because I am only working with one such data set.
    df_housing = pd.read_csv("AHP_by_Building_cleaned.csv")
    # same thing with zips and boros
    df_zips_boros = pd.read_csv("nyc_zipcodes_and_boros.csv")
    df_zips_boros.rename(columns={"ZipCode":"Zipcode"}, inplace=True)

    # this line filters out housing projects not complete after the specified year
    # but keeps preservation projects since those projects must be working on existing units
    df_housing = df_housing[(df_housing["Project End Year"] <= year) |
                            (df_housing["Reporting Construction Type"] == "Preservation")]

    def extract_boro(zipcode: int)->str:
        """
        This function takes one input:
        zipcode: a zip code.
    
        Returns a boro given a zipcode.
        Self note: Had to manually add a couple of zipcodes to nyc_zips_and_boros.csv.
        """
        #print("Zipcode is: ", zipcode)
        if zipcode == 10000:
            return "New York"
        output_zip = df_zips_boros[df_zips_boros["Zipcode"]==zipcode]["Borough"]
        if output_zip.empty:
            return "Other"
        #print(output_zip)
        # output_zip is a series containing 1 thing
        # iloc[0] returns the only thing stored inside (the borough value)
        return output_zip.iloc[0]

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
        if zipcode == 10000:
            return df_housing[unit_type].sum()
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

        Example: given a ZIP of 12345 and a percent bracket of "Low Income Units",
        return a value that denotes "this many people in this zip qualify for Low Income category".
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

    df_zip_income = df_zip_income[df_zip_income["Median income (dollars)"] != 0]
    # This line removes one boro that has like 40 households residing in it and a median income of 0
    # Basically an irrelevant data point
    df_zip_income["Borough"] = df_zip_income["Zipcode"].apply(extract_boro)
    #print(df_zip_income)
    df_zip_income.to_csv(savefile_name, index=False)

def draw_graphs(income_csv: str, choropleth_name: str, year: int):
    """
    Step 4: draw graphs relevant to the project.

    This function takes in 3 inputs:
    income_csv: name of a Income by ZIP csv to read.
    choropleth_name: name that the folium choropleth map should be saved to.
    year: the year corresponding to the income csv, to be used in naming some things.
    """
    print("Beginning Step 4: drawing graphs")
    df_zip_income = pd.read_csv(income_csv)

    # scatter plot: area median income vs. Housing to Households Ratio
    # These lines fix an issue where the NYC column has a Total Affordable Housing value of
    # 200k and ruins the Seaborn scatterplot dot size scaling system.
    df_zip_income_mod = df_zip_income
    df_zip_income_mod["Total Affordable Housing"] = \
        df_zip_income_mod["Total Affordable Housing"].apply(lambda housing: min(housing, 50000))

    sns.scatterplot(
        data=df_zip_income_mod,
        x="Median income (dollars)",
        y="Housing to Households Ratio",
        hue="Borough",
        size="Total Affordable Housing",
        sizes=(20,200)
    ).set(title="Housing to Household Ratios per ZIP")
    plt.savefig(f"visualizations/NYC_Housing_to_Household_by_ZIP_{year}.png")
    plt.show()

    zips = None
    with open("nyc-zip-code-tabulation-areas-polygons.geojson",mode="r",encoding="utf_8") as zips:
        zips = geojson.load(zips)

    def draw_choropleth(column: str, filename: str, df: pd.DataFrame)->int:
        """
        This function takes two inputs:
        column: the name of a DataFrame column.
        filename: the name of a file to save the map to.

        Draws a Choropleth map using the given column and stores it in the given filename.
        """
        choropleth_map = folium.Map(location=[40.7, -73.9])
        folium.Choropleth(
            geo_data=zips,
            name="choropleth",
            data=df,
            columns=["Zipcode", column],
            key_on="feature.properties.postalCode",
            legend_name="Housing to Household Ratio",
            fill_color="YlOrRd",
            fill_opacity=0.75

        ).add_to(choropleth_map)
        folium.LayerControl().add_to(choropleth_map)
        choropleth_map.save(filename)
        return 0
    # =======================================================
    # based on the examples on the Folium Quick Start webpage
    # draw_choropleth("Housing to Households Ratio", "nyc_zips_choropleth.html", df_zip_income)

    # because a few outliers are making it hard to show the finer details of the other zips:
    # a second choropleth map that excludes these outliers
    draw_choropleth("Housing to Households Ratio", choropleth_name,\
                    df_zip_income[df_zip_income["Housing to Households Ratio"] < 0.5])

    # a choropleth on average income
    draw_choropleth("Median income (dollars)",
                    f"visualizations/nyc_zips_income_{year}_choropleth.html",
                    df_zip_income)

def find_best_degree(x_train, y_train):
    """
    This function takes in two inputs:
    x_train: a training set produced by train_test_split.
    y_train: a training set produced by train_test_split.

    Using these two training sets, return the best degree for a polynomial regression
    and the MSE for that degree.
    Taken from fit_poly() of assignment 7.
    """
    # stores paired values of best degree found so far and its corresponding error value
    degree_error_combo = [-1, 2**32]
    # if the current regression degree is better than the prev one by less than this %
    # then it is considered "good enough".
    min_error_threshold = 0.05
    for degree in range(1,12):
        poly = PolynomialFeatures(degree=degree)
        poly_features = poly.fit_transform(x_train.to_frame())

        #print("poly features:")
        #print(poly_features)
        reg = linear_model.LinearRegression().fit(poly_features, y_train)
        y_predicted = reg.predict(poly_features)
        error = mean_squared_error(y_train, y_predicted)
        print(f"Testing linear regression model of degree {degree}")
        print("Mean Squared Error is: ", error)
        if error < degree_error_combo[1]:
            if 1.0 - abs(error / degree_error_combo[1]) > min_error_threshold:
                degree_error_combo[0] = degree
                degree_error_combo[1] = error
            else:
                break
        else:
            break
    # for loop ends here
    return degree_error_combo[0], degree_error_combo[1]

def draw_regression(df: pd.DataFrame,
                    x_test: list,
                    y_pred: list,
                    scatter_name: str,
                    regression_name: str,
                    year: int):
    """
    Step 5.5: draw regression graphs.

    This function takes in 5 inputs:
    df: a DataFrame containing x and y columns to source scatterplot points from.
    x_test: list of x-values for the regression line.
    y_pred: list of y-values for the regression line.
    scatter_name: name of the scatterplot to be saved.
    regression_name: name of the regression graph to be saved.

    Using the inputs, this function draws a scatterplot with model prediction line
    and a regression scatterplot showing the error of the model relative to all data.
    The function then stores the two scatterplots using the given input names.
    """
    sns.scatterplot(
        data=df,
        x="Median income (dollars)",
        y="Housing to Households Ratio",
        hue="Borough",
        size="Total Affordable Housing",
        sizes=(20,200)
    ).set(title="Housing to Household Ratios per ZIP with regression line")
    plt.plot(x_test, y_pred, color="black")
    plt.savefig(scatter_name)
    plt.show()

    sns.scatterplot(
        data=df,
        x="Median income (dollars)",
        y="Predicted/Actual Error",
        #hue="Borough",
        #size="Total Affordable Housing",
        #sizes=(20,200)
    ).set(title=f"Regression graph for year {year}")
    plt.axhline(y=0, color="black")
    plt.savefig(regression_name)
    plt.show()

def predict(income_csv: str,
            scatterplot_name: str,
            regression_name: str,
            graphing: bool,
            year: int):
    """
    Step 5: predict values.

    This function takes in 5 inputs:
    income_csv: name of a Income by ZIP data file to read from.
    scatterplot_name: name of a scatter plot to be generated.
    regression_name: name of a regression plot to be generated.
    graphing: tells the function if it should draw graphs.
    year: year corresponding to the income by ZIP data file.

    This function tries to create a linear regression model to predict
    a zipcode's H/H ratio based on its average median income.

    Work for this function is lifted from several functions from Assignment 7.
    """
    print("Beginning Step 5: attempting to do predictive modeling")
    print(f"Data set to be processed: {income_csv}")
    df_zip_income = pd.read_csv(income_csv)

    x_train,x_test,y_train,y_test =\
        train_test_split(df_zip_income["Median income (dollars)"],\
                         df_zip_income["Housing to Households Ratio"],
                         test_size=0.25,
                         random_state=10000)

    # taken from fit_poly() of assignment 7

    best_degree, best_error = find_best_degree(x_train, y_train)
    print("Best degree and error:")
    print(best_degree)
    print(best_error)

    # taken from fit_model() of assignment 7

    poly = PolynomialFeatures(degree=best_degree)
    poly_features = poly.fit_transform(x_train.to_frame())
    my_reg = linear_model.LassoCV(cv=5).fit(poly_features, y_train)

    x_test_poly = poly.fit_transform(x_test.to_frame())
    y_predicted = my_reg.predict(x_test_poly)


    # print("my_reg coefficients and intercept:")
    # print(my_reg.coef_)
    # print(my_reg.intercept_)

    # print("diagnostics: get params")
    # print(my_reg.get_params())

    # print("y_predicted and y_test:")
    # print(y_predicted)
    # print(y_test)

    print("MSE and r2 scores for this regression:")
    print(mean_squared_error(y_test, y_predicted))
    print(r2_score(y_test, y_predicted))

    # "deals with" outliers by artificially reducing them to 50000
    # the scatter plot generated using the data sizes each dot based on total affordable housing
    # this ensures that the "all of NYC" dot doesn't skew the dot sizes too greatly
    df_zip_income["Total Affordable Housing"] = \
        df_zip_income["Total Affordable Housing"].apply(lambda housing: min(housing, 50000))

    # calculating error of this regression so it can be plotted
    x_test_poly_all = poly.fit_transform(df_zip_income["Median income (dollars)"].to_frame())
    y_predicted_all = my_reg.predict(x_test_poly_all)

    df_zip_income["Predicted H/H Ratio"] = y_predicted_all
    df_zip_income["Predicted H/H Ratio"].apply(lambda ratio: round(ratio, 3))
    df_zip_income["Predicted/Actual Error"] = \
        df_zip_income["Predicted H/H Ratio"] - \
            df_zip_income["Housing to Households Ratio"]

    if graphing:
        draw_regression(df_zip_income,
                        x_test,
                        y_predicted,
                        scatterplot_name,
                        regression_name,
                        year)

    # returning some x and y values to be graphed to show a particular year's predictions.
    # the x, y values are custom made to ensure the prediction line is smooth
    my_x_test = []
    for xval in range(0, 200000, 1000):
        my_x_test.append(xval)
    my_x_test_poly = poly.fit_transform(pd.Series(my_x_test).to_frame())
    my_y_predicted = my_reg.predict(my_x_test_poly)

    print("Predictive modeling step complete")
    print()

    return my_x_test,\
            my_y_predicted,\
            mean_squared_error(y_test, y_predicted),\
            r2_score(y_test, y_predicted)


def main():
    """
    Main function.
    Each function call below correlates to a "step" of this project.

    Plans for next steps:
    """
    print("Beginning project steps")

    # this only needs to be called once, since housing data for all years are all in one csv.
    clean_store_ahs_data("Affordable_Housing_Production_by_Building.csv",
                         "AHP_by_Building_cleaned.csv")

    # the 2 calls below will be repeated for every year-based zipcode income prediction.
    # Important: do not include margin of error in the raw csv files

    for year in range(2011, 2022):
        print(f"Cleaning and modifying data for year {year}")
        clean_store_income_data(f"raw_datasets/NYC_income_by_zip_{year}.csv",
                                f"processed_datasets/NYC_Income_by_ZIP_{year}_Cleaned.csv", year)
        add_data_to_income(f"processed_datasets/NYC_Income_by_ZIP_{year}_Cleaned.csv",
                           f"processed_datasets/NYC_Income_by_ZIP_{year}_Expanded.csv", year)

    # initializing a dict to turn into a df to store predictive model outputs for each year
    predictions_dict = {"Year": [0],
                        "xvals": [[1,2,3,4,5,6,7,8,9,0]],
                        "yvals": [[1,2,3,4,5,6,7,8,9,0]],
                        "MSE": [0.0],
                        "R2": [0.0]}
    predictions_df = pd.DataFrame.from_dict(predictions_dict)
    #print(predictions_df)

    # preliminary prediction on the 2021 data set and drawing a regression graph
    predict("processed_datasets/NYC_Income_by_ZIP_2021_Expanded.csv",
           "visualizations/NYC_Household_vs_Income_with_regression_2021.png",
           "visualizations/Regression_error_graph_2021.png", 2021, True)

    # making models for 2011 to 2021 data sets and retrieving the x and y values
    # for each model so that they can be all graphed at once

    # dictionary of years and corresponding line colors.
    # 2020 is in blue to highlight the fact that its model is weird and should be investigated
    line_colors_dict = {2021: "#ff0000",
                        2020: "#0000dd",
                        2019: "#bb0000",
                        2018: "#990000",
                        2017: "#880000",
                        2016: "#770000",
                        2015: "#660000",
                        2014: "#550000",
                        2013: "#330000",
                        2012: "#110000",
                        2011: "#000000"}

    sns.FacetGrid(pd.read_csv("processed_datasets/NYC_Income_by_ZIP_2021_expanded.csv"))
    plt.figure(figsize=(6,6))
    plt.ylim(0.0, 0.1)
    plt.title("Predictive models from 2011 (black) to 2021 (red)")
    plt.xlabel("Average Housing to Household Ratio")
    plt.ylabel("Area Median Income")

    for year in range(2011, 2022):
        x_test, y_predicted, mse, r2_val = \
        predict(f"processed_datasets/NYC_Income_by_ZIP_{year}_expanded.csv",
                f"visualizations/NYC_Household_vs_Income_with_regression_{year}.png",
                f"visualizations/Regression_error_graph_{year}.png", False, year)

        # add new row to end of predictions df with data on the model for each year
        # This code left commented out because I couldn't figure out if I wanted
        # to store a bunch of x-test and y-predicted lists, stick it in a .csv,
        # then try to read it back and not break the formatting.
        #predictions_df.loc\
            #[len(predictions_df.index)] =\
                #[year, x_test, y_predicted, mse, r2_val]

        # add regression line to graph
        plt.plot(x_test, y_predicted, color=line_colors_dict[year])
        # couldn't figure out a way to manipulate predictions_df to fit into sns
        # to neatly produce a bunch of lines based on x-vals, y-vals, and year
        # so instead here's a less elegant solution of adding each line individually

    plt.savefig("visualizations/NYC_Housing_vs_Income_2011-2021_predictions_overlaid.png")
    plt.show()

    # These lines are meant to investigate the 2020 values a little closer
    # becase the regression line for 2021 breaks the trend formed by the other reg lines.
    # See the "2011-2021 predictions" graph and line 837/838 comments for more context.
    # Previously they were for 2021 and produced the scatterplot with regression and
    # regression error graphs for that year.
    draw_graphs("visualizations/NYC_Income_by_ZIP_expanded.csv",
               "visualizations/nyc_zips_choropleth_2.html", 2020)
    predict("NYC_Income_by_ZIP_expanded.csv",
            "visualizations/NYC_Housing_Household_vs_Income_with_regression.png",
            "visualizations/Regression_error_graph.png", 2020, True)

    # after doing the cleaning and imputing for 2021, do the same for the other years

if __name__ == "__main__":
    main()
