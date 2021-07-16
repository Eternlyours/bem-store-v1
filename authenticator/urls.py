from django.urls import path
from .views import LogoutView, LoginView, SigninView, CustomChangePasswordView
from authenticator.decorators import check_recaptcha


urlpatterns = [
        path(r'logout/', LogoutView.as_view(), name='logout'),
        path('login/', check_recaptcha(LoginView.as_view()), name='login'),
        path('signin/', check_recaptcha(SigninView.as_view()), name='signin'),
        path('user/password/change/', check_recaptcha(CustomChangePasswordView.as_view()), name='change-password-custom-view')
]