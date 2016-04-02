from __future__ import unicode_literals, division
from django.db import models
from django.utils import timezone
from datetime import datetime
from jsonfield import JSONField
from time import sleep
from textblob import TextBlob
import json
# import twitter


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
    senator = models.ForeignKey(Senator, on_delete=models.CASCADE)
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
    search = models.ForeignKey(Search, on_delete=models.CASCADE)
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


def search_twitter():
    """
    Calls twitter api and creates database entries with the results of those searches.
    """
    while True:
        # try:
        senators = Senator.objects.all()

        api = twitter.Api(consumer_key='WcqDv7hfaVTaPcKirWnkKCdoj',consumer_secret='dI6QKXlFXQ3qjSIHle3kfFAAsktCsCthXBJa8mtsDsvNH8bQUg',access_token_key='3092104835-CU1ALu2qBDZ8aRBm7mTqlyRXHPxNtnh8j7UMr7p', access_token_secret='i2Nu4HQmQ0399dH9MpkHQNPjSyWMJY0PikHd0ORWhBHt5') # Oauth information

        for senator in senators:
            terms = json.loads(senator.search_terms)
            for term in terms:
                try:
                    tweets = api.GetSearch(term=term, count=100, result_type='recent') # Search twitter for that search term
                    search = Search(senator=senator, search_term=term)
                    search.save()
                    print term
                    for tweet in tweets:
                        if not Tweet.objects.filter(tweet_id=int(tweet.id)).exists():
                            sentiment = TextBlob(tweet.text).sentiment
                            tweet = Tweet(search=search, tweet_id=int(tweet.id),
                                          user=tweet.user.screen_name,
                                          user_followers=int(tweet.user.followers_count),
                                          text=tweet.text, tweeted_at=tweet.created_at,
                                          retweets=int(tweet.retweet_count),
                                          favorites=int(tweet.favorite_count),
                                          hashtags=[hashtag.text for hashtag in tweet.hashtags],
                                          verified=tweet.user.verified,
                                          subjectivity=sentiment.subjectivity,
                                          polarity=sentiment.polarity)
                            tweet.save()
                    sleep(30)
                except:
                    print "Waiting for API to refresh"
                    sleep(1200)
        # except:
        #     sleep(60)
