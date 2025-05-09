from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from .models import User

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(email=data['email'], password=data['password'])
        if not user:
            raise serializers.ValidationError('Invalid email or password')
        if not user.is_active:
            raise serializers.ValidationError('Account is inactive')
        data['user'] = user
        return data

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ['email', 'phone_number', 'full_name', 'password', 'age', 'avatar', 'gender']

    def validate_password(self, value):
        validate_password(value)
        return value

    def create(self, validated_data):
        password = validated_data.pop('password')
        validated_data['role'] = 'student'
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        return user

    def validate(self, data):
        if 'role' in data or 'is_staff' in data or 'is_superuser' in data:
            raise serializers.ValidationError("You can't set role or permissions directly.")
        return data

class BaseUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id', 'email', 'phone_number', 'full_name', 'age', 'avatar',
            'gender', 'role', 'bio', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ('id', 'created_at', 'updated_at')
        extra_kwargs = {
            'role': {'read_only': True},
            'is_active': {'read_only': True},
        }

class UserSerializer(BaseUserSerializer):
    password = serializers.CharField(write_only=True, required=False)

    class Meta(BaseUserSerializer.Meta):
        fields = BaseUserSerializer.Meta.fields + ['password']

    def validate_password(self, value):
        if value:
            try:
                validate_password(value)
            except serializers.ValidationError as e:
                raise serializers.ValidationError(f"Password is not strong enough: {e}")
        return value

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        validated_data.setdefault('role', 'student')
        user = User.objects.create_user(**validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user

class UserDetailSerializer(BaseUserSerializer):
    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
