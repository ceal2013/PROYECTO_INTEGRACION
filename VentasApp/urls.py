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

	# URLs para Clientes
	path('clientes/', views.listar_clientes, name='listar_clientes'),
	path('clientes/crear/', views.crear_cliente, name='crear_cliente'),
	path('clientes/editar/<str:rut>/', views.editar_cliente, name='editar_cliente'),
	path('clientes/eliminar/<str:rut>/', views.eliminar_cliente, name='eliminar_cliente'),
]
