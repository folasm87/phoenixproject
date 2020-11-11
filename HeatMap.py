# -*- coding: utf-8 -*-



import pandas as pd
import folium
from folium import plugins
import webbrowser
import CleanData as cleanData



def loadData():
    atlantic_df_raw = cleanData.readData('atlantic.csv')

    atlantic_df = cleanData.condenseData(atlantic_df_raw)
    
    atlantic_df = cleanData.removeWhitespace(atlantic_df)
    
    atlantic_df = cleanData.processMaxWind(atlantic_df)
    
    atlantic_df = cleanData.createAdditionalColumns(atlantic_df)
    
    cleanData.writeData(atlantic_df, 'atlantic_df.csv')

    df = cleanData.readData('atlantic_df.csv')
    
    return df



#1. How many hurricanes make landfall.
def hurricaneLandFall(data):
    filter_hurricane = data['Status']=='HU'
    filter_landfall = data['Event']=='L'
    df_landfall = data.loc[filter_hurricane&filter_landfall]
    df_landfall = df_landfall.drop_duplicates(subset=['ID'], keep='last', inplace=False)
    return df_landfall
    

#2. How many hurricanes reach a certain magnitude, but don’t necessarily make landfall.
def hurricaneNoLandFall(data):
    filter_hurricane = data['Status']=='HU'
    filter_no_landfall = data['Event'] != 'L'
    df_landfall = hurricaneLandFall(data)
    df_no_landfall = data.loc[filter_hurricane&filter_no_landfall]
    df_no_landfall = df_no_landfall.loc[~df_no_landfall['ID'].isin(df_landfall['ID'])]
    df_no_landfall = df_no_landfall.drop_duplicates(subset=['ID'], keep='last', inplace=False)
    return df_no_landfall


#HeatMap of Hurricanes
def mapHurricane(data, map_path):
    df_Coord = data[["Latitude", "Longitude"]]
    map_hurricane = folium.Map(location = [25.7617, -80.191788], zoom_start = 13)
    map_hurricane.add_child(plugins.HeatMap(df_Coord, radius=15))
    map_hurricane.save(map_path)
    webbrowser.open_new_tab(map_path)



def unique(list1): 
    list_set = set(list1) 
    # convert the set to the list 
    unique_list = (list(list_set)) 
    return unique_list

def printNumHurricanes(data, message):  
    n = len(data['ID'])
    print(message + " " + str(n))
    
def printUniqueHurricanes(data, message):
    n = len(pd.unique(data['ID']))
    print(message + " " + str(n))


def printUniqueMethodHurricanes(data, message):
    df_unique_id = unique(data['ID'].tolist())
    #print(df_unique_id)
    n = len(df_unique_id) 
    print(message + " " + str(n))





"""

df = loadData()

df_landfall = hurricaneLandFall(df)
#mapHurricane(df_landfall, "landfall.html")
message1 = "Number of hurricanes to make Landfall:"
printNumHurricanes(df_landfall, message1)
#printUniqueHurricanes(df_landfall, message1)
#printUniqueMethodHurricanes(df_landfall, message1)

df_no_landfall = hurricaneNoLandFall(df)
#mapHurricane(df_no_landfall, "no_landfall.html")
message2 = "Number of hurricanes to reach a certain magnitude but no landfall:"
printNumHurricanes(df_no_landfall, message2)
#printUniqueHurricanes(df_no_landfall, message2)
#printUniqueMethodHurricanes(df_no_landfall, message2)
"""

