from __future__ import unicode_literals, division
from datetime import datetime
from time import sleep
import json

from django.db import models
from django.utils import timezone


class Senator(models.Model):
    """
    Table that contains data about each senator currently serving other than
    the ones currently running for president in 2016 (Cruz, Rubio, Sanders)
    as they are major outliers.

    created_at: the time that the senator is entered.
    updated_at: the last time that the senator was edited.
    state: the state that the sentor serves.
    name: the senator's name.
    gender: the senator's gender.
    party: the political party the senator belongs to.
    search_terms: the terms that will be used in Twitter queries stored in a list.
    For each senator, this will include their first name and last name together, their title and last name, and their twitter handle if they have one. Example: for Kelly Ayotte, her search terms would be entered as '["Kelly Ayotte", "Senator Ayotte", "@KellyAyotte"]'
    election_year: the year that the senator faces re-election.
    """
    created_at = models.DateTimeField(auto_now_add=True, blank=True)
    updated_at = models.DateTimeField(auto_now_add=True, blank=True)
    state = models.TextField(null=True, blank=True)
    name = models.TextField(null=True, blank=True)
    gender = models.TextField(null=True, blank=True)
    party = models.TextField(null=True, blank=True)
    search_terms = models.TextField(null=True, blank=True)
    election_year = models.TextField(null=True, blank=True)

    @property
    def search_terms_as_list(self):
        return json.dumps(search_terms)

    @property
    def twitter_url(self):
        return "https://twitter.com/" + self.search_terms_as_list[-1]


class Search(models.Model):
    """
    Table that contains search results for a search on Twitter.

    created_at: the time that the senator is entered.
    updated_at: the last time that the senator was edited.
    senator: which senator the search results refer to.
    search_term: the term that was searched on Twitter, from the search_terms array from the Senator table.
    """
    created_at = models.DateTimeField(auto_now_add=True, blank=True)
    updated_at = models.DateTimeField(auto_now_add=True, blank=True)
    senator = models.ForeignKey(Senator, on_delete=models.CASCADE, related_name="searches",
                                related_query_name="search")
    search_term = models.TextField(null=True, blank=True)


class Tweet(models.Model):
    """
    Table that contains a singular tweet about a candidate.

    created_at: the time that the senator is entered.
    updated_at: the last time that the senator was edited.
    search: references the search that the tweet came from.
    tweet_id: the Twiter id for the tweet. Used to only add the tweets
    user: the username that made a tweet.
    user_followers: the number of followers a user has. Used as a proxy for throwaway accounts.
    text: the tweet's text.
    location: where the tweet was made, usually unavailable, but sometimes is there.
    retweets: how many retweets the tweet got.
    favorites: how many favorites the tweet got.
    hashtags: any hashtags included in the tweet.
    """
    created_at = models.DateTimeField(auto_now_add=True, blank=True)
    updated_at = models.DateTimeField(auto_now_add=True, blank=True)
    search = models.ForeignKey(Search, on_delete=models.CASCADE, related_name="tweets",
                               related_query_name="tweet")
    tweet_id = models.BigIntegerField(null=True, blank=True)
    user = models.TextField(null=True, blank=True)
    user_followers = models.IntegerField(null=True, blank=True)
    verified = models.BooleanField(blank=True, default=True)
    text = models.TextField(null=True, blank=True)
    tweeted_at = models.TextField(null=True, blank=True)
    retweets = models.IntegerField(null=True, blank=True)
    favorites = models.IntegerField(null=True, blank=True)
    hashtags = models.TextField(null=True, blank=True)
    polarity = models.FloatField(null=True, blank=True)
    subjectivity = models.FloatField(null=True, blank=True)

    
