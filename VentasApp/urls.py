from django.urls import path
from . import views
from django.views.generic import RedirectView

urlpatterns = [
	path('', RedirectView.as_view(url='login/')),
	path('login/', views.login_view, name='login'),
	path('logout/', views.user_logout, name='logout'),
	path('home/', views.home, name='home'),

	# URLs para Administración (CRUDs)
	path('productos/', views.listar_productos, name='listar_productos'),
	path('productos/crear/', views.crear_producto, name='crear_producto'),
	path('productos/editar/<str:codigo>/', views.editar_producto, name='editar_producto'),
	path('productos/eliminar/<str:codigo>/', views.eliminar_producto, name='eliminar_producto'),
]
