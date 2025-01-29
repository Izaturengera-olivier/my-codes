from django.contrib import admin
from django.urls import path
from newsapp.views import *
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('about/', about, name='about'),


    path('', index, name='index'),
    path('admin/', admin.site.urls),
    path('login/', login_view, name='login'),
    path('news/', news_list, name='news_list'),
    path('search/', search, name='search'),

    path('contact/', contact_us, name='contact_us'),
    path('article/<int:article_id>/', article_detail, name='article_detail'),
    path('signup/', signup_view, name='signup'),
    # path('home/', home_view, name='home'),
    path('terms-conditions/', terms_conditions, name='terms_conditions'),

    path('news/<int:pk>/', news_detail, name='news_detail'),
    path('logout/', lambda request: logout(request) or redirect('login'), name='logout'),
    path('privacy-policy/', privacy_policy, name='privacy_policy'),
    path('password_reset/', password_reset_request, name='password_reset'),
    path('messages/<int:message_id>/reply/', reply_message, name='reply_message'),

    path('password_reset/', password_reset_request, name='password_reset_request'),
    path('password_reset_verify/', password_reset_verify, name='password_reset_verify'),
    path('admin-dashboard/', admin_dashboard, name='admin_dashboard'),
    # Add URLs for specific menus
    path('manage-news/', manage_news, name='manage_news'),
    path('manage-articles/', manage_articles, name='manage_articles'),
    path('manage-messages/', manage_messages, name='manage_messages'),
    path('manage-users/', manage_users, name='manage_users'),
    path('subscribe/', subscribe_view, name='subscribe'),
    path('deactivate_user/<int:user_id>/', deactivate_user, name='deactivate_user'),
    path('activate_user/<int:user_id>/', activate_user, name='activate_user'),
    path('make_admin/<int:user_id>/', make_admin, name='make_admin'),
    path('revoke_admin/<int:user_id>/', revoke_admin, name='revoke_admin'),
    path('delete_account/<int:user_id>/', delete_account, name='delete_user'),

]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
