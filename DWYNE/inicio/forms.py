from django import forms
from .models import User, Producto

class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    class Meta:
        model = User
        fields = ['email', 'full_name', 'password']


class LoginForm(forms.Form):
    email = forms.EmailField(label='Correo electrónico', widget=forms.EmailInput(attrs={'placeholder': 'Correo electrónico'}))
    password = forms.CharField(label='Contraseña', widget=forms.PasswordInput(attrs={'placeholder': 'Contraseña'}))
    
class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ['titulo', 'descripcion', 'precio', 'imagen', 'video']