# Blog Analaysis Package

This is the code base used for analysis of blog posts from WordPress. The analysis consists of: 1)pre-processing which
places the json events into a Python Pandas dataframe; 2) temporal sequence analysis which pulls out distinct temporal
event patterns and does a K-Means clustering of these; 3) a text similarity analysis which pulls out the similar posts;
and 4) and graph based analysis which pulls out subgraphs using interactions around posts and blog follows.

## Prerequisites

This distribution supports either MacOS or Linux. The MacOSX assumes that Python Anaconda package manager is installed. This is a simplifying assumption that allows me to sidestep some of the arduous install involved in getting all the packages (e.g. numpy, scipy, snap.py) together in one environment.

The Linux install makes no such assumption.

## Building

To put everything together, running

      make deps check

will create the python virtualenv under anaconda, download snap.py and run a small set of tests.

On `Linux` run

      sudo make deps

then

      make check

## Organization

The distribution as mentioned is split into four components. The Python modules that implement these pieces are stored in
the `analysis` subdirectory. Each module has a main class which provides a build method that constructs a set of internal lists and tables that are used the
analysis. A class implements additional functionality -- K-Means clustering or graph rendering -- that are specific to its analysis.

*preprocessing.py*. Parses the json of the original records and places them into a dataframe and other structures that are used in the subsequent analyses.
The main class is Preprocessor which parses the blog json data and creates and internal Pandas dataframe used by subsequent analyses. An instance of Preprocessor is
created by supplying the path to the json file containing the blog event information.
    
*activity_patterns.py*. Teases out the temporal patterns and does the temporal pattern clustering. The main class is ActivityAnalyzer. An instance of
ActivityAnalyzer is created by providing an instance of Preprocessor that has run its `build` method. Besides build, ActivityAnalyzer provides
a `compute_clusters method` that computes the set of temporal actvity clusters. This is accessed by the cluster member variable computed during each invocation of compute_clusters.

*nlp.py*. Constructs the tfidf vectors and computes the pairwise distances for the posts. The main class is PostSimilarityAnalyzer. Instances of the class are instantiated by
providing an instance of Preprocessor that has run the `build` method. The `get_similarity_group_counter` method provides a table storing posts grouped by similarity.
    
*graph_analysis.py*. This contains routines to create the allegrographdb nodes and it also does the community detection. The main class is GraphAnalyzer. A GraphAnalyzer instance
is created by providing an instance of ActivityAnalyzer on which the `build` method has been run. GraphAnalyzer provides a `build` method that computes the core graph nodes, edges and freatures. The `display_summary_graph` method displays the larger graphs provided in the writeup which show all the nodes. The `display_community_graph` method displays the subgraph of the communitities detected around the paragraph-length blog posts. The method `write_triples` takes the name of a file to which rdf triple representation of the graph is stored in. The `build` method must be run to write the triples and generate the display. The member `modularity` stores a metric of the quality of the community subgraphs identified during `build`. The member variable `sig_communities_by_id` stores the nodes associated with each subgraph computed during the `build` method invocation. Analysis based upon this data is given in the writeup.

## Use of IPython Notebooks

The code can be invoked in an IPython Notebook to facilitate display of the graphs.

After running

      make deps check

start a notebook by running

      make notebook

As an example, the complete graph is displayed in the notebook using the following operations

      import analysis
      from analysis import (activity_patterns, graph_analysis, nlp, preprocessing)
      from analysis.preprocessing import Preprocessor
      from analysis.activity_patterns import  ActivityAnalyzer
      from analysis.nlp import  PostSimilarityAnalyzer
      from analysis.graph_analysis import  GraphAnalyzer
      import numpy as np
      import snap
      import matplotlib.pyplot as plt
      get_ipython().magic(u'matplotlib inline')

      # In[3]:

      preproc = Preprocessor('./data/wrangler_test.json')


      # In[4]:

      patterns = ActivityAnalyzer(preproc)
      patterns.build()



      # In[5]:

      text_proc = PostSimilarityAnalyzer(preproc)
      text_proc.build()


      # In[6]:

      graph_proc = GraphAnalyzer(patterns)
      graph_proc.build()


      # In[9]:

      graph_proc.diplay_summary_graph()




