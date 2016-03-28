from django.shortcuts import render
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from collections import Counter, OrderedDict
from .models import *


# Create your views here.
def index(request):
    """Home page with links to other views"""
    return render(request, 'TwitterData/index.html')


def count_words_used_json(request):
    """"""
    tweets = Tweet.objects.all()
    tweets_list = []
    for tweet in tweets:
        tweets_list += tweet.text.split(' ')

    tweet_word_count = Counter(tweets_list)
    tweet_word_count = OrderedDict(sorted(tweet_word_count.items(), key=lambda x: (-x[1], x[0])))

    return HttpResponse(json.dumps(tweet_word_count), content_type="application/json")
