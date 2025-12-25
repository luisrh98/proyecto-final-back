# accounts/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser

# Modelo de usuario personalizado
class Usuario(AbstractUser):
    TIPO_USUARIO = (
        ('admin', 'Administrador'),
        ('gestor', 'Gestor'),
        ('cliente', 'Cliente'),
    )
    email = models.EmailField(unique=True)
    tipo = models.CharField(max_length=10, choices=TIPO_USUARIO, default='cliente')
    telefono = models.CharField(max_length=15, blank=True, null=True)
    token_2fa = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return self.username


class Direccion(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name='direccion')
    calle = models.CharField(max_length=255)
    ciudad = models.CharField(max_length=100)
    codigo_postal = models.CharField(max_length=20)
    pais = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.calle}, {self.ciudad}"
    

class SolicitudGestor(models.Model):
    ESTADO_CHOICES = (
        ('pendiente', 'Pendiente'),
        ('aprobada', 'Aprobada'),
        ('rechazada', 'Rechazada'),
    )

    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='solicitudes')
    nombre_tienda = models.CharField(max_length=255)
    identificacion_fiscal = models.CharField(max_length=50)
    direccion = models.CharField(max_length=255)  # Nueva dirección
    telefono = models.CharField(max_length=20)    # Nuevo teléfono
    estado = models.CharField(max_length=10, choices=ESTADO_CHOICES, default='pendiente')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Solicitud de {self.usuario.username} - {self.nombre_tienda}"
