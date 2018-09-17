Build Crime Data Set
================
Christopher Prener, Ph.D.
(September 16, 2018)

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
# spatial packages
library(gateway)       # work with st. louis spatial data
library(ggmap)         # batch geocoding
```

    ## Loading required package: ggplot2

``` r
library(sf)
```

    ## Linking to GEOS 3.6.1, GDAL 2.1.3, proj.4 4.9.3

``` r
# other packages
library(janitor)       # frequency tables
library(here)          # file path management
```

    ## here() starts at /Users/chris/GitHub/Lab/Barriers-NhoodPaper

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
2017 crimes:

``` r
data2016 <- cs_load_year(here("data", "raw", "stlmpd", "csv", "2016"))
data2017 <- cs_load_year(here("data", "raw", "stlmpd", "csv", "2017"))
data2018 <- cs_load_year(here("data", "raw", "stlmpd", "csv", "2018"))
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

All of the data passes the validation
    checks.

``` r
cs_validate_year(data2017, year = "2017")
```

    ## Warning in cs_validate_year(data2017, year = "2017"): Validation warning -
    ## not all data tables contain the expected 20 variables.

    ## Warning in cs_validate_year(data2017, year = "2017"): Validation warning -
    ## not all data tables contain the expected variable names.

    ## Warning in cs_validate_year(data2017, year = "2017"): Validation warning -
    ## not all data tables contain the expected variable classes.

    ## # A tibble: 12 x 7
    ##    month monthName oneMonth valMonth varCount valVars valClasses
    ##    <dbl> <chr>     <lgl>    <lgl>    <lgl>    <lgl>   <lgl>     
    ##  1     1 Jan       TRUE     TRUE     TRUE     TRUE    TRUE      
    ##  2     2 Feb       TRUE     TRUE     TRUE     TRUE    TRUE      
    ##  3     3 Mar       TRUE     TRUE     TRUE     TRUE    TRUE      
    ##  4     4 Apr       TRUE     TRUE     TRUE     TRUE    TRUE      
    ##  5     5 May       TRUE     TRUE     FALSE    NA      NA        
    ##  6     6 Jun       TRUE     TRUE     TRUE     TRUE    TRUE      
    ##  7     7 Jul       TRUE     TRUE     TRUE     TRUE    TRUE      
    ##  8     8 Aug       TRUE     TRUE     TRUE     TRUE    TRUE      
    ##  9     9 Sep       TRUE     TRUE     TRUE     TRUE    TRUE      
    ## 10    10 Oct       TRUE     TRUE     TRUE     TRUE    TRUE      
    ## 11    11 Nov       TRUE     TRUE     TRUE     TRUE    TRUE      
    ## 12    12 Dec       TRUE     TRUE     TRUE     TRUE    TRUE

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

## Check for and Address Missing Spatial Data

Before proceeding, we’ll check for missing spatial
data.

``` r
violentCrimes <- cs_missing_xy(violentCrimes, varx = XCoord, vary = YCoord, newVar = xyCheck)

table(violentCrimes$xyCheck)
```

    ## 
    ## FALSE  TRUE 
    ##  5742   368

About 6% of the violent crimes are missing spatial
data.

``` r
part1Crimes <- cs_missing_xy(part1Crimes, varx = XCoord, vary = YCoord, newVar = xyCheck)

table(part1Crimes$xyCheck)
```

    ## 
    ## FALSE  TRUE 
    ## 24998   494

About 2% of the part 1 crimes are missing spatial data. Since these have
the same root data, we’ll pull out those observations that are missing
spatial data and attempt to geocode them with the Google Maps API.

We start with 494 observations

``` r
part1Crimes %>% 
  filter(xyCheck == TRUE) %>%
  mutate(fullAddress = paste0(ILEADSAddress, " ", ILEADSStreet, ", St. Louis, MO" )) -> part1Crimes_miss

part1Crimes %>% 
  filter(xyCheck == FALSE) -> part1Crimes_valid

nrow(part1Crimes_miss)
```

    ## [1] 494

Removing the truly “unknown” addresses yields a set of 429 addresses
that could potentially be geocoded.

``` r
part1Crimes_miss %>%
  tabyl(Description)
```

    ##                                     Description   n     percent
    ##    AGG.ASSAULT-FIREARM/CITIZEN ADULT 1ST DEGREE  17 0.034412955
    ##    AGG.ASSAULT-FIREARM/CITIZEN ADULT 3RD DEGREE   5 0.010121457
    ##    AGG.ASSAULT-FIREARM/CITIZEN CHILD 1ST DEGREE   5 0.010121457
    ##    AGG.ASSAULT-FIREARM/POLC.OFFICER  3RD DEGREE   1 0.002024291
    ##  AGG.ASSAULT-HNDS,FST,FEET/CTZEN ADLT 2ND DEGRE   1 0.002024291
    ##  AGG.ASSAULT-HNDS,FST,FEET/CTZEN ADLT 3RD DEGRE   1 0.002024291
    ##  AGG.ASSAULT-HNDS,FST,FEET/CTZEN CHLD 1ST DEGRE   1 0.002024291
    ##      AGG.ASSAULT-KNIFE/CITIZEN ADULT 1ST DEGREE   1 0.002024291
    ##     AGG.ASSAULT-KNIFE/POLICE OFFICER 3RD DEGREE   1 0.002024291
    ##  AGG.ASSAULT-OTH DANG WEP/CTZEN ADLT 1ST DEGREE   2 0.004048583
    ##  AGG.ASSAULT-OTH DANG WEP/CTZEN ADLT 2ND DEGREE   3 0.006072874
    ##  AGG.ASSAULT-OTH DANG WEP/CTZEN ADLT 3RD DEGREE   4 0.008097166
    ##    AGG.ASSAULT-OTH DANG WEP/POL OFFC 3RD DEGREE   1 0.002024291
    ##                        ARSON-2ND DEGREE/SUCCESS   1 0.002024291
    ##                 ARSON-KNOWINGLY BURNING/SUCCESS   2 0.004048583
    ##         ASSLT-AGGRAV-FIREARM-1ST-ADULT-DOMESTIC   3 0.006072874
    ##         ASSLT-AGGRAV-FIREARM-2ND-ADULT-DOMESTIC   1 0.002024291
    ##         ASSLT-AGGRAV-FIREARM-3RD-ADULT-DOMESTIC   1 0.002024291
    ##         ASSLT-AGGRAV-OTH-WPN-2ND-CHILD-DOMESTIC   1 0.002024291
    ##         ASSLT-AGGRAV-OTH-WPN-3RD-ADULT-DOMESTIC   2 0.004048583
    ##         ASSLT-AGGRAV-OTH-WPN-3RD-CHILD-DOMESTIC   2 0.004048583
    ##        ASSLT-AGGRV-HND/FST/FT-2ND-ADUL-DOMESTIC   2 0.004048583
    ##        ASSLT-AGGRV-HND/FST/FT-3RD-ADUL-DOMESTIC   1 0.002024291
    ##                   AUTO THEFT-PERM RETNT/ATTEMPT   2 0.004048583
    ##                  AUTO THEFT-PERM RETNT/JOY RIDE  16 0.032388664
    ##         AUTO THEFT-PERM RETNT/UNRECOV OVER 48HR   4 0.008097166
    ##            AUTO THEFT-TRUCK/PERM RETNT/JOY RIDE   1 0.002024291
    ##   AUTO THEFT-TRUCK/PERM RETNT/UNRECOV OVER 48HR   2 0.004048583
    ##        BURGLARY-RESDNCE/UNK TIM/ATT FORCE ENTRY   2 0.004048583
    ##    BURGLARY-RESDNCE/UNK TIM/FORC ENT/UNOCCUPIED   1 0.002024291
    ##          BURGLARY-RESIDENCE/DAY/ATT FORCE ENTRY   2 0.004048583
    ##     BURGLARY-RESIDENCE/DAY/FORCE ENT/UNOCCUPIED   1 0.002024291
    ##       BURGLARY-RESIDENCE/DAY/UNLAW ENT/OCCUPIED   1 0.002024291
    ##     BURGLARY-RESIDENCE/NIT/FORCE ENT/UNOCCUPIED   1 0.002024291
    ##     BURGLARY-RESIDENCE/NIT/UNLAW ENT/UNOCCUPIED   2 0.004048583
    ##                                        HOMICIDE   6 0.012145749
    ##            LARC-ALL OTH/FRM PRSN/$500 - $24,999   1 0.002024291
    ##             LARCENY-ALL OTH/FRM PRSN/UNDER $500   1 0.002024291
    ##                LARCENY-ALL OTHER $500 - $24,999   7 0.014170040
    ##                    LARCENY-ALL OTHER UNDER $500   6 0.012145749
    ##                     LARCENY-BICYCLES UNDER $500   3 0.006072874
    ##            LARCENY-FROM BUILDING $500 - $24,999   4 0.008097166
    ##                LARCENY-FROM BUILDING UNDER $500  10 0.020242915
    ##             LARCENY-FROM MTR VEH $500 - $24,999  17 0.034412955
    ##                 LARCENY-FROM MTR VEH UNDER $500  22 0.044534413
    ##                LARCENY-MTR VEH PARTS UNDER $500  15 0.030364372
    ##                 LARCENY-SHOPLIFT $500 - $24,999   1 0.002024291
    ##                     LARCENY-SHOPLIFT UNDER $500   1 0.002024291
    ##                                RAPE -- FORCIBLE 262 0.530364372
    ##      RAPE-ATTEMPT FORCIBLE RAPE/FORCIBLE INCEST  31 0.062753036
    ##        ROBBERY-COMMERCE PL/FIREARM USED/SUCCESS   1 0.002024291
    ##       ROBBERY-HIGHWAY       /KNIFE USED/ATTEMPT   1 0.002024291
    ##       ROBBERY-HIGHWAY     /FIREARM USED/ATTEMPT   1 0.002024291
    ##       ROBBERY-HIGHWAY  /FIREARM USED/SUCCESSFUL   4 0.008097166
    ##       ROBBERY-HIGHWAY  /STRNGARM/INJURY/ATTEMPT   1 0.002024291
    ##       ROBBERY-HIGHWAY  /STRNGARM/NO INJ/SUCCESS   4 0.008097166
    ##       ROBBERY-HIGHWAY/OTHR WEPN USED/SUCCESSFUL   1 0.002024291

Rape incidents comprise almost 66% of these incidents that cannot be
located.

``` r
source(here("source", "geocodeCrimes.R"))
```

## Project Both Sets of Data

  - need to filter out prior crimes
  - need to pull in data from 2017 / 2018 and search for 2016
crimes

<!-- end list -->

``` r
x <- st_as_sf(part1Crimes_valid, coords = c("XCoord", "YCoord"), crs = 102696)
```

## Export Data
