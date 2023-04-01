# 39542-research-project
Author: (JasonWu00)[github.com/JasonWu00]

Optional research project for the CSCI 39542 "Introduction to Data Science" course.

This README is a work in progress and will be updated with more clarifying data once I find the time.

### Nature of Project
This is an optional research project offered by the instructors of CSCI 39542 "Introduction to Data Science" at Hunter College. The student does most of the work for the project (deciding project scope, collecting data sets, analyzing data sets, etc) independently with a small amount of instructor oversight.

### Purpose of Project
This specific project aims to make some observations on the availability of affordable housing in New York City in the last few years.

I intend to assess the following:
- the distribution of affordable housing in New York City, calculated per zip code
  - both in terms of raw housing numbers and housing as a proportion of in-need people
- the distribution of the affordable housing / in-need people disparity
- the change of this disparity over the course of several years

Note that I am not a professional in city planning or otherwise well-versed on the intricacies of affordable housing. The observations made in this project are not legal or policy advice and should not be taken as indisputable truth.

### File sourcing
The NYC Zip Codes GeoJSON file (`nyc-zip-code-tabulation-areas0polygons.geojson`) is from [this link](https://www.kaggle.com/datasets/saidakbarp/nyc-zipcode-geodata?resource=download) and released to the Public Domain under CC0.

The Income Bracket by ZIP CSV file (`nyc_income_by_zip_2021*.csv`) is from [the US Census](https://data.census.gov/table?q=Income+and+Earnings&t=Earnings+(Individuals):Income+(Households,+Families,+Individuals)&g=1600000US3651000,3651000$8600000&tid=ACSST5Y2021.S1901).

The Affordable Housing CSV (`Affordable_Housing_Production_by_Building.csv`) is from [NYC Open Data](https://data.cityofnewyork.us/Housing-Development/Affordable-Housing-Production-by-Building/hg8x-zxpr).

The NYC Zips and Boroughs CSV (`NYC_zipcodes_and_boros.csv`) is from [this GitHub repository by Eric Gregory Webb](https://github.com/erikgregorywebb/nyc-housing/blob/master/Data/nyc-zip-codes.csv).