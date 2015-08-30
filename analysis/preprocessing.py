import pandas as pd
import json
import numpy as np
import matplotlib.pyplot as plt
import time
from collections import Counter

class Preprocessor(object):

    def __init__(self, json_file):
        """
        Parameters

        json_file : string
            Name of the file containing the json blog events
        """
        self.ulist = [json.loads(l) for l in open(json_file).readlines()]
        self.events_df = pd.DataFrame(collect_all_blog_events(self.ulist))
        self.events_df['dt'] = pd.to_datetime(self.events_df['date'])
        self.events_df['content_len'] = self.events_df['content'].map(lambda x: len(x))
        self.reduced_events = [{'user': self.itmval(itm, 'user'), 'blog': self.itmval(itm, 'blog'), 'type': self.itmval(itm, 'type'), 'post': self.itmval(itm, 'post'), 'dt': self.itmval(itm, 'dt')} for itm in self.events_df.itertuples() ]
        self.content_events = [{'user': self.itmval(itm, 'user'), 'post': self.itmval(itm, 'post'), 'content':self.itmval(itm, 'content')} for itm in self.events_df[self.events_df['content_len'] > 1000].itertuples()]
        self.user_total_views = [(x['user_id'], sum([ct['all_time_views'] for ct in x['user_blogs']])) for x in self.ulist]
        self.blogs_per_user =  [(x['user_id'], len(x['user_blogs'])) for x in self.ulist] 
        self.user_mapping = {uev["user_id"] : idx for (idx, uev) in enumerate(self.ulist)}

    def cpos(self, nm):
        """
        Parameters

        nm : string
           Name of the column

        Returns
           int index of the column
        """
        return self.events_df.columns.get_loc(nm)

    def itmval(self, itm, nm):
        """
        itm : array_like
           Row in which we are searching for a value
        nm  : string
           Column name within the row

        Returns
           value within the cell.
        """
        return itm[self.cpos(nm)+1]

def collect_all_blog_events(ulist):
    """Collect all the events about a blog
    """
    elist = []
    #First collect the blogs owned by the users in the list
    # Also linking to users that interacted with them
    for user_rec in ulist:
        uid = user_rec["user_id"]
        collect_all_owned_blog_events(user_rec["user_blogs"], uid, elist)
        collect_all_user_events(uid, user_rec["user_events"], elist)
    return elist
    
def collect_all_owned_blog_events(blgs, owner, elist):
    """Collect all the blogs that this user owns.
    There will be blog events from users that may not
    necessarily be in the list. I store these in the
    out_of_band_events Counter
    """    
    for blg in blgs:
        blg_id = blg["blog_id"]
        for blg_ev in blg["blog_events"]:
            ev = {}
            ev["date"] = blg_ev["date"]
            ev["blog"] = blg_id
            ev["post"] = ''
            ev["content"] = ''
            ev['title'] = ''
            event_data = blg_ev["event_data"]
            elist.append(process_event(ev, owner, blg_ev["name"], event_data))

def collect_all_user_events(user_id, user_events, elist):
    """For the events that this user initiated record the event
    """
    for user_event in user_events:
        ev = {}
        ev["date"] = user_event["date"]
        ev["user"] = str(long(user_id))
        ev["post"] = ''
        ev["content"] = ''
        ev['title'] = ''
        elist.append(process_event(ev, user_id, user_event["name"], user_event["event_data"]))
        
def process_event(ev, owner, etype, event_data):
    if etype == "follow_in":
        ev["type"] = "follow"
        ev["post"] = ''
        ev["user"] = str(long(event_data["follower"]))
    elif etype == "like_in":
        ev["type"] = "like"
        ev["post"] = '{}_{}'.format(event_data["blog_id"], event_data["post_id"])
        ev["user"] = str(long(event_data["liked_by"]))
    elif etype == "publish_post":
        ev["post"] = '{}_{}'.format(event_data["blog_id"], event_data["post_id"])
        ev["user"] = owner
        if "content" in event_data:
            ev["type"] = "content_post"
            ev["title"] = event_data["title"]
            ev["content"] = event_data["content"]
        elif "post_id" in event_data:
            ev["type"] = "publish"            
    elif etype == "publish_page" and "post_id" in event_data:
        ev["type"] = "publish"
        ev["post"] = '{}_{}'.format(event_data["blog_id"], event_data["post_id"])
        ev["user"] = owner
    elif etype == "comment_in" and "comment_approved" in event_data:
        ev["type"] = "comment"
        ev["post"] = ''
        ev["user"] = str(long(event_data["commenter"]))
    elif etype == "follow_out" or etype == "self_follow":
        ev["type"] = "follow"
        ev["blog"] = event_data["followed_blog"]
        ev["post"] = ''
    elif etype == "like_out" or etype == "self_like":
        ev["type"] = "like"
        ev["post"] = '{}_{}'.format(event_data["favorited_blog"], event_data["favorited_post"])
        ev["blog"] = event_data["favorited_blog"]
    elif etype == "comment_out" or etype == "self_comment":
        ev["type"] = "comment"
        ev["post"] = '{}_{}'.format(event_data["commented_blog"], event_data["commented_post"])
        ev["blog"] = event_data["commented_blog"]
    else:
        print etype, event_data
    return ev






