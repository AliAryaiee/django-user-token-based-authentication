import time
from datetime import timedelta

from knox.auth import AuthToken
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from rest_framework import exceptions, permissions, status
from rest_framework.authtoken.serializers import AuthTokenSerializer

from . import serializers, models
from .utils import send_otp_client


User = get_user_model()


class UserRegister(APIView):
    """
        User Register
    """

    def get_user_object(self, mobile: str):
        """
            Get User Object
        """
        try:
            return User.objects.get(phone=mobile)
        except User.DoesNotExist:
            return None

    def post(self, request):
        """
            Create New User by POST Request
        """
        # 0 - Check the User Exists in Database
        if self.get_user_object(request.data.get("phone")):
            response = {
                "response": f"{request.data.get('phone')} Already Exists in Database!"
            }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        serialized_user = serializers.UserRegisterSerializer(data=request.data)

        if serialized_user.is_valid(raise_exception=True):
            validated_data = serialized_user.validated_data

            # 1 - Create User and Save It Into the Database
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
class SendOTP(APIView):
    """
        Send OTP
    """

    def get_user_object(self, mobile: str):
        """
            Get User Object
        """
        try:
            return User.objects.get(phone=mobile)
        except User.DoesNotExist:
            return None

    def post(self, request):
        """
            Send OTP POST Method
        """
        serialized_mobile = serializers.MobileSerializer(data=request.data)
        serialized_mobile.is_valid(raise_exception=True)
        mobile_number = serialized_mobile.validated_data["phone"]
        if self.get_user_object(mobile_number):
            msg, otp_code = send_otp_client(mobile_number)
            print(msg)
            issued_at = int(time.time())
            expiry = timedelta(minutes=4)
            otp_data = {
                "otp_code": otp_code,
                "phone": mobile_number,
                "expiry": issued_at + int(expiry.total_seconds()),
            }
            serialized_otp = serializers.OTPSerializer(data=otp_data)
            serialized_otp.is_valid(raise_exception=True)
            serialized_otp.save()
            # return Response({"message": otp_code}, status=status.HTTP_202_ACCEPTED)
            return Response(serialized_otp.data, status=status.HTTP_202_ACCEPTED)
        return Response({}, status=status.HTTP_400_BAD_REQUEST)


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

    def get_otp_object(self, otp_code: str):
        """
            Get User Object
        """
        try:
            return models.OTP.objects.get(otp_code=otp_code)
        except models.OTP.DoesNotExist:
            return None

    def post(self, request):
        """
            Send OTP POST Method
        """
        otp_code = request.query_params["otp-code"]
        db_otp = self.get_otp_object(otp_code)
        issued_at = int(time.time())
        if db_otp:
            # print(f"OTP Query => {otp_code}")
            otp_object = serializers.OTPSerializer(instance=db_otp)
            # otp_object.is_valid(raise_exception=True)
            validated_otp = otp_object.data
            expiry = validated_otp["expiry"]
            if expiry < issued_at:
                print(expiry, issued_at)
                return Response({}, status=status.HTTP_404_NOT_FOUND)
            mobile = validated_otp["phone"]
            db_user = self.get_user_object(user_id=request.user.id)
            if db_user:
                serialized_data = serializers.UserProfileSerializer(
                    instance=db_user
                )
                user_phone_number = serialized_data.data["phone"]
                if mobile == user_phone_number:
                    return Response(validated_otp, status=status.HTTP_202_ACCEPTED)

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
                serialized_data = serializers.ChangePasswordSerializer(
                    data=request.data
                )
                serialized_data.is_valid(raise_exception=True)
                old_password = serialized_data.validated_data["old_password"]
                is_matched = db_user.check_password(old_password)
                if is_matched:
                    # 1 - Set New Password
                    new_password = serialized_data.validated_data["new_password"]
                    db_user.set_password(new_password)
                    db_user.save()

                    # 2 - Return Token
                    _, token = AuthToken.objects.create(db_user)
                    return Response({"token": token}, status=status.HTTP_200_OK)

                bad_response = {
                    "response": "Old Password Is Not Matched!"
                }
                return Response(bad_response, status=status.HTTP_400_BAD_REQUEST)


class ForgotPassword(APIView):
    """
        Forgot Password
    """

    def put(self, request):
        """
            docstring
        """
        return Response(request.data, status=status.HTTP_200_OK)


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
