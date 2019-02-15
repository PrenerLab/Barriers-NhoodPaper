import pysal as pysal
import numpy as numpy

# grid data pathways
shp_path = "/Users/thbraswell/Documents/Github/Barriers-NhoodPaper/data/clean/gridDataCurrent.shp"
dbf_path = "/Users/thbraswell/Documents/Github/Barriers-NhoodPaper/data/clean/gridDataCurrent.dbf"

# store function to open grid shapefile
f = pysal.open(dbf_path)
print f.header
# create rook spatial weight
w = pysal.weights.Rook.from_shapefile(shp_path)
print w.n
print w.histogram

# read in dependent variables: St. louis violent crime rates, violent crime counts, and barrier counts
y1 = numpy.array([f.by_col('vc_rate')]).T
print y1.shape
y2 = numpy.array([f.by_col('v_crimes')]).T
print y2.shape
y3 = numpy.array([f.by_col('barriers')]).T
print y3.shape

# create global moran's i
mi1 = pysal.Moran(y1, w, two_tailed=False)
print "Global Moran's I For Violent Crime Rates " "%.5f"%mi1.I
print "P-Value " "%.5f"%mi1.p_norm

mi2 = pysal.Moran(y2, w, two_tailed=False)
print "Global Moran's I For Violent Crime Counts " "%.5f"%mi2.I
print "P-Value " "%.5f"%mi2.p_norm

mi3 = pysal.Moran(y3, w, two_tailed=False)
print "Global Moran's I For Barrier Counts " "%.5f"%mi3.I
print "P-Value " "%.5f"%mi3.p_norm

# Regression

## Create arrays for explanatory variables.
x1_names = ['p_nhblk16', 'p_pov16', 'p_popChg', 'p_vac16', 'p_vacChg70', 'barriers']
x1 = numpy.array([f.by_col(var) for var in x1_names]).T
print x1.shape

x2_names = ['p_nhblk16', 'p_pov16', 'p_popChg', 'p_vac16', 'pop16', 'barriers']
x2 = numpy.array([f.by_col(var) for var in x2_names]).T
print x2.shape

x3_names = ['p_nhblk16', 'p_pov16', 'p_popChg', 'p_vac16', 'pop16']
x3 = numpy.array([f.by_col(var) for var in x3_names]).T
print x3.shape

x4_names = ['barriers']
x4 = numpy.array([f.by_col(var) for var in x4_names]).T
print x4.shape

## create name for dependent variables
y1_name = 'vc_rate'
y2_name = 'v_crimes'
y3_name = 'barriers'

## Crime Rate Models - OLS and GMM Spatial Lag

ols_vc_rate = pysal.spreg.OLS(y1, x1, w=w, name_y=y1_name, name_x=x1_names, spat_diag=True, moran=True, white_test=True, robust='white')

print ols_vc_rate.summary

gmm_lag_vc_rate = pysal.spreg.twosls_sp.GM_Lag(y1, x1, w=w, name_y=y1_name, name_x=x1_names, w_lags=1, spat_diag=True, robust='white')

print gmm_lag_vc_rate.summary

## Crime Count Models - OLS and GMM Spatial Lag

ols_vc_count_bar = pysal.spreg.OLS(y2, x4, w=w, name_y=y2_name, name_x=x4_names, spat_diag=True, moran=True, white_test=True, robust='white')
print ols_vc_count_bar.summary

ols_vc_count = pysal.spreg.OLS(y2, x2, w=w, name_y=y2_name, name_x=x2_names, spat_diag=True, moran=True, white_test=True, robust='white')

print ols_vc_count.summary


gmm_lag_vc_count = pysal.spreg.twosls_sp.GM_Lag(y2, x2, w=w, name_y=y2_name, name_x=x2_names, w_lags=1, spat_diag=True, robust='white')

print gmm_lag_vc_count.summary

## Barrier Location Models - OLS and GMM Spatial Lag

ols_barriers = pysal.spreg.OLS(y3, x3, w=w, name_y=y3_name, name_x=x3_names, spat_diag=True, moran=True, white_test=True, robust='white')

print ols_barriers.summary

gmm_lag_barriers = pysal.spreg.twosls_sp.GM_Lag(y3, x3, w=w, name_y=y3_name, name_x=x3_names, w_lags=1, spat_diag=True, robust='white')
print gmm_lag_barriers.summary

# Save output
with open('outfile.txt', 'w') as outfile:
    print >>outfile, ols_vc_count_bar.summary, ols_vc_count.summary, gmm_lag_vc_count.summary, \
        ols_barriers.summary, gmm_lag_barriers.summary
