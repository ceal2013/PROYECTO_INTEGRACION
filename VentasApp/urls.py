from django.urls import path
from . import views
from django.views.generic import RedirectView

urlpatterns = [
	path('', RedirectView.as_view(url='login/')),
	path('login/', views.login_view, name='login'),
	path('logout/', views.user_logout, name='logout'),
	path('home/', views.home, name='home'),
]
