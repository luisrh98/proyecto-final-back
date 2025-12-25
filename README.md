Instalar virtual enviroment:
    python -m virtualenv venv

Modulos instalados dentro del virtual enviroment:
    pip install django
    python -m pip install Pillow
    pip install psycopg2
    pip install djangorestframework 
    pip install djangorestframework-simplejwt
    pip install faker
    pip install djangorestframework dj-rest-auth
    pip install django-cors-headers
    pip install django-cookies-samesite


Para generar un archivo Requirements.txt:
    pip freeze > requirements.txt
Para instalarlo:
    pip install -r requirements.txt


Ejemplo de Endpoints Generados
Vistas y configuraciones:

Usuarios

    GET /api/accounts/usuarios/: Lista todos los usuarios.
    POST /api/accounts/usuarios/: Crea un nuevo usuario (registro).
    GET /api/accounts/usuarios/<id>/: Detalles de un usuario específico.
    PUT /api/accounts/usuarios/<id>/: Actualiza un usuario.
    DELETE /api/accounts/usuarios/<id>/: Elimina un usuario.

Categorías

    GET /api/products/categorias/: Lista todas las categorías.
    POST /api/products/categorias/: Crea una nueva categoría.
    GET /api/products/categorias/<id>/: Detalles de una categoría específica.
    PUT /api/products/categorias/<id>/: Actualiza una categoría.
    DELETE /api/products/categorias/<id>/: Elimina una categoría.

Productos

    GET /api/products/productos/: Lista todos los productos.
    POST /api/products/productos/: Crea un nuevo producto.
    GET /api/products/productos/<id>/: Detalles de un producto específico.
    PUT /api/products/productos/<id>/: Actualiza un producto.
    DELETE /api/products/productos/<id>/: Elimina un producto.

Pedidos

    GET /api/orders/pedidos/: Lista todos los pedidos.
    POST /api/orders/pedidos/: Crea un nuevo pedido.
    GET /api/orders/pedidos/<id>/: Detalles de un pedido específico.
    PUT /api/orders/pedidos/<id>/: Actualiza un pedido.
    DELETE /api/orders/pedidos/<id>/: Elimina un pedido.

Notificaciones

    GET /api/communications/notificaciones/: Lista todas las notificaciones.
    POST /api/communications/notificaciones/: Crea una nueva notificación.
    GET /api/communications/notificaciones/<id>/: Detalles de una notificación específica.
    PUT /api/communications/notificaciones/<id>/: Actualiza una notificación.
    DELETE /api/communications/notificaciones/<id>/: Elimina una notificación.



                                                        FRONT
    
    instalar vue:

        npm install -g @vue/cli

    instalar modulos:

        npm install axios
        npm install vue-router@4
        npm install -D sass-embedded
        npm install jwt-decode
        npm install @mdi/js
        npm install --save nuxt-stripe-module
        npm install @stripe/stripe-js
