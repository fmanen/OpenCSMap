from django.urls import path
from . import views

app_name = 'search'

urlpatterns = [
    path('', views.search_index, name='search'),
    path('about', views.about, name='about'),
    path('results', views.simple_aggregations_search_view, name='results'),
    path('advanced_search', views.advanced_search, name='advanced_search'),
    path('all_research', views.all_research, name='all_research'),
    path('advanced_search_results', views.aggregations_for_advanced_search_view, name='advanced_search_results'),
    path('simple_search_papers_results/<str:topic>/<str:affiliation>', views.simple_search_papers_results_view, name='simple_search_papers_results'),
    path('simple_search_papers_results/<str:affiliation>', views.simple_search_papers_all_results_view, name='simple_search_papers_results'),
    path('advanced_search_papers_results/<str:topic>/<str:affiliation>/<str:authors>/<str:results_by>/<str:type_of_pub>/<int:from_date>/<int:to_date>', views.advanced_search_papers_results_view, name='advanced_search_papers_results'),
    path('advanced_search_papers_results/<str:topic>/<str:affiliation>/<str:authors>/<str:results_by>/<str:type_of_pub>/<str:city>/<int:from_date>/<int:to_date>', views.advanced_search_papers_results_city_view, name='advanced_search_papers_results_city'),
]