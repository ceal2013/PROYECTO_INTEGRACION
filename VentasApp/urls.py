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

	# URLs para Usuarios
	path('usuarios/', views.listar_usuarios, name='listar_usuarios'),
	path('usuarios/crear/', views.crear_usuario, name='crear_usuario'),
	path('usuarios/editar/<int:id_usuario>/', views.editar_usuario, name='editar_usuario'),
	path('usuarios/eliminar/<int:id_usuario>/', views.eliminar_usuario, name='eliminar_usuario'),

	# URLs para Control de Día
	path('control_dia/', views.control_dia, name='control_dia'),

	# URLs para Ventas (Vendedor)
	path('nueva_venta/', views.crear_venta, name='crear_venta'),
	path('get_next_folio/', views.get_next_folio, name='get_next_folio'),

	# URLs para Reportes (Jefe de Ventas)
	path('reporte_diario/', views.reporte_diario, name='reporte_diario'),
]
