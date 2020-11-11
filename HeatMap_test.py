# -*- coding: utf-8 -*-


import unittest
import HeatMap as hm


class HeatMapTest(unittest.TestCase):
    
    
    #Test to determine that all values in the landfall dataframe 'Event' column have a value of 'L'
    def testLandFallCols(self):
        df = hm.loadData()
        df_landfall = hm.hurricaneLandFall(df)
        found = df_landfall[df_landfall['Event'].str.contains('L')]
        land_count = len(found)
        
        df_unique_id = hm.unique(df_landfall['ID'].tolist())
        id_count = len(df_unique_id) 
        self.assertEqual(land_count, id_count)
    
    
    #Test to determine that all values in the no_landfall dataframe 'Event' column do NOT have a value of 'L'
    def testNoLandFallCols(self):
        df = hm.loadData()
        df_no_landfall = hm.hurricaneNoLandFall(df)
        found = df_no_landfall[df_no_landfall['Event'].str.contains('L', na=False)]
        land_count = len(found)
        
        self.assertEqual(land_count, 0)
    
if __name__ == '__main__':
    unittest.main()      