from django.shortcuts import render
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from collections import Counter, OrderedDict
from .models import *
import ast
import string

WORDS_TO_EXCLUDE = ["", "-", "the", "rt", "of", "to", "a", "i", "is", "on", "in", "he", "she",
                    "from", "for", "all", "and", "can", "how", "about", "at", "&amp;", "by",
                    "didn't", "these", "that", "been", "up", "has", "via", "our", "get", "go",
                    "are", "gets", "why", "says", " ", "you", "her", "his", "be", "this", "as",
                    "we", "with", "out", "if", "no", "so", "do", "it", "  ", "   ", "senator",
                    "an", "or", "but", "who", "its", "any", "r", "amp", " ", "\n","their", "my"]

CHARS_TO_EXCLUDE = set(string.punctuation)

# Create your views here.
def index(request):
    """Home page with links to other views"""
    senators = Senator.objects.all()
    return render(request, 'TwitterData/index.html', {'senators': senators})


def count_words_used(tweets):
    """"""
    tweets_list = []
    for tweet in tweets:
        tweet = "".join(char for char in tweet.text if char not in CHARS_TO_EXCLUDE)
        tweets_list += tweet.replace('"','').replace("'","").lower().split(' ')

    tweet_word_count = Counter(tweets_list)
    tweet_word_count = OrderedDict(sorted(tweet_word_count.items(), key=lambda x: (-x[1], x[0])))

    return tweet_word_count


def count_hashtags_used(tweets):
    """"""
    hashtag_list = []
    for tweet in tweets:
        hashtag_list.extend(ast.literal_eval(tweet.hashtags))
    hashtag_count = Counter(hashtag_list)
    hashtag_count = OrderedDict(sorted(hashtag_count.items(), key=lambda x: (-x[1], x[0])))

    return hashtag_count


def senator_data(request, pk):
    """"""
    senator_data = Senator.objects.get(pk=pk)
    search_terms = json.loads(senator_data.search_terms)
    twitter_url = "https://twitter.com/" + search_terms[-1]
    searches = Search.objects.filter(senator_id = senator_data)
    tweets = Tweet.objects.filter(search_id__in = searches)
    tweet_count = tweets.count()
    tweets_with_polarity = tweets.exclude(polarity__isnull=True)
    avg_polarity = [tweet.polarity for tweet in tweets_with_polarity]

    if len(avg_polarity) > 0:
        avg_polarity = round(sum(avg_polarity)/len(avg_polarity), 4)
    else:
        avg_polarity = 0

    most_used_words = count_words_used(tweets)
    for word in WORDS_TO_EXCLUDE:
        try:
            del most_used_words[word]
        except:
            pass

    for term in search_terms:
        term = "".join(char for char in term if char not in CHARS_TO_EXCLUDE)
        term = term.lower().split(" ")
        for t in term:
            try:
                del most_used_words[t]
            except:
                pass

    most_used_words = OrderedDict(list(most_used_words.items())[:100])

    most_used_hashtags = count_hashtags_used(tweets)
    most_used_hashtags = OrderedDict(list(most_used_hashtags.items())[:100])

    return render(request, 'TwitterData/senator_data.html', {'senator':senator_data, 'twitter_url':twitter_url, 'tweets':tweets, 'tweet_count':tweet_count, 'avg_polarity':avg_polarity, 'most_used_words':most_used_words, 'most_used_hashtags':most_used_hashtags})
