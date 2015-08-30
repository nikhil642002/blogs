from scipy.spatial.distance import pdist
from sklearn.metrics import pairwise_distances
from sklearn.feature_extraction.text import TfidfVectorizer
from constants import (HTML_TOKENS, )
import numpy as np
import re
from collections import Counter


class PostSimilarityAnalyzer(object):

    def __init__(self, preprocessor):
        """Do the bare minimum of cleaning creating a vectorizer and
        setting the internal corpus to use
        """
        self.tfv = TfidfVectorizer(stop_words='english')
        self.corpus = preprocessor.content_events
        self.cleaned_corpus = {}

    def build(self):
        """
        Run the pipeline to compute the internal model.
        """
        self.clean_corpus()
        self.vectorize_corpus()
        self.compute_pairwise_distances()
        self.compute_sorted_distances()
        self.compute_content_map()

    def clean_corpus(self):
        """
        Clean up the original corpus
        """
        self.cleaned_corpus = {}
        for post in self.corpus:
            pc = re.sub(r'[\n\r\t]', ' ', post['content'])
            pc = re.sub(r'<[^>]+>', '', pc)
            pc = re.sub(r'&[a-zA-Z]+;', '', pc)
            pc = re.sub(r'[^0-9a-zA-Z ]', '', pc)
            pc = ' '.join([wd for wd in pc.split() if wd not in HTML_TOKENS])
            self.cleaned_corpus[post['post']] = pc.lower()

    def vectorize_corpus(self):
        """"
        Vectorize the cleaned corpus
        """
        self.tfvects = self.tfv.fit_transform(self.cleaned_corpus.values())

    def compute_pairwise_distances(self):
        """
        Compute the pairwise distances
        """
        self.tfid_dist_matrix = pairwise_distances(self.tfvects, metric='cosine')

    def compute_sorted_distances(self):
        """
        Compute the pairwise distances and sort
        """
        self.sorted_indexes_by_cos_dist = [np.argsort(x) for x in self.tfid_dist_matrix]

    def compute_content_map(self):
        """
        Compute content dictionary
        """
        self.sim_dict_content = {self.cleaned_corpus.keys()[idx]: ' '.join([wd for wd in self.cleaned_corpus.values()[ix].split()][:15])  for (idx, ix) in enumerate([sd[1] for sd in self.sorted_indexes_by_cos_dist])}

    def get_similarity_group_counter(self):
        """
        Return a counter for storing the similarity groups"""
        return Counter(self.sim_dict_content.values())
    
