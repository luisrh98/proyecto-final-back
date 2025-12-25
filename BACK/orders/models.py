from django.db import models
from django.conf import settings
from products.models import Producto  # Para relacionar con OrderItem


class Pedido(models.Model):
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='pedidos'
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    estado = models.CharField(max_length=20, default='pendiente')
    calle = models.CharField(max_length=255, null=True, blank=True)
    ciudad = models.CharField(max_length=100, null=True, blank=True)
    codigo_postal = models.CharField(max_length=20, null=True, blank=True)
    pais = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return f"Pedido {self.id} de {self.usuario.username}"


class OrderItem(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='items')
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=1)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.cantidad} x {self.producto.titulo}"


class MetodoPago(models.Model):
    nombre = models.CharField(max_length=50)  # Ej.: Tarjeta de Crédito, PayPal, etc.
    descripcion = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nombre


class Pago(models.Model):
    pedido = models.OneToOneField(Pedido, on_delete=models.CASCADE, related_name='pago')
    metodo = models.ForeignKey(MetodoPago, on_delete=models.SET_NULL, null=True)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_transaccion = models.DateTimeField(auto_now_add=True)
    transaccion_id = models.CharField(max_length=100, blank=True, null=True)
    factura_url = models.URLField(null=True, blank=True)

    def __str__(self):
        return f"Pago de {self.monto} para el Pedido {self.pedido.id}"
