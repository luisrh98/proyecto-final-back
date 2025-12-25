from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.admin import AdminSite

from orders.models import MetodoPago, OrderItem, Pago, Pedido
from products.models import Categoria, Producto, Reseña
from .models import SolicitudGestor, Usuario, Direccion

# Panel personalizado
class MyAdminSite(AdminSite):
    site_header = 'Panel de Administración de Bonshop'
    site_title = 'Bonshop Admin'
    index_title = 'Bienvenido al Panel de Administración'

admin_site = MyAdminSite(name='admin')

# ------------------------------
# Usuario y Direcciones Inline
# ------------------------------
class DireccionInline(admin.StackedInline):
    model = Direccion
    extra = 0

class UsuarioAdmin(UserAdmin):
    list_display = ('username', 'email', 'tipo', 'is_active', 'telefono')
    list_filter = ('tipo', 'is_active')
    search_fields = ('username', 'email')
    inlines = [DireccionInline]
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Información Personal', {'fields': ('first_name', 'last_name', 'email', 'telefono')}),
        ('Permisos', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Tipo de Usuario', {'fields': ('tipo',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'tipo', 'telefono'),
        }),
    )

admin_site.register(Usuario, UsuarioAdmin)

# ------------------------------
# SolicitudGestor
# ------------------------------
class SolicitudGestorAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'nombre_tienda', 'identificacion_fiscal', 'estado', 'fecha_creacion')
    list_filter = ('estado', 'fecha_creacion')
    search_fields = ('usuario__username', 'nombre_tienda', 'identificacion_fiscal')

admin_site.register(SolicitudGestor, SolicitudGestorAdmin)

# ------------------------------
# Categoría
# ------------------------------
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'descripcion')
    search_fields = ('nombre',)

admin_site.register(Categoria, CategoriaAdmin)

# ------------------------------
# Producto con Reseñas inline
# ------------------------------
class ReseñaInline(admin.TabularInline):
    model = Reseña
    extra = 0

class ProductoAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'vendedor', 'precio', 'categoria', 'creado_en')
    list_filter = ('categoria', 'vendedor')
    search_fields = ('titulo', 'descripcion')
    inlines = [ReseñaInline]

admin_site.register(Producto, ProductoAdmin)

# ------------------------------
# Reseña
# ------------------------------
class ReseñaAdmin(admin.ModelAdmin):
    list_display = ('producto', 'usuario', 'rating', 'creado_en')
    list_filter = ('producto', 'usuario', 'rating')
    search_fields = ('comentario',)

admin_site.register(Reseña, ReseñaAdmin)

# ------------------------------
# Pedido con OrderItems inline
# ------------------------------
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0

class PedidoAdmin(admin.ModelAdmin):
    list_display = ('id', 'usuario', 'total', 'estado', 'fecha_creacion')
    list_filter = ('estado', 'fecha_creacion')
    search_fields = ('usuario__username', 'id')
    inlines = [OrderItemInline]

admin_site.register(Pedido, PedidoAdmin)

# ------------------------------
# OrderItem
# ------------------------------
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('pedido', 'producto', 'cantidad', 'precio_unitario')
    list_filter = ('pedido', 'producto')

admin_site.register(OrderItem, OrderItemAdmin)

# ------------------------------
# Método de Pago
# ------------------------------
class MetodoPagoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'descripcion')

admin_site.register(MetodoPago, MetodoPagoAdmin)

# ------------------------------
# Pago
# ------------------------------
class PagoAdmin(admin.ModelAdmin):
    list_display = ('pedido', 'metodo', 'monto', 'fecha_transaccion')
    list_filter = ('metodo', 'fecha_transaccion')

admin_site.register(Pago, PagoAdmin)
