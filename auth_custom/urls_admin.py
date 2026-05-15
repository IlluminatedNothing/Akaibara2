from django.urls import path

from .views_admin import admin_create_user, users_list

urlpatterns = [
    path('admin/create-user/', admin_create_user, name='auth_admin_create_user'),
    path('admin/users/', users_list, name='auth_users_list'),
]

