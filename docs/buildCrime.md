Build Crime Data Set
================
Christopher Prener, Ph.D.
(September 21, 2018)

## Introduction

This notebook creates the crime data set for further analysis.

## Dependencies

This notebook depends on the following packages:

``` r
# primary data tools
library(compstatr)     # work with stlmpd crime data

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
library(lubridate)     # date time tools
```

    ## 
    ## Attaching package: 'lubridate'

    ## The following object is masked from 'package:base':
    ## 
    ##     date

``` r
library(readr)         # working with csv data

# spatial packages
library(gateway)       # work with st. louis spatial data
library(ggmap)         # batch geocoding
```

    ## Loading required package: ggplot2

``` r
library(sf)            # working with spatial
```

    ## Linking to GEOS 3.6.1, GDAL 2.1.3, proj.4 4.9.3

``` r
# other packages
library(janitor)       # frequency tables
library(here)          # file path management
```

    ## here() starts at /Users/chris/GitHub/Lab/Barriers-NhoodPaper

    ## 
    ## Attaching package: 'here'

    ## The following object is masked from 'package:lubridate':
    ## 
    ##     here

``` r
library(testthat)      # unit testing
```

    ## 
    ## Attaching package: 'testthat'

    ## The following object is masked from 'package:dplyr':
    ## 
    ##     matches

## Create Data

Data downloaded from the STLMPD website come in `.csv` format but with
the wrong file extension. The following bash script copies them to a new
subdirectory and fixes the file extension issue:

``` bash
# change working directory
cd ..

# execute cleaning script
bash source/reformatHTML.sh
```

    ## mkdir: data/raw/stlmpd/csv/2016: File exists
    ## mkdir: data/raw/stlmpd/csv/2017: File exists
    ## mkdir: data/raw/stlmpd/csv/2018: File exists

## Load Data

With our data renamed, we build a year list objects for 2016, 2017, and
2018 crimes:

``` r
data2016 <- cs_load_year(here("data", "raw", "stlmpd", "csv", "2016"))
data2017 <- cs_load_year(here("data", "raw", "stlmpd", "csv", "2017"))
data2018 <- cs_load_year(here("data", "raw", "stlmpd", "csv", "2018"))
```

    ## Warning in cs_load_year(here("data", "raw", "stlmpd", "csv", "2018")):
    ## There are fewer than 12 files in the specified folder. You are only loading
    ## a partial year.

We can visually verify that the 2018 folder is the one causing the
warning here, and that we have the maximum number of files we can work
from.

## Validate Data

Next we make sure there are no problems with the crime files in terms of
incongruent columns:

``` r
cs_validate_year(data2016, year = "2016")
```

    ## [1] TRUE

All of the data passes the validation checks.

``` r
cs_validate_year(data2017, year = "2017")
```

    ## [1] FALSE

We can use the `verbose = TRUE` option on `cs_validate_year()` to
identify areas where the validation checks have failed:

``` r
cs_validate_year(data2017, year = "2017", verbose = TRUE)
```

    ## # A tibble: 12 x 9
    ##    namedMonth codedMonth valMonth codedYear valYear oneMonth varCount
    ##    <chr>      <chr>      <lgl>        <int> <lgl>   <lgl>    <lgl>   
    ##  1 January    January    TRUE          2017 TRUE    TRUE     TRUE    
    ##  2 February   February   TRUE          2017 TRUE    TRUE     TRUE    
    ##  3 March      March      TRUE          2017 TRUE    TRUE     TRUE    
    ##  4 April      April      TRUE          2017 TRUE    TRUE     TRUE    
    ##  5 May        May        TRUE          2017 TRUE    TRUE     FALSE   
    ##  6 June       June       TRUE          2017 TRUE    TRUE     TRUE    
    ##  7 July       July       TRUE          2017 TRUE    TRUE     TRUE    
    ##  8 August     August     TRUE          2017 TRUE    TRUE     TRUE    
    ##  9 September  September  TRUE          2017 TRUE    TRUE     TRUE    
    ## 10 October    October    TRUE          2017 TRUE    TRUE     TRUE    
    ## 11 November   November   TRUE          2017 TRUE    TRUE     TRUE    
    ## 12 December   December   TRUE          2017 TRUE    TRUE     TRUE    
    ## # ... with 2 more variables: valVars <lgl>, valClasses <lgl>

The data for May 2017 do not pass the validation checks. We can extract
this month and confirm that there are too many columns in the May 2017
release. Once we have that confirmed, we can standardize that month and
re-run our validation.

``` r
# extract data
may2017 <- cs_extract_month(data2017, month = "May")

# unit test column number
expect_equal(ncol(may2017), 26)

# remove object
rm(may2017)

# standardize months
data2017 <- cs_standardize(data2017, month = "May", config = 26)

# validate data
cs_validate_year(data2017, year = "2017")
```

    ## [1] TRUE

We now get a `TRUE` value for `cs_validate_year()` and can move on to
2018 data.

``` r
cs_validate_year(data2018, year = "2018")
```

    ## [1] TRUE

## Collapse Data

With the data validated, we collapse each year into a single, flat
object:

``` r
data2016_flat <- cs_collapse(data2016)
data2017_flat <- cs_collapse(data2017)
data2018_flat <- cs_collapse(data2018)
```

What we need for this project is a single object with only the crimes
for 2016. Since crimes were *reported* in both the 2017 and 2018
flattened for 2016, we need to merge all three tables and then retain
only the 2016 crimes. The `cs_combine()` function will do this, and
return only the known crimes for
2016:

``` r
crimes2016 <- cs_combine(type = "year", date = 2016, data2016_flat, data2017_flat, data2018_flat)
```

### Clean-up Enviornment

With our data created, we can remove some of the intermediary objects
we’ve
created:

``` r
rm(data2016, data2016_flat, data2017, data2017_flat, data2018, data2018_flat)
```

## Remove Unfounded Crimes and Subset Based on Type of Crime:

The following code chunk removes unfounded crimes (those where `Count ==
-1`) and then creates a data frame for all part one crimes:

``` r
crimes2016 %>% 
  cs_filter_count(var = Count) %>%
  filter(ILEADSStreet != "UNKNOWN") %>%
  cs_filter_crime(var = Crime, crime = "Part 1") -> part1Crimes
```

## Check for and Address Missing Spatial Data

Before proceeding, we’ll check for missing spatial
data.

``` r
part1Crimes <- cs_missing_xy(part1Crimes, varx = XCoord, vary = YCoord, newVar = xyCheck)

table(part1Crimes$xyCheck)
```

    ## 
    ## FALSE  TRUE 
    ## 24951   422

About 2% of the part 1 crimes are missing spatial data. Since these have
the same root data, we’ll pull out those observations that are missing
spatial data and attempt to geocode them with the Google Maps API.

``` r
expect_equal(as.integer(table(part1Crimes$xyCheck)[2]), 422)
```

We start with 422 observations. We’ll concatenate a street address to
produce something we can run through Google’s API using
`ggmap::mutate_geocode()` for those that need geocoding and separate out
the already geocoded data:

``` r
# subset out missing spatial data
part1Crimes %>% 
  filter(xyCheck == TRUE) %>%
  mutate(fullAddress = paste0(ILEADSAddress, " ", ILEADSStreet, ", St. Louis, MO" )) -> part1Crimes_miss

# subset out valid spatial data
part1Crimes %>% 
  filter(xyCheck == FALSE) -> part1Crimes_valid

# logic check that we remain with 422 missing spatial data points
expect_equal(as.integer(table(part1Crimes_miss$xyCheck)[1]), 422)
```

These are still 422 observations. These observations are not a
representative slice of crimes in St. Louis. They are overwhelmginly
drawn from rapes, larcenies, and aggrevated assault.

``` r
part1Crimes_miss %>%
  cs_crime_cat(var = Crime, newVar = crimeCat, output = "string") %>%
  tabyl(crimeCat)
```

    ##             crimeCat   n     percent
    ##   Aggravated Assault  46 0.109004739
    ##                Arson   3 0.007109005
    ##             Burgalry   8 0.018957346
    ##        Forcible Rape 270 0.639810427
    ##             Homicide   8 0.018957346
    ##              Larceny  56 0.132701422
    ##  Motor Vehicle Theft  21 0.049763033
    ##              Robbery  10 0.023696682

Rape incidents comprise almost 64% of these incidents that cannot be
located.

The geocoding code chunk is powered by a script
`source/geocodeCrimes.R`, which is not automatically executed when this
notebook is knit. We use logic checks above to ensure that the sample
size fed into `geocodeCrimes.R` is consistent. This code chunk will not
be executed automatically given the resources it requires.

``` r
source(here("source", "geocodeCrimes.R"))
```

The results of the geocoding are that 56 of the 422 observations are
geocoded; 366 remain not geocoded.

The geocoded data are saved in an `intermediate/` subdirectory so that
they can be loaded back in when the notebook is knit.

### Clean-up Enviornment Again

At this point, we have a number of objects that we no longer need. Some
are only produced by the geocoding process, and thus this code chunk,
like the last, needs to be executed manually:

``` r
rm(part1Crimes_fail)
rm(part1Crimes_success)
```

Some are produced each iteration and can be cleaned automatically:

``` r
rm(crimes2016)
rm(part1Crimes)
```

## Project Both Sets of Data

First, we project the main set of previously geocoded data, remove
excess columns, and transform the data to NAD
1983:

``` r
valid <- st_as_sf(part1Crimes_valid, coords = c("XCoord", "YCoord"), crs = 102696)

valid %>%
  select(-xyCheck) %>%
  st_transform(crs = 4269) -> valid
```

Second, we project the geocoded data after loading it from the
previously saved `.csv` file and remove excecess
columns:

``` r
part1Crimes_success <- read_csv(file = here("data", "raw", "stlmpd", "intermediate", "missingXY_success.csv"))
```

    ## Parsed with column specification:
    ## cols(
    ##   .default = col_character(),
    ##   Count = col_integer(),
    ##   Crime = col_integer(),
    ##   District = col_integer(),
    ##   ILEADSAddress = col_integer(),
    ##   Neighborhood = col_integer(),
    ##   CADAddress = col_integer(),
    ##   XCoord = col_integer(),
    ##   YCoord = col_integer(),
    ##   xyCheck = col_logical(),
    ##   lon = col_double(),
    ##   lat = col_double()
    ## )

    ## See spec(...) for full column specifications.

``` r
success <- st_as_sf(part1Crimes_success, coords = c("lon", "lat"), crs = 4269)

success <- select(success, -XCoord, -YCoord, -xyCheck, -fullAddress)
```

Finally, we bind the two objects together:

``` r
combined <- rbind(valid, success)
```

## Export Data

With the data bound together, we write it to the `data/clean/`
directory:

``` r
st_write(combined, dsn = here("data", "clean", "crimes2016.shp"), delete_layer = TRUE)
```

    ## Warning in abbreviate_shapefile_names(obj): Field names abbreviated for
    ## ESRI Shapefile driver

    ## Deleting layer `crimes2016' using driver `ESRI Shapefile'
    ## Writing layer `crimes2016' to data source `/Users/chris/GitHub/Lab/Barriers-NhoodPaper/data/clean/crimes2016.shp' using driver `ESRI Shapefile'
    ## features:       25007
    ## fields:         18
    ## geometry type:  Point
