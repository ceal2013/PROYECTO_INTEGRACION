from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.hashers import check_password
from datetime import date
from django.db import transaction
from django.http import JsonResponse
from decimal import Decimal
import json

from .forms import LoginForm, ProductoForm, ClienteForm, UsuarioForm, VentaForm, DetalleVentaForm
from django import forms
from .models import Usuario, Producto, Cliente, ControlDia, Venta, DetalleVenta
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


# --- VISTA DE REGISTRO DE VENTAS (Vendedor) ---
@custom_login_required
@role_required(allowed_roles=['Vendedor', 'Jefe de Ventas'])
@transaction.atomic  # Asegura que toda la venta se guarde correctamente
def crear_venta(request):
	# 1. Verificar si el día está abierto
	try:
		control_hoy = ControlDia.objects.get(fecha=date.today())
		if control_hoy.estado == 'Cerrado':
			messages.error(request, 'El día está CERRADO. No se pueden registrar nuevas ventas.')
			return redirect('home')
	except ControlDia.DoesNotExist:
		messages.error(request, 'No se ha abierto el día. Contacte al Jefe de Ventas.')
		return redirect('home')
	if request.method == 'POST':
		# 2. Procesar el POST (enviado por JavaScript/Fetch)
		try:
			data = json.loads(request.body)
			tipo_documento = data.get('tipo_documento')
			cliente_id = data.get('cliente_id')
			cliente_nuevo = data.get('cliente_nuevo')
			productos_data = data.get('productos')
			# 3. Validar Cliente (si es Factura)
			cliente_obj = None
			if tipo_documento == 'Factura':
				if cliente_id:
					cliente_obj = Cliente.objects.get(id=cliente_id)
				elif cliente_nuevo:
					cliente_form = ClienteForm(cliente_nuevo)
					if cliente_form.is_valid():
						cliente_obj = cliente_form.save()
					else:
						return JsonResponse({'status': 'error', 'message': 'Datos del cliente inválidos.'}, status=400)
				else:
					return JsonResponse({'status': 'error', 'message': 'Para Factura, debe seleccionar un cliente.'}, status=400)
			# 4. Calcular totales
			subtotal_venta = Decimal('0.00')
			detalles_venta = []
			if not productos_data:
				return JsonResponse({'status': 'error', 'message': 'No hay productos en la venta.'}, status=400)
			for item in productos_data:
				producto = Producto.objects.get(codigo=item['codigo'])
				cantidad = int(item['cantidad'])
				precio_unitario = Decimal(producto.precio_unitario)
				subtotal_item = precio_unitario * cantidad

				if producto.stock < cantidad:
					return JsonResponse({'status': 'error', 'message': f'Stock insuficiente para {producto.nombre}.'}, status=400)

				detalles_venta.append({
					'producto': producto,
					'cantidad': cantidad,
					'precio_unitario': precio_unitario,
					'subtotal': subtotal_item
				})
				subtotal_venta += subtotal_item
			iva = (subtotal_venta * Decimal('0.19')).quantize(Decimal('0.00'))
			total = subtotal_venta + iva
			# 5. Guardar la Venta
			venta = Venta.objects.create(
				tipo_documento=tipo_documento,
				subtotal=subtotal_venta.quantize(Decimal('0.00')),
				iva=iva,
				total=total.quantize(Decimal('0.00')),
				id_usuario_id=request.session.get('usuario_id'),
				id_cliente=cliente_obj,
				id_control=control_hoy
			)
			# 6. Guardar Detalles de Venta y actualizar Stock
			for detalle in detalles_venta:
				DetalleVenta.objects.create(
					id_venta=venta,
					id_producto=detalle['producto'],
					cantidad=detalle['cantidad'],
					precio_unitario=detalle['precio_unitario'],
					subtotal=detalle['subtotal']
				)
				producto_obj = detalle['producto']
				producto_obj.stock -= detalle['cantidad']
				producto_obj.save()
			messages.success(request, 'Venta registrada exitosamente.')
			return JsonResponse({'status': 'success', 'message': 'Venta registrada.'})
		except Exception as e:
			return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
	else:
		# 7. Preparar el GET
		venta_form = VentaForm()
		cliente_form = ClienteForm()
		detalle_form = DetalleVentaForm()
		
		# Obtenemos los productos
		productos_qs = Producto.objects.filter(stock__gt=0).values('codigo', 'nombre', 'precio_unitario', 'stock')
		
		# Convertimos Decimal a string para JSON
		productos_list = []
		for p in productos_qs:
			p['precio_unitario'] = str(p['precio_unitario'])
			productos_list.append(p)
		clientes = list(Cliente.objects.values('id', 'rut', 'razon_social'))
		context = {
			'venta_form': venta_form,
			'cliente_form': cliente_form,
			'detalle_form': detalle_form,
			'productos_json': json.dumps(productos_list), # Usamos la lista convertida
			'clientes_json': json.dumps(clientes),
		}
		return render(request, 'ventas/crear_venta.html', context)
