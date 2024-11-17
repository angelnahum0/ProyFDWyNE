# En nombre_de_la_app/views.py
from django.shortcuts import render, redirect, get_object_or_404
from .forms import UserRegistrationForm, LoginForm, ProductoForm
from django.contrib import messages
from django.contrib.auth.models import Group
from django.contrib.auth import authenticate, login, logout
from .models import Producto


def index(request):
    if not request.user.is_authenticated:
        return render(request, 'inicio/index.html')
    if request.user.user_type == 'usuario':
        return render(request, 'inicio/indexusr.html')
    if request.user.user_type == 'admin':
        return render(request, 'inicio/indexadmin.html')
    
def product(request):
    if not request.user.is_authenticated:
        return render(request, 'inicio/index.html')
    if request.user.user_type == 'usuario':
        return render(request, 'inicio/indexusr.html')
    if request.user.user_type == 'admin':
        productos = Producto.objects.all()
        return render(request, 'inicio/product.html',{'productos': productos})

def detalle_producto(request, identificador):
    if not request.user.is_authenticated:
        return render(request, 'inicio/index.html')
    if request.user.user_type == 'usuario':
        return render(request, 'inicio/indexusr.html')
    if request.user.user_type == 'admin':
        producto = get_object_or_404(Producto, identificador=identificador)
        return render(request, 'inicio/detalle_producto.html', {'producto': producto})

def vendedores(request):
    if not request.user.is_authenticated:
        return render(request, 'inicio/index.html')
    if request.user.user_type == 'usuario':
        return render(request, 'inicio/indexusr.html')
    if request.user.user_type == 'admin':
        return render(request, 'inicio/vendedores.html')

def adminbdcompradores(request):
    if not request.user.is_authenticated:
        return render(request, 'inicio/index.html')
    if request.user.user_type == 'usuario':
        return render(request, 'inicio/indexusr.html')
    if request.user.user_type == 'admin':
        return render(request, 'inicio/bdcompradores.html')

def about(request):
    return render(request, 'inicio/about.html')

def contact(request):
    return render(request, 'inicio/contact.html')

def contact(request):
    return render(request, 'inicio/contact.html')
def contact(request):
    return render(request, 'inicio/contact.html')

def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            # Intentar autenticar al usuario usando email y password
            user = authenticate(request, email=email, password=password)

            if user is not None:
                # Si el usuario es autenticado, iniciar sesión
                login(request, user)
                messages.success(request, 'Inicio de sesión exitoso.')
                return redirect('index')  # Redirige a la página principal o donde quieras
            else:
                messages.error(request, 'Correo o contraseña incorrectos.')
        else:
            messages.error(request, 'Formulario no válido.')

    else:
        form = LoginForm()

    return render(request, 'inicio/login.html', {'form': form})

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            # Crear un nuevo usuario
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])  # Cifra la contraseña
            user.save()
            messages.success(request, 'Usuario registrado con éxito.')
            return redirect('login')  # Redirige al formulario de inicio de sesión
    else:
        form = UserRegistrationForm()

    return render(request, 'inicio/register.html', {'form': form})
def user_logout(request):
    logout(request)
    return redirect('login')  # Redirige a la página de login después de cerrar sesión

def producto_edit(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES, instance=producto)
        if form.is_valid():
            form.save()
            return redirect('product')
    else:
        form = ProductoForm(instance=producto)
    return render(request, 'inicio/editar.html', {'form': form})

def producto_delete(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == 'POST':
        producto.delete()
        return redirect('product')
    return render(request, 'inicio/confirmar_borrar.html', {'producto': producto})

