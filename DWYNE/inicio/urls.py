# En nombre_de_la_app/urls.py
from django.urls import path
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('login/', views.user_login, name='login'),
    path('register/', views.register, name='register'),
    path('logout/', views.user_logout, name='logout'),
    path('product/', views.product, name='product'),
    path('productos/<int:identificador>/', views.detalle_producto, name='detalle_producto'),
    path('productos/editar/<int:pk>/', views.producto_edit, name='producto_edit'),
    path('productos/borrar/<int:pk>/', views.producto_delete, name='producto_delete'),
    path('vendedores/', views.vendedores, name='vendedores'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)