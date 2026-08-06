from django.contrib.auth import authenticate
from rest_framework import serializers


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        username = attrs.get("username")
        password = attrs.get("password")

        user = authenticate(username=username, password=password)

        if not user:
            raise serializers.ValidationError(
                "Invalid username or password."
            )

        if not user.is_active:
            raise serializers.ValidationError(
                "User account is disabled."
            )

        attrs["user"] = user
        return attrs

from apps.users.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
        )

from rest_framework_simplejwt.serializers import TokenRefreshSerializer


class RefreshSerializer(TokenRefreshSerializer):
    pass

from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    def save(self):
        refresh_token = self.validated_data["refresh"]
        token = RefreshToken(refresh_token)
        token.blacklist()


class CurrentUserSerializer(serializers.Serializer):
    """
    Serializer for the authenticated user's current context.
    """

    user = serializers.SerializerMethodField()
    tenant = serializers.SerializerMethodField()
    company = serializers.SerializerMethodField()

    def get_user(self, request):
        return UserSerializer(request.user).data

    def get_tenant(self, request):
        tenant = getattr(request, "tenant", None)

        if tenant is None:
            return None

        return {
            "id": str(tenant.id),
            "name": tenant.name,
            "slug": tenant.slug,
        }

    def get_company(self, request):
        company = getattr(request, "company", None)

        if company is None:
            return None

        return {
            "id": str(company.id),
            "name": company.name,
            "code": company.code,
        }