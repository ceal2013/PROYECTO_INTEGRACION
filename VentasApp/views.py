from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.hashers import check_password
from datetime import date

from .forms import LoginForm, ProductoForm, ClienteForm, UsuarioForm
from django import forms
from .models import Usuario, Producto, Cliente, ControlDia
from .decorators import custom_login_required, role_required


def login_view(request):
	form = LoginForm(request.POST or None)
	if request.method == 'POST' and form.is_valid():
		username = form.cleaned_data.get('username')
		password = form.cleaned_data.get('password')
		try:
			usuario = Usuario.objects.get(username=username)
		except Usuario.DoesNotExist:
			messages.error(request, 'Usuario no encontrado')
			return render(request, 'login.html', {'form': form})

		if check_password(password, usuario.password):
			# Guardar datos en sesión manualmente
			request.session['usuario_id'] = usuario.id_usuario
			request.session['username'] = usuario.username
			request.session['rol'] = usuario.rol
			return redirect('home')
		else:
			messages.error(request, 'Contraseña incorrecta')

	return render(request, 'login.html', {'form': form})


def user_logout(request):
	request.session.flush()
	return redirect('login')


@custom_login_required
def home(request):
	return render(request, 'home.html')


# --- CRUD de Productos (Solo Jefe de Ventas) ---
@custom_login_required
@role_required(allowed_roles=['Jefe de Ventas'])
def listar_productos(request):
	productos = Producto.objects.all()
	return render(request, 'administracion/listar_productos.html', {'productos': productos})


@custom_login_required
@role_required(allowed_roles=['Jefe de Ventas'])
def crear_producto(request):
	if request.method == 'POST':
		form = ProductoForm(request.POST)
		if form.is_valid():
			form.save()
			messages.success(request, 'Producto creado exitosamente.')
			return redirect('listar_productos')
	else:
		form = ProductoForm()

	return render(request, 'administracion/form_producto.html', {'form': form, 'accion': 'Crear'})


@custom_login_required
@role_required(allowed_roles=['Jefe de Ventas'])
def editar_producto(request, codigo):
	producto = get_object_or_404(Producto, codigo=codigo)
	if request.method == 'POST':
		form = ProductoForm(request.POST, instance=producto)
		if form.is_valid():
			form.save()
			messages.success(request, 'Producto actualizado exitosamente.')
			return redirect('listar_productos')
	else:
		form = ProductoForm(instance=producto)

	return render(request, 'administracion/form_producto.html', {'form': form, 'accion': 'Editar'})


@custom_login_required
@role_required(allowed_roles=['Jefe de Ventas'])
def eliminar_producto(request, codigo):
	producto = get_object_or_404(Producto, codigo=codigo)
	try:
		producto.delete()
		messages.success(request, 'Producto eliminado exitosamente.')
	except Exception:
		messages.error(request, 'No se puede eliminar el producto, está siendo usado en una venta.')

	return redirect('listar_productos')


# --- CRUD de Clientes (Solo Jefe de Ventas) ---
@custom_login_required
@role_required(allowed_roles=['Jefe de Ventas'])
def listar_clientes(request):
	clientes = Cliente.objects.all()
	return render(request, 'administracion/listar_clientes.html', {'clientes': clientes})


@custom_login_required
@role_required(allowed_roles=['Jefe de Ventas'])
def crear_cliente(request):
	if request.method == 'POST':
		form = ClienteForm(request.POST)
		if form.is_valid():
			form.save()
			messages.success(request, 'Cliente creado exitosamente.')
			return redirect('listar_clientes')
	else:
		form = ClienteForm()

	return render(request, 'administracion/form_cliente.html', {'form': form, 'accion': 'Crear'})


@custom_login_required
@role_required(allowed_roles=['Jefe de Ventas'])
def editar_cliente(request, rut):
	cliente = get_object_or_404(Cliente, rut=rut)
	if request.method == 'POST':
		form = ClienteForm(request.POST, instance=cliente)
		if form.is_valid():
			form.save()
			messages.success(request, 'Cliente actualizado exitosamente.')
			return redirect('listar_clientes')
	else:
		form = ClienteForm(instance=cliente)

	return render(request, 'administracion/form_cliente.html', {'form': form, 'accion': 'Editar'})


@custom_login_required
@role_required(allowed_roles=['Jefe de Ventas'])
def eliminar_cliente(request, rut):
	cliente = get_object_or_404(Cliente, rut=rut)
	try:
		cliente.delete()
		messages.success(request, 'Cliente eliminado exitosamente.')
	except Exception:
		messages.error(request, 'No se puede eliminar el cliente, está siendo usado en una venta.')

	return redirect('listar_clientes')


# --- CRUD de Usuarios (Solo Jefe de Ventas) ---
@custom_login_required
@role_required(allowed_roles=['Jefe de Ventas'])
def listar_usuarios(request):
	usuarios = Usuario.objects.all()
	return render(request, 'administracion/listar_usuarios.html', {'usuarios': usuarios})


@custom_login_required
@role_required(allowed_roles=['Jefe de Ventas'])
def crear_usuario(request):
	if request.method == 'POST':
		form = UsuarioForm(request.POST)
		if form.is_valid():
			form.save()  # UsuarioForm maneja el hash de la contraseña
			messages.success(request, 'Usuario creado exitosamente.')
			return redirect('listar_usuarios')
	else:
		form = UsuarioForm()

	return render(request, 'administracion/form_usuario.html', {'form': form, 'accion': 'Crear'})


@custom_login_required
@role_required(allowed_roles=['Jefe de Ventas'])
def editar_usuario(request, id_usuario):
	usuario = get_object_or_404(Usuario, id_usuario=id_usuario)
	if request.method == 'POST':
		form = UsuarioForm(request.POST, instance=usuario)
		if form.is_valid():
			form.save()
			messages.success(request, 'Usuario actualizado exitosamente.')
			return redirect('listar_usuarios')
	else:
		# Ocultamos la contraseña actual, solo permitimos cambiarla
		form = UsuarioForm(instance=usuario)
		form.fields['password'].widget = forms.PasswordInput(render_value=False)
		form.fields['password_confirm'].widget = forms.PasswordInput(render_value=False)

	return render(request, 'administracion/form_usuario.html', {'form': form, 'accion': 'Editar'})


@custom_login_required
@role_required(allowed_roles=['Jefe de Ventas'])
def eliminar_usuario(request, id_usuario):
	usuario = get_object_or_404(Usuario, id_usuario=id_usuario)
	# Evitar que el Jefe de Ventas se elimine a sí mismo
	if usuario.id_usuario == request.session.get('usuario_id'):
		messages.error(request, 'No puedes eliminar tu propia cuenta de administrador.')
		return redirect('listar_usuarios')

	try:
		usuario.delete()
		messages.success(request, 'Usuario eliminado exitosamente.')
	except Exception:
		messages.error(request, 'No se puede eliminar el usuario, está asociado a ventas.')

	return redirect('listar_usuarios')


# --- VISTA DE CONTROL DE DÍA (Solo Jefe de Ventas) ---
@custom_login_required
@role_required(allowed_roles=['Jefe de Ventas'])
def control_dia(request):
	# Obtenemos o creamos el control para la fecha de HOY
	control_hoy, created = ControlDia.objects.get_or_create(
		fecha=date.today(),
		defaults={'id_usuario_id': request.session.get('usuario_id')}
	)
	if request.method == 'POST':
		# Invertimos el estado
		if control_hoy.estado == 'Cerrado':
			control_hoy.estado = 'Abierto'
			messages.success(request, 'El día ha sido ABIERTO. Ya se pueden registrar ventas.')
		else:
			control_hoy.estado = 'Cerrado'
			messages.warning(request, 'El día ha sido CERRADO. No se registrarán nuevas ventas.')
        
		control_hoy.id_usuario_id = request.session.get('usuario_id') # Actualizamos quien hizo el cambio
		control_hoy.save()
		return redirect('control_dia')
	return render(request, 'control/control_dia.html', {'control_hoy': control_hoy})
