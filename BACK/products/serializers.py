import os
from rest_framework import serializers
from .models import Categoria, Producto, Reseña

ALLOWED_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
ALLOWED_MIME_TYPES = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']

class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = '__all__'

class ReseñaSerializer(serializers.ModelSerializer):
    usuario = serializers.StringRelatedField(read_only=True)  # [1]
    producto = serializers.PrimaryKeyRelatedField(
        queryset=Producto.objects.all(),
        write_only=True  # [2]
    )

    class Meta:
        model = Reseña
        fields = ['id', 'producto', 'usuario', 'rating', 'comentario', 'creado_en']
        read_only_fields = ['id', 'creado_en', 'usuario']  # [3]

    def create(self, validated_data):
        validated_data['usuario'] = self.context['request'].user  # [4]
        return super().create(validated_data)
    
#Serializer para leer productos

class ProductoReadSerializer(serializers.ModelSerializer):
    categoria = serializers.StringRelatedField()
    vendedor = serializers.SerializerMethodField()
    reseñas = ReseñaSerializer(many=True, read_only=True)
    imagen = serializers.SerializerMethodField()

    class Meta:
        model = Producto
        fields = [
            'id', 'titulo', 'descripcion', 'precio', 'imagen', 
            'categoria', 'vendedor', 'creado_en', 'actualizado_en', 'reseñas'
        ]

    def get_vendedor(self, obj):
        return {
            'id': obj.vendedor.id,
            'nombre': obj.vendedor.username,
            'email': obj.vendedor.email
        }

    def get_imagen(self, obj):
        if obj.imagen:
            return self.context['request'].build_absolute_uri(obj.imagen.url)
        return None

class ProductoWriteSerializer(serializers.ModelSerializer):
    categoria = serializers.PrimaryKeyRelatedField(queryset=Categoria.objects.all())
    vendedor = serializers.SerializerMethodField()
    reseñas = ReseñaSerializer(many=True, read_only=True)
    

    class Meta:
        model = Producto
        fields = [
            'id', 'titulo', 'descripcion', 'precio', 'imagen', 
            'categoria', 'vendedor', 'creado_en', 'actualizado_en', 'reseñas'
        ]

    def get_vendedor(self, obj):
        return {
            'id': obj.vendedor.id,
            'nombre': obj.vendedor.username,
            'email': obj.vendedor.email
        }

    def get_imagen(self, obj):
        if obj.imagen:
            return self.context['request'].build_absolute_uri(obj.imagen.url)
        return None
    
    def validate_precio(self, value):
        if value < 0:
            raise serializers.ValidationError("El precio no puede ser negativo.")
        return value
        
    imagen = serializers.ImageField(
        required=False,
        allow_null=True,
        error_messages={
            'invalid_image': 'Por favor, sube una imagen válida en formato JPG, PNG, GIF o WEBP.'
        }
    )

    def validate_imagen(self, imagen):
        if imagen:
            ext = os.path.splitext(imagen.name)[1].lower()
            if ext not in ALLOWED_EXTENSIONS:
                raise serializers.ValidationError("Formato de imagen no permitido. Usa JPG, PNG, GIF o WEBP.")
            if hasattr(imagen, 'content_type') and imagen.content_type not in ALLOWED_MIME_TYPES:
                raise serializers.ValidationError("El tipo MIME del archivo no es una imagen válida.")
        return imagen

    def create(self, validated_data):
        # Asignar el usuario autenticado como el vendedor
        validated_data['vendedor'] = self.context['request'].user
        return super().create(validated_data)