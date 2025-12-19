from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.hashers import check_password
from datetime import date, datetime, time
from django.utils import timezone
from django.db import transaction
from django.http import JsonResponse
from django.db.models import Sum, Count, F, DecimalField, Max
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
    rol = request.session.get('rol')
    fecha_hoy_chile = timezone.localdate()

    try:
        control_hoy = ControlDia.objects.get(fecha=fecha_hoy_chile)
    except ControlDia.DoesNotExist:
        control_hoy = None

    total_vendido = Decimal('0.00')

    if rol == 'Jefe de Ventas':
        hoy_inicio = timezone.make_aware(datetime.combine(fecha_hoy_chile, time.min))
        hoy_fin = timezone.make_aware(datetime.combine(fecha_hoy_chile, time.max))
        ventas_hoy = Venta.objects.filter(fecha__range=(hoy_inicio, hoy_fin))
        total_agregado = ventas_hoy.aggregate(total=Sum('total'))
        total_vendido = total_agregado.get('total') or Decimal('0.00')

    context = {
        'control_hoy': control_hoy,
        'total_vendido': total_vendido
    }
    return render(request, 'home.html', context)


# --- CRUDs ---
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
            form.save()
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
        form = UsuarioForm(instance=usuario)
        form.fields['password'].widget = forms.PasswordInput(render_value=False)
        form.fields['password_confirm'].widget = forms.PasswordInput(render_value=False)
    return render(request, 'administracion/form_usuario.html', {'form': form, 'accion': 'Editar'})

@custom_login_required
@role_required(allowed_roles=['Jefe de Ventas'])
def eliminar_usuario(request, id_usuario):
    usuario = get_object_or_404(Usuario, id_usuario=id_usuario)
    if usuario.id_usuario == request.session.get('usuario_id'):
        messages.error(request, 'No puedes eliminar tu propia cuenta de administrador.')
        return redirect('listar_usuarios')
    try:
        usuario.delete()
        messages.success(request, 'Usuario eliminado exitosamente.')
    except Exception:
        messages.error(request, 'No se puede eliminar el usuario, está asociado a ventas.')
    return redirect('listar_usuarios')


# --- CONTROL DÍA ---
@custom_login_required
@role_required(allowed_roles=['Jefe de Ventas'])
def control_dia(request):
    fecha_hoy_chile = timezone.localdate()
    control_hoy, created = ControlDia.objects.get_or_create(
        fecha=fecha_hoy_chile,
        defaults={'id_usuario_id': request.session.get('usuario_id')}
    )
    if request.method == 'POST':
        if control_hoy.estado == 'Cerrado':
            control_hoy.estado = 'Abierto'
            control_hoy.hora_apertura = timezone.localtime().time() 
            messages.success(request, f'El día ha sido ABIERTO a las {control_hoy.hora_apertura.strftime("%H:%M")}.')
        else:
            control_hoy.estado = 'Cerrado'
            messages.warning(request, 'El día ha sido CERRADO. No se registrarán nuevas ventas.')
        
        control_hoy.id_usuario_id = request.session.get('usuario_id')
        control_hoy.save()
        return redirect('control_dia')
    return render(request, 'control/control_dia.html', {'control_hoy': control_hoy})


# --- CREAR VENTA (VENDEDOR) ---
@custom_login_required
@role_required(allowed_roles=['Vendedor', 'Jefe de Ventas'])
@transaction.atomic
def crear_venta(request):
    fecha_hoy_chile = timezone.localdate()

    try:
        control_hoy = ControlDia.objects.get(fecha=fecha_hoy_chile)
        if control_hoy.estado == 'Cerrado':
            messages.error(request, 'El día está CERRADO. No se pueden registrar nuevas ventas.')
            return redirect('home')
    except ControlDia.DoesNotExist:
        messages.error(request, 'No se ha abierto el día. Contacte al Jefe de Ventas.')
        return redirect('home')
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            tipo_documento = data.get('tipo_documento')
            folio_num = data.get('folio')
            
            # Validación Folio
            if folio_num is not None:
                try:
                    folio_num = int(folio_num)
                except (ValueError, TypeError):
                    return JsonResponse({'status': 'error', 'message': 'Folio inválido.'}, status=400)
            else:
                max_folio_q = Venta.objects.filter(tipo_documento=tipo_documento).aggregate(max_folio=Max('folio'))
                folio_num = (max_folio_q['max_folio'] or 0) + 1
            
            cliente_id = data.get('cliente_id')
            cliente_datos = data.get('cliente_datos') # Datos del formulario
            productos_data = data.get('productos')
            metodo_pago_seleccionado = data.get('metodo_pago', 'Efectivo') # Capturar Pago

            # Procesar Cliente
            cliente_obj = None
            if tipo_documento == 'Factura':
                if cliente_id:
                    # CLIENTE EXISTENTE (Verificar si hay cambios para actualizar)
                    cliente_obj = Cliente.objects.get(id=cliente_id)
                    if cliente_datos:
                        cambios = False
                        if cliente_obj.razon_social != cliente_datos.get('razon_social'):
                            cliente_obj.razon_social = cliente_datos.get('razon_social')
                            cambios = True
                        if cliente_obj.giro != cliente_datos.get('giro'):
                            cliente_obj.giro = cliente_datos.get('giro')
                            cambios = True
                        if cliente_obj.direccion != cliente_datos.get('direccion'):
                            cliente_obj.direccion = cliente_datos.get('direccion')
                            cambios = True
                        
                        if cambios:
                            cliente_obj.save() # Guardar actualización
                elif cliente_datos:
                    # CLIENTE NUEVO
                    cliente_form = ClienteForm(cliente_datos)
                    if cliente_form.is_valid():
                        cliente_obj = cliente_form.save()
                    else:
                        return JsonResponse({'status': 'error', 'message': 'Datos del cliente inválidos.'}, status=400)
                else:
                    return JsonResponse({'status': 'error', 'message': 'Para Factura, faltan los datos del cliente.'}, status=400)

            # Calcular totales
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

            # Guardar Venta
            venta = Venta.objects.create(
                tipo_documento=tipo_documento,
                folio=folio_num,
                subtotal=subtotal_venta.quantize(Decimal('0.00')),
                iva=iva,
                total=total.quantize(Decimal('0.00')),
                id_usuario_id=request.session.get('usuario_id'),
                id_cliente=cliente_obj,
                id_control=control_hoy,
                metodo_pago=metodo_pago_seleccionado # Guardar Metodo Pago
            )

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
        venta_form = VentaForm()
        cliente_form = ClienteForm()
        detalle_form = DetalleVentaForm()
        productos_qs = Producto.objects.filter(stock__gt=0).values('codigo', 'nombre', 'precio_unitario', 'stock')
        productos_list = []
        for p in productos_qs:
            p['precio_unitario'] = str(p['precio_unitario'])
            productos_list.append(p)
        clientes = list(Cliente.objects.values('id', 'rut', 'razon_social', 'giro', 'direccion'))
        context = {
            'venta_form': venta_form,
            'cliente_form': cliente_form,
            'detalle_form': detalle_form,
            'productos_json': productos_list,
            'clientes_json': clientes,
        }
        return render(request, 'ventas/crear_venta.html', context)


# --- REPORTE DIARIO ---
@custom_login_required
@role_required(allowed_roles=['Jefe de Ventas'])
def reporte_diario(request):
    fecha_str = request.GET.get('fecha')
    hoy_chile = timezone.localdate()

    if fecha_str:
        try:
            fecha_reporte = date.fromisoformat(fecha_str)
        except ValueError:
            fecha_reporte = hoy_chile
            messages.error(request, 'Formato de fecha inválido. Mostrando reporte de hoy.')
    else:
        fecha_reporte = hoy_chile

    start_of_day = timezone.make_aware(datetime.combine(fecha_reporte, time.min))
    end_of_day = timezone.make_aware(datetime.combine(fecha_reporte, time.max))

    ventas_dia = Venta.objects.filter(fecha__range=(start_of_day, end_of_day))

    total_por_documento = ventas_dia.values('tipo_documento').annotate(
        cantidad=Count('id_venta'),
        total=Sum('total')
    ).order_by('tipo_documento')

    total_por_vendedor = ventas_dia.values('id_usuario__username').annotate(
        cantidad=Count('id_venta'),
        total=Sum('total')
    ).order_by('id_usuario__username')

    # NUEVO: Agrupación por Método de Pago
    total_por_pago = ventas_dia.values('metodo_pago').annotate(
        cantidad=Count('id_venta'),
        total=Sum('total')
    ).order_by('-total')

    totales_generales = ventas_dia.aggregate(
        total_neto=Sum('subtotal'),
        total_iva=Sum('iva'),
        total_recaudado=Sum('total'),
        cantidad_ventas=Count('id_venta')
    )

    context = {
        'fecha_reporte': fecha_reporte,
        'total_por_documento': total_por_documento,
        'total_por_vendedor': total_por_vendedor,
        'total_por_pago': total_por_pago, # Agregar al contexto
        'totales_generales': totales_generales,
        'ventas_dia': ventas_dia.order_by('-fecha'),
    }

    return render(request, 'reportes/reporte_diario.html', context)


def get_next_folio(request):
    tipo_documento = request.GET.get('tipo_documento')
    if not tipo_documento:
        return JsonResponse({'error': 'Falta tipo de documento'}, status=400)

    max_folio = Venta.objects.filter(tipo_documento=tipo_documento).aggregate(max_folio=Max('folio'))
    next_folio = (max_folio['max_folio'] or 0) + 1

    return JsonResponse({'next_folio': next_folio})


# --- API VOUCHER (AJAX) ---
@custom_login_required
def obtener_detalle_venta(request, id_venta):
    try:
        venta = Venta.objects.get(id_venta=id_venta)
        detalles = DetalleVenta.objects.filter(id_venta=venta)
        
        items = []
        for d in detalles:
            items.append({
                'producto': d.id_producto.nombre,
                'cantidad': d.cantidad,
                'precio': int(d.precio_unitario),
                'subtotal': int(d.subtotal)
            })
            
        data = {
            'folio': venta.folio,
            'tipo': venta.tipo_documento,
            'fecha': venta.fecha.strftime("%d/%m/%Y %H:%M"),
            'vendedor': venta.id_usuario.username.title(),
            'cliente': venta.id_cliente.razon_social if venta.id_cliente else "Público General",
            'total': int(venta.total),
            'metodo_pago': venta.metodo_pago, # Agregar método pago
            'items': items,
            'status': 'success'
        }
        return JsonResponse(data)
    except Venta.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Venta no encontrada'})