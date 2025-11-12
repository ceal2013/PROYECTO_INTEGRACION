from django.db import models
from django.conf import settings
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils import timezone


class UsuarioManager(BaseUserManager):
    """Manager personalizado para el modelo Usuario."""

    def create_user(self, username, password=None, rol='Vendedor', **extra_fields):
        if not username:
            raise ValueError('El username debe ser proporcionado')
        username = self.model.normalize_username(username)
        user = self.model(username=username, rol=rol, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        # Forzar rol de superusuario a 'Jefe de Ventas'
        return self.create_user(username=username, password=password, rol='Jefe de Ventas', **extra_fields)


class Usuario(AbstractBaseUser, PermissionsMixin):
    ROL_VENDEDOR = 'Vendedor'
    ROL_JEFE = 'Jefe de Ventas'
    ROL_CHOICES = [
        (ROL_VENDEDOR, ROL_VENDEDOR),
        (ROL_JEFE, ROL_JEFE),
    ]

    id_usuario = models.AutoField(primary_key=True)
    username = models.CharField(max_length=50, unique=True)
    rol = models.CharField(max_length=30, choices=ROL_CHOICES, default=ROL_VENDEDOR)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['rol']

    objects = UsuarioManager()

    def __str__(self):
        return self.username


class Cliente(models.Model):
    rut = models.CharField(max_length=15, unique=True)
    razon_social = models.CharField(max_length=100)
    giro = models.CharField(max_length=100)
    direccion = models.CharField(max_length=150)

    def __str__(self):
        return self.rut


class Producto(models.Model):
    codigo = models.CharField(max_length=20, unique=True)
    nombre = models.CharField(max_length=100)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField()

    def __str__(self):
        return self.nombre


class ControlDia(models.Model):
    ESTADO_ABIERTO = 'Abierto'
    ESTADO_CERRADO = 'Cerrado'
    ESTADO_CHOICES = [
        (ESTADO_ABIERTO, ESTADO_ABIERTO),
        (ESTADO_CERRADO, ESTADO_CERRADO),
    ]

    fecha = models.DateField(unique=True)
    estado = models.CharField(max_length=10, choices=ESTADO_CHOICES, default=ESTADO_CERRADO)
    id_usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.fecha} - {self.estado}"


class Venta(models.Model):
    TIPO_BOLETA = 'Boleta'
    TIPO_FACTURA = 'Factura'
    TIPO_CHOICES = [
        (TIPO_BOLETA, TIPO_BOLETA),
        (TIPO_FACTURA, TIPO_FACTURA),
    ]

    id_venta = models.AutoField(primary_key=True)
    fecha = models.DateTimeField(default=timezone.now)
    tipo_documento = models.CharField(max_length=20, choices=TIPO_CHOICES)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    iva = models.DecimalField(max_digits=10, decimal_places=2)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    id_usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    id_cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT, null=True, blank=True)
    id_control = models.ForeignKey(ControlDia, on_delete=models.PROTECT)

    def __str__(self):
        return f"Venta {self.id_venta}"


class DetalleVenta(models.Model):
    id_venta = models.ForeignKey(Venta, on_delete=models.CASCADE, related_name='detalles')
    id_producto = models.ForeignKey(Producto, on_delete=models.PROTECT)
    cantidad = models.PositiveIntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Venta {self.id_venta.id_venta} - {self.id_producto.nombre} x {self.cantidad}"

