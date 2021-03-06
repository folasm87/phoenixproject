import numpy as np
import pandas as pd

def readData(dataset_path):
    # read data
    atlantic_df = pd.read_csv(dataset_path)
        
    # set as data frame
    atlantic_df = pd.DataFrame(atlantic_df)
    return atlantic_df
    
def condenseData(atlantic_df):
    # only select hurricanes from 1950 onwards, when they began naming storms
    atlantic_df = atlantic_df[atlantic_df['Date'] > 19500000]
        
    # subsetting relevant variables/columns
    atlantic_df = atlantic_df[["ID", "Name", "Date", "Time", \
                               "Event", "Status", "Latitude", \
                               "Longitude", "Maximum Wind", \
                               "Minimum Pressure"]]
    return atlantic_df
    
def removeWhitespace(data):
    # using str.strip() method on all columns labeled 'object' to remove whitespace for easier sorting/querying later on
    # print(data.dtypes)
    data['ID'] = data['ID'].str.strip()
    data['Name'] = data['Name'].str.strip()
    data['Event'] = data['Event'].str.strip()
    data['Status'] = data['Status'].str.strip()
    data['Longitude'] = data['Longitude'].str.strip()
    data['Latitude'] = data['Latitude'].str.strip()
        
    return data
        
def processMaxWind(data):
    # process 'Maximum Wind' from int to float
    data['Maximum Wind'] = [float(mw) for mw in data['Maximum Wind']]
        
    return data 
    
def createAdditionalColumns(data):
    # process datetime
    # start with turning time into strings, to enforce proper %H%M format
    data['Time'].unique()

    ## convert longitude and latitude to decimal format for plotting
    # initial datetime conversion in the same loop
    for i in range(len(data)):
        # time
        # ints under four digits when converted to strings need to be prepended with 4 - len() zeroes
        timeClean = data.iloc[i, data.columns.get_loc('Time')]
        if len(str(timeClean)) == 4:
            data.iloc[i, data.columns.get_loc('Time')] = str(timeClean)
        else:
            zeroes = '0' * (4 - len(str(timeClean)))
            data.iloc[i, data.columns.get_loc('Time')] = zeroes + str(timeClean)
        
        # longitude
        longClean = data.iloc[i, data.columns.get_loc('Longitude')]
        if longClean[-1] == 'W':
            data.iloc[i, data.columns.get_loc('Longitude')] = float(longClean.replace('W', '')) * -1
        else:
            data.iloc[i, data.columns.get_loc('Longitude')] = float(longClean.replace('E', ''))
    
        # latitude
        latClean = data.iloc[i, data.columns.get_loc('Latitude')]
        if latClean[-1] == 'N':
            data.iloc[i, data.columns.get_loc('Latitude')] = float(latClean.replace('N', ''))
        else:
            data.iloc[i, data.columns.get_loc('Latitude')] = float(latClean.replace('S', '')) * -1

    # second loop for creating datetime and category variables
    # use 0 for non-hurricanes (tropical storms, etc.)
    # 1: Maximum W 64 <= x < 82
    # 2: 82 <= x < 95
    # 3: 95 <= x < 112
    # 4: 112 <= x < 136
    # 5: x >= 136

    datetime_list = []
    category_list = []
    for j in range(len(data)):
        # create a datetime list by combining variables 'Date' and 'Time'
        datetime_list.append(str(data.iloc[j, data.columns.get_loc('Date')]) + ' ' + data.iloc[j, data.columns.get_loc('Time')])
    
        # create a list of hurricane categories, based on wind value
        windValue = data.iloc[j, data.columns.get_loc('Maximum Wind')]
    
        if data.iloc[j, data.columns.get_loc('Status')] != 'HU':
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
    data['Datetime'] = datetime_list
    data['Datetime'] = pd.to_datetime(data['Datetime'], format = '%Y%m%d %H%M')
    data['Category'] = category_list

    # replace -999 values for 'Minimum Pressure' with NaN
    data = data.replace(-999, pd.NA)

    # clean longitude data, as some points are <-180
    # e.g. -359.1 (359.1W) should be 0.9 (0.9E)
    data['Longitude'].loc[lambda i: i < -180] = data['Longitude'].loc[lambda i: i < -180] + 360
        
    return data

def hurricaneQuery(data, varCondition, varMaxMin, n):
    ### uses aggregated dataset 'atlantic_df_aggr'
    
    # varCondition = str, variable used as a condition, to search by
    ## e.g. varCondition would be windspeed, if you are searching for storms with the highest windspeeds
    # varMaxMin = bool, used to find high/low values
    ## True for ascending, if you are searching for the lowest values, e.g. lowest pressures
    ## False for descending, if you are searching for the highest values, e.g. highest windspeeds
    # n = int, number of variables to retrieve
    
    return data[['ID', 'Name', varCondition]].sort_values(by = [varCondition], ascending = varMaxMin).head(n)
    
def experiments(data):
    # trying groupby() for initial exploratory analysis
    print(data.groupby('ID').mean())
    print(data.groupby('Status').mean())

# Cleaning the dataset
data = readData("atlantic.csv")
data = condenseData(data)
data = removeWhitespace(data)
data = processMaxWind(data)
data = createAdditionalColumns(data)

# experiments(data)
# data.to_csv('atlantic_hurricanes.csv')
