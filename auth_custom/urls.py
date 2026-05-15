from django.urls import path, include

from .views import akaibara_login, akaibara_login_submit, akaibara_login_orig, akaibara_logout

urlpatterns = [
    path('', akaibara_login, name='auth_home'),
    path('login/', akaibara_login, name='auth_login'),
    path('login/submit/', akaibara_login_submit, name='auth_login_submit'),
    path('logout/', akaibara_logout, name='auth_logout'),
    path('login-orig/', akaibara_login_orig, name='auth_login_orig'),
    path('', include('auth_custom.urls_admin')),
]

