from datetime import timezone
from decimal import Decimal
from django.conf import settings
from django.http import FileResponse, HttpResponse, JsonResponse
from django.views import View
from rest_framework.response import Response
from rest_framework import viewsets, status, generics
from rest_framework.views import APIView
from django.db.models import Sum, Count, Prefetch
from io import BytesIO
from reportlab.pdfgen import canvas
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from .models import Pedido  # O ajusta según tu modelo de pedido


from products.models import Producto
from .models import MetodoPago, Pago, Pedido, OrderItem
from .serializers import PedidoFiltradoPorGestorSerializer, PedidoSerializer, OrderItemSerializer
from rest_framework.decorators import permission_classes, api_view
from rest_framework.permissions import IsAuthenticated, AllowAny
import stripe
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

class EnviosPendientesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        gestor = request.user  # Asumimos que el gestor es el usuario autenticado

        # Obtenemos los OrderItem cuyos productos pertenecen a este gestor (vendedor)
        queryset = OrderItem.objects.select_related('producto', 'pedido').filter(
            producto__vendedor=gestor,
            pedido__estado='pendiente'  # Aquí filtro los pedidos pendientes de envío (ajusta el estado si es necesario)
        )

        serializer = OrderItemSerializer(queryset, many=True)
        return Response(serializer.data)

class PedidoViewSet(viewsets.ModelViewSet):
    queryset = Pedido.objects.all()
    serializer_class = PedidoSerializer

class OrderItemViewSet(viewsets.ModelViewSet):
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer

class MetodoPagoList(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        metodos_pago = MetodoPago.objects.all().values('id', 'nombre')
        return Response(metodos_pago)
    
@permission_classes([IsAuthenticated])
class MisPedidosView(generics.ListAPIView):
    serializer_class = PedidoSerializer

    def get_queryset(self):
        return Pedido.objects.filter(usuario=self.request.user).order_by('-fecha_creacion')

# Configura la clave secreta de Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY

@api_view(['POST'])
@permission_classes([AllowAny])
def procesar_pago(request):
    try:
        # Validar que el usuario tenga una dirección configurada
        if not hasattr(request.user, 'direccion'):
            return Response({'error': 'No tienes una dirección configurada'}, status=status.HTTP_400_BAD_REQUEST)

        # Obtener datos del carrito y monto
        data = request.data
        amount = data.get('amount')  # Monto en centavos
        currency = data.get('currency', 'usd')
        cart_items = data.get('cart_items', [])
        metodo_pago_id = data.get('metodo_pago_id')

        # Validar monto mínimo
        if amount < 500:
            return Response({'error': 'El monto debe ser mayor o igual a 5 USD.'}, status=status.HTTP_400_BAD_REQUEST)

        # Crear Payment Intent en Stripe
        payment_intent = stripe.PaymentIntent.create(
            amount=amount,
            currency=currency,
            automatic_payment_methods={'enabled': True},
        )

        # Obtener dirección del usuario (ahora es OneToOne)
        direccion_usuario = request.user.direccion

        # Crear pedido con dirección copiada
        pedido = Pedido.objects.create(
            usuario=request.user,
            total=amount / 100,
            estado='pendiente',
            calle=direccion_usuario.calle,
            ciudad=direccion_usuario.ciudad,
            codigo_postal=direccion_usuario.codigo_postal,
            pais=direccion_usuario.pais
        )

        # Crear items del pedido
        for item in cart_items:
            producto = Producto.objects.get(id=item['producto_id'])
            OrderItem.objects.create(
                pedido=pedido,
                producto=producto,
                cantidad=item['cantidad'],
                precio_unitario=producto.precio
            )

        # Registrar pago
        metodo_pago = MetodoPago.objects.get(id=metodo_pago_id)
        pago = Pago.objects.create(
            pedido=pedido,
            metodo=metodo_pago,
            monto=amount / 100,
            transaccion_id=payment_intent['id']
        )

        return Response({
            'clientSecret': payment_intent['client_secret'],
            'pago_id': pago.id,
            'order_id': pedido.id,
        }, status=status.HTTP_200_OK)

    except Producto.DoesNotExist:
        return Response({'error': 'Uno o más productos no existen.'}, status=status.HTTP_404_NOT_FOUND)
    except MetodoPago.DoesNotExist:
        return Response({'error': 'Método de pago inválido'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    

def generar_pdf_pedido(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id)
    usuario = pedido.usuario

    # Crear un archivo PDF en memoria
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)

    # Definir márgenes
    margin_left = 50
    margin_top = 750  # Aumentado para mejorar el margen superior

    # Agregar un encabezado de la tienda
    p.setFont("Helvetica-Bold", 20)
    p.drawString(margin_left, margin_top, "BonShop")
    p.setFont("Helvetica", 12)
    p.drawString(margin_left, margin_top - 20, "Factura de Pedido")

    # Líneas de separación
    p.setStrokeColorRGB(0.2, 0.2, 0.8)
    p.setLineWidth(1.5)
    p.line(margin_left, margin_top - 40, 550, margin_top - 40)  # Línea bajo el título

    # Información del usuario
    p.setFont("Helvetica-Bold", 12)
    p.drawString(margin_left, margin_top - 60, f"Pedido #{pedido.id}")
    p.setFont("Helvetica", 10)
    p.drawString(margin_left, margin_top - 80, f"Usuario: {usuario.username}")
    p.drawString(margin_left, margin_top - 100, f"Nombre: {usuario.first_name} {usuario.last_name}")
    p.drawString(margin_left, margin_top - 120, f"Correo electrónico: {usuario.email}")

    # Dirección de Envío
    p.setFont("Helvetica-Bold", 12)
    p.drawString(margin_left, margin_top - 150, "Dirección de Envío:")
    p.setFont("Helvetica", 10)
    if pedido.calle and pedido.ciudad and pedido.codigo_postal and pedido.pais:
        direccion = f"{pedido.calle}, {pedido.ciudad}, {pedido.codigo_postal}, {pedido.pais}"
    else:
        direccion = "Sin dirección disponible"
    p.drawString(margin_left, margin_top - 170, direccion)

    # Estado y Total
    p.setFont("Helvetica-Bold", 12)
    p.drawString(margin_left, margin_top - 200, f"Estado: {pedido.estado}")
    p.drawString(margin_left, margin_top - 220, f"Total: {pedido.total} €")

    # Línea de separación
    p.setStrokeColorRGB(0.5, 0.5, 0.5)
    p.setLineWidth(0.5)
    p.line(margin_left, margin_top - 240, 550, margin_top - 240)

    # Productos en formato tabla
    p.setFont("Helvetica-Bold", 12)
    p.drawString(margin_left, margin_top - 260, "Productos:")
    p.setFont("Helvetica", 10)

    y_position = margin_top - 280
    for item in pedido.items.all():
        p.drawString(margin_left, y_position, f"{item.cantidad} x {item.producto.titulo} - {item.precio_unitario} €")
        y_position -= 15

    # Línea de separación de productos
    p.setStrokeColorRGB(0.5, 0.5, 0.5)
    p.line(margin_left, y_position - 10, 550, y_position - 10)

    # Detalles de pago
    if pedido.pago:
        p.setFont("Helvetica-Bold", 12)
        p.drawString(margin_left, y_position - 30, "Detalles del Pago:")
        p.setFont("Helvetica", 10)
        p.drawString(margin_left, y_position - 50, f"Método de pago: {pedido.pago.metodo.nombre}")
        p.drawString(margin_left, y_position - 70, f"Transacción ID: {pedido.pago.transaccion_id}")
        p.drawString(margin_left, y_position - 90, f"Fecha de pago: {pedido.pago.fecha_transaccion.strftime('%d-%m-%Y %H:%M:%S')}")
    
    # Añadir pie de página con el logo de la tienda (si tienes)
    p.setFont("Helvetica-Oblique", 8)
    p.drawString(margin_left, y_position - 120, "Gracias por comprar con nosotros!")
    p.drawString(450, y_position - 120, "www.bonshop.vercel.app")

    # Termina el PDF y vuelve al principio del archivo
    p.showPage()
    p.save()
    buffer.seek(0)

    # Crea una respuesta para enviar el PDF
    response = FileResponse(buffer, as_attachment=True, filename=f"pedido_{pedido_id}.pdf")
    return response

class EstadisticasPedidosView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        # Total de pedidos
        total_pedidos = Pedido.objects.count()

        # Total de ingresos
        ingresos_totales = Pago.objects.aggregate(total_ingresos=Sum('monto'))['total_ingresos'] or 0

        # Promedio por pedido
        promedio_pedido = ingresos_totales / total_pedidos if total_pedidos > 0 else 0

        # Productos vendidos
        productos_vendidos = OrderItem.objects.aggregate(total_vendidos=Sum('cantidad'))['total_vendidos'] or 0


        # Datos a retornar
        estadisticas = {
            'total_pedidos': total_pedidos,
            'ingresos_totales': ingresos_totales,
            'promedio_pedido': promedio_pedido,
            'productos_vendidos': productos_vendidos,
            'beneficios_totales': ingresos_totales * Decimal('0.05'),
        }

        return Response(estadisticas)
    
class PedidoFacturaView(APIView):
    permission_classes = [AllowAny]  # Si se requiere autenticación

    def get(self, request):
        payment_intent_id = request.query_params.get('paymentIntentId')

        if not payment_intent_id:
            return Response({'error': 'paymentIntentId es requerido.'}, status=400)

        try:
            # Buscar el pago utilizando el paymentIntentId
            pago = Pago.objects.get(transaccion_id=payment_intent_id)
            pedido = pago.pedido  # Obtener el pedido relacionado con el pago

            # Obtener los detalles del pedido
            factura_data = {
                'id': pedido.id,
                'amount_paid': int(pago.monto * 100),  # Si el monto está en EUR, asegúrate de convertirlo a centavos
                'currency': 'eur',  # O la moneda que estés utilizando
                'status': pedido.estado,
                'created': pago.fecha_transaccion.timestamp(),
                'order_id': pedido.id
            }

            return Response(factura_data, status=200)

        except Pago.DoesNotExist:
            return Response({'error': 'Pago no encontrado para este paymentIntentId.'}, status=404)
        except Exception as e:
            return Response({'error': str(e)}, status=500)