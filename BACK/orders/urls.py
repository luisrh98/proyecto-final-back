from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EnviosPendientesView, EstadisticasPedidosView, MetodoPagoList, MisPedidosView, PedidoFacturaView, PedidoViewSet, OrderItemViewSet, procesar_pago
from orders import views

router = DefaultRouter()
router.register(r'pedidos', PedidoViewSet)
router.register(r'order-items', OrderItemViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('procesar-pago/', procesar_pago, name='procesar-pago'),
    path('metodos-pago/', MetodoPagoList.as_view(), name='metodos_pago'),
    path('mis-pedidos/', MisPedidosView.as_view(), name='mis-pedidos'),
    path('envios-pendientes/', EnviosPendientesView.as_view(), name='envios-pendientes'),
    path('estadisticas-pedidos/', EstadisticasPedidosView.as_view(), name='estadisticas-pedidos'),
    path('pedido/pdf/<int:pedido_id>/', views.generar_pdf_pedido, name='generar_pdf_pedido'),
    path('factura/', PedidoFacturaView.as_view(), name='pedido_factura'),
]
