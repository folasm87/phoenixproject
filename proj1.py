# -*- coding: utf-8 -*-
"""
Created on Sat Nov  7 13:57:05 2020

@author: Khoi Tran (kt2np)
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

# ints under four digits when converted to strings need to be prepended with 4 - len() zeroes
for i in range(len(atlantic_df['Time'])):
    if len(str(atlantic_df.loc[atlantic_df.index[i], 'Time'])) == 4:
        atlantic_df.loc[atlantic_df.index[i], 'Time'] = str(atlantic_df.loc[atlantic_df.index[i], 'Time'])
    else:
        zeroes = '0' * (4 - len(str(atlantic_df.loc[atlantic_df.index[i], 'Time'])))
        atlantic_df.loc[atlantic_df.index[i], 'Time'] = zeroes + str(atlantic_df.loc[atlantic_df.index[i], 'Time'])

datetime_list = []
for i in range(len(atlantic_df)):
    datetime_list.append(str(atlantic_df.loc[atlantic_df.index[i], 'Date']) + ' ' + atlantic_df.loc[atlantic_df.index[i], 'Time'])

atlantic_df['Datetime'] = datetime_list
atlantic_df['Datetime'] = pd.to_datetime(atlantic_df['Datetime'], format = '%Y%m%d %H%M')
