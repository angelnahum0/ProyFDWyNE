# En nombre_de_la_app/views.py
from django.shortcuts import render, redirect, get_object_or_404
from .forms import UserRegistrationForm, LoginForm, ProductoForm, PedidoForm, DireccionesForm, UserEditForm, PasswordCambioForm, SearchForm, ActualizarEstadoProductoForm, TrabajadorForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.contrib.auth.views import LoginView
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.http import HttpResponseBadRequest
from .models import Producto, Direcciones, Pedido, DetallePedido, Trabajadores
import requests
from bs4 import BeautifulSoup
from django.http import JsonResponse


def index(request):
    #revisa si el usuario esta autenticado
    if not request.user.is_authenticated:
        productos = Producto.objects.all()
        return render(request, 'inicio/index.html',{'productos': productos})
    #si el usuario es un usuario
    if request.user.user_type == 'usuario':
        productos = Producto.objects.all()
        return render(request, 'inicio/index.html',{'productos': productos})
    #si el usuario es un administrador
    if request.user.user_type == 'admin':
        return render(request, 'inicio/index.html')
    #si el usuario es un vendedor
    if request.user.user_type == 'vendedor':
        pedidos = Pedido.objects.all()
        return render(request, 'inicio/index.html', {'pedidos': pedidos} )
@login_required
def product(request):
    #revisa si el usuario esta autenticado
    if not request.user.is_authenticated:
        return redirect('index')
    #si el usuario es un usuario
    if request.user.user_type == 'usuario':
        return redirect('index')
    #si el usuario es un administrador
    if request.user.user_type == 'admin':
        productos = Producto.objects.all()
        return render(request, 'inicio/product.html',{'productos': productos})



def detalle_producto(request, id):
    #revisa si el usuario esta autenticado
    if not request.user.is_authenticated:
        producto = get_object_or_404(Producto, id=id)
        return render(request, 'inicio/detalle_producto.html', {'producto': producto})
    #si el usuario es un usuario
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
    #si el usuario es un administrador
    if request.user.user_type == 'admin':
        producto = get_object_or_404(Producto, id=id)
        return render(request, 'inicio/detalle_producto.html', {'producto': producto})
    
@login_required
def vendedores(request):
    #revisa si el usuario esta autenticado
    if not request.user.is_authenticated:
        return redirect('index')
    #si el usuario es un usuario
    if request.user.user_type == 'usuario':
        return redirect('index')
    #si el usuario es un administrador
    if request.user.user_type == 'admin':
        vendedores = Trabajadores.objects.all()
        return render(request, 'inicio/vendedores.html', {'vendedores': vendedores})
@login_required
def vendedor(request):
    #revisa si el usuario esta autenticado
    if not request.user.is_authenticated:
        return render(request, 'inicio/index.html')
    #si el usuario es un usuario
    if request.user.user_type == 'usuario':
        return render(request, 'inicio/indexusr.html')
    #si el usuario es un administrador
    if request.user.user_type == 'admin':
        return render(request, 'inicio/vendedores.html')
@login_required
def agregar_vendedor(request):
    #revisa si el usuario esta autenticado
    if not request.user.is_authenticated:
        return render(request, 'inicio/index.html')
    #si el usuario es un usuario
    if request.user.user_type == 'usuario':
        return render(request, 'inicio/indexusr.html')
    #si el usuario es un administrador
    if request.user.user_type == 'admin':
        if request.method == 'POST':
            # Crear instancias de los formularios
            usuario_form = UserRegistrationForm(request.POST)
            trabajador_form = TrabajadorForm(request.POST)
            
            if usuario_form.is_valid() and trabajador_form.is_valid():
                # Guardar el Usuario
                usuario = usuario_form.save(commit=False)
                usuario.set_password(usuario_form.cleaned_data['password'])  # Cifra la contraseña
                usuario.user_type = 'vendedor' # Asignar el tipo de usuario vendedor
                usuario = usuario_form.save()
                
                # Crear y guardar el Trabajador con la relación con el Usuario
                trabajador = trabajador_form.save(commit=False)
                trabajador.usuario = usuario
                trabajador.save()
                
                return redirect('vendedores')  # Redirigir a una página de éxito
            
        else:
            usuario_form = UserRegistrationForm()
            trabajador_form = TrabajadorForm()

        return render(request, 'inicio/agregar_vendedor.html', {'usuario_form': usuario_form, 'trabajador_form': trabajador_form})
    
@login_required
def borrar_vendedor(request, id):
    #revisa si el usuario esta autenticado
    if not request.user.is_authenticated:
        return redirect('index')
    #si el usuario es un usuario
    if request.user.user_type == 'usuario':
        return redirect('index')
    #si el usuario es un administrador
    if request.user.user_type == 'admin':
        # Obtener el vendedor
        vendedor = get_object_or_404(Trabajadores, id=id)
        if request.method == 'POST':
            # Borrar el vendedor
            vendedor.delete()
            return redirect('vendedores')
        #mostrar la confirmación de borrar vendedor
        return render(request, 'inicio/confirmar_borrar_trabajador.html', {'vendedor': vendedor})
@login_required
def editar_vendedor(request, id):
    #revisa si el usuario esta autenticado
    if not request.user.is_authenticated:
        return redirect('index')
    #si el usuario es un usuario
    if request.user.user_type == 'usuario':
        return redirect('index')
    #si el usuario es un administrador
    if request.user.user_type == 'admin':
        vendedor = get_object_or_404(Trabajadores, id=id)  # Obtener el trabajador
        if request.method == 'POST':
            trabajador_form = TrabajadorForm(request.POST, instance=vendedor)  # Solo editar el trabajador
            if trabajador_form.is_valid():
                trabajador_form.save()  # Guardar los cambios en el trabajador
                
                return redirect('vendedores')  # Redirigir a la lista de vendedores 
        else:
            # Mostrar el formulario con los datos actuales del trabajador
            trabajador_form = TrabajadorForm(instance=vendedor)

        return render(request, 'inicio/editar_trabajador.html', {'trabajador_form': trabajador_form})


def about(request):
    return render(request, 'inicio/about.html')

def contact(request):
    productos = Producto.objects.all()
    return render(request, 'inicio/contact.html',{'productos': productos})
    

def user_login(request):
    storage = messages.get_messages(request)  # Obtén y limpia mensajes antiguos
    storage.used = True  # Marca todos como leídos
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            # Obtener los datos del formulario
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
        # Crear una instancia del formulario 
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
    #revisa si el usuario esta autenticado
    if not request.user.is_authenticated:
        return redirect('index')
    #revisa si el usuario es un usuario
    if request.user.user_type == 'usuario':
        return redirect('index')
    #revisa si el usuario es un administrador
    if request.user.user_type == 'admin':
        producto = get_object_or_404(Producto, pk=pk)
        if request.method == 'POST':
            # Crear una instancia del formulario con los datos actuales del producto
            form = ProductoForm(request.POST, request.FILES, instance=producto)
            if form.is_valid():
                form.save()
                return redirect('product')
        else:
            form = ProductoForm(instance=producto)
        return render(request, 'inicio/editar.html', {'form': form})

def producto_delete(request, pk):
    #revisa si el usuario esta autenticado
    if not request.user.is_authenticated:
        return redirect('index')
    #revisa si el usuario es un usuario
    if request.user.user_type == 'usuario':
        return redirect('index')
    #revisa si el usuario es un administrador
    if request.user.user_type == 'admin':
        # Obtener el producto
        producto = get_object_or_404(Producto, pk=pk)
        if request.method == 'POST':
            # Borrar el producto
            producto.delete()
            return redirect('product')
        return render(request, 'inicio/confirmar_borrar.html', {'producto': producto})


def add_to_cart(request, product_id):
    if request.method == 'POST':
        # Obtener la cantidad del producto
        try:
            cantidad = int(request.POST.get('cantidad', 1))
        except ValueError:
            return HttpResponseBadRequest("Cantidad no válida")
        # Obtener el producto
        producto = get_object_or_404(Producto, id=product_id) 
        # Verificar si la cantidad es válida
        if cantidad > producto.stock:
            messages.error(request, f"No puedes agregar más de {producto.stock} unidades.")
            return redirect('detalle_producto', id=product_id)
        # Obtener el carrito de la sesión
        cart = request.session.get('cart', {})
        # Añadir el producto al carrito
        if str(product_id) in cart:
            # Si el producto ya está en el carrito, incrementar la cantidad
            cart[str(product_id)] += cantidad
        else:
            # Si el producto no está en el carrito, añadirlo con la cantidad
            cart[str(product_id)] = cantidad
        # Guardar el carrito en la sesión
        request.session['cart'] = cart
        messages.success(request, f"{cantidad} unidades añadidas al carrito.")
        return redirect('detalle_producto', id=product_id)
    else:
        return HttpResponseBadRequest("Método no permitido")
@login_required
def carrito(request):
    # Obtener los productos del carrito
    cart = request.session.get('cart', {})
    products = Producto.objects.filter(id__in=cart.keys())
    # Crear una lista de diccionarios con los productos, cantidades y subtotales
    cart_items = [
        {'product': product, 'quantity': cart[str(product.id)], 'subtotal': product.precio * cart[str(product.id)]}
        for product in products
    ]
    # Calcular el total
    total = sum(item['subtotal'] for item in cart_items)
    # Renderizar la plantilla con los productos del carrito
    return render(request, 'inicio/cart.html', {'cart_items': cart_items, 'total': total})
@login_required
def eliminar_del_carrito(request, producto_id):
    # Eliminar un producto del carrito
    cart = request.session.get('cart', {})
    if str(producto_id) in cart:
        del cart[str(producto_id)]
    # Guardar el carrito en la sesión
    request.session['cart'] = cart
    return redirect('carrito')
@login_required
def agregar_direccion(request):
    #revisa si el usuario esta autenticado
    if request.method == 'POST':
        # Crear una instancia del formulario
        form = DireccionesForm(request.POST)
        if form.is_valid():
            direccion = form.save(commit=False)
            # Asignar el usuario actual a la dirección
            direccion.usuario = request.user
            direccion.save()
            messages.success(request, 'Dirección agregada exitosamente.')
            return redirect('procesar_pedido')
    else:
        form = DireccionesForm()
    return render(request, 'inicio/agregar_direccion.html', {'form': form})
@login_required
def pedido_exitoso(request):
    return render(request, 'inicio/pedido_exitoso.html')

@login_required
def agregar_producto(request):
    #revisa si el usuario esta autenticado
    if not request.user.is_authenticated:
        return redirect('index')
    #revisa si el usuario es un usuario
    if request.user.user_type == 'usuario':
        return redirect('index')
    #revisa si el usuario es un administrador
    if request.user.user_type == 'admin':
        if request.method == 'POST':
            form = ProductoForm(request.POST, request.FILES)
            if form.is_valid():
                form.save()
                return redirect('product')
        else:
            form = ProductoForm()
        return render(request, 'inicio/agregar_producto.html', {'form': form})
@login_required
def procesar_pedido(request):
    # Obtener el carrito de la sesión
    cart = request.session.get('cart', {})
    if not cart:
        # Si el carrito está vacío, mostrar un mensaje de error
        messages.error(request, "Tu carrito está vacío. No se puede procesar el pedido.")
        return redirect('carrito')
    # Obtener las direcciones del usuario
    user = request.user
    direcciones = Direcciones.objects.filter(usuario_id=user)
    # Si el usuario no tiene direcciones, mostrar un mensaje y permitir agregar una dirección
    if not direcciones:
        messages.error(request, "Necesitas agregar una dirección para procesar el pedido.")
        return redirect('agregar_direccion')
    # Procesar el formulario de pedido
    if request.method == 'POST':
        # Crear una instancia del formulario
        form = PedidoForm(request.POST, user=user)
        if form.is_valid():
            # Crear una instancia del pedido
            pedido = form.save(commit=False)
            # Asignar el usuario y el total al pedido
            pedido.usuario = user
            # Calcular el total del pedido
            pedido.total = sum(
                Producto.objects.get(id=prod_id).precio * cantidad
                for prod_id, cantidad in cart.items()
            )
            # Guardar el pedido
            pedido.save()
            # Crear y guardar los detalles del pedido
            for prod_id, cantidad in cart.items():
                # Obtener el producto
                producto = Producto.objects.get(id=prod_id)
                # Crear y guardar el detalle del pedido
                DetallePedido.objects.create(
                    pedido=pedido,
                    producto=producto,
                    cantidad=cantidad,
                    subtotal=producto.precio * cantidad
                )
                # Reducir el stock del producto
                producto.stock -= cantidad
                # Guardar el producto
                producto.save()
            # Limpiar el carrito
            request.session['cart'] = {}
            messages.success(request, f"Pedido procesado exitosamente. Total: ${pedido.total:.2f}")
            return redirect('pedido_exitoso')
    else:
        form = PedidoForm(user=request.user)  # Pasa el usuario aquí
    return render(request, 'inicio/procesar_pedido.html', {'form': form})
@login_required
def mi_cuenta(request):
    return render(request, 'inicio/user_account.html')

@login_required
def editar_perfil(request):
    if request.method == 'POST':
        # Crear una instancia del formulario con los datos actuales del usuario
        form = UserEditForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            # Actualizar la sesión del usuario
            messages.success(request, 'Perfil actualizado exitosamente.')
            return redirect('mi_cuenta')
    else:
        # Mostrar el formulario con los datos actuales del usuario
        form = UserEditForm(instance=request.user)
    return render(request, 'inicio/editar_perfil.html', {'form': form})

@login_required
def cambiar_password(request):
    # Cambiar la contraseña del usuario
    if request.method == 'POST':
        # Crear una instancia del formulario
        form = PasswordCambioForm(data=request.POST, user=request.user)
        if form.is_valid():
            form.save()
            # Actualizar la sesión del usuario
            update_session_auth_hash(request, form.user)
            # Mostrar un mensaje de éxito
            messages.success(request, 'Contraseña actualizada exitosamente.')
            # Redirigir a la página de inicio
            return redirect('mi_cuenta')
    else:
        # Mostrar el formulario
        form = PasswordCambioForm(user=request.user)
    return render(request, 'inicio/cambiar_password.html', {'form': form})
@login_required
def mis_pedidos(request):
    # Obtener los pedidos del usuario
    pedidos = Pedido.objects.filter(usuario=request.user)
    return render(request, 'inicio/mis_pedidos.html', {'pedidos': pedidos})

@login_required
def actualizar_estado_pedido(request, id):
    # Obtener el pedido
    pedido = get_object_or_404(Pedido, id=id)
    # Obtener el trabajador
    trabajador = Trabajadores.objects.get(usuario=request.user)
    # Actualizar el estado del pedido
    form = ActualizarEstadoProductoForm(request.POST, trabajador=trabajador, instance=pedido)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return redirect('index')
    else:
        form = ActualizarEstadoProductoForm(instance=pedido, trabajador=trabajador)
    return render(request, 'inicio/actualizar_pedido.html', {'form': form})

@login_required
def detalle_pedido(request, id):
    # Obtener el pedido
    pedido = get_object_or_404(Pedido, id=id)
    return render(request, 'inicio/detalle_pedido.html', {'pedido': pedido})
@login_required
def mis_direcciones(request):
    # Obtener las direcciones del usuario
    direcciones = Direcciones.objects.filter(usuario=request.user)
    return render(request, 'inicio/mis_direcciones.html', {'direcciones': direcciones})
@login_required
def editar_direccion(request, id):
    # Obtener la dirección
    direccion = get_object_or_404(Direcciones, id=id)
    if request.method == 'POST':
        # Crear una instancia del formulario con los datos actuales de la dirección
        form = DireccionesForm(request.POST, instance=direccion)
        if form.is_valid():
            form.save()
            return redirect('mis_direcciones')
    else:
        form = DireccionesForm(instance=direccion)
    return render(request, 'inicio/editar_direccion.html', {'form': form})

@login_required
def borrar_direccion(request, id):
    # Obtener la dirección
    direccion = get_object_or_404(Direcciones, id=id)
    # Confirmar el borrado de la dirección
    if request.method == 'POST':
        direccion.delete()
        return redirect('mis_direcciones')
    return render(request, 'inicio/confirmar_borrar_direccion.html', {'direccion': direccion})

def buscar_productos(request):
    # Buscar productos
    form = SearchForm(request.GET or None)
    productos = None
    # Si el formulario es válido, buscar productos
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
    # Plantilla de inicio de sesión personalizada
    template_name = 'inicio/login.html'
    # Redirigir a la página siguiente después de iniciar sesión
    def get_redirect_url(self):
        next_url = self.request.GET.get('next')
        return next_url or super().get_redirect_url()
    
