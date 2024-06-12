from django.urls import path

from . import views


app_name = 'polls'
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('<int:pk>/', views.DetailView.as_view(), name='detail'),
    path('<int:pk>/results/', views.ResultsView.as_view(), name='results'),
    path('<int:question_id>/vote/', views.vote, name='vote'),
    path('polls/', views.poll, name='poll'),
    path('polls/<int:id>/update-vote/', views.update_poll_vote, name='update_poll_vote'),
    path('polls/<int:id>/', views.get_poll_details, name='get_poll_details'),
    path('polls/list-tags/', views.list_tags, name='list_tags'),
] 

