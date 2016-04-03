from django.shortcuts import render
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from collections import Counter, OrderedDict
from .models import *
from scipy.stats import chisquare
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


def search_for_word(request, word):
    """"""
    tweets = Tweet.objects.filter(text__icontains = word)
    tweet_count = tweets.count()

    female_republican_tweets = tweets.filter(search__senator__gender = "Female", search__senator__party = "Republican").count()
    male_republican_tweets = tweets.filter(search__senator__gender = "Male", search__senator__party = "Republican").count()
    female_democrat_tweets = tweets.filter(search__senator__party = "Democratic", search__senator__gender = "Female").count()
    male_democrat_tweets = tweets.filter(search__senator__party = "Democratic", search__senator__gender = "Male").count()

    female_tweets = female_republican_tweets + female_democrat_tweets
    male_tweets = male_democrat_tweets + male_republican_tweets
    republican_tweets = female_republican_tweets + male_republican_tweets
    democratic_tweets = female_democrat_tweets + male_democrat_tweets

    senators_mentioned = tweets.order_by().values_list('search__senator__name', flat = True).distinct()
    tweets_with_polarity = tweets.exclude(polarity__isnull=True)
    avg_polarity = [tweet.polarity for tweet in tweets_with_polarity]

    if len(avg_polarity) > 0:
        avg_polarity = round(sum(avg_polarity)/len(avg_polarity), 4)
    else:
        avg_polarity = 0

    stat_difference_gender = chisquare([male_tweets, female_tweets], f_exp = [(tweet_count * 77/100), (tweet_count * 20/100)])
    stat_difference_party = chisquare([republican_tweets, democratic_tweets], f_exp = [(tweet_count * 52/100), (tweet_count * 45/100)])

    stat_difference_republicans = chisquare([female_republican_tweets, male_republican_tweets], f_exp = [(tweet_count * 6/100), (tweet_count * 46/100)])
    stat_difference_democrats = chisquare([female_democrat_tweets, male_democrat_tweets], f_exp = [(tweet_count * 14/100), (tweet_count * 30/100)])

    stat_difference_women = chisquare([female_republican_tweets, female_democrat_tweets], f_exp = [(tweet_count * 6/100), (tweet_count * 13/100)])
    stat_difference_men = chisquare([male_republican_tweets, male_democrat_tweets], f_exp = [(tweet_count * 46/100), (tweet_count * 30/100)])

    stat_difference_party_gender = chisquare([female_republican_tweets, female_democrat_tweets, male_democrat_tweets, male_republican_tweets], f_exp = [(tweet_count * 6/100), (tweet_count * 14/100), (tweet_count  * 46/100), (tweet_count * 30/100)])

    return render(request, 'TwitterData/search.html', {'word':word, 'tweet_count':tweet_count,
     'polarity':avg_polarity, 'senators_mentioned':senators_mentioned, 'stat_difference_party':round(stat_difference_party[1], 4),
     'stat_difference_gender':round(stat_difference_gender[1], 4), 'female_tweets':female_tweets, 'male_tweets':male_tweets,
     'republican_tweets': republican_tweets, 'democratic_tweets': democratic_tweets,
     'female_republican_tweets': female_republican_tweets, 'male_republican_tweets': male_republican_tweets,
     'female_democrat_tweets': female_democrat_tweets, 'male_democrat_tweets': male_democrat_tweets,
     'stat_difference_democrats':round(stat_difference_democrats[1],4), 'stat_difference_republicans':round(stat_difference_republicans[1],4),
     'stat_difference_men':round(stat_difference_men[1],4), 'stat_difference_women':round(stat_difference_women[1],4), 'stat_difference_party_gender':round(stat_difference_party_gender[1],4)})


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
