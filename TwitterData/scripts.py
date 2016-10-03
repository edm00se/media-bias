from .models import *

import twitter
from textblob import TextBlob

def search_twitter():
    """
    Calls twitter api and creates database entries with the results of those searches.
    """
    while True:
        senators = Senator.objects.all()

        #Twitter Authentication Information Excluded
        
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
