import unittest
import pandas as pd
import numpy as np
from CleanData import *


class CleanDataTest(unittest.TestCase):
    
    # test read_data function 
    def test_readData(self):
        data = readData("atlantic.csv")
        
        # assert that the read data has the correct columns
        assert list(data.columns) == ['ID', 'Name', 'Date', 'Time', 'Event', 
                                      'Status', 'Latitude','Longitude', 
                                      'Maximum Wind', 'Minimum Pressure', 
                                      'Low Wind NE','Low Wind SE', 
                                      'Low Wind SW', 'Low Wind NW', 
                                      'Moderate Wind NE', 'Moderate Wind SE', 
                                      'Moderate Wind SW', 'Moderate Wind NW',
                                      'High Wind NE', 'High Wind SE', 
                                      'High Wind SW', 'High Wind NW'
                                      ]
        
    
    # test condense_data function
    def test_condenseData(self):
        data = readData("atlantic.csv")
        
        condensed_data = condenseData(data)
        
        # assertions for all remaining columns in df
        assert list(condensed_data.columns) == ["ID", "Name", "Date", "Time",
                                                "Event", "Status", "Latitude",
                                                "Longitude", "Maximum Wind",
                                                "Minimum Pressure"
                                                ]
        
        # assertions for columns that should have been removed from df
        assert "Low Wind SE" not in condensed_data.columns
        assert "Low Wind SW" not in condensed_data.columns
        
 
    # test create_additional_columns function 
    def test_createAdditionalColumns(self):
        data = readData("atlantic.csv")
        data = condenseData(data)
        data = removeWhitespace(data)
        data = processMaxWind(data)
        data = createAdditionalColumns(data)

        
        # assertions for all added columns
        assert "Datetime" in data.columns
        assert "Category" in data.columns
        
    
if __name__ == '__main__':
    unittest.main()  