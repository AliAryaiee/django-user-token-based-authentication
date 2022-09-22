from knox.auth import AuthToken
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from rest_framework import exceptions, permissions, status
from rest_framework.authtoken.serializers import AuthTokenSerializer

from . import serializers


User = get_user_model()


class UserRegister(APIView):
    """
        User Register
    """

    # serializer_class = serializers.UserRegisterSerializer

    def post(self, request):
        """
            Create New User by POST Request
        """
        serialized_user = serializers.UserRegisterSerializer(data=request.data)

        if serialized_user.is_valid(raise_exception=True):
            # 1 - Create User and Save It Into the Database
            validated_data = serialized_user.validated_data
            del validated_data["confirm_password"]
            db_user = serialized_user.save()

            # 2 - Return Token
            _, token = AuthToken.objects.create(db_user)
            return Response({"token": token})


class UserLogin(APIView):
    """
        docstring
    """

    def post(self, request):
        """
            User Authentication
        """
        # print("DATA", request.data)
        token_serializer = AuthTokenSerializer(data=request.data)
        token_serializer.is_valid(raise_exception=True)
        validated_token_data = token_serializer.validated_data
        # print("Token Serialized Data", validated_token_data)
        user = validated_token_data["user"]
        _, token = AuthToken.objects.create(user)
        return Response({"token": token})


class UserProfile(APIView):
    """
        Retrieve User Profile
    """
    permission_classes = [permissions.IsAuthenticated]

    def get_user_object(self, user_id: str):
        """
            Get User Object
        """
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            return None

    def get(self, request):
        """
            Retrieve User Profile GET Request
        """
        user = request.user
        if user.is_authenticated:
            # print("USER", user)
            user_id = user.id or 0
            db_user = self.get_user_object(user_id=user_id)
            if db_user:
                serialized_data = serializers.UserProfileSerializer(
                    instance=db_user
                )
                return Response(serialized_data.data, status=status.HTTP_200_OK)

            return Response(
                {"response": "Token is Invalid!"},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(
            {"response": "You Must Be Authenticated!"},
            status=status.HTTP_401_UNAUTHORIZED
        )
