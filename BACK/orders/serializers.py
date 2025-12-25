from rest_framework import serializers

from accounts.serializers import DireccionSerializer
from products.serializers import ProductoReadSerializer
from .models import Pedido, OrderItem

class OrderItemSerializer(serializers.ModelSerializer):
    producto_titulo = serializers.CharField(source='producto.titulo', read_only=True)
    
    # Campos anidados para la dirección del pedido
    pedido_calle = serializers.CharField(source='pedido.calle', read_only=True)
    pedido_ciudad = serializers.CharField(source='pedido.ciudad', read_only=True)
    pedido_codigo_postal = serializers.CharField(source='pedido.codigo_postal', read_only=True)
    pedido_pais = serializers.CharField(source='pedido.pais', read_only=True)
    
    pedido_id = serializers.IntegerField(source='pedido.id', read_only=True)  # <-- Aquí el id del pedido

    class Meta:
        model = OrderItem
        fields = [
            'id', 
            'producto_titulo', 
            'cantidad', 
            'precio_unitario',
            'pedido_calle',
            'pedido_ciudad',
            'pedido_codigo_postal',
            'pedido_pais',
            'pedido_id',   # <-- Añadido aquí
        ]

class PedidoSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Pedido
        fields = ['id', 'usuario', 'fecha_creacion', 'total', 'estado', 
                  'calle', 'ciudad', 'codigo_postal', 'pais', 'items']
        

class PedidoFiltradoPorGestorSerializer(serializers.Serializer):
    pedido = PedidoSerializer()
    items = OrderItemSerializer(many=True)
        

