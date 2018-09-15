# executed *manually* as part of the buildCrime.Rmd notebook

missingXY <- mutate_geocode(missingXY, location = fullAddress, output = "latlon", source = "google")

missingXY <- filter(missingXY, is.na(lon) == FALSE)

write_csv(missingXY, here("data", "raw", "stlmpd", "intermediate", "missingXY.csv"))
