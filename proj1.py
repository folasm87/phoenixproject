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

atlantic_df = pd.read_csv('atlantic.csv')

# set as data frame
atlantic_df = pd.DataFrame(atlantic_df)
    
## cleaning data
# 1950 onwards, when they began naming storms
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

# trying groupby() for exploratory analysis
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
    if len(str(atlantic_df.loc[atlantic_df.index[i], 'Time'])) == 4:
        atlantic_df.loc[atlantic_df.index[i], 'Time'] = str(atlantic_df.loc[atlantic_df.index[i], 'Time'])
    else:
        zeroes = '0' * (4 - len(str(atlantic_df.loc[atlantic_df.index[i], 'Time'])))
        atlantic_df.loc[atlantic_df.index[i], 'Time'] = zeroes + str(atlantic_df.loc[atlantic_df.index[i], 'Time'])
        
    # longitude
    if atlantic_df.loc[atlantic_df.index[i], 'Longitude'][-1] == 'W':
        atlantic_df.loc[atlantic_df.index[i], 'Longitude'] = float(atlantic_df.loc[atlantic_df.index[i], 'Longitude'].replace('W', '')) * -1
    else:
        atlantic_df.loc[atlantic_df.index[i], 'Longitude'] = float(atlantic_df.loc[atlantic_df.index[i], 'Longitude'].replace('E', ''))
    
    # latitude
    if atlantic_df.loc[atlantic_df.index[i], 'Latitude'][-1] == 'N':
        atlantic_df.loc[atlantic_df.index[i], 'Latitude'] = float(atlantic_df.loc[atlantic_df.index[i], 'Latitude'].replace('N', ''))
    else:
        atlantic_df.loc[atlantic_df.index[i], 'Latitude'] = float(atlantic_df.loc[atlantic_df.index[i], 'Latitude'].replace('S', '')) * -1

# second loop for creating datetime variable in proper format
datetime_list = []
for i in range(len(atlantic_df)):
    datetime_list.append(str(atlantic_df.loc[atlantic_df.index[i], 'Date']) + ' ' + atlantic_df.loc[atlantic_df.index[i], 'Time'])

atlantic_df['Datetime'] = datetime_list
atlantic_df['Datetime'] = pd.to_datetime(atlantic_df['Datetime'], format = '%Y%m%d %H%M')

# clean longitude data, as some points are <-180
# e.g. -359.1 (359.1W) should be 0.9 (0.9E)
atlantic_df['Longitude'].loc[lambda s: s < -180] = atlantic_df['Longitude'].loc[lambda x: x < -180] + 360


# view new datatypes
print(atlantic_df.dtypes)

# view min and max longitude and latitude points
# use these figures to download a map from openstreetmap.org
boundaries = ((atlantic_df.Longitude.min(), atlantic_df.Longitude.max(), atlantic_df.Latitude.min(), atlantic_df.Latitude.max()))

hurricane_map = plt.imread('map.png')
fig, ax = plt.subplots(figsize = (8, 8))
ax.scatter(atlantic_df.Longitude, atlantic_df.Latitude, zorder = 1, alpha = 0.2, c = 'b', s = 10)
ax.set_title('Plotting Hurricane Data on the Atlantic Ocean Map')
# axis limits for plot set to min and max figures for latitude and longitude
ax.set_xlim(boundaries[0], boundaries[1])
ax.set_ylim(boundaries[2], boundaries[3])
ax.imshow(hurricane_map, zorder = 0, extent = boundaries, aspect = 'auto')
