from django.contrib import admin
from django.urls import path,include
from . import views
urlpatterns = [
    path('register/',views.UserRegistrationView.as_view(), name="register"),
    path('login/',views.UserLoginView.as_view(), name="login"),
    path('profile/',views.ProfileView.as_view(), name="profile"),
    path('resetpassword/',views.ResetPassword.as_view(), name="resetpassword"),
    path('confirm/', views.confirm, name="confirm"),
    path('blog/', views.BlogCreate.as_view(), name="blog"),
    path('blog/<int:pk>', views.BlogDetailView.as_view(), name="blog"),

]
