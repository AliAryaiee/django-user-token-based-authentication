from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from rest_framework import exceptions, permissions, status

from . import serializers


User = get_user_model()


class UserRegister(APIView):
    """
        User Register
    """

    def post(self, request):
        """
            Create New User by POST Request
        """
        serialized_user = serializers.UserRegisterSerializer(data=request.data)

        if serialized_user.is_valid(raise_exception=True):
            validated_data = serialized_user.validated_data
            del validated_data["confirm_password"]
            user_db = serialized_user.create(validated_data)
            serialized_response = serializers.AuthResponse(user_db)
            return Response(serialized_response.data)
