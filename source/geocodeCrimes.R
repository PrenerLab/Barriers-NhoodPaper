# executed *manually* as part of the buildCrime.Rmd notebook

part1Crimes_miss <- mutate_geocode(part1Crimes_miss, location = fullAddress, output = "latlon", source = "google", messaging = FALSE)

part1Crimes_success <- filter(part1Crimes_miss, is.na(lon) == FALSE)
part1Crimes_fail <- filter(part1Crimes_miss, is.na(lon) == TRUE)

write_csv(part1Crimes_success, here("data", "raw", "stlmpd", "intermediate", "missingXY_success.csv"))
write_csv(part1Crimes_fail, here("data", "raw", "stlmpd", "intermediate", "missingXY_fail.csv"))
