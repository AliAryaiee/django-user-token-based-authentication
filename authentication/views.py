from base64 import urlsafe_b64encode

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


# OTP
class Mobile(object):
    """
        Mobile Number
    """

    def __init__(self, mobile: str):
        """
            docstring
        """
        self.number = mobile


class Operator(object):
    """
        Operator
    """

    MTN = ["093", "090"]
    MCI = ["091", "099"]

    def set_operator(self, mobile: Mobile):
        """
            docstring
        """
        operator = self._get_operator_(mobile)
        return operator(mobile)

    def _get_operator_(self, mobile: Mobile):
        """
            docstring
        """
        if mobile.number[:3] in self.MTN:
            return self.set_mtn
        if mobile.number[:3] in self.MCI:
            return self.set_mci

    def set_mtn(self, mobile: Mobile):
        """
            docstring
        """
        mobile.operator = "MTN"
        print(f"Mobile {mobile.number} Is Belong to MTN")

    def set_mci(self, mobile: Mobile):
        """
            docstring
        """
        mobile.operator = "MCI"
        print(f"Mobile {mobile.number} Is Belong to MCI")


class SendOTP(APIView):
    """
        Send OTP
    """

    def post(self, request):
        """
            Send OTP POST Method
        """
        serialized_data = serializers.MobileSerializer(data=request.data)
        serialized_data.is_valid(raise_exception=True)
        mobile_number = serialized_data.validated_data["mobile"]
        mobile = Mobile(mobile_number)
        operator = Operator()
        operator.set_operator(mobile)
        return Response({})


class ConfirmOTP(APIView):
    """
        Confirm OTP
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

    def post(self, request):
        """
            Send OTP POST Method
        """
        otp_code = request.query_params["otp-code"]
        user = request.user
        if user.is_authenticated:
            user_id = user.id or 0
            db_user = self.get_user_object(user_id=user_id)
            if db_user:
                serialized_data = serializers.UserProfileSerializer(
                    instance=db_user
                )

                mobile = Mobile(serialized_data.data["phone"])
                operator = Operator()
                operator.set_operator(mobile)
                print(f"OTP {otp_code} <=> {mobile.number}")
                return Response({}, status=status.HTTP_200_OK)

        return Response({}, status=status.HTTP_400_BAD_REQUEST)


# Change Password
class UserChangePassword(APIView):
    """
        Change User Password
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

    def put(self, request):
        """
            Change User Password POST Request
        """
        user = request.user
        if user.is_authenticated:
            user_id = user.id or 0
            db_user = self.get_user_object(user_id=user_id)
            if db_user:
                serialized_data = serializers.UserSerializer(
                    instance=db_user
                )
                validated_data = serialized_data.validated_data
                # url

                return Response(serialized_data.data, status=status.HTTP_200_OK)

            return Response(
                {"response": "Token is Invalid!"},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(
            {"response": "You Must Be Authenticated!"},
            status=status.HTTP_401_UNAUTHORIZED
        )


# Users's Tokens
class UserTokens(APIView):
    """
        Tokens
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

    def get_tokens(self, user_id: str):
        """
            Get
        """
        try:
            return AuthToken.objects.all().filter(user=user_id)
        except:
            return None

    def post(self, request):
        """
            Retrieve List of User's Token
        """
        user = request.user
        if user.is_authenticated:
            # user_id = user.username
            user_id = user.id
            print("USER ID", user_id)
            db_tokens = self.get_user_object(user_id=user_id)
            if db_tokens:
                tokens_db = self.get_tokens(user_id)
                serialized_tokens = serializers.TokenSerializer(
                    instance=tokens_db,
                    many=True
                )
                tokens = [
                    token["digest"]
                    for token in serialized_tokens.data
                ]
                response = {
                    "user_id": user_id,
                    "username": user.username,
                    "tokens": tokens
                }
                return Response(response)

            return Response({})
