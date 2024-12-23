from django import forms
from .models import User, Producto, Pedido, Direcciones, Trabajadores
from django.core.exceptions import ValidationError
from allauth.account.forms import SignupForm, LoginForm

#formularios usados para los registros de usuarios, login, busqueda, direcciones, edicion de usuario, productos, pedidos, cambio de contraseña, actualizacion de estado de productos y trabajadores

#formulario de registro de usuario
class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    class Meta:
        model = User
        fields = ['email', 'name', 'password']
    def clean_email(self):
        email = self.cleaned_data.get('email')
        # Verifica si el correo ya está registrado
        if User.objects.filter(email=email).exists():
            raise ValidationError('Este correo ya está registrado. Usa otro correo.')
        return email

#formulario de login
class LoginForm(forms.Form):
    email = forms.EmailField(label='Correo electrónico', widget=forms.EmailInput(attrs={'placeholder': 'Correo electrónico'}))
    password = forms.CharField(label='Contraseña', widget=forms.PasswordInput(attrs={'placeholder': 'Contraseña'}))

#formulario de busqueda
class SearchForm(forms.Form):
    query = forms.CharField(label='', max_length=100, required=False, widget=forms.TextInput(attrs={'placeholder': 'Buscar Productos'})) 

#formulario de direcciones
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
#formulario de edicion de usuario
class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['email', 'name']
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Correo Electrónico'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre Completo'}),
        }
#formulario de productos
class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ['titulo', 'descripcion', 'precio','stock', 'imagen', 'video', 'keywords']
#formulario de pedidos
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

#formulario de cambio de contraseña
class PasswordCambioForm(forms.Form):
    old_password = forms.CharField(
        label="Contraseña actual",
        widget=forms.PasswordInput,
        strip=False,
    )
    new_password1 = forms.CharField(
        label="Nueva contraseña",
        widget=forms.PasswordInput,
        strip=False,
    )
    new_password2 = forms.CharField(
        label="Confirmar nueva contraseña",
        widget=forms.PasswordInput,
        strip=False,
    )

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get('new_password') != cleaned_data.get('new_password2'):
            raise forms.ValidationError('Las contraseñas no coinciden')
        return cleaned_data
    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_old_password(self):
        old_password = self.cleaned_data.get("old_password")
        if not self.user.check_password(old_password):
            raise forms.ValidationError("La contraseña actual es incorrecta.")
        return old_password

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("new_password1")
        password2 = cleaned_data.get("new_password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Las contraseñas no coinciden.")
        return cleaned_data

    def save(self, commit=True):
        password = self.cleaned_data["new_password1"]
        self.user.set_password(password)
        if commit:
            self.user.save()
        return self.user
    
    
#formulario de actualizacion de estado de productos
class ActualizarEstadoProductoForm(forms.ModelForm):
    class Meta:
        model = Pedido
        fields = ['estado']

    def __init__(self, *args, **kwargs):
        trabajador = kwargs.pop('trabajador', None)
        super().__init__(*args, **kwargs)
        if trabajador:
            # Filtra los estados según el rol del trabajador
            if trabajador.rol == 'almacenista':
                self.fields['estado'].choices = [
                    ('pendiente', 'Pendiente'),
                    ('procesando', 'Procesando'),
                ]
            elif trabajador.rol == 'repartidor':
                self.fields['estado'].choices = [
                    ('enviado', 'Enviado'),
                    ('completado', 'Completado'),
                ]
            elif trabajador.rol == 'gerente':
                self.fields['estado'].choices = [
                    ('enviado', 'Enviado'),
                    ('completado', 'Completado'),
                    ('cancelado', 'Cancelado'),
                ]
#formulario de actualizacion de trabajadores
class TrabajadorForm(forms.ModelForm):
    class Meta:
        model = Trabajadores
        fields = [ 'nombre', 'apellidopat', 'apellidomat', 'salario', 'correo', 'rol']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre'}),
            'apellidopat': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Apellido Paterno'}),
            'apellidomat': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Apellido Materno'}),
            'correo': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Correo Electrónico'}),
            'salario': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Salario'}),
            'correo': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Correo Electrónico'}),
            'rol': forms.Select(attrs={'class': 'form-control'}),
        }
        usuario = forms.ModelChoiceField(queryset=User.objects.filter(user_type='vendedor'), required=False)

class CustomSignupForm(SignupForm):
    password = forms.CharField(widget=forms.PasswordInput)
    class Meta:
        model = User
        fields = ['email', 'name', 'password']
    def clean_email(self):
        email = self.cleaned_data.get('email')
        # Verifica si el correo ya está registrado
        if User.objects.filter(email=email).exists():
            raise ValidationError('Este correo ya está registrado. Usa otro correo.')
        return email

    def save(self, request):
        user = super().save(request)
        user.save()
        return user

class CustomLoginForm(LoginForm):
    def clean(self):
        email = self.cleaned_data.get('email')
        if not email:
            raise forms.ValidationError('El correo electrónico es obligatorio.')
        return self.cleaned_data