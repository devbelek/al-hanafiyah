from django.urls import path
from .views import GlobalSearchView, SearchSuggestionsView

urlpatterns = [
    path('', GlobalSearchView.as_view(), name='global-search'),
    path('suggestions/', SearchSuggestionsView.as_view(), name='search-suggestions'),
]