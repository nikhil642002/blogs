# import the package
import analysis
from analysis import (activity_patterns, graph_analysis, nlp, preprocessing)
from analysis.preprocessing import Preprocessor
from analysis.activity_patterns import  ActivityAnalyzer
from analysis.nlp import  PostSimilarityAnalyzer
from analysis.graph_analysis import  GraphAnalyzer
import numpy as np
import snap


import unittest

class TestAnalysis(unittest.TestCase):
    preproc = Preprocessor('./data/wrangler_test.json')
    patterns = ActivityAnalyzer(preproc)
    text_proc = PostSimilarityAnalyzer(preproc)
    graph_proc = GraphAnalyzer(patterns)
    
    def test_analysis_preprocessing(self):
        self.assertTrue(len(self.preproc.user_total_views) == 69)
        self.assertTrue((629158849234, 148355) in self.preproc.user_total_views)

    def test_analysis_activity(self):
        self.patterns.build()
        test_list = [162.,    1.,    8.,    1.,   16.,    1.]
        self.assertTrue(max(self.patterns.cluster_counts) >= 150)

    def test_nlp(self):
        self.text_proc.build()
        most_common_two = self.text_proc.get_similarity_group_counter().most_common(n=2)
        self.assertTrue(most_common_two[0] == (u'24th october 2014 121am photo when i finished reading the last page all i felt', 5))
        self.assertTrue(most_common_two[1] == (u'29th october 2014 1216pm blogging 201 day 8 make your home a hub todays assignment', 4))

    def test_graph(self):
        self.graph_proc.build()
        self.assertTrue(self.graph_proc.modularity >= 0.60)
        
        
        

if __name__ == '__main__':
    unittest.main()
