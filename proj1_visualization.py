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
from proj1 import atlantic_df, atlantic_df_aggr
import HeatMap as hm

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
#fig0.savefig('95pctDurationHurricanes.png')

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
#fig1.savefig('5pctDurationHurricanes.png')

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
#fig2.savefig('hurricaneCategoryHistogram.png')

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
#fig3.savefig('hurricaneCategoryByYearHistogram.png')

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
#fig4.suptitle('Storm Duration (hours) by Category', size = 'large')

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
hm.mapHurricane(df_no_landfall, "no_landfall.html")
    
    
    