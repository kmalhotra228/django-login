from django.urls import path
from . import views

app_name = 'member'

urlpatterns = [
    path('signup',views.signupUser,name = 'signup'),
    path('logout',views.logoutUser,name = 'logout'),
    path('login',views.loginUser,name = 'login'),
    path('',views.home, name = 'home')
]

