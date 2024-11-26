# En nombre_de_la_app/views.py
from django.shortcuts import render, redirect, get_object_or_404
from .forms import UserRegistrationForm, LoginForm, ProductoForm, PedidoForm, DireccionesForm
from django.contrib import messages
from django.contrib.auth.models import Group
from django.contrib.auth import authenticate, login, logout
from .models import Producto, Direcciones, Pedido, DetallePedido


def index(request):
    if not request.user.is_authenticated:
        productos = Producto.objects.all()
        return render(request, 'inicio/index.html',{'productos': productos})
    if request.user.user_type == 'usuario':
        productos = Producto.objects.all()
        return render(request, 'inicio/indexusr.html',{'productos': productos})
    if request.user.user_type == 'admin':
        return render(request, 'inicio/indexadmin.html' )
    
def product(request):
    if not request.user.is_authenticated:
        return render(request, 'inicio/index.html')
    if request.user.user_type == 'usuario':
        return render(request, 'inicio/indexusr.html')
    if request.user.user_type == 'admin':
        productos = Producto.objects.all()
        return render(request, 'inicio/product.html',{'productos': productos})

def detalle_producto(request, id):
    if not request.user.is_authenticated:
        producto = get_object_or_404(Producto, id=id)
        return render(request, 'inicio/detalle_producto.html', {'producto': producto})
    if request.user.user_type == 'usuario':
        producto = get_object_or_404(Producto, id=id)
        return render(request, 'inicio/detalle_producto.html', {'producto': producto})
    if request.user.user_type == 'admin':
        producto = get_object_or_404(Producto, id=id)
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

def add_to_cart(request, product_id):
    cart = request.session.get('cart', {})
    cart[product_id] = cart.get(product_id, 0) + 1
    request.session['cart'] = cart  
    return redirect('detalle_producto',id=product_id)

def carrito(request):
    cart = request.session.get('cart', {})
    products = Producto.objects.filter(id__in=cart.keys())
    cart_items = [
        {'product': product, 'quantity': cart[str(product.id)], 'subtotal': product.precio * cart[str(product.id)]}
        for product in products
    ]
    total = sum(item['subtotal'] for item in cart_items)
    return render(request, 'inicio/cart.html', {'cart_items': cart_items, 'total': total})

def eliminar_del_carrito(request, producto_id):
    cart = request.session.get('cart', {})
    if str(producto_id) in cart:
        del cart[str(producto_id)]
    request.session['cart'] = cart
    return redirect('carrito')

def agregar_direccion(request):
    if request.method == 'POST':
        form = DireccionesForm(request.POST)
        if form.is_valid():
            direccion = form.save(commit=False)
            direccion.usuario = request.user
            direccion.save()
            messages.success(request, 'Dirección agregada exitosamente.')
            return redirect('procesar_pedido')
    else:
        form = DireccionesForm()
    return render(request, 'inicio/agregar_direccion.html', {'form': form})

def pedido_exitoso(request):
    return render(request, 'inicio/pedido_exitoso.html')

def procesar_pedido(request):
    cart = request.session.get('cart', {})
    if not cart:
        messages.error(request, "Tu carrito está vacío. No se puede procesar el pedido.")
        return redirect('carrito')

    user = request.user
    direcciones = Direcciones.objects.filter(usuario_id=user)
    if not direcciones:
        messages.error(request, "Necesitas agregar una dirección para procesar el pedido.")
        return redirect('agregar_direccion')
    
    if request.method == 'POST':
        form = PedidoForm(request.POST, user=user)
        if form.is_valid():
            pedido = form.save(commit=False)
            pedido.usuario = user
            pedido.total = sum(
                Producto.objects.get(id=prod_id).precio * cantidad
                for prod_id, cantidad in cart.items()
            )
            pedido.save()

            for prod_id, cantidad in cart.items():
                producto = Producto.objects.get(id=prod_id)
                DetallePedido.objects.create(
                    pedido=pedido,
                    producto=producto,
                    cantidad=cantidad,
                    subtotal=producto.precio * cantidad
                )
                producto.stock -= cantidad
                producto.save()

            request.session['cart'] = {}
            messages.success(request, f"Pedido procesado exitosamente. Total: ${pedido.total:.2f}")
            return redirect('pedido_exitoso')
    else:
        form = PedidoForm(user=request.user)  # Pasa el usuario aquí

    return render(request, 'inicio/procesar_pedido.html', {'form': form})