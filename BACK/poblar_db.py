import os
import django
from faker import Faker
from random import randint, choice

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proyecto_final.settings')
django.setup()

# Importar modelos
from accounts.models import Usuario, Direccion
from products.models import Categoria, Producto, Reseña
from orders.models import Pedido, OrderItem, MetodoPago, Pago
from communications.models import Notificacion , Mensaje

fake = Faker('es_ES')  # Usar datos en español

# Crear usuarios
def crear_usuarios(cantidad=10):
    usuarios = []
    for _ in range(cantidad):
        username = fake.user_name()
        email = fake.email()
        password = "password"
        tipo = choice(['admin', 'gestor', 'cliente'])
        telefono = fake.numerify(text="###########")[:15] if randint(0, 1) else None  # Limita a 15 caracteres
        token_2fa = fake.uuid4() if randint(0, 1) else None
        usuario = Usuario.objects.create_user(
            username=username,
            email=email,
            password=password,
            tipo=tipo,
            telefono=telefono,
            token_2fa=token_2fa
        )
        usuarios.append(usuario)
    return usuarios

# Crear categorías
def crear_categorias(cantidad=5):
    categorias = []
    for _ in range(cantidad):
        nombre = fake.word().capitalize()
        descripcion = fake.sentence()
        categoria = Categoria.objects.create(nombre=nombre, descripcion=descripcion)
        categorias.append(categoria)
    return categorias

# Crear productos
def crear_productos(categorias, vendedores, cantidad=20):
    productos = []
    for _ in range(cantidad):
        titulo = fake.sentence(nb_words=3)
        descripcion = fake.paragraph()
        precio = round(fake.pydecimal(left_digits=3, right_digits=2, positive=True), 2)
        imagen = "productos/default.jpg"  # Imagen por defecto
        categoria = choice(categorias)
        vendedor = choice(vendedores)
        producto = Producto.objects.create(
            titulo=titulo,
            descripcion=descripcion,
            precio=precio,
            imagen=imagen,
            categoria=categoria,
            vendedor=vendedor
        )
        productos.append(producto)
    return productos

# Crear pedidos
def crear_pedidos(usuarios, cantidad=10):
    pedidos = []
    for _ in range(cantidad):
        usuario = choice(usuarios)
        total = round(fake.pydecimal(left_digits=3, right_digits=2, positive=True), 2)
        estado = choice(['pendiente', 'completado', 'cancelado'])
        pedido = Pedido.objects.create(usuario=usuario, total=total, estado=estado)
        pedidos.append(pedido)
    return pedidos

# Crear items de pedido
def crear_order_items(pedidos, productos, cantidad=30):
    for _ in range(cantidad):
        pedido = choice(pedidos)
        producto = choice(productos)
        cantidad_item = randint(1, 5)
        precio_unitario = producto.precio
        OrderItem.objects.create(
            pedido=pedido,
            producto=producto,
            cantidad=cantidad_item,
            precio_unitario=precio_unitario
        )

# Crear reseñas
def crear_reseñas(usuarios, productos, cantidad=20):
    for _ in range(cantidad):
        usuario = choice(usuarios)
        producto = choice(productos)
        rating = randint(1, 5)
        comentario = fake.paragraph() if randint(0, 1) else None
        Reseña.objects.create(
            producto=producto,
            usuario=usuario,
            rating=rating,
            comentario=comentario
        )

# Crear direcciones
def crear_direcciones(usuarios):
    for usuario in usuarios:
        if hasattr(usuario, 'direccion'):  # Si el usuario ya tiene una dirección
            direccion = usuario.direccion
            direccion.calle = fake.street_address()
            direccion.ciudad = fake.city()
            direccion.codigo_postal = fake.postcode()
            direccion.pais = fake.country()
            direccion.save()
        else:  # Si el usuario no tiene una dirección, créala
            calle = fake.street_address()
            ciudad = fake.city()
            codigo_postal = fake.postcode()
            pais = fake.country()
            Direccion.objects.create(
                usuario=usuario,
                calle=calle,
                ciudad=ciudad,
                codigo_postal=codigo_postal,
                pais=pais
            )

# Crear métodos de pago
def crear_metodos_pago(cantidad=5):
    nombres = ['Tarjeta de Crédito', 'PayPal', 'Transferencia Bancaria', 'Criptomonedas', 'Efectivo']
    for nombre in nombres:
        descripcion = fake.sentence()
        MetodoPago.objects.create(nombre=nombre, descripcion=descripcion)

def crear_pagos(pedidos, metodos_pago):
    for pedido in pedidos:
        metodo = choice(metodos_pago)
        monto = pedido.total
        transaccion_id = fake.uuid4()
        Pago.objects.create(
            pedido=pedido,
            metodo=metodo,
            monto=monto,
            transaccion_id=transaccion_id
        )

# Crear notificaciones
def crear_notificaciones(usuarios, cantidad=20):
    for _ in range(cantidad):
        usuario = choice(usuarios)
        mensaje = fake.sentence()
        leido = choice([True, False])
        Notificacion.objects.create(usuario=usuario, mensaje=mensaje, leido=leido)

# Crear mensajes
def crear_mensajes(usuarios, cantidad=15):
    for _ in range(cantidad):
        remitente = choice(usuarios)
        destinatario = choice(usuarios)
        contenido = fake.paragraph()
        leido = choice([True, False])
        Mensaje.objects.create(remitente=remitente, destinatario=destinatario, contenido=contenido, leido=leido)

# Función principal
def poblar_db():
    print("Creando usuarios...")
    usuarios = crear_usuarios(20)
    print("Creando categorías...")
    categorias = crear_categorias(5)
    print("Creando productos...")
    productos = crear_productos(categorias, usuarios, 50)
    print("Creando pedidos...")
    pedidos = crear_pedidos(usuarios, 20)
    print("Creando items de pedido...")
    crear_order_items(pedidos, productos, 100)
    print("Creando reseñas...")
    crear_reseñas(usuarios, productos, 30)
    print("Creando direcciones...")
    crear_direcciones(usuarios)
    print("Creando métodos de pago...")
    crear_metodos_pago()
    print("Creando pagos...")
    metodos_pago = list(MetodoPago.objects.all())
    crear_pagos(pedidos, metodos_pago)
    print("Creando notificaciones...")
    crear_notificaciones(usuarios, 50)
    print("Creando mensajes...")
    crear_mensajes(usuarios, 30)
    print("¡Base de datos poblada con éxito!")

if __name__ == "__main__":
    poblar_db()