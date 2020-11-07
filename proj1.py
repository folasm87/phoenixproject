#!/usr/bin/env python
# coding: utf-8

# In[1]:


import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


# In[84]:


atlantic_df = pd.read_csv('atlantic.csv')

# set as data frame
atlantic_df = pd.DataFrame(atlantic_df)


# In[85]:


atlantic_df
for col in atlantic_df.columns: 
    print(col)


# In[86]:


atlantic_df = atlantic_df[atlantic_df['Date'] > 19500000]
# 1950 onwards, when they began naming storms
atlantic_df = atlantic_df[["ID", "Name", "Date", "Time", "Event", "Status", "Latitude", "Longitude", "Maximum Wind", "Minimum Pressure"]]
# subsetting relevant variables/columns


# In[89]:


atlantic_df.groupby('ID').mean()

atlantic_df.groupby('Status').mean()


# In[90]:


# using str.strip() method on all columns labeled 'object' to remove whitespace for easier sorting/querying later on
atlantic_df['ID'] = atlantic_df['ID'].str.strip()
atlantic_df['Name'] = atlantic_df['Name'].str.strip()
atlantic_df['Event'] = atlantic_df['Event'].str.strip()
atlantic_df['Status'] = atlantic_df['Status'].str.strip()
atlantic_df['Longitude'] = atlantic_df['Longitude'].str.strip()
atlantic_df['Latitude'] = atlantic_df['Latitude'].str.strip()


# In[91]:


atlantic_df.dtypes
# convert date and time to datetime format


# In[75]:


atlantic_df[["Name", "Date", "Time", "Event", "Status", "Latitude", "Longitude", "Maximum Wind", "Minimum Pressure"]]


# In[ ]:




