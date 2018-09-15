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
library(ggmap)         # batch geocoding
```

    ## Loading required package: ggplot2

``` r
library(janitor)       # frequency tables
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
  filter(ILEADSStreet != "UNKNOWN") %>%
  mutate(fullAddress = paste0(ILEADSAddress, " ", ILEADSStreet, ", St. Louis, MO" )) -> missingXY

nrow(missingXY)
```

    ## [1] 429

Removing the truly “unknown” addresses yields a set of 429 addresses
that could potentially be geocoded.

``` r
missingXY %>%
  tabyl(Description)
```

    ##                                     Description   n     percent
    ##    AGG.ASSAULT-FIREARM/CITIZEN ADULT 1ST DEGREE   8 0.018648019
    ##    AGG.ASSAULT-FIREARM/CITIZEN ADULT 3RD DEGREE   4 0.009324009
    ##    AGG.ASSAULT-FIREARM/CITIZEN CHILD 1ST DEGREE   5 0.011655012
    ##    AGG.ASSAULT-FIREARM/POLC.OFFICER  3RD DEGREE   1 0.002331002
    ##  AGG.ASSAULT-HNDS,FST,FEET/CTZEN ADLT 2ND DEGRE   1 0.002331002
    ##  AGG.ASSAULT-HNDS,FST,FEET/CTZEN ADLT 3RD DEGRE   1 0.002331002
    ##      AGG.ASSAULT-KNIFE/CITIZEN ADULT 1ST DEGREE   1 0.002331002
    ##     AGG.ASSAULT-KNIFE/POLICE OFFICER 3RD DEGREE   1 0.002331002
    ##  AGG.ASSAULT-OTH DANG WEP/CTZEN ADLT 1ST DEGREE   2 0.004662005
    ##  AGG.ASSAULT-OTH DANG WEP/CTZEN ADLT 2ND DEGREE   3 0.006993007
    ##  AGG.ASSAULT-OTH DANG WEP/CTZEN ADLT 3RD DEGREE   4 0.009324009
    ##                        ARSON-2ND DEGREE/SUCCESS   1 0.002331002
    ##                 ARSON-KNOWINGLY BURNING/SUCCESS   2 0.004662005
    ##         ASSLT-AGGRAV-FIREARM-1ST-ADULT-DOMESTIC   3 0.006993007
    ##         ASSLT-AGGRAV-FIREARM-2ND-ADULT-DOMESTIC   1 0.002331002
    ##         ASSLT-AGGRAV-FIREARM-3RD-ADULT-DOMESTIC   1 0.002331002
    ##         ASSLT-AGGRAV-OTH-WPN-3RD-ADULT-DOMESTIC   2 0.004662005
    ##         ASSLT-AGGRAV-OTH-WPN-3RD-CHILD-DOMESTIC   2 0.004662005
    ##        ASSLT-AGGRV-HND/FST/FT-2ND-ADUL-DOMESTIC   2 0.004662005
    ##        ASSLT-AGGRV-HND/FST/FT-3RD-ADUL-DOMESTIC   1 0.002331002
    ##                   AUTO THEFT-PERM RETNT/ATTEMPT   2 0.004662005
    ##                  AUTO THEFT-PERM RETNT/JOY RIDE  13 0.030303030
    ##         AUTO THEFT-PERM RETNT/UNRECOV OVER 48HR   4 0.009324009
    ##            AUTO THEFT-TRUCK/PERM RETNT/JOY RIDE   1 0.002331002
    ##   AUTO THEFT-TRUCK/PERM RETNT/UNRECOV OVER 48HR   2 0.004662005
    ##        BURGLARY-RESDNCE/UNK TIM/ATT FORCE ENTRY   2 0.004662005
    ##    BURGLARY-RESDNCE/UNK TIM/FORC ENT/UNOCCUPIED   1 0.002331002
    ##          BURGLARY-RESIDENCE/DAY/ATT FORCE ENTRY   2 0.004662005
    ##     BURGLARY-RESIDENCE/DAY/FORCE ENT/UNOCCUPIED   1 0.002331002
    ##       BURGLARY-RESIDENCE/DAY/UNLAW ENT/OCCUPIED   1 0.002331002
    ##     BURGLARY-RESIDENCE/NIT/UNLAW ENT/UNOCCUPIED   1 0.002331002
    ##                                        HOMICIDE   5 0.011655012
    ##            LARC-ALL OTH/FRM PRSN/$500 - $24,999   1 0.002331002
    ##             LARCENY-ALL OTH/FRM PRSN/UNDER $500   1 0.002331002
    ##                LARCENY-ALL OTHER $500 - $24,999   6 0.013986014
    ##                    LARCENY-ALL OTHER UNDER $500   3 0.006993007
    ##                     LARCENY-BICYCLES UNDER $500   2 0.004662005
    ##            LARCENY-FROM BUILDING $500 - $24,999   4 0.009324009
    ##                LARCENY-FROM BUILDING UNDER $500   7 0.016317016
    ##             LARCENY-FROM MTR VEH $500 - $24,999  13 0.030303030
    ##                 LARCENY-FROM MTR VEH UNDER $500  11 0.025641026
    ##                LARCENY-MTR VEH PARTS UNDER $500   3 0.006993007
    ##                 LARCENY-SHOPLIFT $500 - $24,999   1 0.002331002
    ##                     LARCENY-SHOPLIFT UNDER $500   1 0.002331002
    ##                                RAPE -- FORCIBLE 253 0.589743590
    ##      RAPE-ATTEMPT FORCIBLE RAPE/FORCIBLE INCEST  31 0.072261072
    ##        ROBBERY-COMMERCE PL/FIREARM USED/SUCCESS   1 0.002331002
    ##       ROBBERY-HIGHWAY  /FIREARM USED/SUCCESSFUL   4 0.009324009
    ##       ROBBERY-HIGHWAY  /STRNGARM/INJURY/ATTEMPT   1 0.002331002
    ##       ROBBERY-HIGHWAY  /STRNGARM/NO INJ/SUCCESS   4 0.009324009
    ##       ROBBERY-HIGHWAY/OTHR WEPN USED/SUCCESSFUL   1 0.002331002

Rape incidents comprise almost 66% of these incidents that cannot be
located.

``` r
source(here("source", "geocodeCrimes.R"))
```
