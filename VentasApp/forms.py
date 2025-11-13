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
        # Añadir clases de Bootstrap a todos los campos
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})


class VentaForm(forms.ModelForm):
    class Meta:
        model = Venta
        fields = ['tipo_documento', 'id_cliente']
        widgets = {
            'tipo_documento': forms.Select(attrs={'class': 'form-select', 'id': 'tipo_documento'}),
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
