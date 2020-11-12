# -*- coding: utf-8 -*-
"""
Project: Hurricanes
Team: Phoenix
Names: Steph Verbout, Mark Folashade, Lindsey Shavers, Khoi Tran
Computing IDs: sv8jy, mf4us, lns4pr, kt2np
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from datetime import datetime, timedelta
from math import sin, cos, sqrt, atan2, radians
import HeatMap as hm

atlantic_df = pd.read_csv('atlantic.csv')

# set as data frame
atlantic_df = pd.DataFrame(atlantic_df)
    
### Cleaning data
# only select hurricanes from 1950 onwards, when they began naming storms
atlantic_df = atlantic_df[atlantic_df['Date'] > 19500000]

# subsetting relevant variables/columns
atlantic_df = atlantic_df[["ID", "Name", "Date", "Time", \
                           "Event", "Status", "Latitude", \
                           "Longitude", "Maximum Wind", \
                           "Minimum Pressure"]]

# using str.strip() method on all columns labeled 'object' to remove whitespace for easier sorting/querying later on
print(atlantic_df.dtypes)
atlantic_df['ID'] = atlantic_df['ID'].str.strip()
atlantic_df['Name'] = atlantic_df['Name'].str.strip()
atlantic_df['Event'] = atlantic_df['Event'].str.strip()
atlantic_df['Status'] = atlantic_df['Status'].str.strip()
atlantic_df['Longitude'] = atlantic_df['Longitude'].str.strip()
atlantic_df['Latitude'] = atlantic_df['Latitude'].str.strip()

# trying groupby() for initial exploratory analysis
print(atlantic_df.groupby('ID').mean())
print(atlantic_df.groupby('Status').mean())

# process 'Maximum Wind' from int to float
atlantic_df['Maximum Wind'] = [float(mw) for mw in atlantic_df['Maximum Wind']]

# process datetime
# start with turning time into strings, to enforce proper %H%M format
atlantic_df['Time'].unique()

## convert longitude and latitude to decimal format for plotting
# initial datetime conversion in the same loop
for i in range(len(atlantic_df)):
    # time
    # ints under four digits when converted to strings need to be prepended with 4 - len() zeroes
    timeClean = atlantic_df.iloc[i, atlantic_df.columns.get_loc('Time')]
    if len(str(timeClean)) == 4:
        atlantic_df.iloc[i, atlantic_df.columns.get_loc('Time')] = str(timeClean)
    else:
        zeroes = '0' * (4 - len(str(timeClean)))
        atlantic_df.iloc[i, atlantic_df.columns.get_loc('Time')] = zeroes + str(timeClean)
        
    # longitude
    longClean = atlantic_df.iloc[i, atlantic_df.columns.get_loc('Longitude')]
    if longClean[-1] == 'W':
        atlantic_df.iloc[i, atlantic_df.columns.get_loc('Longitude')] = float(longClean.replace('W', '')) * -1
    else:
        atlantic_df.iloc[i, atlantic_df.columns.get_loc('Longitude')] = float(longClean.replace('E', ''))
    
    # latitude
    latClean = atlantic_df.iloc[i, atlantic_df.columns.get_loc('Latitude')]
    if latClean[-1] == 'N':
        atlantic_df.iloc[i, atlantic_df.columns.get_loc('Latitude')] = float(latClean.replace('N', ''))
    else:
        atlantic_df.iloc[i, atlantic_df.columns.get_loc('Latitude')] = float(latClean.replace('S', '')) * -1

# second loop for creating datetime and category variables
# use 0 for non-hurricanes (tropical storms, etc.)
# 1: Maximum W 64 <= x < 82
# 2: 82 <= x < 95
# 3: 95 <= x < 112
# 4: 112 <= x < 136
# 5: x >= 136

datetime_list = []
category_list = []
for j in range(len(atlantic_df)):
    # create a datetime list by combining variables 'Date' and 'Time'
    datetime_list.append(str(atlantic_df.iloc[j, atlantic_df.columns.get_loc('Date')]) + ' ' + atlantic_df.iloc[j, atlantic_df.columns.get_loc('Time')])
    
    # create a list of hurricane categories, based on wind value
    windValue = atlantic_df.iloc[j, atlantic_df.columns.get_loc('Maximum Wind')]
    
    if atlantic_df.iloc[j, atlantic_df.columns.get_loc('Status')] != 'HU':
        category_list.append(0.0)
    else:
        if windValue > 136:
            category_list.append(5.0)
        elif windValue > 112:
            category_list.append(4.0)
        elif windValue > 95:
            category_list.append(3.0)
        elif windValue > 82:
            category_list.append(2.0)
        elif windValue > 62:
            category_list.append(1.0)
        else:
            category_list.append(0.0)
    
# join 'Datetime' and 'Category' lists to the main dataset
atlantic_df['Datetime'] = datetime_list
atlantic_df['Datetime'] = pd.to_datetime(atlantic_df['Datetime'], format = '%Y%m%d %H%M')
atlantic_df['Category'] = category_list

# replace -999 values for 'Minimum Pressure' with NaN
atlantic_df = atlantic_df.replace(-999, pd.NA)

# clean longitude data, as some points are <-180
# e.g. -359.1 (359.1W) should be 0.9 (0.9E)
atlantic_df['Longitude'].loc[lambda i: i < -180] = atlantic_df['Longitude'].loc[lambda i: i < -180] + 360

### Create aggregated dataset per hurricane (per ID): atlantic_aggr_df
## identify variables such as distance moved (change in long/lat), duration (change in datetime), change in windspeed/pressure/etc.

# force sort data frames before aggregation
atlantic_df = atlantic_df.sort_values(by = ['ID', 'Datetime'], ascending = True)

# two column dataframe of unique hurricanes
hurricane_list = atlantic_df[['ID', 'Name']].drop_duplicates().sort_values(by = ['ID'])

# empty dataframe to form into aggregate dataframe
# create a list to name columns
aggrColumnNames = ['ID', 'Name', \
                   'initialDate', 'endDate', 'duration', \
                   'netDistanceKm', 'totalDistanceKm', \
                   'maxLandSpeed', 'minLandSpeed', 'meanLandSpeed', \
                   'pressureMean', 'pressureStDev',  'pressureMin', \
                   'pressure25Pct', 'pressureMedian', 'pressure75Pct', \
                   'pressureMax', 'pressureDelta', 'windMean', 'windStDev', \
                   'windMin', 'wind25Pct', 'windMedian', 'wind50Pct', \
                   'windMax', 'windDelta', 'maxCategory', 'landfallBool', \
                   'landfallTimeDelta', 'landfallDatetime', \
                   'landfallCategory', 'landfallLong', 'landfallLat']

atlantic_df_aggr = pd.DataFrame(columns = aggrColumnNames)

## function for calculating distance traveled given coordinates, in kilometers
def coord_to_km(lat1, lat2, long1, long2):
    # convert coordinates to radian values
    delta_lat = radians(lat2) - radians(lat1)
    delta_long = radians(long2) - radians(long1)
    
    # calculate change in coordinates in kilometers
    a = sin(delta_lat / 2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(delta_long / 2)**2
    distance_km = 2 * atan2(sqrt(a), sqrt(1 - a))
    return distance_km
    
## loop through each hurricane (by ID)
for k in range(len(hurricane_list)):
    ## create a subset dataframe for easier calculation/referencing
    subset_df = atlantic_df[atlantic_df['ID'] == hurricane_list.iloc[k, hurricane_list.columns.get_loc('ID')]]
    
    ## 'Duration' variables (3)
    # initial date, final date, duration
    # duration = delta between datetimes, object type is Timedelta for duration
    durationList = [subset_df.Datetime.min(), \
                    subset_df.Datetime.max(), \
                    (subset_df.Datetime.max() - subset_df.Datetime.min()).total_seconds() / 3600]
    
    ## 'Distance Traveled' variable (1)
    # calculate total distance traveled by hurricane
    # not the delta because max and min because hurricanes do not necessarily travel in a linear fashion
    # not an aggregate as hurricanes may move backwards in terms of latitude/longitude, so an aggregate function is not appropriate
    # convert changes in coordinates to an understandable unit of distance, kilometers
    distance_float = 0
    
    ## Use same loop to create statistics for hurricane land speed, distance traveled/time
    # list to store hurricane land speeds
    speed_list = []
    for m in range(1, len(subset_df)):
        distance = coord_to_km(subset_df.iloc[m - 1, subset_df.columns.get_loc('Latitude')], \
                               subset_df.iloc[m, subset_df.columns.get_loc('Latitude')], \
                               subset_df.iloc[m - 1, subset_df.columns.get_loc('Longitude')], \
                               subset_df.iloc[m, subset_df.columns.get_loc('Longitude')])
        distance_float += distance
        
        # calculate speed, in km/hr
        speed_list.append(distance / ((subset_df.iloc[m, subset_df.columns.get_loc('Datetime')] - subset_df.iloc[m - 1, subset_df.columns.get_loc('Datetime')]).seconds / 3600))
    
    # calculate net distance, distance between start and end of hurricane
    net_distance = coord_to_km(subset_df.Latitude[subset_df.Datetime == subset_df.Datetime.min()], \
                               subset_df.Latitude[subset_df.Datetime == subset_df.Datetime.max()], \
                               subset_df.Longitude[subset_df.Datetime == subset_df.Datetime.max()], \
                               subset_df.Longitude[subset_df.Datetime == subset_df.Datetime.max()])
    ## New 'Distance' variables (2)
    # once the distance-calculating for loop ends, append each total distance traveled value to the distance-recording list
    # also add the net distance traveled, from initial storm start to end
    distanceList = [net_distance, distance_float]
    
    ## new 'Landspeed' variables (3)
    # once the for loop ends, create a short summary stats list for landspeed and append it to the landspeed list external to the (larger) for loop
    # max landspeed, min landspeed, mean landspeed
    landSpeedList = [max(speed_list), min(speed_list), sum(speed_list) / len(speed_list)]
    
    ## 'Minimum Pressure' summary stats ()
    # Series including mean, standard deviation, 50th & 75th percentiles, and maximum values
    pressureList = subset_df['Minimum Pressure'].describe().iloc[1:8].tolist()
    pressureList.append(subset_df['Minimum Pressure'].max() - subset_df['Minimum Pressure'].min())
    
    ## 'Maximum Wind' summary stats (8)
    # Series including mean, standard deviation, 50th & 75th percentiles, and maximum values
    windList = subset_df['Maximum Wind'].describe().iloc[1:8].tolist()
    # add windDelta, diff between min and max
    windList.append(subset_df['Maximum Wind'].max() - subset_df['Maximum Wind'].min())
    
    ## 'Category' variable, 'maxCategory' (1)
    categoryList = [subset_df['Category'].max()]
    
    ## 'Landfall' variables (6)
    if subset_df.Event.isin(['L']).any():
        # if the storm reached land or not
        landfallBool = True
        # how long it took the storm to reach land
        landfallTimeDelta = subset_df.Datetime[subset_df.Event == 'L'].min() - subset_df.Datetime.min()
        # when the storm reached land
        landfallDatetime = subset_df.Datetime[subset_df.Event == 'L'].min()
        # category of the storm when it reached land
        landfallCategory = subset_df.Category[subset_df.Event == 'L'].iloc[0]
        # landfall longitude
        landfallLong = subset_df.loc[subset_df.Event == 'L', 
                                     ['Longitude', 'Latitude']].iloc[0][0]
        # landfall latitude
        landfallLat = subset_df.loc[subset_df.Event == 'L', 
                                    ['Longitude', 'Latitude']].iloc[0][1]
    else:
        landfallBool = False
        landfallTimeDelta = None
        landfallDatetime = None
        landfallCategory = None
        landfallLong = None
        landfallLat = None
    landfallList = [landfallBool, landfallTimeDelta, landfallDatetime, landfallCategory, landfallLong, landfallLat]
    
    ## append to empty data frame
    appendList = hurricane_list.iloc[k].tolist() + durationList + distanceList + landSpeedList + pressureList + windList + categoryList + landfallList
    appendSeries = pd.Series(appendList, index = aggrColumnNames)
    atlantic_df_aggr = atlantic_df_aggr.append(appendSeries, ignore_index = True)

## FOR TESTING VISUALIZATION
# view min and max longitude and latitude points
# use these figures to download a map from openstreetmap.org
# visualize a map for top 95th percentile longest duration storms
top95duration = atlantic_df_aggr[atlantic_df_aggr.duration >= \
                                 atlantic_df_aggr.duration.quantile(0.95)].sort_values(by = ['duration'], ascending = False)
top95duration = pd.merge(atlantic_df[atlantic_df.ID.isin(top95duration.ID.tolist())], 
                         top95duration, on = ['ID', 'Name'])
top95duration['categoryStr'] = ['Category ' + str(cat)[0] for cat in top95duration.Category]

# boundaries of the scatterplot to fall within the map
boundaries = (atlantic_df.Longitude.min(), atlantic_df.Longitude.max(), \
              atlantic_df.Latitude.min(), atlantic_df.Latitude.max())

# lists for coloring scatterpoints based on hurricane Category
colors0 = [mcolors.CSS4_COLORS['midnightblue'], mcolors.CSS4_COLORS['indigo'], \
           mcolors.CSS4_COLORS['purple'], mcolors.CSS4_COLORS['maroon'], \
           mcolors.CSS4_COLORS['orangered'], mcolors.CSS4_COLORS['orange']]
categoriesHurricane = ['Category 0', 'Category 1', \
                       'Category 2', 'Category 3', \
                       'Category 4', 'Category 5']
# dictionary for colors
c0 = dict(zip(categoriesHurricane, colors0))     

# plotting
hurricane_map = plt.imread('map.png')
fig0, ax = plt.subplots(figsize = (8, 8))
categoriesPlot = top95duration.groupby('categoryStr')

for cat, category in categoriesPlot:
    category.plot(ax = ax, kind = 'scatter',
                  x = 'Longitude', y = 'Latitude',
                  label = cat, color = c0[cat], 
                  alpha = 0.375, s = 5)
ax.set_title('Plotting The 95th Percentile of Longest-Lasting Hurricanes in the Atlantic Ocean')
# axis limits for plot set to min and max figures for latitude and longitude
ax.set_xlim(boundaries[0], boundaries[1])
ax.set_ylim(boundaries[2], boundaries[3])
ax.grid(linestyle = ':', linewidth = 1.25, color = 'grey')
plt.xlabel("Longitude")
plt.ylabel("Latitude")
ax.imshow(hurricane_map, zorder = 0, 
          extent = boundaries, aspect = 'auto')
fig0.savefig('95pctDurationHurricanes.png')

# visualized a map for bottom 5th percentile duration storms
bottom5duration = atlantic_df_aggr[atlantic_df_aggr.duration <= \
                                 atlantic_df_aggr.duration.quantile(0.05)].sort_values(by = ['duration'], ascending = False)
bottom5duration = pd.merge(atlantic_df[atlantic_df.ID.isin(bottom5duration.ID.tolist())], 
                           bottom5duration, on = ['ID', 'Name'])

fig1, ax = plt.subplots(figsize = (8, 8))
ax.scatter(bottom5duration.Longitude,
           bottom5duration.Latitude,
           zorder = 1, 
           s = bottom5duration.duration / 6, # adjust sizing to keep it relatively consistent with the top 95% map
           alpha = 0.50,
           # all hurricanes here are Category 0
           c = mcolors.CSS4_COLORS['midnightblue'])
ax.set_title('Plotting The 5th Percentile of Shortest Hurricanes in the Atlantic Ocean')
# axis limits for plot set to min and max figures for latitude and longitude
ax.set_xlim(boundaries[0], boundaries[1])
ax.set_ylim(boundaries[2], boundaries[3])
ax.grid(linestyle = ':', linewidth = 1.25, color = 'grey')
plt.xlabel("Longitude")
plt.ylabel("Latitude")
ax.imshow(hurricane_map, zorder = 0, 
          extent = boundaries, aspect = 'auto')
fig1.savefig('5pctDurationHurricanes.png')

## histogram
fig2, ax = plt.subplots(figsize = (8, 8))
bins = (1, 2, 3, 4, 5, 6)
ax.hist(atlantic_df_aggr.maxCategory[atlantic_df_aggr['maxCategory'] > 0], \
        bins = bins, align = 'left', \
        rwidth = 0.8, color = 'c')
ax.set_xticks(bins[:-1])
plt.title("Histogram of Hurricanes by Category 1950-2015") 
plt.xlabel("Category")
plt.ylabel("Frequency")
plt.show()
fig2.savefig('hurricaneCategoryHistogram.png')

## histogram, hurricanes by Category per year
fig3, ax = plt.subplots(figsize = (32, 8))
bins1 = np.linspace(1950, 2016, 67)
# data is lists of year values, per category
categoryYearData = [pd.DatetimeIndex(atlantic_df_aggr.initialDate[atlantic_df_aggr.maxCategory == 0]).year.tolist(), \
                    pd.DatetimeIndex(atlantic_df_aggr.initialDate[atlantic_df_aggr.maxCategory == 1]).year.tolist(), \
                    pd.DatetimeIndex(atlantic_df_aggr.initialDate[atlantic_df_aggr.maxCategory == 2]).year.tolist(), \
                    pd.DatetimeIndex(atlantic_df_aggr.initialDate[atlantic_df_aggr.maxCategory == 3]).year.tolist(), \
                    pd.DatetimeIndex(atlantic_df_aggr.initialDate[atlantic_df_aggr.maxCategory == 4]).year.tolist(), \
                    pd.DatetimeIndex(atlantic_df_aggr.initialDate[atlantic_df_aggr.maxCategory == 5]).year.tolist()]
    
# plotting
ax.hist(categoryYearData, bins = bins1, 
        label = ['Category 0', 'Category 1', \
                 'Category 2', 'Category 3', \
                 'Category 4', 'Category 5'], \
        align = 'left', rwidth = 10)
ax.set_xticks(np.arange(1950, 2016, step = 1))
ax.set_yticks(np.arange(0, 21, step = 1))
plt.xlim([1949, 2016])
plt.title("Histogram of Hurricanes by Category and Year") 
plt.xlabel("Year")
plt.ylabel("Frequency")
plt.legend(loc = 'upper right')
plt.show()
fig3.savefig('hurricaneCategoryByYearHistogram.png')

## bar plot, storm duration per category
categoryDurationData0 = [atlantic_df_aggr.duration[atlantic_df_aggr.maxCategory == 0].tolist(), \
                         atlantic_df_aggr.duration[atlantic_df_aggr.maxCategory == 1].tolist(), \
                         atlantic_df_aggr.duration[atlantic_df_aggr.maxCategory == 2].tolist(), \
                         atlantic_df_aggr.duration[atlantic_df_aggr.maxCategory == 3].tolist(), \
                         atlantic_df_aggr.duration[atlantic_df_aggr.maxCategory == 4].tolist(), \
                         atlantic_df_aggr.duration[atlantic_df_aggr.maxCategory == 5].tolist()]

categoryDurationData1 = pd.DataFrame([list(map(np.min, categoryDurationData0)), 
                                      list(map(np.mean, categoryDurationData0)), 
                                      list(map(np.median, categoryDurationData0)), 
                                      list(map(np.max, categoryDurationData0))], \
                                      columns = [0, 1, 2, 3, 4, 5], \
                                      index = ['Min', 'Mean', 'Median', 'Max']) 

categoryDurationData2 = pd.DataFrame(categoryDurationData0).transpose()    

# plotting
fig4, axes = plt.subplots(2, 3, figsize = (16, 8))
fig4.suptitle('Storm Duration (hours) by Category', size = 'large')

# set a universal y-limit equal to the largest number in the dataset, rounded to the nearest hundred, plus 50
yLimit = round(atlantic_df_aggr.duration.max(),  -2) + 50
for idx, (col, ax) in enumerate(zip(categoryDurationData2.columns, axes.flatten())):
    ax.bar(categoryDurationData2.index, categoryDurationData2[col])
    ax.set_ylim(0, yLimit)
    ax.set_yticks(np.arange(0, yLimit, step = 50))
    ax.text(0, yLimit - 200, 
            'Summary Stats:\n' + \
            str(categoryDurationData2[col].count()) + ' Storms\n' + \
            str(categoryDurationData1[col].loc['Min']) + ' hours minimum\n' + \
            str(categoryDurationData1[col].loc['Max']) + ' hours maximum\n' + \
            str(categoryDurationData1[col].loc['Median']) + ' hours median\n' + \
            str(round(categoryDurationData1[col].loc['Mean'], 2)) + ' hours mean\n', \
            size = 'x-small')
    ax.set_ylabel('Duration (hrs)', \
                  size = 'small')
    ax.set_title('Category ' + str(col))
    ax.set_xticks([])
    plt.subplots_adjust(wspace = 0.25, hspace = 0.25)
plt.show()
fig4.savefig('hurricaneDurationByCategoryHistogram.png')

## HeatMap
df_heatmap = hm.loadData()

# Landfall HeatMap
df_landfall = hm.hurricaneLandFall(df_heatmap)
hm.mapHurricane(df_landfall, "landfall.html")

# No Landfall HeatMap
df_no_landfall = hm.hurricaneNoLandFall(df_heatmap)
hm.mapHurricane(df_no_landfall, "no_landfall.html"
