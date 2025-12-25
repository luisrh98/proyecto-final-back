from rest_framework import viewsets, status
from .models import Categoria, Producto, Reseña
from .serializers import CategoriaSerializer, ProductoReadSerializer, ProductoWriteSerializer, ReseñaSerializer
from rest_framework.permissions import AllowAny, IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.parsers import MultiPartParser, FormParser

class CategoriaViewSet(viewsets.ModelViewSet):
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer
    permission_classes = [AllowAny]

class ProductoPagination(PageNumberPagination):
    page_size = 6

class ProductoViewSet(viewsets.ModelViewSet):
    queryset = Producto.objects.all()
    pagination_class = ProductoPagination
    permission_classes = [AllowAny]
    # Añadimos los parsers para manejar formularios con archivos
    parser_classes = [MultiPartParser, FormParser]

    def get_serializer_class(self):
        if self.request.method in ['POST', 'PUT', 'PATCH']:
            return ProductoWriteSerializer  # Serializer para escritura
        return ProductoReadSerializer  # Serializer para lectura

    def get_queryset(self):
        queryset = Producto.objects.all()

        categoria_id = self.request.query_params.get('categoria')
        if categoria_id:
            queryset = queryset.filter(categoria__id=categoria_id)

        # Filtro por nombre (usando query param 'search')
        search_query = self.request.query_params.get('search', None)
        if search_query:
            queryset = queryset.filter(titulo__icontains=search_query)

        # Ordenación por precio (usando query param 'ordering')
        ordering = self.request.query_params.get('ordering', None)
        if ordering in ['precio', '-precio']:
            queryset = queryset.order_by(ordering)

        return queryset

    def create(self, request, *args, **kwargs):
        """
        Manejo especial para la creación de productos con imágenes
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        """
        Asigna el vendedor automáticamente al crear un producto
        """
        serializer.save(vendedor=self.request.user)

    @action(detail=True, methods=['get'])
    def reseñas(self, request, pk=None):
        """Obtiene todas las reseñas de un producto específico"""
        producto = self.get_object()
        reseñas = Reseña.objects.filter(producto=producto)
        serializer = ReseñaSerializer(reseñas, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def mis_productos(self, request):
        """Obtiene los productos subidos por el usuario autenticado."""
        productos = Producto.objects.filter(vendedor=request.user)
        serializer = self.get_serializer(productos, many=True)
        return Response(serializer.data)
    

class ReseñaViewSet(viewsets.ModelViewSet):
    serializer_class = ReseñaSerializer
    queryset = Reseña.objects.all()
    permission_classes = [IsAuthenticated]  # ← Cambiado a autenticación requerida

    def perform_create(self, serializer):
        serializer.save(usuario=self.request.user)  # ← Asignación automática del usuario

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context