from django import forms
from .models import User, Producto, Pedido, Direcciones

class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    class Meta:
        model = User
        fields = ['email', 'full_name', 'password']


class LoginForm(forms.Form):
    email = forms.EmailField(label='Correo electrónico', widget=forms.EmailInput(attrs={'placeholder': 'Correo electrónico'}))
    password = forms.CharField(label='Contraseña', widget=forms.PasswordInput(attrs={'placeholder': 'Contraseña'}))
    
class DireccionesForm(forms.ModelForm):
    class Meta:
        model = Direcciones
        fields = ['codpos', 'ciudad', 'colonia', 'calle']
        widgets = {
            'codpos': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Código Postal'}),
            'ciudad': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ciudad'}),
            'colonia': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Colonia'}),
            'calle': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Calle y numero'}),
        }


class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ['titulo', 'descripcion', 'precio','stock', 'imagen', 'video']

class PedidoForm(forms.ModelForm):
    direccion_envio = forms.ModelChoiceField(
        queryset=Direcciones.objects.none(),
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Dirección de Envío"
    )
    metodo_pago = forms.ChoiceField(
        choices=Pedido.METODOS_PAGO,
        widget=forms.RadioSelect,
        label="Método de Pago"
    )
    class Meta:
        model = Pedido
        fields = ['direccion_envio', 'metodo_pago']
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # Extraer el usuario del contexto
        super().__init__(*args, **kwargs)
        if user:
            # Filtrar direcciones según el usuario
            self.fields['direccion_envio'].queryset = Direcciones.objects.filter(usuario_id=user)