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
import folium
import geojson
from sklearn import linear_model
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import PolynomialFeatures

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
    This function takes one input:
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
    print("Beginning step 1: importing housing data")
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
    index: a DataFrame index containing a zip code.

    Returns the zip code stored in the index.

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
    - [bracket] Housing: number of affordable housing intended for this percent income bracket
    - [bracket] H/H ratio: percent of households in that bracket that could receive affordable
    housing, assuming a random and fair assignment of housing to households
    - Borough: the borough for a given zip code.

    The DataFrame is then saved to a new .csv file.
    """
    print("Beginning Step 3: adding data to income")
    df_zip_income = pd.read_csv("NYC_Income_Brackets_by_ZIP_cleaned.csv")
    df_housing = pd.read_csv("AHP_by_Building_cleaned.csv")
    df_zips_boros = pd.read_csv("nyc_zipcodes_and_boros.csv")
    df_zips_boros.rename(columns={"ZipCode":"Zipcode"}, inplace=True)

    def extract_boro(zipcode: int)->str:
        """
        This function takes one input:
        zipcode: a zip code.
    
        Returns a boro given a zipcode.
        Self note: Had to manually add a couple of zipcodes to nyc_zips_and_boros.csv.
        """
        print("Zipcode is: ", zipcode)
        if zipcode == 10000:
            return "New York"
        output_zip = df_zips_boros[df_zips_boros["Zipcode"]==zipcode]["Borough"]
        if output_zip.empty:
            return "Other"
        #print(output_zip)
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

    df_zip_income = df_zip_income[df_zip_income["Median income (dollars)"] != 0]
    # This line removes one boro that has like 40 households residing in it and a median income of 0
    # Basically an irrelevant data point
    df_zip_income["Borough"] = df_zip_income["Zipcode"].apply(extract_boro)
    print(df_zip_income)
    df_zip_income.to_csv("NYC_Income_by_ZIP_Expanded.csv", index=False)

def get_zip_boro_csv():
    """
    An obsolete function.
    Initially I planned to create my own Zipcode-Borough CSV using the affordable housing CSV.
    However it was missing quite a few zip codes so I dropped this idea.
    """
    print("Beginning Step 2.5: building a custom ZIP-Borough CSV")
    df_housing = pd.read_csv("AHP_by_Building_cleaned.csv", usecols=["Borough","Postcode"])
    #print(df_housing)
    df_housing.rename(columns={"Postcode":"Zipcode"}, inplace=True)
    df_housing.drop_duplicates(subset=["Zipcode"], inplace=True)
    df_housing.to_csv("zips_and_boros.csv", index=False)

def draw_graphs():
    """
    Step 4: draw stuff.
    """
    print("Beginning Step 4: drawing graphs")
    df_zip_income = pd.read_csv("NYC_Income_by_ZIP_expanded.csv")
    df_housing = pd.read_csv("AHP_by_Building_cleaned.csv")

    def reduce_total_housing_outlier(housing: int)->int:
        """
        A single-use function to fix an issue with the NYC column having a value of 200k
        for Total Affordable Housing and thus ruining the Seaborn scatterplot dot size scaling
        """
        if housing > 50000:
            return housing/10
        return housing

    # scatter plot: area median income vs. Housing to Households Ratio
    xcol = df_zip_income["Median income (dollars)"]
    ycol = df_zip_income["Housing to Households Ratio"]
    plt.scatter(xcol,
                ycol,
                c="Blue")
    plt.title("Area income and housing availability, by ZIP")
    plt.xlabel("Median income (US Dollars)")
    plt.ylabel("Housing to Household Ratio")
    plt.show()

    df_zip_income_mod = df_zip_income
    df_zip_income_mod["Total Affordable Housing"] = \
        df_zip_income_mod["Total Affordable Housing"].apply(reduce_total_housing_outlier)
    sns.scatterplot(
        data=df_zip_income_mod,
        x="Median income (dollars)",
        y="Housing to Households Ratio",
        hue="Borough",
        size="Total Affordable Housing",
        sizes=(20,200)
    )
    plt.savefig("NYC_Housing_to_Household_by_ZIP.png")
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
    draw_choropleth("Housing to Households Ratio", "nyc_zips_choropleth.html", df_zip_income)

    # because a few outliers are making it hard to show the finer details of the other zips:
    # a second choropleth map that excludes these outliers
    draw_choropleth("Housing to Households Ratio", "nyc_zips_choropleth_2.html",\
                    df_zip_income[df_zip_income["Housing to Households Ratio"] < 0.5])

    # a choropleth on average income
    draw_choropleth("Median income (dollars)", "nyc_zips_income_choropleth.html", df_zip_income)

def predict():
    """
    Step 5: predict values.

    Work for this function is lifted from several functions from Assignment 7.
    """
    print("Beginning Step 5: attempting to do predictive modeling")
    df_zip_income = pd.read_csv("NYC_Income_by_ZIP_expanded.csv")
    #df_zip_income = df_zip_income[df_zip_income["Housing to Households Ratio"] < 0.5]
    df_zip_income["Housing to Households Ratio"] = \
        df_zip_income["Housing to Households Ratio"].apply(lambda ratio: ratio*100)
    x_train,x_test,y_train,y_test =\
        train_test_split(df_zip_income["Median income (dollars)"],\
                         df_zip_income["Housing to Households Ratio"],
                         test_size=0.25,
                         random_state=10000)

    print("contents of xtrain and ytrain:")
    print(x_train)
    print(y_train)
    # taken from fit_poly() of assignment 7
    degree_error_combo = [-1, 2**32]
    for degree in range(1,6):
        poly = PolynomialFeatures(degree=degree, include_bias=False)
        poly_features = poly.fit_transform(x_train.to_frame())

        #print("poly features:")
        #print(poly_features)
        reg = linear_model.LinearRegression().fit(poly_features, y_train)
        y_predicted = reg.predict(poly_features)
        error = mean_squared_error(y_train, y_predicted)
        if error < degree_error_combo[1]:
            degree_error_combo[0] = degree
            degree_error_combo[1] = error

    print("Best degree and error:")
    print(degree_error_combo[0])
    print(degree_error_combo[1])

    # taken from fit_model() of assignment 7
    poly = PolynomialFeatures(degree=degree_error_combo[0], include_bias=False)
    poly_features = poly.fit_transform(x_train.to_frame())
    my_reg = linear_model.LassoCV().fit(poly_features, y_train)

    x_test_poly = poly.fit_transform(x_test.to_frame())
    y_predicted = my_reg.predict(x_test_poly)

    print("my_reg coefficients and intercept:")
    print(my_reg.coef_)
    print(my_reg.intercept_)

    print("y_predicted and y_test:")
    print(y_predicted)
    print(y_test)

    print("MSE and r2 scores for regression:")
    print(mean_squared_error(y_predicted, y_test))
    print(r2_score(y_predicted, y_test))

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
    )
    plt.plot(x_test, y_predicted)
    plt.show()

def main():
    """
    Main function.
    Each function call below correlates to a "step" of this project.

    Plans for next steps:

    figure out what to predict (x and y values)
    possible x and y values (for a given zip, or for all of NYC):
    - x: number of in-need households
    - y: number of affordable housing
    figure out how to draw choropleth graphs and other graphs as noted in project proposal
    """
    print("Beginning project steps")
    #clean_store_ahs_data()
    #clean_store_income_data()
    #get_zip_boro_csv()
    #add_data_to_income()
    #draw_graphs()
    predict()

if __name__ == "__main__":
    main()
