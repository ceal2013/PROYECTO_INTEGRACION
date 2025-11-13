import re
from django import forms
from .models import Usuario, Producto, Cliente, Venta, DetalleVenta  # Importamos modelos usados en formularios


class LoginForm(forms.Form):
    username = forms.CharField(
        label='Usuario',
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ingrese su nombre de usuario',
            'required': 'required'
        })
    )
    password = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ingrese su contraseña',
            'required': 'required'
        })
    )


class UsuarioForm(forms.ModelForm):
    password = forms.CharField(label='Contraseña', widget=forms.PasswordInput)
    password_confirm = forms.CharField(label='Confirmar contraseña', widget=forms.PasswordInput)

    class Meta:
        model = Usuario
        fields = ['username', 'rol']

    def clean_password_confirm(self):
        password = self.cleaned_data.get("password")
        password_confirm = self.cleaned_data.get("password_confirm")
        if password and password_confirm and password != password_confirm:
            raise forms.ValidationError("Las contraseñas no coinciden")
        return password_confirm

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user


class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ['codigo', 'nombre', 'precio_unitario', 'stock']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Añadir clases de Bootstrap a todos los campos
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})


class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ['rut', 'razon_social', 'giro', 'direccion']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})

    def _validar_rut(self, rut_limpio):
        # Función de validación (Módulo 11)
        try:
            dv = rut_limpio[-1].lower()
            cuerpo = rut_limpio[:-1]
            if not cuerpo.isdigit():
                return False
            suma = 0
            multiplo = 2
            for i in reversed(cuerpo):
                suma += int(i) * multiplo
                multiplo = multiplo + 1 if multiplo < 7 else 2
            
            dv_esperado_num = 11 - (suma % 11)
            
            if dv_esperado_num == 11:
                dv_esperado = '0'
            elif dv_esperado_num == 10:
                dv_esperado = 'k'
            else:
                dv_esperado = str(dv_esperado_num)
            
            return dv == dv_esperado
        except Exception:
            return False

    def clean_rut(self):
        rut = self.cleaned_data.get('rut')
        if not rut:
            raise forms.ValidationError("El RUT es obligatorio.")
        # 1. Limpiar el RUT de puntos y guiones
        rut_limpio = re.sub(r'[^0-9kK]+', '', str(rut)).lower()
        
        # 2. Validar
        if not self._validar_rut(rut_limpio):
            raise forms.ValidationError("El RUT ingresado no es válido.")
        # 3. Formatear (Normalizar) para guardar
        dv = rut_limpio[-1].upper()
        cuerpo = rut_limpio[:-1]
        
        # Formatear cuerpo con puntos (Ej: 12345678 -> 12.345.678)
        cuerpo_formateado = ""
        while len(cuerpo) > 3:
            cuerpo_formateado = "." + cuerpo[-3:] + cuerpo_formateado
            cuerpo = cuerpo[:-3]
        cuerpo_formateado = cuerpo + cuerpo_formateado
        
        return f"{cuerpo_formateado}-{dv}"


class VentaForm(forms.ModelForm):
    class Meta:
        model = Venta
        fields = ['tipo_documento', 'folio', 'id_cliente']
        widgets = {
            'tipo_documento': forms.Select(attrs={'class': 'form-select', 'id': 'tipo_documento'}),
            'folio': forms.NumberInput(attrs={'class': 'form-control', 'id': 'folio', 'readonly': True}),
            'id_cliente': forms.Select(attrs={'class': 'form-select', 'id': 'id_cliente'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Hacemos que el cliente no sea obligatorio por defecto (se valida con JS)
        self.fields['id_cliente'].required = False


class DetalleVentaForm(forms.ModelForm):
    class Meta:
        model = DetalleVenta
        fields = ['id_producto', 'cantidad']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Añadimos 'form-control' a los campos del detalle
        self.fields['id_producto'].widget.attrs.update({'class': 'form-control producto-select'})
        self.fields['cantidad'].widget.attrs.update({'class': 'form-control cantidad-input', 'min': '1'})
