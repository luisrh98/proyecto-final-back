from django.db import models
from django.conf import settings  # Para referirte al modelo de usuario que definiste en accounts
from accounts.models import Usuario

class Categoria(models.Model):
    nombre = models.CharField(max_length=50)
    descripcion = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nombre


class Producto(models.Model):
    titulo = models.CharField(max_length=100)
    descripcion = models.TextField()
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    imagen = models.ImageField(upload_to='productos/', blank=True, null=True)
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True, related_name='productos')
    vendedor = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='productos')
    creado_en = models.DateTimeField(auto_now_add=True)  # Se genera automáticamente al crear
    actualizado_en = models.DateTimeField(auto_now=True)  # Se actualiza automáticamente al modificar

    def __str__(self):
        return self.titulo


class Reseña(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='reseñas')
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField()  # Por ejemplo, del 1 al 5
    comentario = models.TextField(blank=True, null=True)
    creado_en = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Reseña de {self.usuario.username} para {self.producto.titulo}"
