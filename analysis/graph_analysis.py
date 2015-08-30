# coding: utf-8
import networkx as nx
import matplotlib.pyplot as plt
from collections import Counter
import time
import cPickle as pk
import snap


class GraphAnalyzer(object):
    """
    Provides a build function that creates data structures on which the 
    display and analysis depends.
    """
    def __init__(self, activity_analyzer):
        """
        Build from basic data provided from the pre-processing step
        """
        self.by_user_blog = activity_analyzer.by_user_blog
        self.by_user_post = activity_analyzer.by_user_post
        self.by_blog = activity_analyzer.by_blog
        self.content_events = activity_analyzer.preprocessor.content_events
        self.all_users = []
        self.all_blogs = []
        self.all_posts = []
        self.user_blog_links = []
        self.user_post_links = []
        self.node_to_id = {}
        self.id_to_node = {}
        self.events_df = activity_analyzer.preprocessor.events_df
        self.group_colors = [u'lightcoral', u'yellowgreen',  u'mediumslateblue', u'fuchsia', u'lemonchiffon', u'saddlebrown',
                                            u'seagreen',u'plum',u'midnightblue',u'darkolivegreen',u'darkslategray',u'cyan', u'azure',
                                            u'indianred',u'darkmagenta',u'steelblue',u'tomato']

    def build(self):
        """
        Construct intermediate structures.
        """
        self.all_users = [x[0] for x in self.by_user_blog.keys()]
        self.all_blogs = [x[1] for x in self.by_user_blog.keys()]
        self.all_posts = list(set([x[1] for x in self.by_user_post.keys()]))
        self.user_blog_links = {k:set([x[0] for x in vals]) for (k, vals) in self.by_user_blog.iteritems()}
        self.user_post_links = {k:set([x[0] for x in vals]) for (k, vals) in self.by_user_post.iteritems()}
        self.user_post_graph =  nx.Graph()
        self.all_post_users = list(set([x[0] for x in self.by_user_post.keys()]))
        self.nodes = list(set(self.all_post_users+self.all_posts))
        self.user_post_graph.add_nodes_from(self.nodes)

        self.up_likes = [k for (k, v) in self.user_post_links.items() if 'like' in v]
        self.up_comments = [k for (k, v) in self.user_post_links.items() if 'comment' in v]
        self.up_follows = [k for (k, v) in self.user_post_links.items() if 'follow' in v]
        self.up_posts = [k for (k, v) in self.user_post_links.items() if 'publish' in v]
        self.large_posts = Counter(self.events_df[self.events_df['content_len'] > 1000]['post'])
        self.up_posts_to_articles = [x for x in self.up_posts if x[1] in self.large_posts]
        self.up_comments_to_articles = [x for x in self.up_comments if x[1] in self.large_posts]
        self.up_likes_articles = [x for x in self.up_likes if x[1] in self.large_posts]
        self.build_graph_analytics()
            
    def diplay_summary_graph(self):
        """Generic routine for plotting a 
        graph
        """
        plt.figure(num=None, figsize=(70, 50), dpi=80)
        up_pos=nx.random_layout(self.user_post_graph)
        nx.draw_networkx_nodes(self.user_post_graph,up_pos,
                               nodelist=self.all_post_users,
                               node_color='r',
                               alpha=0.8)
        nx.draw_networkx_nodes(self.user_post_graph,up_pos,
                               nodelist=self.all_posts,
                               node_color='b',
                               alpha=0.8)
        nx.draw_networkx_edges(self.user_post_graph,up_pos,edgelist=self.up_likes,alpha=0.5,edge_color='m')
        nx.draw_networkx_edges(self.user_post_graph,up_pos,edgelist=self.up_comments,alpha=0.5,edge_color='teal')
        nx.draw_networkx_edges(self.user_post_graph,up_pos,edgelist=self.up_posts,alpha=0.5,edge_color='y')
        #draw_networkx_labels(G, pos, labels=None, font_size=12, font_color='k', font_family='sans-serif', font_weight='normal', alpha=1.0, ax=None)

    def write_triples(self, triple_file):
        blog_map = {}
        user_map = {}
        post_map = {}
        counter = 0
        with open(triple_file, 'w') as bt:
            for blog in self.all_blogs:
                if blog not in blog_map:
                    blog_map[blog] = bname.format(blog)
                    counter += 1
                    bt.write(blog_string.format(blog_map[blog]))
            for user in self.nodes:
                user_map[user] = uname.format(user)
                counter += 1
                bt.write(user_string.format(user_map[user]))
            for post in self.all_posts:
                post_map[post] = pname.format(post)
                counter += 1
                bt.write(post_string.format(post_map[post]))
                blog = post.split('_')[0]
                if blog not in blog_map:
                    blog_map[blog] = bname.format(blog)
                    counter += 1
                    bt.write(blog_string.format(blog_map[blog]))
                inside_of_edge = user_post.format(post_map[post],blog_map[blog] )
                bt.write(inside_of_edge)
            for comment_edge in self.up_comments:
                comment_ent = user_comment_pos.format(post_map[comment_edge[1]],user_map[comment_edge[0]])
                bt.write(comment_ent)
            for post_edge in self.up_posts:
                post_ent = user_post_creator.format(user_map[post_edge[0]], post_map[post_edge[1]])
                bt.write(post_ent)
            for post_like_edge in self.up_likes:
                post_like = likes_thing.format(user_map[post_like_edge[0]], post_map[post_like_edge[1]])
                bt.write(post_like)
            for blog_like_edge in self.ub_likes:
                likes_blog = likes_thing.format(user_map[blog_like_edge[0]], blog_map[blog_like_edge[1]])
                bt.write(likes_blog)
            for blog_follow in self.ub_follows:
                follow_edge = user_follow.format(user_map[blog_follow[0]], blog_map[blog_follow[1]])
                bt.write(follow_edge)
            for content_ev in self.content_events:
                article_content_edge = post_has_article_content.format(post_map[content_ev['post']])
                bt.write(article_content_edge)

    def build_graph_analytics(self):
        """
        Put the structures together for the graph analytics
        """
        for (idx, node) in enumerate(self.nodes):
            self.node_to_id[node] = idx
            self.id_to_node[idx] = node

        self.g_article_posts = snap.TUNGraph.New(len(self.node_to_id), len(self.up_likes_articles))
        for node in self.nodes:
            self.g_article_posts.AddNode(self.node_to_id[node])
        for (a, b) in self.up_likes_articles:
            self.g_article_posts.AddEdge(self.node_to_id[a], self.node_to_id[b])
        for (a, b) in self.up_posts_to_articles:
            self.g_article_posts.AddEdge(self.node_to_id[a], self.node_to_id[b])
        self.cmtyv = snap.TCnComV()
        self.modularity = snap.CommunityCNM(self.g_article_posts, self.cmtyv)
        self.sig_communities = [[node for node in cc] for cc in self.cmtyv if cc.Len() > 2]
        self.sig_communities_by_id = [[self.id_to_node[id] for id in l] for l in self.sig_communities]
        self.user_post_graph_cnm =  nx.Graph()
        self.user_post_graph_cnm.add_nodes_from(self.nodes)

    def display_community_graph(self):
        """
        Display the subgraph identified by community detection
        """
        plt.figure(num=None, figsize=(70, 50), dpi=80)
        up_pos_cnm=nx.random_layout(user_post_graph_cnm)
        for (idx, comm) in enumerate(self.sig_communities_by_id):
            comm_u_cnm = []
            comm_p_cnm = []
            for n in self.all_post_users:
                if n in comm:
                    comm_u_cnm.append(n)
            for n in self.all_posts_res:
                if n in comm:
                    comm_p_cnm.append(n)
            nx.draw_networkx_nodes(self.user_post_graph_cnm,up_pos_cnm,
                                   nodelist=comm_u_cnm,
                                   node_color=self.group_colors[idx],
                                   alpha=0.8)
            nx.draw_networkx_nodes(self.user_post_graph_cnm,up_pos_cnm,
                                   nodelist=comm_p_cnm,
                                   node_color=self.group_colors[idx],
                                   alpha=0.8)
            elsg1_cnm = [e for e in self.up_likes if e[0] in comm_u_cnm and e[1] in comm_p_cnm]
            ecsg1_cnm = [e for e in self.up_comments if e[0] in comm_u_cnm and e[1] in comm_p_cnm]
            epsg1_cnm = [e for e in self.up_posts if e[0] in comm_u_cnm and e[1] in comm_p_cnm]
            nx.draw_networkx_edges(self.user_post_graph_cnm,up_pos,edgelist=elsg1_cnm,alpha=0.5,edge_color='m')
            nx.draw_networkx_edges(self.user_post_graph_cnm,up_pos,edgelist=ecsg1_cnm,alpha=0.5,edge_color='teal')
            nx.draw_networkx_edges(self.user_post_graph_cnm,up_pos,edgelist=epsg1_cnm,alpha=0.5,edge_color='y')


