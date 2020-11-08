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
import folium
from folium import plugins
import seaborn as sns
import webbrowser

atlantic_df = pd.read_csv('atlantic.csv')

# set as data frame
atlantic_df = pd.DataFrame(atlantic_df)


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


print(atlantic_df.dtypes)


save_df = 'atlantic_modified35.csv'

atlantic_df.to_csv(save_df)


df = pd.read_csv(save_df)


#1. How many hurricanes make landfall.
## count(select unique ID (or name) by Status = 'HU' and Event = 'L')

filter_hurricane = df['Status']=='HU'
filter_landfall = df['Event']=='L'
filter_no_landfall = df['Event'] != 'L'

df_1 = df.loc[filter_hurricane&filter_landfall]


n = len(pd.unique(df_1['ID'])) 
  
print("Number of hurricanes :", n)


df_save = df_1.drop_duplicates(subset=['ID'], keep='last', inplace=False)
save_2 = 'uniq10.csv'

df_save.to_csv(save_2)


atlanticDF = df_save[["Latitude", "Longitude"]]

#print(atlanticDF)


#HeatMap of Hurricanes that made landfall

m = folium.Map(location = [37.773972, -122.431297], zoom_start = 13)


m.add_children(plugins.HeatMap(atlanticDF, radius=15))

m.save("mymap.html")
webbrowser.open_new_tab("mymap.html")

#print(map_van)

def cmp(x,y):
     return x==y and len(x)>1
 
def unique(list1): 
    list_set = set(list1) 
    # convert the set to the list 
    unique_list = (list(list_set)) 
    return unique_list

df_unique_id = unique(df_save['ID'].tolist())

print(df_unique_id)
n = len(df_unique_id) 
  
print("Number of hurricanes(2) :",  
      n)

#2. How many hurricanes reach a certain magnitude, but don’t necessarily make landfall.
df_2 = df.loc[filter_hurricane&filter_no_landfall]

df_no_landfall = df_2.loc[~df_2['ID'].isin(df_1['ID'])]

n = len(pd.unique(df_no_landfall['ID'])) 
  
print("Number of hurricanes to reach a certain magnitude but no landfall:", n)
