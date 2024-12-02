# En nombre_de_la_app/urls.py
from django.urls import path
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from inicio.views import CustomLoginView
from django.urls import include
from . import views

# urls que se usan en la aplicación
urlpatterns = [
    path('', views.index, name='index'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('register/', views.register, name='register'),
    path('logout/', views.user_logout, name='logout'),
    path('product/', views.product, name='product'),
    path('productos/<int:id>/', views.detalle_producto, name='detalle_producto'),
    path('productos/editar/<int:pk>/', views.producto_edit, name='producto_edit'),
    path('productos/borrar/<int:pk>/', views.producto_delete, name='producto_delete'),
    path('carrito/', views.carrito, name='carrito'),
    path('add_to_cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('carrito/eliminar/<int:producto_id>/', views.eliminar_del_carrito, name='eliminar_del_carrito'),
    path('carrito/procesar/', views.procesar_pedido, name='procesar_pedido'),
    path('pedido/exitoso/', views.pedido_exitoso, name='pedido_exitoso'),
    path('direccion/agregar/', views.agregar_direccion, name='agregar_direccion'),
    path('agregar_producto/', views.agregar_producto, name='agregar_producto'),
    path('mi_cuenta/', views.mi_cuenta, name='mi_cuenta'),
    path('mi_cuenta/editar/', views.editar_perfil, name='editar_perfil'),
    path('mi_cuenta/cambiar_password/', views.cambiar_password, name='cambiar_password'),
    path('mi_cuenta/mis_pedidos/', views.mis_pedidos, name='mis_pedidos'),
    path('mi_cuenta/mis_pedidos/<int:id>/', views.detalle_pedido, name='detalle_pedido'),
    path('mi_cuenta/mis_direcciones/', views.mis_direcciones, name='mis_direcciones'),
    path('mi_cuenta/mis_direcciones/<int:id>/', views.editar_direccion, name='editar_direccion'),
    path('mi_cuenta/mis_direcciones/borrar/<int:id>/', views.borrar_direccion, name='borrar_direccion'),
    path('buscar/', views.buscar_productos, name='buscar_productos'),
    path('vendedores/', views.vendedores, name='vendedores'),
    path('vendedores/<int:id>/', views.vendedor, name='vendedor'),
    path('agregar_vendedor/', views.agregar_vendedor, name='agregar_vendedor'),
    path('pedidos/<int:id>/', views.detalle_pedido, name='pedidos'),
    path('pedidos/<int:id>/actualizar_pedido/', views.actualizar_estado_pedido, name='actualizar_pedido'),
    path('editar_vendedor/<int:id>/', views.editar_vendedor, name='editar_vendedor'),
    path('borrar_vendedor/<int:id>/', views.borrar_vendedor, name='borrar_vendedor'),
    path('scrape/', views.scrape_view, name='scrape'),
    path('accounts/', include('allauth.urls')),  # Rutas para autenticación social
    
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)