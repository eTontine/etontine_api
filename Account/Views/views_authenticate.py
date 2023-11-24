from rest_framework.generics import GenericAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate, logout
from rest_framework_simplejwt.views import TokenRefreshView
from Account.models import Users
from Account.serializers import UsersSerializer

class LoginView(APIView):
    permission_classes = [AllowAny]
    serializer_class = UsersSerializer
    def post(self, request):
        phone = request.data.get('phone')
        code = request.data.get('code')

        try:
            user = Users.objects.get(phone=phone)
        except Users.DoesNotExist:
            return Response({'message': 'Incorrect phone or code!'}, status=status.HTTP_400_BAD_REQUEST)

        if not user.check_password(code):
            return Response({'message': 'Incorrect phone or code!'}, status=status.HTTP_400_BAD_REQUEST)

        refresh = RefreshToken.for_user(user)
        user.token = str(refresh.access_token)
        user.save()

        response = {
            'message': 'Welcome! Successfully connected.',
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': self.serializer_class(user).data
        }

        return Response(response, status=status.HTTP_200_OK)

class UserTokenRefreshView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == status.HTTP_200_OK:
            user = self.user
            return Response({
                'refresh': str(response.data.get('refresh')),
                'access': str(response.data.get('access')),
                'user': {
                    'id': user.id,
                    'phone': user.phone,
                }
            })
        return response

class Logout(APIView):
    def post(self, request):
        logout(request)
        return Response({'message': 'Logged out successfully'}, status=status.HTTP_200_OK)
