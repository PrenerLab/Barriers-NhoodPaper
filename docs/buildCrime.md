Build Crime Data Set
================
Christopher Prener, Ph.D.
(September 15, 2018)

## Introduction

This notebook creates the crime data set for further analysis.

## Dependencies

This notebook depends on the following packages:

``` r
# tidyverse packages
library(dplyr)         # data wrangling
```

    ## 
    ## Attaching package: 'dplyr'

    ## The following objects are masked from 'package:stats':
    ## 
    ##     filter, lag

    ## The following objects are masked from 'package:base':
    ## 
    ##     intersect, setdiff, setequal, union

``` r
# other packages
library(compstatr)     # work with stlmpd crime data
library(here)          # file path management
```

    ## here() starts at /Users/chris/GitHub/Lab/Barriers-NhoodPaper

## Create Data

Data downloaded from the STLMPD website come in `.csv` format but with
the wrong file extension. The following bash script copies them to a new
subdirectory and fixes the file extension issue:

``` bash
# change working directory
cd ..

# create csv folder
mkdir data/raw/stlmpd/csv

# copy html files new directory for csv
cp -r data/raw/stlmpd/html/* data/raw/stlmpd/csv

# change file extensions
for file in data/raw/stlmpd/csv/*.html
do
  mv "$file" "${file%%.*}.${file##*.}"
done

for file in data/raw/stlmpd/csv/*.html
do
  mv "$file" "${file%.html}.csv"
done
```

    ## mkdir: data/raw/stlmpd/csv: File exists

## Load Data

With our data renamed, we build a year list object for 2016 crimes:

``` r
data2016 <- cs_load_year(here("data", "raw", "stlmpd", "csv"))
```

## Validate Data

Next we make sure there are no problems with the crime files in terms of
incongruent columns:

``` r
cs_validate_year(data2016, year = "2016")
```

    ## # A tibble: 12 x 7
    ##    month monthName oneMonth valMonth varCount valVars valClasses
    ##    <dbl> <chr>     <lgl>    <lgl>    <lgl>    <lgl>   <lgl>     
    ##  1     1 Jan       TRUE     TRUE     TRUE     TRUE    TRUE      
    ##  2     2 Feb       TRUE     TRUE     TRUE     TRUE    TRUE      
    ##  3     3 Mar       TRUE     TRUE     TRUE     TRUE    TRUE      
    ##  4     4 Apr       TRUE     TRUE     TRUE     TRUE    TRUE      
    ##  5     5 May       TRUE     TRUE     TRUE     TRUE    TRUE      
    ##  6     6 Jun       TRUE     TRUE     TRUE     TRUE    TRUE      
    ##  7     7 Jul       TRUE     TRUE     TRUE     TRUE    TRUE      
    ##  8     8 Aug       TRUE     TRUE     TRUE     TRUE    TRUE      
    ##  9     9 Sep       TRUE     TRUE     TRUE     TRUE    TRUE      
    ## 10    10 Oct       TRUE     TRUE     TRUE     TRUE    TRUE      
    ## 11    11 Nov       TRUE     TRUE     TRUE     TRUE    TRUE      
    ## 12    12 Dec       TRUE     TRUE     TRUE     TRUE    TRUE

All of the data passes the validation checks.

## Collapse Data

With the data validated, we collapse it into a single, flat object:

``` r
data2016_flat <- cs_collapse(data2016)
```

## Remove Unfounded Crimes and Subset Based on Type of Crime:

The following code chunk removes unfounded crimes (those where `Count ==
-1`) and then creates two data frames, one for violent crimes and one
for all part one crimes:

``` r
# violent crimes
data2016_flat %>% 
  cs_filter_count(var = Count) %>%
  cs_filter_crime(var = Crime, crime = "Violent") -> violentCrimes

# part 1 crimes
data2016_flat %>% 
  cs_filter_count(var = Count) %>%
  cs_filter_crime(var = Crime, crime = "Part 1") -> part1Crimes
```
