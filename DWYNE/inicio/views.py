# En nombre_de_la_app/views.py
from django.shortcuts import render, redirect, get_object_or_404
from .forms import UserRegistrationForm, LoginForm, ProductoForm, PedidoForm, DireccionesForm, UserEditForm, PasswordCambioForm, SearchForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.contrib.auth.views import LoginView
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.http import HttpResponseBadRequest
from .models import Producto, Direcciones, Pedido, DetallePedido
import requests
from bs4 import BeautifulSoup
from django.http import JsonResponse


def index(request):
    productos = Producto.objects.all()
    return render(request, 'inicio/index.html',{'productos': productos})
    
def product(request):
    if not request.user.is_authenticated:
        return render(request, 'inicio/index.html')
    if request.user.user_type == 'usuario':
        redirect('index')
    if request.user.user_type == 'admin':
        productos = Producto.objects.all()
        return render(request, 'inicio/product.html',{'productos': productos})

def detalle_producto(request, id):
    if not request.user.is_authenticated:
        producto = get_object_or_404(Producto, id=id)
        return render(request, 'inicio/detalle_producto.html', {'producto': producto})
    if request.user.user_type == 'usuario':
        producto = get_object_or_404(Producto, id=id)
        keywords = producto.keywords.split(',')
        url = "https://unelefante.mx/collections/regalos-de-amor-y-aniversario"
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Encuentra los contenedores de productos
        products = soup.find_all('div', class_='product-collection__content')
        scraped_data = []

        for product in products:
            # Extraer el título del producto
            title = product.find('h4', class_='h6 m-0').text.strip() if product.find('h4', class_='h6 m-0') else 'Título no disponible'

            # Extraer descripción del producto
            description_container = product.find('div', class_='product-collection__description')
            description = description_container.find('p', class_='m-0').text.strip() if description_container else 'Descripción no disponible'
            matches = [keyword for keyword in keywords if keyword.lower() in description.lower()]

            # Extraer el precio del producto
            price_container = product.find('div', class_='product-collection__price')
            price = price_container.find('span', class_='money').text.strip() if price_container else 'Precio no disponible'
            price_value = float(price.replace('$', '').replace(',', '').strip()) if price != 'Precio no disponible' else 0
            producto_precio = float(producto.precio)
            if len(matches) > 0:
                if price_value > producto_precio:
                    scraped_data.append({
                        'title': title,
                        'description': description,
                        'matches' : matches,
                        'price': price,
                    })

        # Retorna los datos en formato JSON
        return render(request, 'inicio/detalle_producto.html', {'producto': producto, 'datos': scraped_data})
    
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
    if request.method == 'POST':
        try:
            cantidad = int(request.POST.get('cantidad', 1))
        except ValueError:
            return HttpResponseBadRequest("Cantidad no válida")
        
        producto = get_object_or_404(Producto, id=product_id)  # Asegúrate de tener el modelo Producto
        if cantidad > producto.stock:
            messages.error(request, f"No puedes agregar más de {producto.stock} unidades.")
            return redirect('detalle_producto', id=product_id)
        
        cart = request.session.get('cart', {})
        if str(product_id) in cart:
            cart[str(product_id)] += cantidad
        else:
            cart[str(product_id)] = cantidad
        
        request.session['cart'] = cart
        messages.success(request, f"{cantidad} unidades añadidas al carrito.")
        return redirect('detalle_producto', id=product_id)
    else:
        return HttpResponseBadRequest("Método no permitido")
@login_required
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

def agregar_producto(request):
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('product')
    else:
        form = ProductoForm()
    return render(request, 'inicio/agregar_producto.html', {'form': form})

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

def mi_cuenta(request):
    return render(request, 'inicio/user_account.html')

def editar_perfil(request):
    if request.method == 'POST':
        form = UserEditForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Perfil actualizado exitosamente.')
            return redirect('mi_cuenta')
    else:
        form = UserEditForm(instance=request.user)
    return render(request, 'inicio/editar_perfil.html', {'form': form})

def cambiar_password(request):
    if request.method == 'POST':
        form = PasswordCambioForm(data=request.POST, user=request.user)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)
            messages.success(request, 'Contraseña actualizada exitosamente.')
            return redirect('mi_cuenta')
    else:
        form = PasswordCambioForm(user=request.user)
    return render(request, 'inicio/cambiar_password.html', {'form': form})

def mis_pedidos(request):
    pedidos = Pedido.objects.filter(usuario=request.user)
    return render(request, 'inicio/mis_pedidos.html', {'pedidos': pedidos})

def detalle_pedido(request, id):
    pedido = get_object_or_404(Pedido, id=id)
    return render(request, 'inicio/detalle_pedido.html', {'pedido': pedido})

def mis_direcciones(request):
    direcciones = Direcciones.objects.filter(usuario=request.user)
    return render(request, 'inicio/mis_direcciones.html', {'direcciones': direcciones})

def editar_direccion(request, id):
    direccion = get_object_or_404(Direcciones, id=id)
    if request.method == 'POST':
        form = DireccionesForm(request.POST, instance=direccion)
        if form.is_valid():
            form.save()
            return redirect('mis_direcciones')
    else:
        form = DireccionesForm(instance=direccion)
    return render(request, 'inicio/editar_direccion.html', {'form': form})

def borrar_direccion(request, id):
    direccion = get_object_or_404(Direcciones, id=id)
    if request.method == 'POST':
        direccion.delete()
        return redirect('mis_direcciones')
    return render(request, 'inicio/confirmar_borrar_direccion.html', {'direccion': direccion})


def buscar_productos(request):
    form = SearchForm(request.GET or None)
    productos = None

    if form.is_valid():
        query = form.cleaned_data['query']
        if query:
            productos = Producto.objects.filter(titulo__icontains=query)

    return render(request, 'inicio/buscar_productos.html', {'form': form, 'productos': productos})

def scrape_view(request):
    # URL del sitio web
    url = "https://unelefante.mx/collections/regalos-de-amor-y-aniversario"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Encuentra los contenedores de productos
    products = soup.find_all('div', class_='product-collection__content')
    scraped_data = []

    for product in products:
        # Extraer el título del producto
        producto = get_object_or_404(Producto, id=4)
        keywords = producto.keywords.split(',')
        title = product.find('h4', class_='h6 m-0').text.strip() if product.find('h4', class_='h6 m-0') else 'Título no disponible'

        # Extraer descripción del producto
        description_container = product.find('div', class_='product-collection__description')
        description = description_container.find('p', class_='m-0').text.strip() if description_container else 'Descripción no disponible'
        matches = [keyword for keyword in keywords if keyword.lower() in description.lower()]
        # Extraer el precio del producto
        price_container = product.find('div', class_='product-collection__price')
        price = price_container.find('span', class_='money').text.strip() if price_container else 'Precio no disponible'

        # Agregar datos al listado
        scraped_data.append({
            'title': title,
            'description': description,
            'matches' : matches,
            'price': price,
        })

    # Retorna los datos en formato JSON
    return JsonResponse({'products': scraped_data})

class CustomLoginView(LoginView):
    template_name = 'inicio/login.html'

    def get_redirect_url(self):
        next_url = self.request.GET.get('next')
        return next_url or super().get_redirect_url()