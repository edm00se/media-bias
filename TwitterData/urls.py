from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.index, name = 'index'),
    url(r'^senator/(?P<pk>\d+)/', views.senator_data, name = "senator"),
    url(r'^search/(?P<word>\w+)/', views.search_for_word, name = "search"),
]
