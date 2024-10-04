from django.urls import path
from .views import login_signup_view, login_signup_view, logout_view, profile_view, entry_view, verify_otp

urlpatterns = [
    path('', entry_view, name='entry'),
    path('signup/', login_signup_view, name='signup'),  
    path('login/', login_signup_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('profile/', profile_view, name='profile'),
    path('verify_otp/', verify_otp, name='verify_otp'),    
]