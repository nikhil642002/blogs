from sklearn.cluster import KMeans
import numpy as np

class ActivityAnalyzer(object):
    """
    Builds and stores structures useful in activity pattern analysis.
    """

    def __init__(self, preprocessor):
        self.by_user_blog = {}
        self.by_user_post = {}
        self.by_blog = {}
        self.bucketed_counts_actions = {}
        self.bucketed_counts_actions_by_user = {}
        self.preprocessor = preprocessor

    def gather_seq(self, seq, delt):
        ((n0, d0), (n1, d2)) = seq[0]
        tseqs = []
        aseqs = [n0]
        for ((n0, d0), (n1, d2)) in seq:
            tdel = d2 - d0
            if tdel < delt:
                aseqs += [tdel, n1]
            else:
                tseqs.append(aseqs)
                aseqs = [n1 ]
        tseqs.append(aseqs)
        return tseqs

    def build(self):
        """Build activity pattern lists.
        """
        self.build_ev_dicts()
        self.by_user_post_ts = {k:sorted([(v[0], v[1].value/1000000) for v in vals], key=lambda x: x[1]) for (k,vals) in self.by_user_post.iteritems() if len(vals) >1}
        self.by_user_post_ts_comb = {k:self.seq_ts(v) for (k,v) in self.by_user_post_ts.items()}
        self.by_user_blog_ts = {k:sorted([(v[0], v[1].value/1000000) for v in vals], key=lambda x: x[1]) for (k,vals) in self.by_user_blog.iteritems() if len(vals) >1}
        self.by_user_blog_ts_comb = {k:self.seq_ts(v) for (k,v) in self.by_user_blog_ts.items()}
        self.all_blog_act_sequences = {k:self.gather_seq(v, 6000000000) for (k,v) in self.by_user_blog_ts_comb.items() if len(v) > 1}
        self.build_time_buckets()
        self.compute_clusters()

    def seq_ts(self, tss):
        "Process the sequence"
        n = len(tss)
        return zip(tss[0:n-2], tss[1:n-1])

    def build_ev_dicts(self):
        for ev in self.preprocessor.reduced_events:
            ev_val = (ev['type'], ev['dt'])
            if len(ev['post']) > 1:
                idx = (ev['user'], ev['post'])
                if idx not in self.by_user_post:
                    self.by_user_post[idx] = [ev_val]
                else:
                    self.by_user_post[idx].append(ev_val)
            else:
                idx_ub = (ev['user'], ev['blog'])
                idx_b = ev['blog']
                if idx_ub not in self.by_user_blog:
                    self.by_user_blog[idx_ub] = [ev_val]
                else:
                    self.by_user_blog[idx_ub].append(ev_val)
                if idx_b not in self.by_blog:
                    self.by_blog[idx_b] = [ev_val]
                else:
                    self.by_blog[idx_b].append(ev_val)

    def build_time_buckets(self):
        for (pair, itms) in self.all_blog_act_sequences.items():
            usr = pair[0]
            if usr not in self.bucketed_counts_actions_by_user:
                self.bucketed_counts_actions_by_user[usr] = (0, 0, 0)
            (sub_minute, ten_minute, longer) = self.bucketed_counts_actions_by_user[usr]
            for seq in itms:
                for itm in seq:
                    if itm not in ['like', 'publish', 'follow', 'comment']:
                        secs = itm/1000.00
                        if secs < 60:
                            sub_minute += 1
                        elif secs < 601:
                            ten_minute += 1
                        else:
                            longer += 1
            self.bucketed_counts_actions_by_user[usr] = (sub_minute, ten_minute, longer)

    def compute_clusters(self):
        """Compute the clusters for activity patterns
        """
        X = [np.array([float(v) for v in x ]) for (k,x) in self.bucketed_counts_actions_by_user.items()]
        self.cluster = KMeans(n_clusters=6)
        self.cluster.fit(X)
        self.cluster_counts = np.zeros(6)
        for idx in self.cluster.labels_:
            self.cluster_counts[idx] += 1.0

