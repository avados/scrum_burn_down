from django.urls import path
from django.conf.urls import url

from . import views

app_name = 'burnDown'
urlpatterns = [
	path('mytests/', views.mytests, name='mytests'),
	path('indexBurnDown/<int:sprint_id>', views.indexBurnDown, name='indexBurnDown'),
    path('indexBurnDown/latest/<int:team_id>', views.latest_sprint, name='latest'),
	path('<int:company_id>/edit/', views.EditView, name='edit'),
	path('<int:company_id>/validate/', views.ValidateView, name='validate'),
	# ex: /polls/
    path('', views.indexSprints, name='index'),
    
    # ex: /polls/5/
    path('<int:pk>/', views.DetailView.as_view(), name='detail'),
    # ex: /polls/5/results/
    path('<int:pk>/results/', views.ResultsView.as_view(), name='results'),
    # ex: /polls/5/vote/
    path('<int:company_id>/vote/', views.vote, name='vote'),

    url(r'^companies/$', views.companies_list),
    url(r'^companies/(?P<pk>[0-9]+)/$', views.company_detail),

# 	url(r'pbis/', views.pbi_list, name='pbi_list'),
 	path('pbis/', views.pbi_list, name='pbi_list'),
    #url(r'^pbis/$', views.pbi_list),
    #path is newer than url in djangi, prefer is
    path('pbisByDate/<int:sprint_id>/', views.pbi_list_date, name='pbisByDate'),
    
]