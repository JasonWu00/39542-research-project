# 39542-research-project

[GitHub repo](https://github.com/JasonWu00/39542-research-project/)

[github.io page](https://jasonwu00.github.io/39542-research-project/)

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

### Project Procedures

For this project I took the following steps:

0. Acquire the raw data sets. A full list of sources of the various data sets I used can be found in [COPYRIGHT.txt](https://github.com/JasonWu00/39542-research-project/blob/master/COPYRIGHT.txt). Most of the data sets came from the US Census and NYC Open Data.
1. Clean up the Affordable Housing data by replacing NA values with appropriate placeholders.
2. Clean up the Income by ZIP data. Since there are multiple data sets for this part (one per year to be analyzed), I called the clean-up function a bunch of times.
3. Expand Income by ZIP data. I added several columns to each Income by ZIP data file corresponding to data that might aid me in my analysis. Some of these columns came in handy.
4. Run predictive modeling (Polynomial model with LassoCV) on the expanded data. I chose this model because at the start of this project I was expecting to find some sort of correlation between two variables I was already thinking about.
5. Draw graphs. I drew some graphs for the 2021 Income by ZIP data and model to establish a general understanding on individual data sets, another graph on all of the predictive models to compare them, and some HTML maps to show some trends.

### Project Findings

### Places for Improvement

### Potential Further Investigation

### Sources

See [COPYRIGHT.txt](https://github.com/JasonWu00/39542-research-project/blob/master/COPYRIGHT.txt).