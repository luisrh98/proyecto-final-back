from django_filters import rest_framework as filters
from .models import Producto

class ProductoFilter(filters.FilterSet):
    min_precio = filters.NumberFilter(field_name="precio", lookup_expr='gte')
    max_precio = filters.NumberFilter(field_name="precio", lookup_expr='lte')

    class Meta:
        model = Producto
        fields = ['categoria', 'min_precio', 'max_precio']