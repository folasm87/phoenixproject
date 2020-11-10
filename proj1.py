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
import datetime
from math import sin, cos, sqrt, atan2, radians
# # install necessary packages
# import folium
# from folium import plugins
# import seaborn as sns
# import webbrowser
# import datetime

atlantic_df = pd.read_csv('atlantic.csv')

# set as data frame
atlantic_df = pd.DataFrame(atlantic_df)
    
### Cleaning data
# only select hurricanes from 1950 onwards, when they began naming storms
atlantic_df = atlantic_df[atlantic_df['Date'] > 19500000]
# subsetting relevant variables/columns
atlantic_df = atlantic_df[["ID", "Name", "Date", "Time", "Event", "Status", "Latitude", "Longitude", "Maximum Wind", "Minimum Pressure"]]
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
        category_list.append(0)
    else:
        if windValue > 136:
            category_list.append(5)
        elif windValue > 112:
            category_list.append(4)
        elif windValue > 95:
            category_list.append(3)
        elif windValue > 82:
            category_list.append(2)
        elif windValue > 62:
            category_list.append(1)
        else:
            category_list.append(0)
    
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
    durationList = [subset_df.Datetime.min(), subset_df.Datetime.max(), subset_df.Datetime.max() - subset_df.Datetime.min()]
    
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

##
# consider further aggregation of totalDistanceKm, netDistanceKm, etc.
# potential variable for time spent at max category(?)
# maybe a shape drawn by the path and area(?)
# variable(s) w/ list for path (lat/long)

### VISUALIZATION
# view min and max longitude and latitude points
# use these figures to download a map from openstreetmap.org
# visualize a map for top 20 longest duration storms
# color = storm ID/name, size = category, alpha = landfall


###UNCOMMENT BELOW FOR PLOTS###
# boundaries = (atlantic_df.Longitude.min(), atlantic_df.Longitude.max(), atlantic_df.Latitude.min(), atlantic_df.Latitude.max())

# ## preliminary plot w/ all data points
# hurricane_map = plt.imread('map.png')
# fig, ax = plt.subplots(figsize = (8, 8))
# ## adjust alpha, color, size for future plots
# # alpha = windspeed
# # color = storm ID/name
# # size = category/status(?)
# ax.scatter(atlantic_df.Longitude, 
#            atlantic_df.Latitude, 
#            zorder = 1, alpha = 0.2, 
#            c = 'b', s = 10)
# ax.set_title('Plotting Hurricane Data on the Atlantic Ocean Map')
# # axis limits for plot set to min and max figures for latitude and longitude
# ax.set_xlim(boundaries[0], boundaries[1])
# ax.set_ylim(boundaries[2], boundaries[3])
# ax.imshow(hurricane_map, zorder = 0, extent = boundaries, aspect = 'auto')

# ## histogram
# fig, ax = plt.subplots(1,1)
# bins = (1,2,3,4,5,6)
# ax.hist(atlantic_df.Category[atlantic_df['Category'] > 0], bins = bins, align = 'left', rwidth = 0.8, color = 'c')
# ax.set_xticks(bins[:-1])
# plt.title("Histogram of Hurricanes by Category 1950-2015") 
# plt.xlabel("Category")
# plt.ylabel("Frequency")
# plt.show()

# ## add heatmap
# landfallDF = df_landfall[["Latitude", "Longitude"]]
# map_landfall = folium.Map(location = [25.7617, -80.191788], zoom_start = 13)
# map_landfall.add_children(plugins.HeatMap(landfallDF, radius=15))
# map_landfall.save("landfall.html")
# webbrowser.open_new_tab("landfall.html")
###UNCOMMENT ABOVE FOR PLOTS###

## saving dataset
# atlantic_df.to_csv('atlantic_hurricanes.csv')
## saving aggregate dataset
# atlantic_df_aggr.to_csv('atlantic_hurricanes_aggr.csv')
