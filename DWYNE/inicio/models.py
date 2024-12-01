from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

#modelos de la base de datos

# modelo de usuario
class UserManager(BaseUserManager):
    def create_user(self, email, full_name, password=None, **extra_fields):
        if not email:
            raise ValueError('El correo debe ser proporcionado')
        email = self.normalize_email(email)
        user = self.model(email=email, full_name=full_name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    # Crear superusuario
    def create_superuser(self, email, full_name, password=None, **extra_fields):
        extra_fields.setdefault('is_admin', True)
        extra_fields.setdefault('is_superuser', True)
        if extra_fields.get('is_admin') is not True:
            raise ValueError('Superuser debe tener is_admin=True.')
        
        user = self.create_user(email, full_name, password, **extra_fields)
        user.save(using=self._db)
        return user
# Crear modelo de usuario
class User(AbstractBaseUser):
    USER_TYPES = (
        ('admin', 'Admin'),
        ('vendedor', 'Vendedor'),
        ('usuario', 'Usuario'),
    )
    user_type = models.CharField(max_length=10, choices=USER_TYPES, default='usuario')
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=255)
    date_joined = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'  # Esto asegura que el email se usa para autenticación
    REQUIRED_FIELDS = ['full_name']

    def __str__(self):
        return self.full_name

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    @property
    def is_staff(self):
        return self.is_admin
#modelo de producto
class Producto(models.Model):
    titulo = models.CharField(max_length=100)
    descripcion = models.TextField()
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField(default=1)  # Renombrado de 'cantidad'
    imagen = models.ImageField(upload_to='productos_imagenes/', blank=True, null=True)
    video = models.FileField(upload_to='productos_videos/', blank=True, null=True)
    keywords = models.TextField(help_text="Palabras clave separadas por comas")  # Ejemplo: "amor, chocolate, regalo"
    def __str__(self):
        return f"{self.id} - {self.titulo}"

    def reduce_stock(self, quantity):
        if self.stock >= quantity:
            self.stock -= quantity
            self.save()
        else:
            raise ValueError("Stock insuficiente.")
#modelo de trabajadores
class Trabajadores(models.Model):
    ROLES = [
        ('almacenista', 'Almacenista'),
        ('repartidor', 'Repartidor'),
        ('gerente', 'Gerente'),
    ]
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)  # Relación uno a uno
    nombre = models.CharField(max_length=30)
    apellidopat = models.CharField(max_length=30)
    apellidomat = models.CharField(max_length=30)
    correo = models.EmailField(unique=True)
    salario = models.DecimalField(max_digits=20, decimal_places=2)
    correo = models.EmailField(unique=True)
    rol = models.CharField(max_length=15, choices=ROLES, default='operador')

    def __str__(self):
        return f"{self.nombre} {self.apellidopat} {self.apellidomat}"
#modelo de direcciones
class Direcciones(models.Model):  # Renombrado a singular
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)  # Relacionar con el usuario
    codpos = models.IntegerField()
    ciudad = models.CharField(max_length=30)
    colonia = models.CharField(max_length=30)
    calle = models.CharField(max_length=30)

    def __str__(self):
        return f"{self.calle}, {self.colonia}, {self.ciudad}"

#modelo de pedidos
class Pedido(models.Model):
    ESTADOS = [
        ('pendiente', 'Pendiente'),
        ('procesando', 'Procesando'),
        ('enviado', 'Enviado'),
        ('completado', 'Completado'),
        ('cancelado', 'Cancelado'),
    ]
    METODOS_PAGO = [
        ('tarjeta', 'Tarjeta de Crédito/Débito'),
        ('transferencia', 'Transferencia Bancaria'),
        ('contra_entrega', 'Pago Contra Entrega'),
    ]

    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    direccion_envio = models.ForeignKey('Direcciones', on_delete=models.CASCADE)
    metodo_pago = models.CharField(max_length=20, choices=METODOS_PAGO)
    estado = models.CharField(max_length=15, choices=ESTADOS, default='pendiente')
    fecha_pedido = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Pedido {self.id} - {self.usuario} - {self.estado}"

#modelo de detalles de pedidos
class DetallePedido(models.Model):
    pedido = models.ForeignKey(Pedido, related_name='detalles', on_delete=models.CASCADE)
    producto = models.ForeignKey('Producto', on_delete=models.CASCADE)
    cantidad = models.IntegerField()
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Producto {self.producto.titulo} - Pedido {self.pedido.id}"


