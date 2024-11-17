from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

class UserManager(BaseUserManager):
    def create_user(self, email, full_name, password=None, **extra_fields):
        if not email:
            raise ValueError('El correo debe ser proporcionado')
        email = self.normalize_email(email)
        user = self.model(email=email, full_name=full_name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, full_name, password=None, **extra_fields):
        extra_fields.setdefault('is_admin', True)
        extra_fields.setdefault('is_superuser', True)
        if extra_fields.get('is_admin') is not True:
            raise ValueError('Superuser debe tener is_admin=True.')
        
        user = self.create_user(email, full_name, password, **extra_fields)
        user.save(using=self._db)
        return user

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

class Producto(models.Model):
    identificador = models.IntegerField(unique=True)  # Identificador numérico único del producto
    titulo = models.CharField(max_length=100)         # Título del producto
    descripcion = models.TextField()                  # Descripción detallada
    precio = models.DecimalField(max_digits=10, decimal_places=2)  # Precio con 2 decimales
    imagen = models.ImageField(upload_to='productos_imagenes/', blank=True, null=True)  # Imagen principal
    video = models.FileField(upload_to='productos_videos/', blank=True, null=True)      # Video promocional

    def __str__(self):
        return f"{self.identificador} - {self.titulo}"

class Vendedores(models.Model):
    identificador = models.IntegerField(unique=True)
    nombre = models.CharField(max_length=30)
    apellidopat = models.CharField(max_length=30)
    apellidomat = models.CharField(max_length=30)
    puesto = models.CharField(max_length=25)
    salario = models.DecimalField(max_digits=20, decimal_places=2)
    correo = models.EmailField(unique=True)
    def __str__(self):
        return self.nombre + self.apellidopat + self.apellidomat

class Direcciones(models.Model):
    identificador = models.IntegerField(unique=True)
    usuario = models.IntegerField()
    codpos = models.IntegerField(max_length=6)
    ciudad = models.CharField(max_length= 30)
    colonia = models.CharField(max_length=30)
    calle = models.CharField(max_length=30)

class ventas(models.Model):
    identificador = models.IntegerField(unique=True)
    usuario = models.IntegerField()
    producto = models.IntegerField()
    direccion = models.IntegerField()
    cantidad = models.IntegerField()
    fecha = models.DateField(auto_now_add=True)
    total = models.DecimalField(max_digits=20, decimal_places=2)

class userdir(models.Model):
    usuario = models.IntegerField(unique=True)
    direccion = models.IntegerField(unique=True)
