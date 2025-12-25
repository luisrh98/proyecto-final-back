from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny


class HomeView(APIView):
    permission_classes = [AllowAny]  # Permite el acceso público

    def get(self, request):
        return Response({"message": "Welcome to the Home Page!"})