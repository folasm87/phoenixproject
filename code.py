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

#define column name list we're interested in
columns = ["Name", "Date", "Time", "Event", "Status", "Latitude", "Longitude", "Maximum Wind", "Minimum Pressure"]

#read in data from "atlantic.csv" using the columns we're interested in and skipping rows until year 1950
df = pd.read_csv("atlantic.csv", usecols = columns, skiprows = range(1,21880))

df.head()

#add new column for year only
df['Year'] = df['Date'].astype(str).str[0:4]
df.head()

#add new column for month only
df['Month'] = df['Date'].astype(str).str[4:6]
df.head()


#want to plot number of tropical cyclones each month for all years ?groupby?
