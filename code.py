# -*- coding: utf-8 -*-
"""
Project: Hurricanes

Team: Phoenix

Names: Steph Verbout, Mark Folashade, Lindsey Shavers, Khoi Tran

computing ID: mf4us, kt2np, sv8jy, lns4pr


"""


import numpy as np
import pandas as pd
import matplotlib.pyplot as plt



atlantic_df = pd.read_csv('atlantic.csv')

# set as data frame
atlantic_df = pd.DataFrame(atlantic_df)



atlantic_df
for col in atlantic_df.columns: 
    print(col)


# 1950 onwards, when they began naming storms
atlantic_df = atlantic_df[atlantic_df['Date'] > 19500000]

atlantic_df = atlantic_df[["ID", "Name", "Date", "Time", "Event", "Status", "Latitude", "Longitude", "Maximum Wind", "Minimum Pressure"]]


atlantic_df.groupby('ID').mean()

atlantic_df.groupby('Status').mean()


atlantic_df['ID'] = atlantic_df['ID'].str.strip()
atlantic_df['Name'] = atlantic_df['Name'].str.strip()
atlantic_df['Event'] = atlantic_df['Event'].str.strip()
atlantic_df['Status'] = atlantic_df['Status'].str.strip()
atlantic_df['Longitude'] = atlantic_df['Longitude'].str.strip()
atlantic_df['Latitude'] = atlantic_df['Latitude'].str.strip()

#add new column for year only
atlantic_df['Year'] = atlantic_df['Date'].astype(str).str[0:4]
#df.head()

#add new column for month only
atlantic_df['Month'] = atlantic_df['Date'].astype(str).str[4:6]


#add new column for day only
atlantic_df['Day'] = atlantic_df['Date'].astype(str).str[6:8]


#cleaning longitude and latitude

atlantic_df['Longitude'] = atlantic_df['Longitude'].replace({'N':''}, regex=True)
atlantic_df['Longitude'] = atlantic_df['Longitude'].replace({'S':''}, regex=True)
atlantic_df['Longitude'] = atlantic_df['Longitude'].replace({'W':''}, regex=True)
atlantic_df['Longitude'] = atlantic_df['Longitude'].replace({'E':''}, regex=True)


atlantic_df['Latitude'] = atlantic_df['Latitude'].replace({'N':''}, regex=True)
atlantic_df['Latitude'] = atlantic_df['Latitude'].replace({'S':''}, regex=True)
atlantic_df['Latitude'] = atlantic_df['Latitude'].replace({'W':''}, regex=True)
atlantic_df['Latitude'] = atlantic_df['Latitude'].replace({'E':''}, regex=True)


atlantic_df.dtypes



#atlantic_df[["Name", "Date", "Time", "Event", "Status", "Latitude", "Longitude", "Maximum Wind", "Minimum Pressure"]]

save_df = 'atlantic_modified12.csv'

atlantic_df.to_csv(save_df)


df = pd.read_csv(save_df)
print("DF:")
print(df)

#1. How many hurricanes make landfall.
## count(select unique ID (or name) by Status = 'HU' and Event = 'L')

filter1 = df['Status']=='HU'
filter2 = df['Event']=='L'
df_1 = df.loc[filter1&filter2]
#df_1 = df.where(filter1&filter2, inplace = True)
print("DF1:")
print(df_1)
df_2 = df_1.drop_duplicates(subset=["ID"])


n = len(pd.unique(df_2['ID'])) 
  
print("Number of hurricanes :",  
      n)

save_2 = 'temp1.csv'

df_2.to_csv(save_2)


#2. How many hurricanes reach a certain magnitude, but don’t necessarily make landfall.


#print(df.head())