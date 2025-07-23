from django.urls import path, include
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='dashboard/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('profile/', views.profile, name='profile'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('accounts/', views.accounts_view, name='accounts'),
    path('post/', views.posts_view, name='post'),
    path('api/fetch-posts/', views.fetch_social_posts, name='fetch_social_posts'),
    path('post/view/<int:post_id>/', views.view_post, name='view_post'),
    path('view_post/', views.view_post, name='view_post'),
    path('create-post/', views.create_post_view, name='create_post'),

    # ✅ Include social_django URLs both at root and at 'auth/'
    path('', include('social_django.urls', namespace='social')),
    path('auth/', include('social_django.urls', namespace='social')),
]
