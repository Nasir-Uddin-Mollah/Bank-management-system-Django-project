from django.urls import path
from .views import UserRegistrationFormView, UserLoginFormView, UserLogout, UserBankAccountUpdateView

urlpatterns = [
    path('register/', UserRegistrationFormView.as_view(), name='register'),
    path('login/', UserLoginFormView.as_view(), name='login'),
    path('logout/', UserLogout, name='logout'),
    path('profile/', UserBankAccountUpdateView.as_view(), name='profile'),
]
