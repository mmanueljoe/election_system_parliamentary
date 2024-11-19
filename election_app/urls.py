from django.urls import path
from django.shortcuts import redirect  # Correct import for redirect
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import LogoutView
from . import views

urlpatterns = [
    path('', lambda request: redirect('login')),  # Redirect root URL to the login page
    # Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),
    path('landing/', views.landing_page, name='landing_page'),
    
    # Candidate Management
    path('candidates/', views.candidate_list, name='candidate_list'),
    path('candidates/add/', views.add_candidate, name='add_candidate'),
    path('candidates/edit/<int:id>/', views.edit_candidate, name='edit_candidate'),
    path('candidates/delete/<int:id>/', views.delete_candidate, name='delete_candidate'),
    
    # Polling Station Management
    path('polling_stations/', views.polling_station_list, name='polling_station_list'),
    path('polling_stations/add/', views.add_polling_station, name='add_polling_station'),
    path('polling_stations/edit/<int:id>/', views.edit_polling_station, name='edit_polling_station'),
    path('polling_stations/delete/<int:id>/', views.delete_polling_station, name='delete_polling_station'),
    

    # Votes Management
    path('votes/', views.vote_list, name='vote_list'),
    path('vote/add/', views.add_vote, name='add_vote'),
    path('votes/update/<int:id>/', views.update_vote, name='update_vote'),
    # path('vote/edit/<int:id>/', views.update_vote, name='update_vote'),
    path('vote/delete/<int:id>/', views.delete_vote, name='delete_vote'),

    # constituencies management
    path('constituencies/', views.constituency_list, name='constituency_list'),
    path('constituencies/add',views.add_constituency,name="add_constituency"),
    path('constituencies/edit/<int:id>',views.edit_constituency,name="edit_constituency"),
    path('consituencies/delete/<int:id>',views.delete_constituency,name="delete_constituency"),

    # Authentication
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
]
