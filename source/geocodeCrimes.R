# executed *manually* as part of the buildCrime.Rmd notebook

part1Crimes_miss <- mutate_geocode(part1Crimes_miss, location = fullAddress, output = "latlon", source = "google")

part1Crimes_success <- filter(part1Crimes_miss, is.na(lon) == FALSE | ILEADSStreet != "UNKNOWN")
part1Crimes_fail <- filter(part1Crimes_miss, is.na(lon) == TRUE | ILEADSStreet == "UNKNOWN")

write_csv(part1Crimes_success, here("data", "raw", "stlmpd", "intermediate", "missingXY_success.csv"))
write_csv(part1Crimes_fail, here("data", "raw", "stlmpd", "intermediate", "missingXY_fail.csv"))
