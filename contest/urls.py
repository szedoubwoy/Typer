from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.home, name='home'),
    path('results/', views.results, name='results'),
    path('leaderboard/', views.leaderboard, name='leaderboard'),
    # path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('betting/', views.betting, name='betting'),
    path('profile/', views.profile, name='profile'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    path('create-user/', views.create_user, name='create_user'),
    path('user-list/', views.user_list, name='user_list'),
    path('edit-user/<int:user_id>/', views.edit_user, name='edit_user'),
    path('delete-user/<int:user_id>/', views.delete_user, name='delete_user'),
    path('articles/', views.article_list, name='article_list'),
    path('create-article/', views.create_article, name='create_article'),
    path('edit-article/<int:article_id>/', views.edit_article, name='edit_article'),
    path('delete-article/<int:article_id>/', views.delete_article, name='delete_article'),
    path('articles/<slug:slug>/', views.view_article, name='view_article'),
    path('edit_bet/<int:bet_id>/', views.edit_bet, name='edit_bet'),
    path('actual_results/', views.actual_results, name='actual_results'),
    path('edit_actual_result/<int:match_id>/', views.edit_actual_result, name='edit_actual_result'),
    path('user-predictions/', views.user_predictions, name='user_predictions'),
    path('create-match', views.create_match, name='create_match'),
    path('edit-points', views.edit_points, name='edit_points'),
    path('edit_bet_status/', views.edit_bet_status, name='edit_bet_status'),
]
