from django.urls import path
from . import views_functional

urlpatterns = [
    path('', views_functional.notification_list, name='notification-list'),
    path('<int:pk>/', views_functional.notification_detail, name='notification-detail'),
    path('<int:pk>/mark_as_read/', views_functional.mark_as_read, name='mark-as-read'),
    path('mark_all_as_read/', views_functional.mark_all_as_read, name='mark-all-as-read'),
    path('settings/', views_functional.notification_settings, name='notification-settings'),
    path('push-subscriptions/', views_functional.push_subscription_list_create, name='push-subscription-list-create'),
    path('push-subscriptions/<int:pk>/', views_functional.push_subscription_delete, name='push-subscription-delete'),
]